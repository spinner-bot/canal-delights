"""Small backend-independent animation clock and easing primitives."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, List, Optional
import math


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_out_cubic(t: float) -> float:
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


@dataclass
class Tween:
    """Deterministic scalar tween; scene code decides what the value drives."""

    start: float
    end: float
    duration: float
    easing: Callable[[float], float] = ease_out_cubic
    elapsed: float = 0.0

    @property
    def done(self) -> bool:
        return self.elapsed >= self.duration

    def step(self, delta_seconds: float) -> float:
        self.elapsed = min(self.duration, self.elapsed + max(0.0, delta_seconds))
        progress = 1.0 if self.duration <= 0 else self.elapsed / self.duration
        eased = self.easing(progress)
        return self.start + (self.end - self.start) * eased


class SceneTransition:
    """Two-phase transition with one scene switch at maximum coverage."""

    def __init__(self, duration: float = .62):
        self.duration = duration
        self.elapsed = 0.0
        self.active = False
        self.switched = False
        self._on_switch: Optional[Callable[[], None]] = None

    @property
    def progress(self) -> float:
        return 1.0 if self.duration <= 0 else clamp01(self.elapsed / self.duration)

    @property
    def cover(self) -> float:
        """0 → 1 → 0 eased curtain coverage."""
        if not self.active:
            return 0.0
        return math.sin(math.pi * self.progress) ** .72

    def start(self, on_switch: Callable[[], None]) -> bool:
        if self.active:
            return False
        self.elapsed = 0.0
        self.active = True
        self.switched = False
        self._on_switch = on_switch
        return True

    def step(self, delta_seconds: float):
        if not self.active:
            return
        self.elapsed = min(self.duration, self.elapsed + max(0.0, delta_seconds))
        if not self.switched and self.progress >= .5:
            self.switched = True
            if self._on_switch:
                self._on_switch()
        if self.progress >= 1:
            self.active = False
            self._on_switch = None


class AnimationClock:
    """Schedule delta-time animation callbacks through ``turtle.Screen``."""

    def __init__(self, screen, fps: int = 30):
        self.screen = screen
        self.frame_ms = max(1, round(1000 / fps))
        self.callbacks: List[Callable[[float], bool]] = []
        self.running = False
        self._last_time = None

    def add(self, callback: Callable[[float], bool]):
        """Add a callback. Return ``False`` from it to remove it."""
        self.callbacks.append(callback)
        if not self.running:
            self.start()

    def set_fps(self, fps: int):
        """Update the cadence used for subsequent timer ticks."""
        self.frame_ms = max(1, round(1000 / fps))

    def start(self):
        if self.running:
            return
        self.running = True
        self._last_time = perf_counter()
        self.screen.ontimer(self._tick, self.frame_ms)

    def stop(self):
        self.running = False
        self._last_time = None

    def _tick(self):
        if not self.running:
            return
        now = perf_counter()
        delta = min(0.1, now - self._last_time) if self._last_time else 0.0
        self._last_time = now
        self.callbacks = [callback for callback in self.callbacks if callback(delta) is not False]
        self.screen.update()
        if self.callbacks:
            self.screen.ontimer(self._tick, self.frame_ms)
        else:
            self.stop()
