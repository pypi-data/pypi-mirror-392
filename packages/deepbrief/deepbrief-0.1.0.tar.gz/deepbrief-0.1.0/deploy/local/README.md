## Local Deployment Guide

This directory lets you run the Deepbrief workflow stack locally with Docker Compose and Dapr.

### 1. Prerequisites

- Docker Desktop or Docker Engine
- Dapr CLI (`brew install dapr/tap/dapr-cli` or follow https://docs.dapr.io/getting-started/install-dapr-cli/)
- Python 3.13 (optional for local scripts/tests)

### 2. Configure environment variables

Create a `.env` file at the repo root (copy `.env.example` if available) and populate at least:

```env
OPENAI_API_KEY=sk-...
OPENAI_API_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
ELEVENLABS_API_KEY=...
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=miniokey
MINIO_SECRET_KEY=miniosecret
```

Docker Compose automatically loads `.env` in the repo root.

### 3. Start services

From the repo root:

```bash

docker-compose -f deploy/local/docker-compose.yaml up
```

This starts the Deepbrief API container plus local dependencies (MinIO, Postgres, etc.). Keep this terminal tab open so you can see container logs; press `Ctrl+C` to stop.

### 4. Start Dapr sidecars

In a separate terminal, run:

```bash
cd deploy/local
dapr run -f dapr.yaml
```

This spins up the Dapr workflow runtime and attaches sidecars as defined in `dapr.yaml`. Leave this running while you test.

### 5. Apply local components (optional)

If you want to inspect or customize bindings/state stores manually:

```bash
dapr components put --file components/minio.yaml
dapr components put --file components/workflowstate.yaml
```

(The `dapr run -f dapr.yaml` command already references these files; this step is only needed if you want to register them individually.)

### 6. Test the API

With Docker Compose and Dapr both running, you can hit the local FastAPI endpoint:

```bash
curl http://localhost:8080/healthz
curl -X POST http://localhost:8080/workflows/research-podcast -H "Content-Type: application/json" -d @test.http
```

Or use the helper CLI (`deploy/local/test.py`) to manage workflow instances:

```bash
# Start a new workflow (stores the instance_id in .workflow-instance)
python deploy/local/test.py start --podcast-name "AI Security Voice" --host-name "Alice"

# Check status of the last run (or pass --instance-id manually)
python deploy/local/test.py status

# Block until completion (default timeout 1800 seconds)
python deploy/local/test.py wait --timeout 1200
```

### 7. Tear down

Press `Ctrl+C` in the Dapr terminal, then stop Docker Compose:

```bash
docker-compose -f deploy/local/docker-compose.yaml down
```

To remove volumes/images:

```bash
docker-compose -f deploy/local/docker-compose.yaml down -v --rmi local
```
