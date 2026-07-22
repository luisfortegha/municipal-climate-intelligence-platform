from ui.components.metrics import render_metrics
from ui.components.infrastructure import render_infrastructure
from ui.components.community import render_community
from ui.components.history import render_history
from ui.components.earth import render_earth_dashboard


def test_component_imports():

    assert callable(render_metrics)
    assert callable(render_infrastructure)
    assert callable(render_community)
    assert callable(render_history)
    assert callable(render_earth_dashboard)