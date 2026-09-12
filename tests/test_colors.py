"""
测试 - 颜色处理
"""

import pytest
from canal_delights.core.styles import (
    validate_rgb, validate_rgba, rgb_to_hex, rgb_to_turtle,
    premultiply_alpha, lerp_color, interpolate_gradient_stops,
)


class TestValidateRGB:
    """RGB 校验测试"""

    def test_valid_rgb(self):
        assert validate_rgb((255, 128, 0)) == (255, 128, 0)
        assert validate_rgb((0, 0, 0)) == (0, 0, 0)
        assert validate_rgb([255, 255, 255]) == (255, 255, 255)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            validate_rgb("not a color")

    def test_invalid_length(self):
        with pytest.raises(ValueError):
            validate_rgb((255, 128))

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            validate_rgb((256, 0, 0))
        with pytest.raises(ValueError):
            validate_rgb((-1, 0, 0))

    def test_invalid_channel_type(self):
        with pytest.raises(ValueError):
            validate_rgb((255.5, 0, 0))


class TestValidateRGBA:
    """RGBA 校验测试"""

    def test_valid_rgba_int(self):
        assert validate_rgba((255, 128, 0, 200)) == (255, 128, 0, 200)

    def test_valid_rgba_float(self):
        # 0.5 -> 127
        result = validate_rgba((255, 128, 0, 0.5))
        assert result == (255, 128, 0, 127)

    def test_rgb_to_rgba(self):
        # RGB 自动添加 alpha=255
        assert validate_rgba((255, 128, 0)) == (255, 128, 0, 255)


class TestColorConversion:
    """颜色转换测试"""

    def test_rgb_to_hex(self):
        assert rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert rgb_to_hex((0, 255, 0)) == "#00ff00"
        assert rgb_to_hex((0, 0, 255)) == "#0000ff"
        assert rgb_to_hex((255, 255, 255)) == "#ffffff"

    def test_rgb_to_turtle(self):
        result = rgb_to_turtle((255, 128, 0))
        assert abs(result[0] - 1.0) < 0.01
        assert abs(result[1] - 0.5) < 0.01
        assert abs(result[2] - 0.0) < 0.01


class TestPremultiplyAlpha:
    """预混色测试"""

    def test_full_opacity(self):
        # alpha=255 应该返回原色
        result = premultiply_alpha((255, 0, 0, 255), (255, 255, 255))
        assert result == (255, 0, 0)

    def test_half_opacity(self):
        # 50% 红色在白色背景上
        result = premultiply_alpha((255, 0, 0, 128), (255, 255, 255))
        # 预期约 (255, 127, 127)
        assert result[0] == 255
        assert 120 < result[1] < 135
        assert 120 < result[2] < 135

    def test_zero_opacity(self):
        # 完全透明应该返回背景色
        result = premultiply_alpha((255, 0, 0, 0), (0, 255, 0))
        assert result == (0, 255, 0)

    def test_rgb_input(self):
        # RGB 输入直接返回
        result = premultiply_alpha((255, 0, 0), (0, 0, 0))
        assert result == (255, 0, 0)


class TestLerpColor:
    """颜色插值测试"""

    def test_endpoints(self):
        assert lerp_color((255, 0, 0), (0, 0, 255), 0.0) == (255, 0, 0)
        assert lerp_color((255, 0, 0), (0, 0, 255), 1.0) == (0, 0, 255)

    def test_middle(self):
        result = lerp_color((0, 0, 0), (255, 255, 255), 0.5)
        assert result == (127, 127, 127)

    def test_clamped(self):
        # t 应该被限制在 0-1
        assert lerp_color((0, 0, 0), (255, 255, 255), -0.5) == (0, 0, 0)
        assert lerp_color((0, 0, 0), (255, 255, 255), 1.5) == (255, 255, 255)


class TestInterpolateGradientStops:
    """渐变色标插值测试"""

    def test_single_stop(self):
        stops = [[(255, 0, 0), 0.0]]
        assert interpolate_gradient_stops(stops, 0.5) == (255, 0, 0)

    def test_two_stops(self):
        stops = [[(255, 0, 0), 0.0], [(0, 0, 255), 1.0]]
        # 中间应该是紫色
        result = interpolate_gradient_stops(stops, 0.5)
        assert result[0] > 0 and result[0] < 255
        assert result[2] > 0 and result[2] < 255

    def test_three_stops(self):
        stops = [[(255, 0, 0), 0.0], [(0, 255, 0), 0.5], [(0, 0, 255), 1.0]]
        # 0.25 应该是红绿中间
        result = interpolate_gradient_stops(stops, 0.25)
        assert result[0] > 0
        assert result[1] > 0

    def test_boundary_values(self):
        stops = [[(255, 0, 0), 0.0], [(0, 0, 255), 1.0]]
        assert interpolate_gradient_stops(stops, 0.0) == (255, 0, 0)
        assert interpolate_gradient_stops(stops, 1.0) == (0, 0, 255)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
