import logging
import random
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-app")

# Metric 1: a counter that only goes up. Labels let us slice by endpoint and status.
REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

# Metric 2: a histogram that records how long requests take, in seconds.
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Time spent handling a request",
    ["endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)


@app.before_request
def start_timer():
    request.start_time = time.perf_counter()


@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        endpoint = request.url_rule.rule if request.url_rule else "unknown"
        elapsed = time.perf_counter() - request.start_time
        REQUESTS.labels(request.method, endpoint, response.status_code).inc()
        LATENCY.labels(endpoint).observe(elapsed)
        log.info("%s %s -> %s in %.3fs", request.method, request.path, response.status_code, elapsed)
    return response


@app.route("/")
def home():
    return jsonify(message="Session 20 monitoring demo", student="Tirth Shah", roll_no="10316")


@app.route("/health")
def health():
    return jsonify(status="UP")


@app.route("/slow")
def slow():
    time.sleep(random.uniform(1.2, 2.0))
    return jsonify(message="That was slow")


@app.route("/error")
def error():
    log.error("Simulated failure on /error")
    return jsonify(error="Something went wrong"), 500


@app.route("/cpu")
def cpu():
    end = time.perf_counter() + 1.0
    total = 0
    while time.perf_counter() < end:
        total += sum(i * i for i in range(2000))
    return jsonify(message="Burned CPU for one second")


@app.route("/metrics")
def metrics():
    # Prometheus reads this endpoint. It also includes process_cpu_* and process_resident_memory_*.
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
