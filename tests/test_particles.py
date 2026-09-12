from canal_delights.core.particles import ParticleSystem


def test_particles_emit_move_and_expire():
    particles = ParticleSystem(seed=1, limit=4)
    particles.emit_splash(.5, .5, 1, count=10)
    assert len(particles.particles) == 4
    assert len(particles.drawing_data()) == 4

    for _ in range(10):
        particles.step(.1)
    assert particles.particles == []
