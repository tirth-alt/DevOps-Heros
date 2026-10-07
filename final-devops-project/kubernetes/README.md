# Kubernetes and Helm

**Name:** Tirth Shah · **Roll Number:** 10316

The application is deployed with the Helm chart in [`helm/stockwise`](../helm/stockwise). `kubernetes/namespace.yaml` creates the namespace.

## Kubernetes objects

| Object | Purpose | Template |
|---|---|---|
| Namespace `stockwise` | Isolates the app | `kubernetes/namespace.yaml` |
| Deployment `stockwise-backend` | FastAPI API, 2 to 5 pods | `templates/backend.yaml` |
| Deployment `stockwise-frontend` | React app on nginx, 2 pods | `templates/frontend.yaml` |
| StatefulSet `stockwise-postgres` | PostgreSQL with its own volume | `templates/postgres.yaml` |
| Services (ClusterIP) | Stable internal addresses for all three | backend, frontend, postgres templates |
| ConfigMap | Non-secret settings such as `LOG_LEVEL` | `templates/configmap.yaml` |
| Secret | Database password, random and kept across upgrades | `templates/secret.yaml` |
| Ingress | `/` to the frontend, `/api` to the backend | `templates/ingress.yaml` |
| HorizontalPodAutoscaler | Scales the backend from 2 to 5 pods at 70% CPU | `templates/hpa.yaml` |
| PersistentVolumeClaim | 1Gi of storage for PostgreSQL | `volumeClaimTemplates` in the StatefulSet |
| Job (Helm hook) | Runs `alembic upgrade head` after each install or upgrade | `templates/migration-job.yaml` |
| ServiceMonitor | Tells Prometheus to scrape `/metrics` | `templates/servicemonitor.yaml` |

## Probes

| Container | Startup | Liveness | Readiness |
|---|---|---|---|
| Backend | `GET /health` (up to 60s) | `GET /health` | `GET /ready`, which runs `SELECT 1` on the database |
| Frontend | | `GET /healthz` | `GET /healthz` |
| PostgreSQL | | `pg_isready` | `pg_isready` |

Liveness only checks that the process is alive. Readiness also checks the database. If PostgreSQL is unreachable, the backend is taken out of the Service without being restarted. The troubleshooting challenge shows this in action.

## Deploy to minikube

```bash
minikube start
minikube addons enable ingress
minikube addons enable metrics-server

# Build the images and load them into minikube
docker build -t stockwise-backend:local application/backend
docker build -t stockwise-frontend:local application/frontend
minikube image load stockwise-backend:local
minikube image load stockwise-frontend:local

kubectl apply -f kubernetes/namespace.yaml
helm upgrade --install stockwise helm/stockwise -n stockwise -f helm/stockwise/values-local.yaml --wait
kubectl get pods,svc,ingress,hpa,pvc -n stockwise
```

![All pods running, services, ingress, HPA and PVC](../screenshots/k8s-resources.png)

## Open the app through the Ingress

```bash
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8088:80
curl -H "Host: stockwise.local" http://localhost:8088/api/stats
./scripts/seed.sh http://localhost:8088        # with HOST_HEADER=stockwise.local
```

To use a browser, add `127.0.0.1 stockwise.local` to `/etc/hosts` and open http://stockwise.local:8088.

![StockWise served through the Ingress at stockwise.local](../screenshots/k8s-app-ingress.png)

## Autoscaling under load

```bash
HOST_HEADER=stockwise.local ./scripts/load-test.sh http://localhost:8088 200
kubectl get hpa -n stockwise -w
```

![HPA scaled the backend to 5 pods at 298% CPU](../screenshots/hpa-scaling.png)

The HPA reads CPU usage from metrics-server and compares it with the CPU **request** of 100m. At 298% it added pods up to the maximum of 5, and later scaled back to 2 when traffic stopped.

## Helm values files

| File | Used for |
|---|---|
| `values.yaml` | Defaults: GHCR images, 2 replicas, HPA, Ingress, probes, resources |
| `values-local.yaml` | minikube: locally built images with `pullPolicy: Never` |
| `values-gitops.yaml` | Argo CD: image tags written by the CI pipeline, database Secret created separately |

```bash
helm lint helm/stockwise
helm template stockwise helm/stockwise -f helm/stockwise/values-local.yaml
helm history stockwise -n stockwise
helm rollback stockwise <revision> -n stockwise
```
