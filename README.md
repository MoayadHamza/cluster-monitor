# cluster-monitor

A self-contained **observability stack** for a small node fleet: a Python
Prometheus exporter, **Prometheus** for scraping/storage, and **Grafana** with a
pre-provisioned dashboard — all wired together with **docker-compose**.

It gives "cluster visibility" (node up/down, provisioning state, CPU, provisioning
duration) and pairs with the [`dc-lab-automation`](../dc-lab-automation) repo, whose
`monitoring_agent` role installs `node_exporter` on each node.

## Architecture

```
exporter (:9101) ──scrape──> Prometheus (:9090) ──query──> Grafana (:3000)
                                                            └─ auto-provisioned
                                                               datasource + dashboard
```

## Run it

```bash
docker compose up --build -d
```

Then open:

- Grafana:    http://localhost:3000  (admin / admin) → dashboard **"Cluster Monitor"**
- Prometheus: http://localhost:9090
- Exporter:   http://localhost:9101/metrics

Tear down with `docker compose down`.

## The exporter

`exporter/app.py` is standard-library only (no third-party deps) and serves
Prometheus text-format metrics:

| Metric | Meaning |
|---|---|
| `cluster_node_up` | node reachable (1/0) |
| `cluster_node_provisioned` | provisioning completed (1/0) |
| `cluster_node_cpu_usage_ratio` | CPU utilization [0,1] |
| `cluster_provisioning_duration_seconds` | last provisioning run duration |

Configure the node list via the `CLUSTER_NODES` env var (comma-separated).

> The metrics here are synthetic so the stack is runnable without real hardware.
> Swapping in real data is just a matter of changing `render_metrics()` to read
> from `node_exporter`, an API, or SSH facts.

## Tests / CI

```bash
cd exporter && pip install -r requirements.txt && pytest -q
```

GitHub Actions (`.github/workflows/ci.yml`) runs the exporter tests, validates the
Grafana dashboard JSON, and validates the compose file.
