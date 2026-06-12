"""A tiny Prometheus exporter that publishes synthetic cluster/provisioning
health metrics. Stands in for an agent that would report node readiness and
provisioning state across a fleet, giving the Grafana dashboard something to
visualize without requiring real hardware.

Exposes Prometheus text-format metrics on :9101/metrics.
"""
from __future__ import annotations

import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("EXPORTER_PORT", "9101"))
NODES = os.environ.get("CLUSTER_NODES", "node01,node02,node03").split(",")

# Deterministic-ish per-node state so the dashboard looks stable but alive.
_STATE = {n: {"provisioned": 1, "seed": i} for i, n in enumerate(NODES)}


def render_metrics() -> str:
    lines = [
        "# HELP cluster_node_up Whether a node is reachable (1) or not (0).",
        "# TYPE cluster_node_up gauge",
        "# HELP cluster_node_provisioned Whether provisioning completed (1) or not (0).",
        "# TYPE cluster_node_provisioned gauge",
        "# HELP cluster_node_cpu_usage_ratio Synthetic CPU utilization ratio [0,1].",
        "# TYPE cluster_node_cpu_usage_ratio gauge",
        "# HELP cluster_provisioning_duration_seconds Last provisioning run duration.",
        "# TYPE cluster_provisioning_duration_seconds gauge",
    ]
    for node, st in _STATE.items():
        up = 1 if random.random() > 0.02 else 0
        cpu = round(min(1.0, max(0.0, 0.3 + 0.2 * random.random() + 0.05 * st["seed"])), 3)
        dur = round(45 + 10 * random.random() + 3 * st["seed"], 1)
        lines.append(f'cluster_node_up{{node="{node}"}} {up}')
        lines.append(f'cluster_node_provisioned{{node="{node}"}} {st["provisioned"]}')
        lines.append(f'cluster_node_cpu_usage_ratio{{node="{node}"}} {cpu}')
        lines.append(f'cluster_provisioning_duration_seconds{{node="{node}"}} {dur}')
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (http.server API)
        if self.path == "/healthz":
            self._respond(200, "ok\n", "text/plain")
        elif self.path in ("/metrics", "/"):
            self._respond(200, render_metrics(), "text/plain; version=0.0.4")
        else:
            self._respond(404, "not found\n", "text/plain")

    def _respond(self, code: int, body: str, content_type: str):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # silence default noisy logging
        return


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"cluster-monitor exporter listening on :{PORT} for nodes={NODES}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
