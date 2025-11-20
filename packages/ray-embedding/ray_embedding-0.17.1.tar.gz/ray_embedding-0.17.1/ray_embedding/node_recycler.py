import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple

from ray import serve


NODE_RECYCLER_DEPLOYMENT_NAME = "NodeRecycler"


@serve.deployment
class NodeRecycler:
    def __init__(
        self,
        ssh_user: str,
        ssh_private_key: str,
        retention_seconds: int = 900,
        recycle_interval_seconds: int = 60,
    ):
        """Create the NodeRecycler task that tracks unhealthy nodes and terminates them."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ssh_user = ssh_user
        key_path = Path(ssh_private_key).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"SSH private key not found: {key_path}")
        self.ssh_private_key = key_path.as_posix()
        self.retention_seconds = retention_seconds
        self.recycle_interval_seconds = max(30, recycle_interval_seconds)

        self._unhealthy_replicas: Dict[str, Dict[str, Any]] = {}
        self._nodes_marked_for_recycle: Dict[str, Dict[str, Any]] = {}
        self._nodes_inflight: Set[str] = set()

        loop = asyncio.get_event_loop()
        self._recycler_task = loop.create_task(self._recycle_loop())
        self.logger.info("NodeRecycler initialized; monitoring unhealthy nodes for recycling")

    def __del__(self):
        if hasattr(self, "_recycler_task") and self._recycler_task and not self._recycler_task.done():
            self._recycler_task.cancel()

    async def report_failure(self, replica_full_id: str, node_ip: str, error: Optional[str] = None) -> str:
        """Mark a replica/node as unhealthy and track it for recycling."""
        timestamp = time.time()
        failure_reason = error or "Replica reported unhealthy state"
        self._unhealthy_replicas[replica_full_id] = {
            "node_ip": node_ip,
            "error": error,
            "timestamp": timestamp,
        }
        existing_entry = self._nodes_marked_for_recycle.get(node_ip)
        node_entry = {
            "timestamp": existing_entry.get("timestamp", timestamp) if existing_entry else timestamp,
            "reason": failure_reason,
            "ready": existing_entry.get("ready", False) if existing_entry else False,
        }
        node_entry["reason"] = failure_reason
        # Ensure the node waits at least one recycle cycle before shutdown.
        if not existing_entry:
            node_entry["ready"] = False
        self._nodes_marked_for_recycle[node_ip] = node_entry
        ack = f"Replica {replica_full_id} on {node_ip} marked for recycling: {failure_reason}"
        self.logger.warning(ack)
        self._purge_stale()
        return ack

    async def check_node_health(self, node_ip: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Return whether a node is healthy along with its recorded failure reason, if any."""
        if not node_ip:
            return True, None

        node_entry = self._nodes_marked_for_recycle.get(node_ip)
        if not node_entry:
            return True, None

        reason = node_entry.get("reason") or "Node marked for recycling"
        return False, reason

    def _get_unhealthy_node_ips(self) -> List[str]:
        """Return the list of node IPs currently marked for recycling."""
        self._purge_stale()
        return list(self._nodes_marked_for_recycle.keys())

    async def _recycle_loop(self):
        """Background loop that periodically advances and executes recycle workflows."""
        while True:
            try:
                await asyncio.sleep(self.recycle_interval_seconds)
                await self._recycle_pending_nodes()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.warning(f"Unexpected error in recycle loop: {exc}")

    async def _recycle_pending_nodes(self):
        """Process nodes marked for recycling, deferring one cycle to allow cleanup."""
        nodes = self._get_unhealthy_node_ips()
        for node_ip in nodes:
            if node_ip in self._nodes_inflight:
                continue
            node_entry = self._nodes_marked_for_recycle.get(node_ip)
            if not node_entry:
                continue
            if not node_entry.get("ready"):
                node_entry["ready"] = True
                self.logger.info(f"Node {node_ip} scheduled for recycling on next cycle to allow graceful shutdown")
                continue
            self._nodes_inflight.add(node_ip)
            try:
                self.logger.info(f"Initiating recycle workflow for node {node_ip}")
                await self._recycle_node(node_ip)
                self._clear_node(node_ip)
                self.logger.info(f"Successfully recycled node {node_ip}")
            except Exception as exc:
                self.logger.error(f"Failed to recycle node {node_ip}: {exc}")
            finally:
                self._nodes_inflight.discard(node_ip)

    async def _recycle_node(self, node_ip: str):
        """Issue the shutdown command for a node marked as unhealthy."""
        ssh_command = [
            "ssh",
            "-i",
            self.ssh_private_key,
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.ssh_user}@{node_ip}",
            "docker stop ray_container",
        ]

        self.logger.info(f"Recycling node {node_ip} via SSH")
        process = await asyncio.create_subprocess_exec(
            *ssh_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()
            raise RuntimeError(
                f"SSH command failed with code {process.returncode}. stdout={stdout_text} stderr={stderr_text}"
            )

    def _clear_node(self, node_ip: str):
        """Remove all tracking data for a node that has been recycled."""
        to_delete = [replica for replica, data in self._unhealthy_replicas.items() if data.get("node_ip") == node_ip]
        for replica in to_delete:
            self._unhealthy_replicas.pop(replica, None)
        self._nodes_marked_for_recycle.pop(node_ip, None)

    def _purge_stale(self):
        """Remove stale replica/node tracking entries once their retention window expires."""
        if not self.retention_seconds:
            return
        cutoff = time.time() - self.retention_seconds
        replica_ids = [replica_id for replica_id, data in self._unhealthy_replicas.items()
                       if data.get("timestamp", 0) < cutoff]
        for replica_id in replica_ids:
            node_ip = self._unhealthy_replicas[replica_id]["node_ip"]
            self._unhealthy_replicas.pop(replica_id, None)
            node_entry = self._nodes_marked_for_recycle.get(node_ip)
            if node_entry and node_entry.get("timestamp", 0) < cutoff:
                self._clear_node(node_ip)
