from types import SimpleNamespace

from canal_delights.app import App
from canal_delights.state import AppState, Mode, StateMachine


def test_preview_height_tracks_wrapped_description():
    app = object.__new__(App)
    _, _, _, height, _ = app._preview_layout(2)
    assert height > .19


def test_suzhou_explore_button_wins_over_forward_throttle():
    app = object.__new__(App)
    app.state = SimpleNamespace(
        mode=Mode.MAP, help_open=False, transition_locked=False,
    )
    app.boat = SimpleNamespace(nearby_city=lambda: 3)
    app.move_direction = 0
    app._pressed_nav = None
    *_, button = app._preview_layout(3)
    nx = button[0] + button[2] / 2
    ny = button[1] + button[3] / 2

    # This point belongs to both controls in the Suzhou layout.
    assert .86 <= nx <= .955 and .37 <= ny <= .51
    app.on_pointer_press(nx * 1200, ny * 800)
    assert app.move_direction == 0
    assert app._pressed_nav is None


def test_runtime_acceleration_updates_cadence_and_particle_budget():
    app = object.__new__(App)

    class Engine:
        supports_acceleration = True
        mode_name = 'accelerated'

        def set_acceleration(self, enabled):
            self.mode_name = 'accelerated' if enabled else 'pure'

    app.engine = Engine()
    app.animations = SimpleNamespace(set_fps=lambda fps: setattr(app, 'fps', fps))
    app.splash = SimpleNamespace(limit=36, drops=list(range(20)))
    app._background_rendered = True

    app._toggle_acceleration()
    assert app.engine.mode_name == 'pure'
    assert app.fps == 10
    assert app.splash.limit == 10
    assert app.splash.drops == list(range(10, 20))

    app._toggle_acceleration()
    assert app.engine.mode_name == 'accelerated'
    assert app.fps == 30


def test_click_sound_only_fires_for_a_real_hit_target():
    app = object.__new__(App)
    app.state = AppState(mode=Mode.MAP)
    calls = []
    app.effects = SimpleNamespace(play=calls.append)
    app.boat = SimpleNamespace(nearby_city=lambda: None, nudge=lambda _direction: None)
    app.machine = SimpleNamespace(open_atlas=lambda: None)
    app.begin_transition = lambda _action: None
    app.render = lambda: None

    app.on_click(600, 600)  # blank map area
    assert calls == []

    app.on_click(100, 80)  # visible atlas-book button
    assert calls == ['scroll']


def test_completed_first_load_is_never_entered_again():
    app = object.__new__(App)
    app.state = AppState(mode=Mode.INTRO)
    app.machine = StateMachine(app.state)
    app._loading_complete = True

    app._enter_journey()
    assert app.state.mode is Mode.MAP
