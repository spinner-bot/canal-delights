"""One-dimensional boat physics projected onto the Grand Canal spline."""

from dataclasses import dataclass
import math
from typing import Optional

from .geometry import cubic_bezier_point


Point = tuple[float, float]

# The five city anchors are also the endpoints of four cubic spline spans.
CITY_POINTS: tuple[Point, ...] = (
    (.17, .78), (.30, .69), (.55, .43), (.80, .28), (.74, .14),
)

ROUTE_SEGMENTS = (
    (CITY_POINTS[0], (.1917, .7650), (.2367, .7483), CITY_POINTS[1]),
    (CITY_POINTS[1], (.3633, .6317), (.4667, .4983), CITY_POINTS[2]),
    (CITY_POINTS[2], (.6333, .3617), (.7683, .3283), CITY_POINTS[3]),
    (CITY_POINTS[3], (.8317, .2317), (.7500, .1633), CITY_POINTS[4]),
)

CITY_STOPS = tuple(index / (len(CITY_POINTS) - 1) for index in range(len(CITY_POINTS)))


def route_point(progress: float) -> Point:
    """Return a point on the route for normalized progress ``0..1``."""
    progress = max(0.0, min(1.0, progress))
    scaled = progress * len(ROUTE_SEGMENTS)
    segment_index = min(len(ROUTE_SEGMENTS) - 1, int(scaled))
    local_t = 1.0 if progress >= 1.0 else scaled - segment_index
    return cubic_bezier_point(*ROUTE_SEGMENTS[segment_index], local_t)


def route_tangent(progress: float) -> Point:
    """Numerically estimate a normalized tangent along the spline."""
    epsilon = .001
    before = route_point(max(0.0, progress - epsilon))
    after = route_point(min(1.0, progress + epsilon))
    dx, dy = after[0] - before[0], after[1] - before[1]
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


@dataclass
class BoatPhysics:
    position: float = 0.0
    velocity: float = 0.0
    acceleration: float = 0.72
    damping: float = 3.2
    max_speed: float = 0.32
    snap_strength: float = 2.4

    def step(self, direction: float, delta_seconds: float) -> bool:
        """Advance physics and return whether the boat visibly changed."""
        dt = max(0.0, min(0.05, delta_seconds))
        previous = self.position
        self.velocity += max(-1.0, min(1.0, direction)) * self.acceleration * dt

        if not direction:
            nearest = min(CITY_STOPS, key=lambda stop: abs(stop - self.position))
            if abs(nearest - self.position) < .055:
                self.velocity += (nearest - self.position) * self.snap_strength * dt

        self.velocity *= math.exp(-self.damping * dt)
        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))
        self.position += self.velocity * dt

        if self.position <= 0:
            self.position, self.velocity = 0.0, max(0.0, self.velocity)
        elif self.position >= 1:
            self.position, self.velocity = 1.0, min(0.0, self.velocity)
        if abs(self.velocity) < .0002:
            self.velocity = 0.0
        return abs(self.position - previous) > 1e-7

    def nudge(self, direction: float):
        self.velocity += max(-1.0, min(1.0, direction)) * .075
        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

    def nearby_city(self, radius: float = .037) -> Optional[int]:
        index = min(range(len(CITY_STOPS)), key=lambda i: abs(CITY_STOPS[i] - self.position))
        return index if abs(CITY_STOPS[index] - self.position) <= radius else None
