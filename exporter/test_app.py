import app


def test_render_metrics_has_help_and_types():
    text = app.render_metrics()
    assert "# HELP cluster_node_up" in text
    assert "# TYPE cluster_node_provisioned gauge" in text


def test_render_metrics_covers_all_nodes():
    text = app.render_metrics()
    for node in app.NODES:
        assert f'cluster_node_up{{node="{node}"}}' in text


def test_metrics_are_valid_numbers():
    for line in app.render_metrics().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        value = line.rsplit(" ", 1)[1]
        float(value)  # raises if not numeric
