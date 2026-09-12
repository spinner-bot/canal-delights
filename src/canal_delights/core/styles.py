"""
样式模块 - 颜色处理、渐变插值、RGBA预混色
"""

from typing import Tuple, Optional, Union, List


# ============================================
# 类型定义
# ============================================

RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Color = Union[RGB, RGBA]


# ============================================
# 颜色校验
# ============================================

def validate_rgb(color: tuple) -> RGB:
    """
    校验 RGB 颜色

    参数:
        color: (r, g, b) 元组，每通道 0-255 整数

    返回:
        校验后的 RGB 元组

    异常:
        ValueError: 颜色格式无效
    """
    if not isinstance(color, (tuple, list)):
        raise ValueError(f"颜色必须是元组或列表，得到: {type(color)}")

    if len(color) not in (3, 4):
        raise ValueError(f"RGB 颜色必须有 3 或 4 个通道，得到: {len(color)}")

    for i, c in enumerate(color[:3]):
        if not isinstance(c, int):
            raise ValueError(f"颜色通道必须是整数，通道 {i} 得到: {type(c)}")
        if c < 0 or c > 255:
            raise ValueError(f"颜色通道必须在 0-255 范围内，通道 {i} 得到: {c}")

    return (color[0], color[1], color[2])


def validate_rgba(color: tuple) -> RGBA:
    """
    校验 RGBA 颜色

    参数:
        color: (r, g, b, a) 元组

    返回:
        校验后的 RGBA 元组
    """
    rgb_part = validate_rgb(color)

    if len(color) == 3:
        return rgb_part + (255,)

    a = color[3]
    if not isinstance(a, (int, float)):
        raise ValueError(f"Alpha 通道必须是数字，得到: {type(a)}")
    if isinstance(a, float):
        if a < 0.0 or a > 1.0:
            raise ValueError(f"浮点 Alpha 必须在 0.0-1.0 范围内，得到: {a}")
        a = int(a * 255)
    else:
        if a < 0 or a > 255:
            raise ValueError(f"整数 Alpha 必须在 0-255 范围内，得到: {a}")

    return rgb_part + (a,)


def is_valid_color(value) -> bool:
    """检查值是否为有效颜色"""
    try:
        validate_rgb(value)
        return True
    except (ValueError, TypeError, IndexError):
        return False


# ============================================
# 颜色转换
# ============================================

def rgb_to_hex(color: RGB) -> str:
    """RGB 转十六进制颜色字符串"""
    r, g, b = validate_rgb(color)
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_turtle(color: RGB) -> Tuple[float, float, float]:
    """RGB 转 Turtle 格式 (0.0-1.0)"""
    r, g, b = validate_rgb(color)
    return (r / 255.0, g / 255.0, b / 255.0)


# ============================================
# RGBA 预混色
# ============================================

def premultiply_alpha(
    foreground: Color,
    background: RGB,
) -> RGB:
    """
    RGBA 预混色

    公式: out = alpha * foreground + (1 - alpha) * background

    参数:
        foreground: 前景色 RGB 或 RGBA
        background: 背景色 RGB

    返回:
        混色后的 RGB
    """
    if len(foreground) == 3:
        return validate_rgb(foreground)

    r_fg, g_fg, b_fg, a = validate_rgba(foreground)
    r_bg, g_bg, b_bg = validate_rgb(background)

    alpha = a / 255.0

    r_out = int(alpha * r_fg + (1 - alpha) * r_bg)
    g_out = int(alpha * g_fg + (1 - alpha) * g_bg)
    b_out = int(alpha * b_fg + (1 - alpha) * b_bg)

    # 限制范围
    r_out = max(0, min(255, r_out))
    g_out = max(0, min(255, g_out))
    b_out = max(0, min(255, b_out))

    return (r_out, g_out, b_out)


