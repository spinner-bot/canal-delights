import pytest

from canal_delights.core.animation import SceneTransition, Tween, ease_in_out_cubic, ease_out_cubic


@pytest.mark.parametrize('easing', [ease_out_cubic, ease_in_out_cubic])
def test_easing_is_clamped(easing):
    assert easing(-1) == 0
    assert easing(2) == 1


def test_tween_reaches_exact_end_and_reports_done():
    tween = Tween(10, 30, duration=0.5)
    assert 10 < tween.step(0.25) < 30
    assert tween.step(0.25) == 30
    assert tween.done


def test_tween_ignores_negative_delta():
    tween = Tween(0, 1, duration=1)
    assert tween.step(-2) == 0


def test_scene_transition_switches_once_at_midpoint():
    calls = []
    transition = SceneTransition(duration=1)
    assert transition.start(lambda: calls.append('switched'))
    assert not transition.start(lambda: calls.append('duplicate'))
    transition.step(.49)
    assert calls == []
    assert 0 < transition.cover < 1
    transition.step(.02)
    transition.step(.2)
    assert calls == ['switched']
    transition.step(.29)
    assert not transition.active
    assert transition.cover == 0
