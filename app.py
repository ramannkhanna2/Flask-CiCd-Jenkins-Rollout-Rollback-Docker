from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import time

app = Flask(__name__)

# Create a custom registry to export only our metrics
registry = CollectorRegistry()

# Metrics
REQUEST_COUNT = Counter(
    "request_count_total",
    "Total number of HTTP requests",
    ["endpoint", "status"],   # 👈 added "status" label
    registry=registry
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    registry=registry
)

# Home endpoint
@app.route("/")
def home():
    with REQUEST_LATENCY.labels(endpoint="/").time():
        time.sleep(0.1)  # Simulate proc. delay (~100ms) to make it realistic
        REQUEST_COUNT.labels(endpoint="/", status="200").inc()   # 👈 updated
        return "Hello from Raman App!"

# Dynamic endpoint /<name>
@app.route("/<name>")
def greet(name):
    endpoint_label = f"/{name}"
    with REQUEST_LATENCY.labels(endpoint=endpoint_label).time():
        time.sleep(1.0)  # Simulate processing delay (~100ms)
        REQUEST_COUNT.labels(endpoint=endpoint_label, status="200").inc()   # 👈 updated
        return f"Hello, {name}!"

# Failing endpoint to simulate errors
@app.route("/fail")
def fail():
    REQUEST_COUNT.labels(endpoint="/fail", status="500").inc()   # 👈 new for failures
    return "Internal Error", 500

# Metrics endpoint
@app.route("/metrics")
def metrics():
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
