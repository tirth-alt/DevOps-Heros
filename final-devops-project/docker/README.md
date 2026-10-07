# Docker

**Name:** Tirth Shah · **Roll Number:** 10316

| Image | Dockerfile | Base | Runs as |
|---|---|---|---|
| Backend | `application/backend/Dockerfile` | `python:3.12-slim` | `appuser` (uid 10001) |
| Frontend | `application/frontend/Dockerfile` | multi-stage: `node:22-alpine` builds, `nginx-unprivileged` serves | `nginx` (uid 101) |

The frontend's nginx serves the React build and forwards `/api/` to the backend. The backend address comes from the `BACKEND_URL` environment variable, so the same image works in Docker Compose and in Kubernetes.

## Run the whole stack

```bash
cd final-devops-project
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml ps
./scripts/seed.sh http://localhost:8000
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 (docs at /docs) |
| PostgreSQL | internal only |

PostgreSQL has a healthcheck. The backend waits for it, runs the Alembic migration, and then starts. The frontend waits for the backend's healthcheck.

![docker compose: three services up, both images non-root](../screenshots/docker-compose-up.png)

## Stop

```bash
docker compose -f docker/docker-compose.yml down      # keep the data
docker compose -f docker/docker-compose.yml down -v   # also delete the database volume
```
