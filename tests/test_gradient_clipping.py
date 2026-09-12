import pytest

from canal_delights.core.geometry import clip_polygon_to_projection_band, polygon_bounds


def test_projection_band_clips_rectangle_horizontally():
    result = clip_polygon_to_projection_band(
        [(0, 0), (10, 0), (10, 8), (0, 8)], (1, 0), 2, 6,
    )
    assert polygon_bounds(result) == pytest.approx((2, 0, 6, 8))


def test_projection_band_can_clip_diagonally():
    result = clip_polygon_to_projection_band(
        [(0, 0), (10, 0), (10, 10), (0, 10)], (1, 1), 8, 12,
    )
    assert result
    assert all(8 - 1e-9 <= x + y <= 12 + 1e-9 for x, y in result)
