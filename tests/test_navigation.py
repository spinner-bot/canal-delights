import pytest

from canal_delights.core.navigation import (
    BoatPhysics, CITY_POINTS, readable_boat_pose, route_point, route_tangent,
)


@pytest.mark.parametrize('index', range(5))
def test_route_passes_through_every_city(index):
    assert route_point(index / 4) == pytest.approx(CITY_POINTS[index])


def test_boat_accelerates_coasts_and_stays_on_route():
    boat = BoatPhysics()
    for _ in range(20):
        boat.step(1, 1 / 30)
    assert boat.position > 0
    assert 0 < boat.velocity <= boat.max_speed

    moving_position = boat.position
    boat.step(0, 1 / 30)
    assert boat.position > moving_position

    for _ in range(500):
        boat.step(1, 1 / 30)
    assert boat.position == 1


def test_nearby_city_only_inside_activation_radius():
    boat = BoatPhysics(position=.25)
    assert boat.nearby_city() == 1
    boat.position = .13
    assert boat.nearby_city() is None


def test_route_tangent_is_normalized():
    x, y = route_tangent(.5)
    assert x * x + y * y == pytest.approx(1.0)


def test_boat_pose_stays_upright_and_flips_after_vertical_threshold():
    angle, flipped = readable_boat_pose((-.3, -.95))
    assert -90 <= angle <= 90
    assert flipped

    reverse_angle, reverse_flipped = readable_boat_pose((.8, -.2), direction=-1)
    assert -90 <= reverse_angle <= 90
    assert reverse_flipped
