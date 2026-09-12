"""
绘图引擎 - 封装所有 Turtle 操作
支持：基础图形、渐变填充、贝塞尔曲线、复合路径
"""

import turtle
import math
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEME, rgb


class DrawingEngine:
    """绘图引擎 - 声明式渲染接口"""

    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = turtle.Screen()
        self.screen.setup(width, height)
        self.screen.bgcolor(self._rgb_to_hex(THEME['canvas']['background']))
        self.screen.title("运河四季·美食绘卷")
        self.screen.tracer(0, 0)  # 关闭自动刷新

        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.up()

        self._gradient_cache = {}

    # ============================================
    # 颜色转换
    # ============================================

    def _rgb_to_hex(self, color):
        """RGB256 转十六进制"""
        if len(color) == 4:  # RGBA
            r, g, b, a = color
        else:
            r, g, b = color
        return f"#{r:02x}{g:02x}{b:02x}"

    def _rgb_to_turtle(self, color):
        """RGB256 转 Turtle 格式 (0-1)"""
        if len(color) == 4:
            r, g, b, a = color
        else:
            r, g, b = color
        return (r / 255, g / 255, b / 255)

    # ============================================
    # 基础设置
    # ============================================

    def clear(self):
        """清空画布"""
        self.pen.clear()
        self.pen.up()
        self.pen.goto(0, 0)

    def update(self):
        """手动刷新屏幕"""
        self.screen.update()

    def set_bgcolor(self, color):
        """设置背景色"""
        self.screen.bgcolor(self._rgb_to_hex(color))

    # ============================================
    # 基础图形绘制
    # ============================================

    def draw_point(self, x, y, size, color):
        """绘制点"""
        self.pen.up()
        self.pen.goto(x, y)
        self.pen.dot(size, self._rgb_to_hex(color))

    def draw_line(self, x1, y1, x2, y2, color, width=1):
        """绘制线段"""
        self.pen.up()
        self.pen.goto(x1, y1)
        self.pen.down()
        self.pen.pensize(width)
        self.pen.pencolor(self._rgb_to_hex(color))
        self.pen.goto(x2, y2)
        self.pen.up()

    def draw_circle(self, x, y, r, fill_style):
        """绘制圆形"""
        self._draw_filled_shape('circle', x, y, r, fill_style)

    def draw_ellipse(self, x, y, rx, ry, fill_style):
        """绘制椭圆"""
        self._draw_filled_shape('ellipse', x, y, rx, ry, fill_style)

    def draw_rect(self, x, y, w, h, fill_style, radius=0):
        """绘制矩形"""
        if radius > 0:
            self._draw_rounded_rect(x, y, w, h, radius, fill_style)
        else:
            self._draw_filled_shape('rect', x, y, w, h, fill_style)

    def draw_polygon(self, points, fill_style):
        """绘制多边形"""
        self._draw_filled_shape('polygon', points, fill_style=fill_style)

    def draw_arc(self, x, y, r, start_angle, end_angle, color, width=1):
        """绘制弧形"""
        self.pen.up()
        # 移动到弧的起点
        start_rad = math.radians(start_angle)
        start_x = x + r * math.cos(start_rad)
        start_y = y + r * math.sin(start_rad)
        self.pen.goto(start_x, start_y)
        self.pen.down()
        self.pen.pensize(width)
        self.pen.pencolor(self._rgb_to_hex(color))

        extent = end_angle - start_angle
        self.pen.circle(r, extent)
        self.pen.up()

    def draw_ring(self, x, y, r_inner, r_outer, fill_style):
        """绘制圆环"""
        # 绘制外圆
        self.draw_circle(x, y, r_outer, fill_style)
        # 用背景色覆盖内圆（简化实现）
        bg_color = THEME['canvas']['background']
        self.draw_circle(x, y, r_inner, {'type': 'solid', 'color': bg_color})

    # ============================================
    # 贝塞尔曲线
    # ============================================

    def draw_bezier(self, control_points, color, width=1):
        """绘制三次贝塞尔曲线"""
        if len(control_points) < 4:
            return

        self.pen.up()
        self.pen.pensize(width)
        self.pen.pencolor(self._rgb_to_hex(color))

        # 计算曲线上的点
        points = []
        steps = 50
        for i in range(steps + 1):
            t = i / steps
            p = self._cubic_bezier_point(control_points, t)
            points.append(p)

        # 绘制
        self.pen.goto(points[0])
        self.pen.down()
        for p in points[1:]:
            self.pen.goto(p)
        self.pen.up()

    def draw_quadratic(self, p0, p1, p2, color, width=1):
        """绘制二次贝塞尔曲线"""
        self.pen.up()
        self.pen.pensize(width)
        self.pen.pencolor(self._rgb_to_hex(color))

        points = []
        steps = 50
        for i in range(steps + 1):
            t = i / steps
            p = self._quadratic_bezier_point(p0, p1, p2, t)
            points.append(p)

        self.pen.goto(points[0])
        self.pen.down()
        for p in points[1:]:
            self.pen.goto(p)
        self.pen.up()

    def _cubic_bezier_point(self, points, t):
        """计算三次贝塞尔曲线上的点"""
        p0, p1, p2, p3 = points[:4]
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    def _quadratic_bezier_point(self, p0, p1, p2, t):
        """计算二次贝塞尔曲线上的点"""
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        return (x, y)

    # ============================================
    # 文字
    # ============================================

    def draw_text(self, text, x, y, size, color, font='Microsoft YaHei', align='center'):
        """绘制文字"""
        self.pen.up()
        self.pen.goto(x, y)
        self.pen.pencolor(self._rgb_to_hex(color))

        align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
        turtle_align = align_map.get(align, 'center')

        self.pen.write(text, align=turtle_align, font=(font, size, 'normal'))

    # ============================================
    # 填充样式处理
    # ============================================

    def _draw_filled_shape(self, shape_type, *args, fill_style=None):
        """绘制带填充样式的图形"""
        if fill_style is None:
            fill_style = {'type': 'solid', 'color': rgb(0, 0, 0)}

        if fill_style['type'] == 'solid':
            self._draw_solid_shape(shape_type, *args, fill_style['color'])
        elif fill_style['type'] == 'gradient':
            self._draw_gradient_shape(shape_type, *args, fill_style['gradient'])

    def _draw_solid_shape(self, shape_type, *args, color):
        """纯色填充图形"""
        hex_color = self._rgb_to_hex(color)
        self.pen.fillcolor(hex_color)
        self.pen.pencolor(hex_color)
        self.pen.down()
        self.pen.begin_fill()

        if shape_type == 'circle':
            x, y, r = args
            self.pen.up()
            self.pen.goto(x, y - r)
            self.pen.down()
            self.pen.circle(r)
        elif shape_type == 'ellipse':
            x, y, rx, ry = args
            self._draw_ellipse_path(x, y, rx, ry)
        elif shape_type == 'rect':
            x, y, w, h = args
            self.pen.up()
            self.pen.goto(x, y)
            self.pen.down()
            for _ in range(2):
                self.pen.forward(w)
                self.pen.left(90)
                self.pen.forward(h)
                self.pen.left(90)
        elif shape_type == 'polygon':
            points = args[0]
            self.pen.up()
            self.pen.goto(points[0])
            self.pen.down()
            for p in points[1:]:
                self.pen.goto(p)
            self.pen.goto(points[0])

        self.pen.end_fill()
        self.pen.up()

    def _draw_gradient_shape(self, shape_type, *args, gradient_def):
        """渐变填充图形"""
        # 获取图形边界
        bounds = self._get_shape_bounds(shape_type, *args)

        if gradient_def['type'] == 'linear':
            self._draw_linear_gradient_fill(bounds, gradient_def)
        elif gradient_def['type'] == 'radial':
            self._draw_radial_gradient_fill(bounds, gradient_def)

    def _get_shape_bounds(self, shape_type, *args):
        """获取图形边界 (x, y, w, h)"""
        if shape_type == 'circle':
            x, y, r = args
            return (x - r, y - r, 2*r, 2*r)
        elif shape_type == 'ellipse':
            x, y, rx, ry = args
            return (x - rx, y - ry, 2*rx, 2*ry)
        elif shape_type == 'rect':
            x, y, w, h = args
            return (x, y, w, h)
        elif shape_type == 'polygon':
            points = args[0]
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            return (min_x, min_y, max_x - min_x, max_y - min_y)
        return (0, 0, 100, 100)

    def _draw_linear_gradient_fill(self, bounds, gradient_def):
        """线性渐变填充"""
        x, y, w, h = bounds
        stops = gradient_def['stops']
        angle = gradient_def['angle']

        # 计算渐变方向
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = math.sin(rad)

        # 用多条线模拟渐变
        steps = max(20, int(max(w, h) / 2))

        for i in range(steps):
            t = i / steps
            color = self._interpolate_gradient_color(stops, t)

            # 计算这条线的位置
            if abs(dx) > abs(dy):
                # 主要水平方向
                line_x = x + w * t
                self.pen.up()
                self.pen.goto(line_x, y)
                self.pen.down()
                self.pen.pensize(max(1, w / steps + 1))
                self.pen.pencolor(self._rgb_to_hex(color))
                self.pen.goto(line_x, y + h)
            else:
                # 主要垂直方向
                line_y = y + h * t
                self.pen.up()
                self.pen.goto(x, line_y)
                self.pen.down()
                self.pen.pensize(max(1, h / steps + 1))
                self.pen.pencolor(self._rgb_to_hex(color))
                self.pen.goto(x + w, line_y)

        self.pen.up()

    def _draw_radial_gradient_fill(self, bounds, gradient_def):
        """径向渐变填充"""
        x, y, w, h = bounds
        stops = gradient_def['stops']
        center = gradient_def.get('center', (0.5, 0.5))

        center_x = x + w * center[0]
        center_y = y + h * center[1]
        max_r = max(w, h) / 2

        # 用多个同心圆模拟径向渐变
        steps = 30
        for i in range(steps, 0, -1):
            t = i / steps
            r = max_r * t
            color = self._interpolate_gradient_color(stops, t)

            self.pen.up()
            self.pen.goto(center_x, center_y - r)
            self.pen.down()
            self.pen.fillcolor(self._rgb_to_hex(color))
            self.pen.begin_fill()
            self.pen.circle(r)
            self.pen.end_fill()

        self.pen.up()

    def _interpolate_gradient_color(self, stops, t):
        """在渐变断点间插值颜色"""
        # t: 0-1 的位置
        # stops: [(color, pos%), ...] pos% 是 0-100

        # 找到 t 所在的区间
        t_percent = t * 100

        for i in range(len(stops) - 1):
            color1, pos1 = stops[i]
            color2, pos2 = stops[i + 1]

            if pos1 <= t_percent <= pos2:
                # 在这个区间内插值
                local_t = (t_percent - pos1) / (pos2 - pos1)
                return self._lerp_color(color1, color2, local_t)

        # 超出范围，返回最后一个颜色
        return stops[-1][0]

    def _lerp_color(self, color1, color2, t):
        """颜色线性插值"""
        r1, g1, b1 = color1[:3]
        r2, g2, b2 = color2[:3]

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return rgb(r, g, b)

    # ============================================
    # 辅助方法
    # ============================================

    def _draw_ellipse_path(self, x, y, rx, ry):
        """绘制椭圆路径"""
        self.pen.up()
        steps = 100
        for i in range(steps + 1):
            angle = 2 * math.pi * i / steps
            px = x + rx * math.cos(angle)
            py = y + ry * math.sin(angle)
            if i == 0:
                self.pen.goto(px, py)
                self.pen.down()
            else:
                self.pen.goto(px, py)

    def _draw_rounded_rect(self, x, y, w, h, r, fill_style):
        """绘制圆角矩形"""
        # 简化实现：用矩形近似
        self._draw_filled_shape('rect', x, y, w, h, fill_style)
