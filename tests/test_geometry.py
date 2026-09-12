"""
测试 - 几何模块
"""

import pytest
import math
from canal_delights.core.geometry import (
    normalized_to_absolute,
    normalized_size_to_absolute,
    apply_transform,
    cubic_bezier_point,
    quadratic_bezier_point,
    sample_ellipse,
    point_in_polygon,
    polygon_bounds,
)


class TestCoordinateConversion:
    """坐标转换测试"""

    def test_normalized_to_absolute(self):
        bounds = (0, 0, 1000, 800)
        assert normalized_to_absolute(0.5, 0.5, bounds) == (500, 400)
        assert normalized_to_absolute(0.0, 0.0, bounds) == (0, 0)
        assert normalized_to_absolute(1.0, 1.0, bounds) == (1000, 800)

    def test_with_offset(self):
        bounds = (100, 100, 500, 400)
        result = normalized_to_absolute(0.5, 0.5, bounds)
        assert result == (350, 300)

    def test_normalized_size(self):
        bounds = (0, 0, 1000, 500)
        # 使用 min(width, height) = 500
        result = normalized_size_to_absolute(0.1, bounds)
        assert result == 50


class TestTransform:
    """变换测试"""

    def test_translate(self):
        transform = {'translate': [0.1, 0.2]}
        bounds = (0, 0, 1000, 1000)
        result = apply_transform((0.5, 0.5), transform, bounds)
        assert result == (0.6, 0.7)

    def test_scale(self):
        transform = {'scale': [2.0, 2.0], 'pivot': [0.5, 0.5]}
        bounds = (0, 0, 1000, 1000)
        # 点在枢轴上，缩放后不变
        result = apply_transform((0.5, 0.5), transform, bounds)
        assert result == (0.5, 0.5)

    def test_rotate(self):
        transform = {'rotate': 90, 'pivot': [0.5, 0.5]}
        bounds = (0, 0, 1000, 1000)
        # 点 (0.5, 0.5) 在枢轴上，旋转后不变
        result = apply_transform((0.5, 0.5), transform, bounds)
        assert abs(result[0] - 0.5) < 0.001
        assert abs(result[1] - 0.5) < 0.001


class TestBezier:
    """贝塞尔曲线测试"""

    def test_cubic_endpoints(self):
        p0, p1, p2, p3 = (0, 0), (1, 2), (3, 2), (4, 0)
        # t=0 应该在 p0
        assert cubic_bezier_point(p0, p1, p2, p3, 0.0) == p0
        # t=1 应该在 p3
        assert cubic_bezier_point(p0, p1, p2, p3, 1.0) == p3

    def test_quadratic_endpoints(self):
        p0, p1, p2 = (0, 0), (2, 4), (4, 0)
        assert quadratic_bezier_point(p0, p1, p2, 0.0) == p0
        assert quadratic_bezier_point(p0, p1, p2, 1.0) == p2

    def test_cubic_middle(self):
        p0, p1, p2, p3 = (0, 0), (0, 10), (10, 10), (10, 0)
        # t=0.5 应该在中间附近
        result = cubic_bezier_point(p0, p1, p2, p3, 0.5)
        assert result[0] == 5.0
        assert result[1] > 0  # 应该被控制点拉高


class TestEllipse:
    """椭圆采样测试"""

    def test_circle_sampling(self):
        points = sample_ellipse(0, 0, 100, 100, steps=100)
        assert len(points) == 101  # steps + 1

        # 所有点应该在圆上
        for p in points:
            distance = math.sqrt(p[0]**2 + p[1]**2)
            assert abs(distance - 100) < 1

    def test_ellipse_bounds(self):
        points = sample_ellipse(500, 400, 200, 100)
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        assert min(xs) >= 300  # 500 - 200
        assert max(xs) <= 700  # 500 + 200
        assert min(ys) >= 300  # 400 - 100
        assert max(ys) <= 500  # 400 + 100


class TestPointInPolygon:
    """点在多边形内测试"""

    def test_square(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10)]

        assert point_in_polygon((5, 5), square) == True
        assert point_in_polygon((15, 5), square) == False
        assert point_in_polygon((-5, 5), square) == False

    def test_triangle(self):
        triangle = [(0, 0), (10, 0), (5, 10)]

        assert point_in_polygon((5, 3), triangle) == True
        assert point_in_polygon((0, 10), triangle) == False


class TestPolygonBounds:
    """多边形边界测试"""

    def test_square_bounds(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10)]
        bounds = polygon_bounds(square)
        assert bounds == (0, 0, 10, 10)

    def test_triangle_bounds(self):
        triangle = [(5, 0), (0, 10), (10, 10)]
        bounds = polygon_bounds(triangle)
        assert bounds == (0, 0, 10, 10)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
