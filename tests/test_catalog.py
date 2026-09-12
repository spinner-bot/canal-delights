from canal_delights.content.catalog import get_all_cities
from canal_delights.content.foods.prototype import get_food_drawing


def test_catalog_contains_five_cities_and_twenty_foods():
    cities = get_all_cities()
    assert len(cities) == 5
    assert all(len(city['foods']) == 4 for city in cities)
    assert sum(len(city['foods']) for city in cities) == 20


def test_every_food_has_real_intro_and_story():
    for city in get_all_cities():
        assert city['description']
        assert city['cuisine']
        for food in city['foods']:
            assert len(food['intro']) >= 20
            assert len(food['story']) >= 40
            assert get_food_drawing(city['id'], food['id'])
