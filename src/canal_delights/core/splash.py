"""Boat-wake droplets only; deliberately not a general ambient particle system."""

from dataclasses import dataclass
import random


@dataclass
class SplashDrop:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float


class SplashSystem:
    def __init__(self, seed: int = 2026, limit: int = 36):
        self.random = random.Random(seed)
        self.limit = limit
        self.drops: list[SplashDrop] = []

    def emit(self, x: float, y: float, direction: float, count: int = 2):
        available = max(0, self.limit - len(self.drops))
        for _ in range(min(count, available)):
            lifetime = self.random.uniform(.26, .48)
            self.drops.append(SplashDrop(
                x=x + self.random.uniform(-.010, .010),
                y=y + self.random.uniform(-.006, .004),
                vx=-direction * self.random.uniform(.020, .048) + self.random.uniform(-.006, .006),
                vy=self.random.uniform(.035, .075),
                life=lifetime,
                max_life=lifetime,
                size=self.random.uniform(.003, .007),
            ))

    def step(self, delta_seconds: float):
        dt = max(0.0, min(.1, delta_seconds))
        alive = []
        for drop in self.drops:
            drop.life -= dt
            if drop.life <= 0:
                continue
            drop.x += drop.vx * dt
            drop.y += drop.vy * dt
            drop.vy -= .14 * dt
            alive.append(drop)
        self.drops = alive

    def drawing_data(self) -> list:
        data = []
        for drop in self.drops:
            fade = drop.life / drop.max_life
            color = (
                int(222 + 25 * fade),
                int(235 + 17 * fade),
                int(231 + 21 * fade),
            )
            data.append(['E', [drop.x, drop.y, drop.size, drop.size * .55], {
                'fill': color, 'z': 75,
            }])
        return data
