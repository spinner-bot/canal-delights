from canal_delights.state import AppState, Mode, StateMachine


def test_all_four_tastings_stamp_a_city():
    state = AppState(mode=Mode.CITY)
    machine = StateMachine(state)

    for _ in range(4):
        machine.open_food()
        machine.complete_tasting()
        machine.next_food()

    assert state.mode is Mode.CITY
    assert state.discovered_foods == {'0_0', '0_1', '0_2', '0_3'}
    assert state.stamped_cities == {0}


def test_atlas_opens_from_map_and_pages_are_bounded():
    state = AppState(mode=Mode.MAP)
    machine = StateMachine(state)

    machine.open_atlas()
    assert state.mode is Mode.ATLAS
    machine.turn_atlas(20)
    assert state.atlas_page == 5
    machine.turn_atlas(-20)
    assert state.atlas_page == 0
    machine.back()
    assert state.mode is Mode.MAP


def test_settings_opens_from_map_and_returns_to_map():
    state = AppState(mode=Mode.MAP)
    machine = StateMachine(state)
    machine.open_settings()
    assert state.mode is Mode.SETTINGS
    machine.back()
    assert state.mode is Mode.MAP


def test_finale_only_opens_after_all_city_stamps():
    state = AppState(mode=Mode.MAP)
    machine = StateMachine(state)

    machine.go_to_finale()
    assert state.mode is Mode.MAP

    state.stamped_cities.update(range(5))
    machine.go_to_finale()
    assert state.mode is Mode.FINALE


def test_first_journey_has_explicit_loading_stage():
    state = AppState()
    machine = StateMachine(state)
    machine.start_loading()
    assert state.mode is Mode.LOADING
    assert not state.can_go_back()
    machine.finish_loading()
    assert state.mode is Mode.MAP
