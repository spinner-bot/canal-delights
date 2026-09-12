import pytest

from canal_delights.core import backend
from canal_delights.core.accelerated import AcceleratedDrawingEngine
from canal_delights.core.engine import DrawingEngine


def test_render_mode_validation():
    assert backend.RenderMode.parse('PURE') is backend.RenderMode.PURE
    assert backend.RenderMode.parse(' accelerated ') is backend.RenderMode.ACCELERATED
    with pytest.raises(ValueError, match='未知渲染模式'):
        backend.RenderMode.parse('magic')


def test_factory_selects_pure_backend(monkeypatch):
    marker = object()
    monkeypatch.setattr(backend, 'DrawingEngine', lambda width, height: (marker, width, height))
    assert backend.create_engine('pure', 640, 480) == (marker, 640, 480)


def test_both_backends_expose_parser_drawing_contract():
    required = {
        'clear', 'update', 'draw_point', 'draw_line', 'draw_polyline',
        'draw_circle', 'draw_ellipse', 'draw_rect', 'draw_rounded_rect',
        'draw_polygon', 'draw_ring', 'draw_arc', 'draw_bezier',
        'draw_quadratic', 'draw_path', 'draw_text', 'draw_gradient_fill',
    }
    for name in required:
        assert callable(getattr(DrawingEngine, name, None))
        assert callable(getattr(AcceleratedDrawingEngine, name, None))
