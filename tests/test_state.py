from canal_delights.state import AppState, Mode, StateMachine


def test_two_tastings_stamp_a_city():
    state = AppState(mode=Mode.CITY)
    machine = StateMachine(state)

    machine.open_food()
    machine.complete_tasting()
    machine.next_food()
    machine.open_food()
    machine.complete_tasting()

    assert state.mode is Mode.CITY
    assert state.discovered_foods == {'0_0', '0_1'}
    assert state.stamped_cities == {0}


def test_finale_only_opens_after_all_city_stamps():
    state = AppState(mode=Mode.MAP)
    machine = StateMachine(state)

    machine.go_to_finale()
    assert state.mode is Mode.MAP

    state.stamped_cities.update(range(5))
    machine.go_to_finale()
    assert state.mode is Mode.FINALE
