import asyncio
import logging
import os.path
import time
from typing import Optional, Dict, Any, List, Union

import torch
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
from ray import serve
from ray.serve.handle import DeploymentHandle
from sentence_transformers import SentenceTransformer

from ray_embedding.mixins import RecyclableMixin


@serve.deployment
class EmbeddingModel(RecyclableMixin):
    FAILED_NODE_REASON = "EmbeddingModel replica is colocated with a failed node."
    FAILED_NODE_LOG_NAME = "EmbeddingModel"

    def __init__(self, model: str, served_model_name: Optional[str] = None,
                 device: Optional[str] = None, backend: Optional[str] = "torch",
                 matryoshka_dim: Optional[int] = None, trust_remote_code: Optional[bool] = False,
                 model_kwargs: Dict[str, Any] = None, cuda_memory_flush_threshold: Optional[float] = 0.8, *,
                 node_recycler: DeploymentHandle = None):
        """Initialize the embedding model replica and register it with the NodeRecycler."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(node_recycler)
        self.model = model
        self.served_model_name = served_model_name or os.path.basename(self.model)
        self.init_device = device
        self.cuda_memory_flush_threshold = cuda_memory_flush_threshold
        self.torch_device = torch.device(self.init_device)
        self.backend = backend or "torch"
        self.matryoshka_dim = matryoshka_dim
        self.trust_remote_code = trust_remote_code or False
        self.model_kwargs = model_kwargs or {}

        if self.init_device is None or self.init_device == "auto":
            self.init_device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.init_device == "cuda":
            self.wait_for_cuda()

        self.logger.info(f"Initializing embedding model: {self.model}")
        self.embedding_model = SentenceTransformer(self.model, device=self.init_device, backend=self.backend,
                                                   trust_remote_code=self.trust_remote_code,
                                                   model_kwargs=self.model_kwargs)

        self.logger.info(f"Successfully initialized model {self.model} using device {self.torch_device}")
        asyncio.get_event_loop().create_task(self._register_with_node_recycler())

    async def __call__(self, text: Union[str, List[str]], dimensions: Optional[int] = None) -> List[List[float]]:
        """Compute embeddings for the input text using the current model."""
        if not text or (isinstance(text, list) and not all(text)):
            raise ValueError("Input text is empty or invalid")

        text = [text] if isinstance(text, str) else text
        truncate_dim = dimensions or self.matryoshka_dim

        # Compute embeddings in PyTorch format
        embeddings = self.embedding_model.encode(
            text, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False,
        ).to(self.torch_device)

        if truncate_dim is not None:
            # Truncate and re-normalize the embeddings
            embeddings = embeddings[:, :truncate_dim]
            embeddings = embeddings / torch.norm(embeddings, dim=1, keepdim=True)

        # Move all embeddings to CPU at once before conversion
        embeddings_list = embeddings.cpu().tolist()

        # don't wait for GC
        del embeddings

        return embeddings_list

    def wait_for_cuda(self, wait: int = 10):
        """Block until CUDA is available or report the replica as unhealthy."""
        if self.init_device == "cuda" and not torch.cuda.is_available():
            time.sleep(wait)
        error_message = self._evaluate_cuda_health()
        if error_message:
            self.logger.error(f"CUDA health check failed during initialization: {error_message}")
            asyncio.get_event_loop().create_task(self._report_cuda_failure_async(error_message))
            raise RuntimeError(error_message)

    async def check_health(self):
        """Verify CUDA availability; immediately fail if this replica was already told by the NodeRecycler to shutdown."""
        if self._failed_node_error:
            raise RuntimeError(self._failed_node_error)
        error_message = self._evaluate_cuda_health()
        if error_message:
            self.logger.error(f"CUDA health check failed during health probe: {error_message}")
            await self.report_cuda_failure(error_message)
            raise RuntimeError(error_message)

    def _evaluate_cuda_health(self) -> Optional[str]:
        """Return an error string if CUDA appears unhealthy, otherwise None."""
        if self.init_device != "cuda":
            return None

        try:
            # Even though CUDA was available at init time,
            # CUDA can become unavailable - this is a known problem in AWS EC2+Docker
            # https://github.com/ray-project/ray/issues/49594
            nvmlInit()
            count = nvmlDeviceGetCount()
            assert count >= 1, "No CUDA devices found"

            # replicas only have access to GPU 0
            handle = nvmlDeviceGetHandleByIndex(0)
            mem_info = nvmlDeviceGetMemoryInfo(handle)
        except Exception as e:
            return f"CUDA health check failed: {e}"

        reserved = torch.cuda.memory_reserved()  # bytes currently reserved by CUDA cache
        threshold_bytes = self.cuda_memory_flush_threshold * mem_info.total

        if reserved > threshold_bytes:
            # flush only when cache exceeds the percentage threshold
            self.logger.warning(f"CUDA cache exceeded {self.cuda_memory_flush_threshold} ({threshold_bytes} bytes)")
            torch.cuda.empty_cache()

        return None

    def __del__(self):
        """Free torch resources when the replica object is destroyed."""
        # Clean up and free any remaining GPU memory
        try:
            if hasattr(self, 'embedding_model'):
                del self.embedding_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")

    async def _report_cuda_failure_async(self, error_message: str):
        """Report an unhealthy replica asynchronously (used during synchronous init)."""
        await self.report_cuda_failure(error_message)
