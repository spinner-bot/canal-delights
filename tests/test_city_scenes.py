import pytest

from canal_delights.content.scenes import FOOD_POSITIONS, SCENE_BUILDERS, get_city_scene


@pytest.mark.parametrize('city_id', SCENE_BUILDERS)
def test_each_city_has_a_distinct_nonempty_scene(city_id):
    scene = get_city_scene(city_id, (120, 80, 60), phase=.5, gradient_steps=6)
    assert len(scene) >= 8
    assert len(FOOD_POSITIONS[city_id]) == 2
    assert all(item[0] in {'R', 'RR', 'C', 'E', 'G', 'L', 'B', 'A'} for item in scene)


def test_city_scenes_are_not_identical_templates():
    signatures = {
        city_id: tuple(item[0] for item in get_city_scene(city_id, (1, 2, 3), 0, 4))
        for city_id in SCENE_BUILDERS
    }
    assert len(set(signatures.values())) == len(SCENE_BUILDERS)