def apply_opacity(
    color: Color,
    opacity: float,
    background: Optional[RGB] = None,
) -> RGB:
    """
    应用不透明度

    参数:
        color: 颜色
        opacity: 不透明度 0.0-1.0
        background: 背景色（opacity < 1 时必须提供）

    返回:
        混色后的 RGB
    """
    if opacity >= 1.0:
        if len(color) == 4:
            return (color[0], color[1], color[2])
        return validate_rgb(color)

    if background is None:
        # 无背景时，丢弃 alpha
        if len(color) == 4:
            return (color[0], color[1], color[2])
        return validate_rgb(color)

    # 合并 opacity 和 alpha
    if len(color) == 4:
        r, g, b, a = validate_rgba(color)
        effective_alpha = (a / 255.0) * opacity
        fg_with_opacity = (r, g, b, int(effective_alpha * 255))
    else:
        r, g, b = validate_rgb(color)
        fg_with_opacity = (r, g, b, int(opacity * 255))

    return premultiply_alpha(fg_with_opacity, background)


# ============================================
# 颜色插值
# ============================================

def lerp_color(color1: RGB, color2: RGB, t: float) -> RGB:
    """
    颜色线性插值

    参数:
        color1: 起始颜色
        color2: 结束颜色
        t: 插值因子 0.0-1.0

    返回:
        插值后的 RGB
    """
    r1, g1, b1 = validate_rgb(color1)
    r2, g2, b2 = validate_rgb(color2)

    t = max(0.0, min(1.0, t))

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return (r, g, b)


def interpolate_gradient_stops(
    stops: List[tuple],
    t: float,
) -> RGB:
    """
    在渐变色标间插值

    参数:
        stops: 色标列表 [[color, position], ...]
               position: 0.0-1.0
        t: 插值位置 0.0-1.0

    返回:
        插值后的 RGB
    """
    if not stops:
        raise ValueError("色标列表不能为空")

    if len(stops) == 1:
        color = stops[0][0]
        if len(color) == 4:
            return (color[0], color[1], color[2])
        return validate_rgb(color)

    # 确保 t 在范围内
    t = max(0.0, min(1.0, t))

    # 找到 t 所在的区间
    for i in range(len(stops) - 1):
        color1, pos1 = stops[i]
        color2, pos2 = stops[i + 1]

        if pos1 <= t <= pos2:
            # 在这个区间内插值
            if pos2 == pos1:
                local_t = 0.0
            else:
                local_t = (t - pos1) / (pos2 - pos1)

            # 处理 RGBA
            if len(color1) == 4:
                color1 = (color1[0], color1[1], color1[2])
            if len(color2) == 4:
                color2 = (color2[0], color2[1], color2[2])

            return lerp_color(color1, color2, local_t)

    # 超出范围，返回最近的色标
    if t < stops[0][1]:
        color = stops[0][0]
    else:
        color = stops[-1][0]

    if len(color) == 4:
        return (color[0], color[1], color[2])
    return validate_rgb(color)


# ============================================
# 样式解析
# ============================================

def parse_style(style_data: dict, background: Optional[RGB] = None) -> dict:
    """
    解析样式，应用预混色

    参数:
        style_data: 样式字典
        background: 背景色（用于预混色）

    返回:
        处理后的样式字典
    """
    result = style_data.copy()

    # 处理填充色
    fill = result.get('fill')
    opacity = result.get('opacity', 1.0)
    blend_with = result.get('blend_with', background)

    if fill is not None:
        if opacity < 1.0 and blend_with is not None:
            result['fill'] = apply_opacity(fill, opacity, blend_with)
        elif len(fill) == 4:
            if blend_with:
                result['fill'] = premultiply_alpha(fill, blend_with)
            else:
                result['fill'] = (fill[0], fill[1], fill[2])

    # 处理描边色
    stroke = result.get('stroke')
    if stroke is not None:
        if opacity < 1.0 and blend_with is not None:
            result['stroke'] = apply_opacity(stroke, opacity, blend_with)
        elif len(stroke) == 4:
            if blend_with:
                result['stroke'] = premultiply_alpha(stroke, blend_with)
            else:
                result['stroke'] = (stroke[0], stroke[1], stroke[2])

    return result


# ============================================
# 字体回退
# ============================================

def get_font_family(preferred: str, available: List[str]) -> str:
    """
    获取可用字体

    参数:
        preferred: 首选字体
        available: 可用字体列表

    返回:
        可用的字体名称
    """
    if preferred in available:
        return preferred

    # 回退到系统默认
    for fallback in ['Microsoft YaHei', 'PingFang SC', 'sans-serif']:
        if fallback in available:
            return fallback

    return 'sans-serif'
