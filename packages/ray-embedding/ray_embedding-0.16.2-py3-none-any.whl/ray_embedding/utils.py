from typing import Optional, Tuple

from ray import serve
from ray.serve._private.common import REPLICA_ID_FULL_ID_STR_PREFIX
from ray.serve.handle import DeploymentHandle
from ray.util import get_node_ip_address, state

from ray_embedding.node_recycler import NODE_RECYCLER_DEPLOYMENT_NAME


def get_head_node_id() -> Tuple[str, str]:
    """Return the head node's (node_id, node_ip) or raise if it cannot be found."""
    try:
        nodes = state.list_nodes(filters=[("is_head_node", "=", True)])
        if not nodes:
            raise RuntimeError("Unable to locate head node for NodeRecycler deployment.")
        head_node = nodes[0]
        return head_node["node_id"], head_node["node_ip"]
    except Exception as exc:
        raise RuntimeError("Unable to locate the head node ID for NodeRecycler deployment.") from exc


def get_node_recycler_handle() -> DeploymentHandle:
    """Return a deployment handle to the NodeRecycler actor, creating one if needed."""
    try:
        return serve.context.get_deployment_handle(NODE_RECYCLER_DEPLOYMENT_NAME)
    except Exception:
        return serve.get_deployment(NODE_RECYCLER_DEPLOYMENT_NAME).get_handle(sync=False)


def get_current_replica_tag() -> Optional[str]:
    """Return the current Serve replica tag, if running inside a replica context."""
    try:
        context = serve.context.get_current_replica_context()
    except Exception:
        context = None
    if context is None:
        return None
    return getattr(context, "replica_tag", None)


def get_current_node_ip() -> Optional[str]:
    """Return the IP address of the node running the current process."""
    try:
        return get_node_ip_address()
    except Exception:
        return None


def _resolve_node_recycler_handle(node_recycler: Optional[DeploymentHandle]) -> Optional[DeploymentHandle]:
    """Ensure we have a deployment handle for the NodeRecycler regardless of caller wiring."""
    if node_recycler is not None:
        return node_recycler
    try:
        return get_node_recycler_handle()
    except Exception:
        return None


def _gather_replica_context() -> Optional[Tuple[str, str, Optional[str]]]:
    """Return the current replica id, node IP, and actor name tuple if available."""
    try:
        context = serve.get_replica_context()
    except Exception:
        context = None

    if context is None:
        return None

    replica_id = getattr(context, "replica_tag", None)
    node_ip = get_current_node_ip()
    if not (replica_id and node_ip):
        return None

    actor_name = _build_replica_actor_name(context)
    return replica_id, node_ip, actor_name


def _build_replica_actor_name(context) -> Optional[str]:
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


async def register_replica_with_node_recycler(node_recycler: Optional[DeploymentHandle] = None) -> Optional[str]:
    """Register the current replica with the NodeRecycler so it can receive failure notices."""
    context = _gather_replica_context()
    if not context:
        return "Replica context unavailable while registering with NodeRecycler."
    handle = _resolve_node_recycler_handle(node_recycler)
    if handle is None:
        return "NodeRecycler handle unavailable while registering replica."
    replica_id, node_ip, actor_name = context
    return await handle.register_replica.remote(replica_id, node_ip, actor_name)


async def report_unhealthy_replica(error: Optional[str] = None,
                                   node_recycler: Optional[DeploymentHandle] = None) -> Optional[str]:
    """Asynchronously report the current replica as unhealthy to the NodeRecycler."""
    handle, replica_data = _resolve_failure_report_context(node_recycler)
    if not handle or replica_data is None:
        return "NodeRecycler context unavailable while reporting unhealthy replica."
    replica_id, node_ip, actor_name = replica_data
    return await handle.report_failure.remote(replica_id, node_ip, error, actor_name)


def _resolve_failure_report_context(
    node_recycler: Optional[DeploymentHandle],
) -> Tuple[Optional[DeploymentHandle], Optional[Tuple[str, str, Optional[str]]]]:
    """Common helper to gather replica context and recycler handle for reporting."""
    context = _gather_replica_context()
    if not context:
        return None, None
    handle = _resolve_node_recycler_handle(node_recycler)
    if handle is None:
        return None, None
    return handle, context
