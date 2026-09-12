"""
绘图引擎 - 封装 Turtle 操作，实现所有 primitive 绘制

职责：
- 对 Turtle 的低层绘制封装
- 基础图形、渐变填充、贝塞尔曲线、复合路径
- 不负责业务状态与城市逻辑
"""

import turtle
import math
from typing import List, Tuple, Optional, Union

from .styles import (
    RGB, Color, rgb_to_hex, rgb_to_turtle,
    validate_rgb, interpolate_gradient_stops,
)
from .geometry import (
    sample_ellipse, sample_cubic_bezier, sample_quadratic_bezier,
    polygon_bounds, clip_polygon_by_line, line_intersection,
)


class DrawingEngine:
    """
    绘图引擎

    职责：
    - 对 Turtle 的低层绘制封装
    - 所有 primitive 的实际绘制
    """

    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height

        # 初始化 Turtle 屏幕
        self.screen = turtle.Screen()
        self.screen.setup(width, height)
        self.screen.title("运河四季·美食绘卷")
        self.screen.tracer(0, 0)  # 关闭自动刷新，手动控制

        # 设置坐标系：(0,0) 在左下角，(width,height) 在右上角
        self.screen.setworldcoordinates(0, 0, width, height)

        # 初始化画笔
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.up()

        # 设置背景色
        from ..config import CANVAS_BG
        self.set_bgcolor(CANVAS_BG)

    # ============================================
    # 基础控制
    # ============================================

    def clear(self):
        """清空画布"""
        self.pen.clear()
        self.pen.up()

    def update(self):
        """手动刷新屏幕"""
        self.screen.update()

    def set_bgcolor(self, color: RGB):
        """设置背景色"""
        self.screen.bgcolor(rgb_to_hex(color))

    def exitonclick(self):
        """点击退出"""
        self.screen.exitonclick()

    def mainloop(self):
        """进入主循环"""
        self.screen.mainloop()

    def onkey(self, callback, key: str):
        """绑定键盘事件"""
        self.screen.onkey(callback, key)

    def listen(self):
        """开始监听键盘"""
        self.screen.listen()

    # ============================================
    # 基础图形
    # ============================================

    def draw_point(self, x: float, y: float, size: float, color: RGB):
        """绘制点"""
        self.pen.up()
        self.pen.goto(x, y)
        self.pen.dot(size, rgb_to_hex(color))

    def draw_line(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        color: RGB,
        width: float = 1.0,
    ):
        """绘制线段"""
        self.pen.up()
        self.pen.goto(x1, y1)
        self.pen.down()
        self.pen.pensize(max(1, width))
        self.pen.pencolor(rgb_to_hex(color))
        self.pen.goto(x2, y2)
        self.pen.up()

    def draw_polyline(
        self,
        points: List[Tuple[float, float]],
        color: RGB,
        width: float = 1.0,
        close: bool = False,
    ):
        """绘制折线"""
        if not points:
            return

        self.pen.up()
        self.pen.goto(points[0])
        self.pen.down()
        self.pen.pensize(max(1, width))
        self.pen.pencolor(rgb_to_hex(color))

        for p in points[1:]:
            self.pen.goto(p)

        if close and len(points) > 2:
            self.pen.goto(points[0])

        self.pen.up()

    # ============================================
    # 填充图形
    # ============================================

    def draw_circle(
        self,
        cx: float, cy: float,
        r: float,
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制圆形"""
        # 转换为多边形以便统一处理渐变
        points = sample_ellipse(cx, cy, r, r)
        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    def draw_ellipse(
        self,
        cx: float, cy: float,
        rx: float, ry: float,
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制椭圆"""
        points = sample_ellipse(cx, cy, rx, ry)
        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    def draw_rect(
        self,
        x: float, y: float,
        w: float, h: float,
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制矩形"""
        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    def draw_rounded_rect(
        self,
        x: float, y: float,
        w: float, h: float,
        r: float,
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制圆角矩形"""
        r = min(r, w / 2, h / 2)
        points = []

        # 四个圆角
        corners = [
            (x + w - r, y + r, 0, 90),      # 右上
            (x + w - r, y + h - r, 270, 360),  # 右下
            (x + r, y + h - r, 180, 270),    # 左下
            (x + r, y + r, 90, 180),         # 左上
        ]

        for cx, cy, start, end in corners:
            steps = 10
            for i in range(steps + 1):
                angle = math.radians(start + (end - start) * i / steps)
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                points.append((px, py))

        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    def draw_polygon(
        self,
        points: List[Tuple[float, float]],
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制多边形"""
        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    def draw_ring(
        self,
        cx: float, cy: float,
        r_inner: float,
        r_outer: float,
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制圆环"""
        # 外圆顺时针，内圆逆时针
        outer_points = sample_ellipse(cx, cy, r_outer, r_outer)
        inner_points = sample_ellipse(cx, cy, r_inner, r_inner)
        inner_points.reverse()

        # 组合为环形多边形
        points = outer_points + inner_points
        self._draw_filled_polygon(points, fill, stroke, stroke_width)

    # ============================================
    # 弧形和曲线
    # ============================================

    def draw_arc(
        self,
        cx: float, cy: float,
        r: float,
        start_angle: float,
        end_angle: float,
        color: RGB,
        width: float = 1.0,
    ):
        """绘制弧形"""
        steps = 50
        points = []
        for i in range(steps + 1):
            t = i / steps
            angle = math.radians(start_angle + (end_angle - start_angle) * t)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append((px, py))

        self.draw_polyline(points, color, width, close=False)

    def draw_bezier(
        self,
        control_points: List[Tuple[float, float]],
        color: RGB,
        width: float = 1.0,
    ):
        """绘制三次贝塞尔曲线"""
        if len(control_points) < 4:
            return

        points = sample_cubic_bezier(
            control_points[0],
            control_points[1],
            control_points[2],
            control_points[3],
        )
        self.draw_polyline(points, color, width, close=False)

    def draw_quadratic(
        self,
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        color: RGB,
        width: float = 1.0,
    ):
        """绘制二次贝塞尔曲线"""
        points = sample_quadratic_bezier(p0, p1, p2)
        self.draw_polyline(points, color, width, close=False)

    def draw_path(
        self,
        commands: List[list],
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """
        绘制复合路径

        命令格式：
        - ['M', x, y] - 移动到
        - ['L', x, y] - 画线到
        - ['Q', x1, y1, x2, y2] - 二次贝塞尔
        - ['C', x1, y1, x2, y2, x3, y3] - 三次贝塞尔
        - ['Z'] - 闭合路径
        """
        points = []
        current_pos = (0, 0)

        for cmd in commands:
            if not cmd:
                continue

            op = cmd[0]

            if op == 'M' and len(cmd) >= 3:
                current_pos = (cmd[1], cmd[2])
                points.append(current_pos)

            elif op == 'L' and len(cmd) >= 3:
                current_pos = (cmd[1], cmd[2])
                points.append(current_pos)

            elif op == 'Q' and len(cmd) >= 5:
                p0 = current_pos
                p1 = (cmd[1], cmd[2])
                p2 = (cmd[3], cmd[4])
                curve_points = sample_quadratic_bezier(p0, p1, p2)
                points.extend(curve_points[1:])  # 跳过起点
                current_pos = p2

            elif op == 'C' and len(cmd) >= 7:
                p0 = current_pos
                p1 = (cmd[1], cmd[2])
                p2 = (cmd[3], cmd[4])
                p3 = (cmd[5], cmd[6])
                curve_points = sample_cubic_bezier(p0, p1, p2, p3)
                points.extend(curve_points[1:])
                current_pos = p3

            elif op == 'Z':
                if points:
                    points.append(points[0])

        if points:
            self._draw_filled_polygon(points, fill, stroke, stroke_width)

    # ============================================
    # 文字
    # ============================================

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        font_size: int,
        color: RGB,
        font_family: str = 'Microsoft YaHei',
        align: str = 'center',
        weight: str = 'normal',
    ):
        """绘制文字"""
        self.pen.up()
        self.pen.goto(x, y)
        self.pen.pencolor(rgb_to_hex(color))

        align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
        turtle_align = align_map.get(align, 'center')

        self.pen.write(
            text,
            align=turtle_align,
            font=(font_family, font_size, weight),
        )

    # ============================================
    # 渐变填充
    # ============================================

    def draw_gradient_fill(
        self,
        polygon: List[Tuple[float, float]],
        gradient: dict,
        bounds: Tuple[float, float, float, float],
    ):
        """
        绘制渐变填充

        参数:
            polygon: 目标多边形
            gradient: 渐变定义
            bounds: 绘制区域
        """
        if not polygon or not gradient:
            return

        gradient_type = gradient.get('type', 'linear')
        stops = gradient.get('stops', [])
        steps = gradient.get('steps', 36)

        if not stops:
            return

        if gradient_type == 'linear':
            self._draw_linear_gradient(polygon, stops, gradient.get('angle', 0), steps)
        elif gradient_type == 'radial':
            self._draw_radial_gradient(polygon, stops, gradient.get('center', [0.5, 0.5]), steps, bounds)

    def _draw_linear_gradient(
        self,
        polygon: List[Tuple[float, float]],
        stops: List[tuple],
        angle: float,
        steps: int,
    ):
        """线性渐变填充"""
        # 获取多边形边界
        min_x, min_y, max_x, max_y = polygon_bounds(polygon)

        # 计算渐变方向
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = math.sin(rad)

        # 计算渐变轴上的投影范围
        projected = []
        for p in polygon:
            proj = (p[0] - min_x) * dx + (p[1] - min_y) * dy
            projected.append(proj)

        min_proj = min(projected)
        max_proj = max(projected)
        proj_range = max_proj - min_proj

        if proj_range < 1e-6:
            # 退化情况：用第一个颜色填充
            color = interpolate_gradient_stops(stops, 0)
            self._fill_polygon(polygon, color)
            return

        # 绘制色带
        for i in range(steps):
            t1 = i / steps
            t2 = (i + 1) / steps

            # 计算色带边界
            proj1 = min_proj + proj_range * t1
            proj2 = min_proj + proj_range * t2

            # 插值颜色
            color = interpolate_gradient_stops(stops, (t1 + t2) / 2)

            # 计算色带的四个角点
            perp_dx = -dy
            perp_dy = dx

            # 扩展范围确保覆盖
            extension = max(max_x - min_x, max_y - min_y)

            corners = [
                (min_x + proj1 * dx - extension * perp_dx,
                 min_y + proj1 * dy - extension * perp_dy),
                (min_x + proj1 * dx + extension * perp_dx,
                 min_y + proj1 * dy + extension * perp_dy),
                (min_x + proj2 * dx + extension * perp_dx,
                 min_y + proj2 * dy + extension * perp_dy),
                (min_x + proj2 * dx - extension * perp_dx,
                 min_y + proj2 * dy - extension * perp_dy),
            ]

            # 裁切到目标多边形
            clipped = self._clip_to_polygon(corners, polygon)

            if clipped:
                self._fill_polygon(clipped, color)

    def _draw_radial_gradient(
        self,
        polygon: List[Tuple[float, float]],
        stops: List[tuple],
        center: List[float],
        steps: int,
        bounds: Tuple[float, float, float, float],
    ):
        """径向渐变填充"""
        min_x, min_y, max_x, max_y = polygon_bounds(polygon)
        width = max_x - min_x
        height = max_y - min_y

        cx = min_x + width * center[0]
        cy = min_y + height * center[1]
        max_r = max(width, height) / 2

        # 从外向内绘制同心多边形
        for i in range(steps, 0, -1):
            t = i / steps
            r = max_r * t

            # 生成圆形采样点
            circle_points = sample_ellipse(cx, cy, r, r)

            # 与目标多边形求交（简化：直接用圆形）
            # TODO: 实现真正的多边形裁切

            color = interpolate_gradient_stops(stops, t)
            self._fill_polygon(circle_points, color)

    def _clip_to_polygon(
        self,
        source: List[Tuple[float, float]],
        target: List[Tuple[float, float]],
    ) -> List[Tuple[float, float]]:
        """
        将 source 多边形裁切到 target 多边形内

        简化实现：保留 target 内的 source 点
        """
        from .geometry import point_in_polygon

        result = []
        for p in source:
            if point_in_polygon(p, target):
                result.append(p)

        # 如果裁切后点太少，返回 target
        return result if len(result) >= 3 else target

    # ============================================
    # 内部辅助方法
    # ============================================

    def _draw_filled_polygon(
        self,
        points: List[Tuple[float, float]],
        fill: Optional[RGB] = None,
        stroke: Optional[RGB] = None,
        stroke_width: float = 1.0,
    ):
        """绘制填充多边形"""
        if not points:
            return

        if fill:
            self._fill_polygon(points, fill)

        if stroke:
            self.draw_polyline(points, stroke, stroke_width, close=True)

    def _fill_polygon(
        self,
        points: List[Tuple[float, float]],
        color: RGB,
    ):
        """填充多边形"""
        if not points:
            return

        self.pen.up()
        self.pen.goto(points[0])
        self.pen.down()
        self.pen.fillcolor(rgb_to_hex(color))
        self.pen.begin_fill()

        for p in points[1:]:
            self.pen.goto(p)

        self.pen.goto(points[0])
        self.pen.end_fill()
        self.pen.up()
