from typing import Optional, Tuple

from ray import serve
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

    async def _refresh_failed_node_status(self) -> Optional[str]:
        """Poll the NodeRecycler to determine if this replica's node is unhealthy."""
        node_ip = self._get_current_node_ip()
        if not node_ip:
            return self._failed_node_error
        try:
            reason = await self.node_recycler.get_failed_node_reason.remote(node_ip)
        except Exception as exc:
            self.logger.warning(f"Failed to pull node failure status from NodeRecycler: {exc}")
            return self._failed_node_error

        if reason and reason != self._failed_node_error:
            self._failed_node_error = reason or self.FAILED_NODE_REASON
            self.logger.error(
                f"{self.FAILED_NODE_LOG_NAME} replica marked unhealthy on {node_ip}: {self._failed_node_error}"
            )
        return self._failed_node_error

    async def report_cuda_failure(self, error_message: str) -> Optional[str]:
        """Report a CUDA failure for the current replica to the NodeRecycler."""
        if not error_message:
            return None
        context = self._gather_replica_context()
        if not context:
            message = "Replica context unavailable while reporting CUDA failure to NodeRecycler."
            self.logger.error(message)
            return message
        replica_full_id, node_ip = context
        ack = await self.node_recycler.report_failure.remote(replica_full_id, node_ip, error_message)
        self._log_node_recycler_response(ack, "Failed to report CUDA failure to NodeRecycler")
        return ack

    def _log_node_recycler_response(self, ack: Optional[str], failure_message: str):
        """Log the response from the NodeRecycler uniformly across replica types."""
        if isinstance(ack, str) and ack and "unavailable" not in ack.lower():
            self.logger.info(ack)
        else:
            self.logger.error(f"{failure_message}: {ack}")

    def _gather_replica_context(self) -> Optional[Tuple[str, str]]:
        """Return the replica full ID (Serve actor name) and node IP for this context."""
        try:
            context = serve.get_replica_context()
        except Exception:
            context = None

        if context is None:
            return None

        replica_id_obj = getattr(context, "replica_id", None)
        if replica_id_obj is None:
            return None
        try:
            replica_full_id = replica_id_obj.to_full_id_str()
        except Exception:
            return None
        node_ip = self._get_current_node_ip()
        if not (node_ip and replica_full_id):
            return None
        return replica_full_id, node_ip

    def _get_current_node_ip(self) -> Optional[str]:
        """Return the IP address of the node running the current process."""
        try:
            return get_node_ip_address()
        except Exception:
            return None
