from typing import Optional, Tuple

from ray import serve
from ray.serve._private.common import REPLICA_ID_FULL_ID_STR_PREFIX
from ray.serve.handle import DeploymentHandle
from ray.util import get_node_ip_address


class RecyclableMixin:
    """Shared helpers for Serve replicas that coordinate with the NodeRecycler."""

    FAILED_NODE_REASON = "Serve replica is colocated with a failed node."
    FAILED_NODE_LOG_NAME = "Serve"

    def __init__(self, node_recycler: DeploymentHandle):
        if node_recycler is None:
            raise ValueError("A NodeRecycler deployment handle is required.")
        self.node_recycler = node_recycler
        self._failed_node_error: Optional[str] = None

    async def mark_failed_node(self, node_ip: Optional[str] = None, reason: Optional[str] = None):
        """Record that this replica resides on a failed node so health checks error."""
        message = reason or self.FAILED_NODE_REASON
        self._failed_node_error = message
        node_suffix = f" on {node_ip}" if node_ip else ""
        self.logger.error(f"{self.FAILED_NODE_LOG_NAME} replica marked unhealthy{node_suffix}: {message}")

    async def _register_with_node_recycler(self) -> Optional[str]:
        """Register the current replica with the NodeRecycler and log the result."""
        context = self._gather_replica_context()
        if not context:
            message = "Replica context unavailable while registering with NodeRecycler."
            self.logger.error(message)
            return message
        replica_id, node_ip, actor_name = context
        ack = await self.node_recycler.register_replica.remote(replica_id, node_ip, actor_name)
        self._log_node_recycler_response(ack, "Failed to register replica with NodeRecycler")
        return ack

    async def report_cuda_failure(self, error_message: str) -> Optional[str]:
        """Report a CUDA failure for the current replica to the NodeRecycler."""
        if not error_message:
            return None
        context = self._gather_replica_context()
        if not context:
            message = "Replica context unavailable while reporting CUDA failure to NodeRecycler."
            self.logger.error(message)
            return message
        replica_id, node_ip, actor_name = context
        ack = await self.node_recycler.report_failure.remote(replica_id, node_ip, error_message, actor_name)
        self._log_node_recycler_response(ack, "Failed to report CUDA failure to NodeRecycler")
        return ack

    def _log_node_recycler_response(self, ack: Optional[str], failure_message: str):
        """Log the response from the NodeRecycler uniformly across replica types."""
        if isinstance(ack, str) and ack and "unavailable" not in ack.lower():
            self.logger.info(ack)
        else:
            self.logger.error(f"{failure_message}: {ack}")

    def _gather_replica_context(self) -> Optional[Tuple[str, str, Optional[str]]]:
        """Return the replica id, node IP, and actor name for the current context."""
        try:
            context = serve.get_replica_context()
        except Exception:
            context = None

        if context is None:
            return None

        replica_id = getattr(context, "replica_tag", None)
        node_ip = self._get_current_node_ip()
        if not (replica_id and node_ip):
            return None
        actor_name = self._build_replica_actor_name(context)
        return replica_id, node_ip, actor_name

    def _build_replica_actor_name(self, context) -> Optional[str]:
        """Construct the Serve actor name for the current replica context."""
        try:
            replica_tag = getattr(context, "replica_tag", None)
            deployment = getattr(context, "deployment", None)
            app_name = getattr(context, "app_name", "")
        except Exception:
            return None

        if not (replica_tag and deployment):
            return None

        suffix = f"{deployment}#{replica_tag}"
        if app_name:
            suffix = f"{app_name}#{suffix}"
        return f"{REPLICA_ID_FULL_ID_STR_PREFIX}{suffix}"

    def _get_current_node_ip(self) -> Optional[str]:
        """Return the IP address of the node running the current process."""
        try:
            return get_node_ip_address()
        except Exception:
            return None
