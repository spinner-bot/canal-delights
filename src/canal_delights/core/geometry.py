"""
几何模块 - 变换、曲线采样、多边形裁切、命中测试
"""

import math
from typing import List, Tuple, Optional


Point = Tuple[float, float]


# ============================================
# 坐标转换
# ============================================

def normalized_to_absolute(
    x: float,
    y: float,
    bounds: Tuple[float, float, float, float],
) -> Point:
    """
    归一化坐标转绝对坐标

    参数:
        x, y: 归一化坐标 0.0-1.0
        bounds: (left, bottom, width, height)

    返回:
        绝对坐标 (x, y)
    """
    left, bottom, width, height = bounds
    abs_x = left + x * width
    abs_y = bottom + y * height
    return (abs_x, abs_y)


def normalized_size_to_absolute(
    size: float,
    bounds: Tuple[float, float, float, float],
) -> float:
    """
    归一化尺寸转绝对尺寸

    使用 min(width, height) 作为基准，避免非等比拉伸
    """
    _, _, width, height = bounds
    return size * min(width, height)


def normalized_points_to_absolute(
    points: List[Point],
    bounds: Tuple[float, float, float, float],
) -> List[Point]:
    """批量转换点坐标"""
    return [normalized_to_absolute(p[0], p[1], bounds) for p in points]


# ============================================
# Transform 变换
# ============================================

def apply_transform(
    point: Point,
    transform: dict,
    bounds: Tuple[float, float, float, float],
) -> Point:
    """
    应用变换到点

    执行顺序：
    1. 确定枢轴点
    2. 缩放（围绕枢轴）
    3. 旋转（围绕枢轴）
    4. 平移

    参数:
        point: 原始点 (x, y) 归一化坐标
        transform: 变换字典
        bounds: 绘制区域

    返回:
        变换后的点
    """
    # A composed transform retains individual operations and pivots.  Merging
    # the two dictionaries loses this information whenever transforms differ.
    if transform and '_chain' in transform:
        result = point
        for step in transform['_chain']:
            result = apply_transform(result, step, bounds)
        return result

    x, y = point

    # 确定枢轴点（默认为中心）
    pivot = transform.get('pivot')
    if pivot:
        px, py = pivot
    else:
        px, py = 0.5, 0.5

    # 缩放
    scale = transform.get('scale')
    if scale:
        sx, sy = scale if len(scale) == 2 else (scale[0], scale[0])
        # 围绕枢轴缩放
        x = px + (x - px) * sx
        y = py + (y - py) * sy

    # 旋转
    rotate = transform.get('rotate')
    if rotate:
        angle_rad = math.radians(rotate)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        # 围绕枢轴旋转
        dx = x - px
        dy = y - py
        x = px + dx * cos_a - dy * sin_a
        y = py + dx * sin_a + dy * cos_a

    # 平移
    translate = transform.get('translate')
    if translate:
        x += translate[0]
        y += translate[1]

    return (x, y)


def transform_points(
    points: List[Point],
    transform: dict,
    bounds: Tuple[float, float, float, float],
) -> List[Point]:
    """批量变换点"""
    return [apply_transform(p, transform, bounds) for p in points]


def compose_transforms(parent: dict, child: dict) -> dict:
    """
    组合父子变换

    Child operations happen in local coordinates, followed by the parent.
    A short chain is equivalent to matrix composition for points and preserves
    distinct pivots without introducing a separate matrix representation.
    """
    return {'_chain': [child, parent]}


# ============================================
# 贝塞尔曲线
# ============================================

def cubic_bezier_point(
    p0: Point,
    p1: Point,
    p2: Point,
    p3: Point,
    t: float,
) -> Point:
    """
    计算三次贝塞尔曲线上的点

    参数:
        p0, p1, p2, p3: 控制点
        t: 参数 0.0-1.0

    返回:
        曲线上的点
    """
    t = max(0.0, min(1.0, t))
    t2 = t * t
    t3 = t2 * t
    mt = 1 - t
    mt2 = mt * mt
    mt3 = mt2 * mt

    x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
    y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]

    return (x, y)


def quadratic_bezier_point(
    p0: Point,
    p1: Point,
    p2: Point,
    t: float,
) -> Point:
    """
    计算二次贝塞尔曲线上的点

    参数:
        p0, p1, p2: 控制点
        t: 参数 0.0-1.0

    返回:
        曲线上的点
    """
    t = max(0.0, min(1.0, t))
    mt = 1 - t

    x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
    y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]

    return (x, y)


def sample_cubic_bezier(
    p0: Point,
    p1: Point,
    p2: Point,
    p3: Point,
    steps: int = 50,
) -> List[Point]:
    """采样三次贝塞尔曲线"""
    points = []
    for i in range(steps + 1):
        t = i / steps
        points.append(cubic_bezier_point(p0, p1, p2, p3, t))
    return points


def sample_quadratic_bezier(
    p0: Point,
    p1: Point,
    p2: Point,
    steps: int = 50,
) -> List[Point]:
    """采样二次贝塞尔曲线"""
    points = []
    for i in range(steps + 1):
        t = i / steps
        points.append(quadratic_bezier_point(p0, p1, p2, t))
    return points


# ============================================
# 椭圆采样
# ============================================

