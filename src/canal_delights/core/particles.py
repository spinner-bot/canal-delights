"""Lightweight deterministic particles expressed in normalized scene space."""

from dataclasses import dataclass
import random


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float


class ParticleSystem:
    def __init__(self, seed: int = 2026, limit: int = 72):
        self.random = random.Random(seed)
        self.limit = limit
        self.particles: list[Particle] = []

    def emit_splash(self, x: float, y: float, direction: float, count: int = 2):
        available = max(0, self.limit - len(self.particles))
        for _ in range(min(count, available)):
            life = self.random.uniform(.30, .62)
            self.particles.append(Particle(
                x=x + self.random.uniform(-.012, .012),
                y=y + self.random.uniform(-.008, .004),
                vx=-direction * self.random.uniform(.018, .045) + self.random.uniform(-.008, .008),
                vy=self.random.uniform(.035, .080),
                life=life,
                max_life=life,
                size=self.random.uniform(.004, .009),
            ))

    def step(self, delta_seconds: float):
        dt = max(0.0, min(.1, delta_seconds))
        alive = []
        for particle in self.particles:
            particle.life -= dt
            if particle.life <= 0:
                continue
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy -= .12 * dt
            alive.append(particle)
        self.particles = alive

    def drawing_data(self) -> list:
        data = []
        for particle in self.particles:
            fade = particle.life / particle.max_life
            color = (int(206 + 35 * fade), int(228 + 22 * fade), int(229 + 24 * fade))
            data.append(['C', [particle.x, particle.y, particle.size * (.55 + .45 * fade)], {
                'fill': color, 'z': 80,
            }])
        return data
