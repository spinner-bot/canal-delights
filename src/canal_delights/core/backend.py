"""Renderer selection shared by the CLI and application."""

from enum import Enum
from typing import Union

from .engine import DrawingEngine


class RenderMode(str, Enum):
    PURE = 'pure'
    ACCELERATED = 'accelerated'

    @classmethod
    def parse(cls, value: Union['RenderMode', str]) -> 'RenderMode':
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            choices = ', '.join(mode.value for mode in cls)
            raise ValueError(f"未知渲染模式 {value!r}，可选值：{choices}") from exc


def create_engine(
    mode: Union[RenderMode, str] = RenderMode.ACCELERATED,
    width: int = 1200,
    height: int = 800,
) -> DrawingEngine:
    selected = RenderMode.parse(mode)
    if selected is RenderMode.PURE:
        return DrawingEngine(width, height)

    # Keep the optional backend import out of pure mode's initialization path.
    from .accelerated import AcceleratedDrawingEngine
    return AcceleratedDrawingEngine(width, height)
