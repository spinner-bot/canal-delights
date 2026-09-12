import pytest

from canal_delights.core.geometry import apply_transform, compose_transforms


def test_composed_transform_keeps_parent_and_child_operations():
    combined = compose_transforms(
        {'scale': [2.0, 2.0], 'pivot': [0.5, 0.5]},
        {'translate': [0.1, 0.0]},
    )
    assert apply_transform((0.5, 0.5), combined, (0, 0, 100, 100)) == pytest.approx((0.7, 0.5))


def test_composed_transform_respects_distinct_pivots():
    combined = compose_transforms(
        {'translate': [0.2, 0.1]},
        {'rotate': 90, 'pivot': [0.0, 0.0]},
    )
    assert apply_transform((0.2, 0.0), combined, (0, 0, 100, 100)) == pytest.approx((0.2, 0.3))
