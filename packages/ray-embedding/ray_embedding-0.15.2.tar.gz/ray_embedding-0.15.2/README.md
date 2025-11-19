# Ray Embedding Service

`ray-embedding` packages everything needed to expose SentenceTransformers models through an OpenAI-compatible API that runs on a Ray Serve cluster.  It provides:

- A FastAPI-based `ModelRouter` that rate-limits requests, shards large batches, and fans out work to autoscaled replicas.
- An `EmbeddingModel` deployment that loads any Hugging Face transformer compatible with `sentence-transformers`, handles Matryoshka truncation, and periodically checks the health of the underlying GPU via CUDA health checks.
- A `NodeRecycler` supervisor that watches for unhealthy replicas, warns colocated peers, and recycles the underlying worker node safely.

This library is designed for the [embedding-models Ray cluster](https://bitbucket.org/docorto/embedding-models/src/dev/), but can be embedded in any Serve app with similar requirements.  See the [reference Serve configuration](https://bitbucket.org/docorto/embedding-models/src/dev/serve-config/serve-config.yaml) for production defaults.

## Architecture

The deployment is organised into three building blocks: API ingress, model replicas, and the recycler that ties health reporting to infrastructure level actions.

![Architecture diagram](docs/diagrams/architecture.png)

1. Clients call the router using standard OpenAI embedding verbs.
2. The router batches, normalises paths, and invokes the selected embedding replica.
3. Each replica registers itself with the recycler, reports GPU/CUDA failures, and warns **other** colocated replicas about failed nodes.
4. When a node is marked unhealthy, the recycler informs every colocated replica/router (except the reporter), waits one recycle cycle for graceful shutdown, then issues an SSH stop to the worker’s Docker runtime.

## Failure & Recycling Workflow

When a replica hits a CUDA error (or any fatal condition), the recycler coordinates a graceful drain so clients experience deterministic errors while Ray’s autoscaler replaces the failed node.

![Failure workflow diagram](docs/diagrams/failure_workflow.png)

1. The router dispatches a batch and receives an exception from a replica.
2. The replica reports the failure; the recycler immediately pings all *other* replicas and the router on that node to start failing their health checks.
3. During the next recycle cycle, the node is terminated via SSH after the replicas have had a chance to flush in-flight work.

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
