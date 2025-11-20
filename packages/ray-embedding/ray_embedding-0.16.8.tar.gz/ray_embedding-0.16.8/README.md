# Ray Embedding package

`ray-embedding` is a Python package that includes everything needed to host SentenceTransformers models in a Ray cluster. The models are exposed through an OpenAI-compatible API. The `ray-embedding` package provides:

- A FastAPI-based `ModelRouter` that accepts requests, shards large batches, and fans out work to autoscaled instances/replicas of models.
- An `EmbeddingModel` that encapsulates any embedding model compatible with `sentence-transformers`, handles Matryoshka truncation, and performs asynchronous CUDA health checks so GPU failures can be reported.
- A `NodeRecycler` supervisor that tracks failure reports from replicas, exposes a pull-based health lookup so colocated replicas/routers can detect failed nodes, and recycles the underlying worker node safely after requesting graceful termination.

This library is designed for the [embedding-models Ray cluster](https://bitbucket.org/docorto/embedding-models/src/dev/), but can be embedded in any Serve app with similar requirements.  See the [reference Serve configuration](https://bitbucket.org/docorto/embedding-models/src/dev/serve-config/serve-config.yaml) for production defaults.

## Architecture

The deployment is organised into three building blocks: API ingress, model replicas, and the recycler that ties health reporting to infrastructure level actions.

![Architecture diagram](docs/diagrams/architecture.png)

1. Clients call the ModelRouter using standard OpenAI embedding verbs.
2. The ModelRouter shards requests into batches and invokes the selected embedding replica.
3. Each replica reports GPU/CUDA failures to the NodeRecycler and periodically polls it to see whether the local node has been quarantined due to another replica’s failure.
4. When a node is marked unhealthy, the NodeRecycler waits one recycle cycle for graceful shutdown, requests `__ray_terminate__` on the affected replicas, then issues an SSH stop to the Ray worker’s Docker container. Ray will automatically restart the stopped worker.

## Failure & Recycling Workflow

When a replica hits a CUDA error (or any fatal condition), the recycler coordinates a graceful drain so clients experience deterministic errors while Ray’s autoscaler replaces the failed node.

![Failure workflow diagram](docs/diagrams/failure_workflow.png)

1. The ModelRouter dispatches a batch and receives an exception from a replica.
2. The replica reports the failure; the NodeRecycler records the node as unhealthy. Peers and routers detect the failed node on their next health poll and begin failing their health checks.
3. During the next recycle cycle, the NodeRecycler invokes `__ray_terminate__` on every remaining replica handle so they can flush in-flight work, then the node is terminated via SSH.

## Quickstart

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-build.txt  # optional, for packaging
   ```
2. **Package & upload models (optional)** – store SentenceTransformers-compatible checkpoints accessible to your Ray cluster.
3. **Deploy to Ray Serve**
   ```bash
   ray pipeline submit serve-config.yaml
   ```
   Update `serve-config.yaml` to point at your models, GPU sizing, and SSH credentials for the recycler.

## Local Development

1. Create a virtual environment and install the package in editable mode: `pip install -e .[dev]` (see `pyproject.toml` for extras).
2. Run lint/test tools of your choice; as a quick syntax check you can execute `python -m compileall ray_embedding`.
3. Update docs/Serve configs and regenerate diagrams as needed (see below).

## Diagram Sources

High-resolution PNGs live under `docs/diagrams` so Bitbucket renders them inline.  To edit them:

```bash
# Edit the .mmd files under docs/diagrams
npx -y @mermaid-js/mermaid-cli@8.13.10 -i docs/diagrams/architecture.mmd -o docs/diagrams/architecture.png -w 1920
npx -y @mermaid-js/mermaid-cli@8.13.10 -i docs/diagrams/failure_workflow.mmd -o docs/diagrams/failure_workflow.png -w 1920
```

## Supported Backends

- pytorch-gpu
- pytorch-cpu

## Planned Backends

- onnx-gpu
- onnx-cpu
- openvino-cpu
- fastembed-onnx-cpu
