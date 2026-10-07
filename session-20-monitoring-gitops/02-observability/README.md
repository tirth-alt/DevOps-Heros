# Observability: Metrics, Logs and Traces

**Name:** Tirth Shah  
**Roll Number:** 10316

## Monitoring vs observability

| | Monitoring | Observability |
|---|---|---|
| Question | "Is the system healthy?" | "Why is the system behaving this way?" |
| Works from | Things you decided to watch in advance | Rich data you can explore for questions you did not plan |
| Typical output | Dashboards and alerts | Finding the cause of a problem you have never seen before |
| Example | "CPU is above 80%" | "Checkout is slow only for users in one region, because one database call takes 2 seconds" |

Monitoring tells you **that** something is wrong. Observability gives you enough information to understand **what and why**. Monitoring is part of observability, not a replacement for it.

A doctor's checkup is a good picture. Monitoring is the thermometer and the blood pressure cuff. Observability is having the scans and the full history, so the doctor can work out a condition nobody predicted.

---

## The three pillars

Observability is built from three kinds of telemetry data.

### 1. Metrics

**Numbers measured over time.** They are small, cheap to store and fast to query, so they suit dashboards and alerts.

- Examples: requests per second, error percentage, CPU usage, memory use, queue length.
- Answers: **how much, how often, how fast?**
- Weakness: they are summaries. A metric says errors went up but not which request failed.

```
http_requests_total{endpoint="/error", status="500"}  338
```

### 2. Logs

**Text records of individual events**, each with a timestamp.

- Examples: an error message, a stack trace, a login attempt, a request line.
- Answers: **what exactly happened?**
- Weakness: they are large and expensive at scale, and hard to follow across many services.

```
2026-10-07 10:09:24 ERROR Simulated failure on /error
2026-10-07 10:09:24 INFO GET /error -> 500 in 0.000s
```

### 3. Traces

**The journey of one request through all the services it touches.** A trace is a tree of **spans**, one for each step, with its start time and duration.

- Examples: a checkout request that calls the cart, payment and inventory services.
- Answers: **where did the time go, and which service caused the failure?**
- Weakness: services must be instrumented, and storing every trace is expensive, so they are often sampled.

```
Trace abc123: POST /checkout                        total 820 ms
 ├─ cart-service       get cart                       40 ms
 ├─ payment-service    charge card                   650 ms   ◄── the slow step
 │    └─ bank-api      authorize                     610 ms
 └─ inventory-service  reserve items                  60 ms
```

A **trace ID** is attached to every log line from that request, which lets you jump from a trace to its logs.

### How the three work together

```
Alert fires (metric)  →  "error rate is 25%"
        ↓
Trace                 →  "failures all come from the payment service"
        ↓
Logs                  →  "payment-service: connection pool exhausted"
```

| Pillar | Tells you | Cost |
|---|---|---|
| Metrics | That a problem exists | Low |
| Traces | Where it is | Medium to high |
| Logs | Why it happened | High |

---

## Why observability is required

- **Modern systems are distributed.** One user action can cross dozens of services, so no single machine has the full story.
- **Failures are unpredictable.** You cannot write an alert for every way a system can break. You need data you can explore.
- **Faster recovery.** Less time guessing means a lower mean time to detect and to resolve an incident.
- **Better releases.** Compare behaviour before and after a deployment, and roll back with evidence.
- **Cost and performance.** Show which service is slow or wasteful.
- **Reliability goals.** Service level objectives need measured data.

The **four golden signals** are a good starting set for any service: **latency**, **traffic**, **errors** and **saturation**. The Grafana dashboard in `01-monitoring` has one panel for each.

---

## Common tools

| Purpose | Open source | Commercial and cloud |
|---|---|---|
| Metrics collection and storage | Prometheus, VictoriaMetrics | Datadog, New Relic, CloudWatch |
| Dashboards | Grafana | Datadog, CloudWatch dashboards |
| Alerting | Alertmanager, Grafana Alerting | PagerDuty, Opsgenie |
| Logs | Loki, Elasticsearch with Kibana (ELK/EFK), Fluent Bit | Splunk, CloudWatch Logs |
| Traces | Jaeger, Tempo, Zipkin | Datadog APM, X-Ray |
| Instrumentation standard | **OpenTelemetry** | Supported by nearly all vendors |
| Host metrics | node-exporter | CloudWatch agent |

**OpenTelemetry** is a vendor-neutral standard and set of libraries for producing metrics, logs and traces. Instrument an app once and send the data to any backend.

A common free stack is called **LGTM**: Loki for logs, Grafana for dashboards, Tempo for traces and Mimir or Prometheus for metrics.

---

## Observability in Kubernetes

Kubernetes adds layers that all need watching: the cluster, the nodes, the Pods and the application inside them.

| Layer | What to watch | How |
|---|---|---|
| Built in, no setup | Pod state, events, logs, resource use | `kubectl get`, `describe`, `logs`, `get events`, `top` |
| Resource metrics | CPU and memory per Pod and node | **metrics-server**, which also powers `kubectl top` and the HPA |
| Object state | Deployments, replicas, restarts, Pod phases | **kube-state-metrics** |
| Node and container health | Node CPU, memory, disk, network | node-exporter and cAdvisor (built into the kubelet) |
| Application metrics | Requests, errors, latency | The app exposes `/metrics`, and Prometheus scrapes it |
| Logs | Output of every container | A log agent such as Fluent Bit or Promtail on each node, sending to Loki or Elasticsearch |
| Traces | Calls between services | OpenTelemetry SDKs, a collector, then Jaeger or Tempo |

### Typical setup

The **kube-prometheus-stack** Helm chart installs Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics and ready-made dashboards in one step.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

Prometheus finds applications through a **ServiceMonitor**, a small Kubernetes object that says which Service to scrape. Pods can also be discovered automatically through the Kubernetes API.

### Useful kubectl commands

```bash
kubectl top nodes
kubectl top pods -A
kubectl logs <pod> --previous
kubectl get events --sort-by=.lastTimestamp
kubectl describe pod <pod>
```

---

## How the demo maps to the pillars

| Pillar | In the `01-monitoring` demo |
|---|---|
| Metrics | Fully shown: Prometheus, PromQL, Grafana and alerts |
| Logs | Shown with `docker compose logs`. A real setup would ship them to Loki or Elasticsearch. |
| Traces | Explained here only. The demo app is a single service, so there is no multi-service journey to trace. |

## Summary

- **Monitoring** watches known signals. **Observability** lets you explain unknown problems.
- The three pillars are **metrics** (what and how much), **logs** (what happened) and **traces** (where the time went).
- Use metrics to detect, traces to locate, and logs to find the cause.
- In Kubernetes, start with `kubectl`, add metrics-server, and move to Prometheus, Grafana and a log stack as the system grows.
