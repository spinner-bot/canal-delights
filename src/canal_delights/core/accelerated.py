"""Accelerated renderer using Turtle's own Tk canvas as a batch backend.

The application still owns a ``turtle.Screen`` and uses Turtle for window,
events and lifecycle.  Unlike the pure backend, a sampled curve or filled
shape is submitted as one retained Canvas item instead of many pen movements.
"""

import math
from typing import List, Tuple

from .engine import DrawingEngine
from .styles import RGB, rgb_to_hex


Point = Tuple[float, float]


class AcceleratedDrawingEngine(DrawingEngine):
    """Drop-in ``DrawingEngine`` with batched Canvas drawing operations."""

    def __init__(self, width: int = 1200, height: int = 800):
        super().__init__(width, height)
        self.mode_name = 'accelerated'
        self._canvas_items_by_layer = {'content': []}
        self.screen.title("运河四季·美食绘卷（加速模式）")

    @property
    def _canvas_items(self) -> List[int]:
        """Items in the active layer (kept for diagnostics and tests)."""
        return self._canvas_items_by_layer.setdefault(self._active_layer, [])

    def _remember(self, item: int) -> int:
        self._canvas_items.append(item)
        return item

    def clear(self, layer=None):
        """Delete retained accelerated items in one layer or in all layers."""
        names = [layer] if layer is not None else list(self._canvas_items_by_layer)
        for name in names:
            for item in self._canvas_items_by_layer.get(name, []):
                self.screen._delete(item)
            self._canvas_items_by_layer.setdefault(name, []).clear()
        super().clear(layer)

    def draw_point(self, x: float, y: float, size: float, color: RGB):
        # Use a compact polygon rather than a Turtle dot operation.  At normal
        # UI sizes 16 sides are visually indistinguishable from an oval.
        radius = max(0.5, size / 2)
        points = [
            (x + radius * math.cos(i * math.tau / 16),
             y + radius * math.sin(i * math.tau / 16))
            for i in range(16)
        ]
        self._fill_polygon(points, color)

    def draw_line(
        self, x1: float, y1: float, x2: float, y2: float,
        color: RGB, width: float = 1.0,
    ):
        self.draw_polyline([(x1, y1), (x2, y2)], color, width)

    def draw_polyline(
        self, points: List[Point], color: RGB,
        width: float = 1.0, close: bool = False,
    ):
        if not points:
            return
        coords = list(points)
        if close and len(coords) > 2 and coords[-1] != coords[0]:
            coords.append(coords[0])
        item = self.screen._createline()
        self.screen._drawline(
            item, coords, fill=rgb_to_hex(color), width=max(1, width), top=True,
        )
        self._remember(item)

    def _fill_polygon(self, points: List[Point], color: RGB):
        if not points:
            return
        item = self.screen._createpoly()
        hex_color = rgb_to_hex(color)
        self.screen._drawpoly(
            item, points, fill=hex_color, outline=hex_color, width=1, top=True,
        )
        self._remember(item)

    def draw_text(
        self, text: str, x: float, y: float, font_size: int, color: RGB,
        font_family: str = 'Microsoft YaHei', align: str = 'center',
        weight: str = 'normal',
    ):
        turtle_align = align if align in {'left', 'center', 'right'} else 'center'
        item, _ = self.screen._write(
            (x, y), text, turtle_align,
            (font_family, font_size, weight), rgb_to_hex(color),
        )
        self._remember(item)
