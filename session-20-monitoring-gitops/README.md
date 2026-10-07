# Session 20: Monitoring, Observability & GitOps

**Name:** Tirth Shah  
**Roll Number:** 10316

| Task | Where | What it contains |
|---|---|---|
| **1. Monitoring** | [01-monitoring](01-monitoring/README.md) | A working demo with Prometheus, Grafana and alert rules. It shows metrics, logs, alerts, CPU and memory use, and application health. |
| **2. Observability** | [02-observability](02-observability/README.md) | The three pillars (metrics, logs, traces), why observability is needed, common tools and Kubernetes observability. |
| **3. GitOps** | [03-gitops](03-gitops/README.md) | What GitOps is, plus an Argo CD demo covering sync, self-healing and rollback through Git. |

## Deliverables

| Deliverable | Location |
|---|---|
| Monitoring demo | `01-monitoring/` (compose file, app, Prometheus config, alerts, Grafana dashboard) |
| Observability documentation | `02-observability/README.md` |
| GitOps demo | `03-gitops/` (manifests and the Argo CD Application) |
| Screenshots | `01-monitoring/screenshots/` and `03-gitops/screenshots/` |
| README.md | This file and one in each folder |

## Quick start

```bash
# Task 1: monitoring demo
cd session-20-monitoring-gitops/01-monitoring
docker compose up -d --build
./load.sh normal 60
# Prometheus http://localhost:9090   Grafana http://localhost:3000 (admin / admin)
docker compose down -v
```

GitOps needs the manifests pushed to GitHub first. See [03-gitops](03-gitops/README.md).
