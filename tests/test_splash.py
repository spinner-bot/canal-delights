from canal_delights.core.splash import SplashSystem


def test_splash_is_bounded_and_expires():
    splash = SplashSystem(seed=1, limit=3)
    splash.emit(.5, .5, 1, count=20)
    assert len(splash.drops) == 3
    assert len(splash.drawing_data()) == 3

    for _ in range(10):
        splash.step(.1)
    assert splash.drops == []


def test_splash_trails_opposite_travel_direction():
    splash = SplashSystem(seed=2)
    splash.emit(.5, .5, 1, count=1)
    assert splash.drops[0].vx < 0