def sample_ellipse(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    steps: int = 100,
) -> List[Point]:
    """采样椭圆为多边形"""
    points = []
    for i in range(steps + 1):
        angle = 2 * math.pi * i / steps
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        points.append((x, y))
    return points


# ============================================
# 多边形操作
# ============================================

def polygon_area(points: List[Point]) -> float:
    """计算多边形面积（有符号）"""
    n = len(points)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]

    return area / 2.0


def polygon_bounds(points: List[Point]) -> Tuple[float, float, float, float]:
    """计算多边形边界框 (min_x, min_y, max_x, max_y)"""
    if not points:
        return (0, 0, 0, 0)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    return (min(xs), min(ys), max(xs), max(ys))


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    判断点是否在多边形内（射线法）

    参数:
        point: 测试点
        polygon: 多边形顶点列表

    返回:
        True 如果在内部
    """
    x, y = point
    n = len(polygon)
    inside = False

    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside

        j = i

    return inside


# ============================================
# 多边形裁切（Sutherland-Hodgman）
# ============================================

def clip_polygon_by_line(
    polygon: List[Point],
    line_start: Point,
    line_end: Point,
) -> List[Point]:
    """
    用直线裁切多边形（保留左侧）

    Sutherland-Hodgman 算法的单边版本
    """
    if not polygon:
        return []

    result = []
    n = len(polygon)

    for i in range(n):
        current = polygon[i]
        next_pt = polygon[(i + 1) % n]

        # 判断点在直线的哪一侧
        def side(p):
            return ((line_end[0] - line_start[0]) * (p[1] - line_start[1]) -
                    (line_end[1] - line_start[1]) * (p[0] - line_start[0]))

        current_side = side(current)
        next_side = side(next_pt)

        if current_side >= 0:  # 当前点在左侧
            result.append(current)
            if next_side < 0:  # 下一个点在右侧，计算交点
                intersection = line_intersection(
                    current, next_pt, line_start, line_end
                )
                if intersection:
                    result.append(intersection)
        elif next_side >= 0:  # 当前点在右侧，下一个点在左侧
            intersection = line_intersection(
                current, next_pt, line_start, line_end
            )
            if intersection:
                result.append(intersection)

    return result


def line_intersection(
    p1: Point,
    p2: Point,
    p3: Point,
    p4: Point,
) -> Optional[Point]:
    """计算两条直线的交点"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if abs(denom) < 1e-10:
        return None  # 平行

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom

    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)

    return (x, y)


def clip_polygon_to_projection_band(
    polygon: List[Point],
    axis: Point,
    lower: float,
    upper: float,
) -> List[Point]:
    """Clip a polygon to ``lower <= dot(point, axis) <= upper``.

    This is the convex half-plane operation needed by linear-gradient bands.
    It also behaves predictably for the concave shapes used by this project,
    although a band may be returned as one connected polygon.
    """
    def projection(point: Point) -> float:
        return point[0] * axis[0] + point[1] * axis[1]

    def clip(points: List[Point], threshold: float, keep_greater: bool) -> List[Point]:
        if not points:
            return []
        output = []
        previous = points[-1]
        previous_value = projection(previous)
        previous_inside = previous_value >= threshold if keep_greater else previous_value <= threshold

        for current in points:
            current_value = projection(current)
            current_inside = current_value >= threshold if keep_greater else current_value <= threshold
            if current_inside != previous_inside:
                denominator = current_value - previous_value
                if abs(denominator) > 1e-12:
                    ratio = (threshold - previous_value) / denominator
                    output.append((
                        previous[0] + (current[0] - previous[0]) * ratio,
                        previous[1] + (current[1] - previous[1]) * ratio,
                    ))
            if current_inside:
                output.append(current)
            previous = current
            previous_value = current_value
            previous_inside = current_inside
        return output

    return clip(clip(list(polygon), lower, True), upper, False)


# ============================================
# 渐变裁切
# ============================================

def clip_gradient_band(
    polygon: List[Point],
    band_start: Point,
    band_end: Point,
    angle: float,
) -> List[Point]:
    """
    裁切渐变色的色带

    参数:
        polygon: 目标多边形
        band_start, band_end: 色带边界线
        angle: 渐变角度

    返回:
        裁切后的多边形
    """
    # 简化实现：用矩形边界裁切
    # TODO: 实现完整的 Sutherland-Hodgman 多边形裁切

    if not polygon:
        return []

    # 计算色带矩形
    min_x = min(band_start[0], band_end[0])
    max_x = max(band_start[0], band_end[0])
    min_y = min(band_start[1], band_end[1])
    max_y = max(band_start[1], band_end[1])

    # 简单的边界框裁切
    result = []
    for p in polygon:
        x, y = p
        if min_x <= x <= max_x and min_y <= y <= max_y:
            result.append(p)

    return result if result else polygon


# ============================================
# 命中测试
# ============================================

def hit_test_point(
    point: Point,
    target: Point,
    radius: float,
) -> bool:
    """点命中测试（圆形区域）"""
    dx = point[0] - target[0]
    dy = point[1] - target[1]
    return dx * dx + dy * dy <= radius * radius


def hit_test_polygon(
    point: Point,
    polygon: List[Point],
) -> bool:
    """多边形命中测试"""
    return point_in_polygon(point, polygon)


def hit_test_rect(
    point: Point,
    rect: Tuple[float, float, float, float],
) -> bool:
    """矩形命中测试 (x, y, w, h)"""
    x, y = point
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh
