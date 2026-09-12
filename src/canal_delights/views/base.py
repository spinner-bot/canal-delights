"""
视图基础类
"""

from typing import List
from ..core.engine import DrawingEngine
from ..core.renderer import DrawingDataParser
from ..config import rgb


class View:
    """视图基类"""

    def __init__(self, engine: DrawingEngine, parser: DrawingDataParser):
        self.engine = engine
        self.parser = parser
        self.bounds = (0, 0, engine.width, engine.height)

    def render(self, state):
        """渲染视图 - 子类实现"""
        raise NotImplementedError

    def draw_text(self, x: float, y: float, text: str, size: int, color: tuple, align: str = 'center'):
        """辅助方法：绘制文字"""
        return ['T', [x, y, text], {'font_size': size, 'color': color, 'align': align}]

    def draw_rect(self, x: float, y: float, w: float, h: float, fill: tuple):
        """辅助方法：绘制矩形"""
        return ['R', [x, y, w, h], {'fill': fill}]

    def draw_circle(self, x: float, y: float, r: float, fill: tuple):
        """辅助方法：绘制圆形"""
        return ['C', [x, y, r], {'fill': fill}]
