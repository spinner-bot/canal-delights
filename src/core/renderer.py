"""
绘图数据解析器 - 将声明式绘图数据转换为实际绘制
支持：归一化坐标、基本单元、渐变填充
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UNIT_TYPES, rgb, rgba


class DrawingDataParser:
    """绘图数据解析器"""

    def __init__(self, engine):
        self.engine = engine

    def parse(self, data, bounds):
        """
        解析绘图数据并渲染

        参数:
            data: 绘图数据列表，每项为一个基本单元
            bounds: (x, y, width, height) 绘制区域（绝对坐标）
        """
        for unit in data:
            self._render_unit(unit, bounds)

    def _render_unit(self, unit, bounds):
        """渲染单个基本单元"""
        if not unit or len(unit) == 0:
            return

        unit_type = unit[0]
        params = unit[1:]

        # 获取单元类型的渲染方法
        renderer = self._get_renderer(unit_type)
        if renderer:
            renderer(params, bounds)

    def _get_renderer(self, unit_type):
        """获取单元类型对应的渲染方法"""
        renderers = {
            'P':  self._render_point,
            'L':  self._render_line,
            'C':  self._render_circle,
            'E':  self._render_ellipse,
            'R':  self._render_rect,
            'G':  self._render_polygon,
            'A':  self._render_arc,
            'B':  self._render_bezier,
            'Q':  self._render_quadratic,
            'RG': self._render_ring,
            'T':  self._render_text,
            'GR': self._render_group,
        }
        return renderers.get(unit_type)

    # ============================================
    # 坐标转换
    # ============================================

    def _to_absolute_x(self, x, bounds):
        """归一化 X 坐标 → 绝对坐标"""
        return bounds[0] + x * bounds[2]

    def _to_absolute_y(self, y, bounds):
        """归一化 Y 坐标 → 绝对坐标"""
        return bounds[1] + y * bounds[3]

    def _to_absolute_size(self, size, bounds):
        """归一化尺寸 → 绝对尺寸"""
        return size * min(bounds[2], bounds[3])

    def _to_absolute_point(self, point, bounds):
        """归一化点坐标 → 绝对坐标"""
        return (self._to_absolute_x(point[0], bounds),
                self._to_absolute_y(point[1], bounds))

    def _to_absolute_points(self, points, bounds):
        """归一化点列表 → 绝对坐标列表"""
        return [self._to_absolute_point(p, bounds) for p in points]

    # ============================================
    # 填充样式解析
    # ============================================

    def _parse_fill_style(self, fill_data):
        """解析填充样式"""
        if fill_data is None:
            return {'type': 'solid', 'color': rgb(0, 0, 0)}

        # 如果是元组/列表，视为 RGB 颜色
        if isinstance(fill_data, (tuple, list)) and len(fill_data) >= 3:
            if isinstance(fill_data[0], int):
                return {'type': 'solid', 'color': fill_data}

        # 如果是字典，已经是填充样式
        if isinstance(fill_data, dict):
            return fill_data

        # 默认
        return {'type': 'solid', 'color': rgb(0, 0, 0)}

    # ============================================
    # 各类型渲染方法
    # ============================================

    def _render_point(self, params, bounds):
        """渲染点: [P, x, y, size, color]"""
        if len(params) < 4:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        size = self._to_absolute_size(params[2], bounds)
        color = params[3]
        self.engine.draw_point(x, y, size, color)

    def _render_line(self, params, bounds):
        """渲染线段: [L, x1, y1, x2, y2, color, width?]"""
        if len(params) < 5:
            return
        x1 = self._to_absolute_x(params[0], bounds)
        y1 = self._to_absolute_y(params[1], bounds)
        x2 = self._to_absolute_x(params[2], bounds)
        y2 = self._to_absolute_y(params[3], bounds)
        color = params[4]
        width = self._to_absolute_size(params[5] if len(params) > 5 else 0.01, bounds)
        width = max(1, width)
        self.engine.draw_line(x1, y1, x2, y2, color, width)

    def _render_circle(self, params, bounds):
        """渲染圆形: [C, x, y, r, fill_style]"""
        if len(params) < 4:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        r = self._to_absolute_size(params[2], bounds)
        fill_style = self._parse_fill_style(params[3])
        self.engine.draw_circle(x, y, r, fill_style)

    def _render_ellipse(self, params, bounds):
        """渲染椭圆: [E, x, y, rx, ry, fill_style]"""
        if len(params) < 5:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        rx = self._to_absolute_size(params[2], bounds)
        ry = self._to_absolute_size(params[3], bounds)
        fill_style = self._parse_fill_style(params[4])
        self.engine.draw_ellipse(x, y, rx, ry, fill_style)

    def _render_rect(self, params, bounds):
        """渲染矩形: [R, x, y, w, h, fill_style, radius?]"""
        if len(params) < 5:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        w = self._to_absolute_size(params[2], bounds)
        h = self._to_absolute_size(params[3], bounds)
        fill_style = self._parse_fill_style(params[4])
        radius = self._to_absolute_size(params[5] if len(params) > 5 else 0, bounds)
        self.engine.draw_rect(x, y, w, h, fill_style, radius)

    def _render_polygon(self, params, bounds):
        """渲染多边形: [G, points[], fill_style]"""
        if len(params) < 2:
            return
        points = self._to_absolute_points(params[0], bounds)
        fill_style = self._parse_fill_style(params[1])
        self.engine.draw_polygon(points, fill_style)

    def _render_arc(self, params, bounds):
        """渲染弧形: [A, x, y, r, start_angle, end_angle, color, width?]"""
        if len(params) < 6:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        r = self._to_absolute_size(params[2], bounds)
        start_angle = params[3]
        end_angle = params[4]
        color = params[5]
        width = max(1, self._to_absolute_size(params[6] if len(params) > 6 else 0.01, bounds))
        self.engine.draw_arc(x, y, r, start_angle, end_angle, color, width)

    def _render_bezier(self, params, bounds):
        """渲染贝塞尔曲线: [B, control_points[], color, width?]"""
        if len(params) < 3:
            return
        points = self._to_absolute_points(params[0], bounds)
        color = params[1]
        width = max(1, self._to_absolute_size(params[2] if len(params) > 2 else 0.01, bounds))
        self.engine.draw_bezier(points, color, width)

    def _render_quadratic(self, params, bounds):
        """渲染二次贝塞尔: [Q, p0, p1, p2, color, width?]"""
        if len(params) < 4:
            return
        p0 = self._to_absolute_point(params[0], bounds)
        p1 = self._to_absolute_point(params[1], bounds)
        p2 = self._to_absolute_point(params[2], bounds)
        color = params[3]
        width = max(1, self._to_absolute_size(params[4] if len(params) > 4 else 0.01, bounds))
        self.engine.draw_quadratic(p0, p1, p2, color, width)

    def _render_ring(self, params, bounds):
        """渲染圆环: [RG, x, y, r_inner, r_outer, fill_style]"""
        if len(params) < 5:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        r_inner = self._to_absolute_size(params[2], bounds)
        r_outer = self._to_absolute_size(params[3], bounds)
        fill_style = self._parse_fill_style(params[4])
        self.engine.draw_ring(x, y, r_inner, r_outer, fill_style)

    def _render_text(self, params, bounds):
        """渲染文字: [T, x, y, text, size, color, font?, align?]"""
        if len(params) < 5:
            return
        x = self._to_absolute_x(params[0], bounds)
        y = self._to_absolute_y(params[1], bounds)
        text = params[2]
        size = self._to_absolute_size(params[3], bounds)
        size = max(8, int(size * 2))  # 调整文字大小
        color = params[4]
        font = params[5] if len(params) > 5 else 'Microsoft YaHei'
        align = params[6] if len(params) > 6 else 'center'
        self.engine.draw_text(text, x, y, size, color, font, align)

    def _render_group(self, params, bounds):
        """渲染组: [GR, units[], transform?]"""
        if len(params) < 1:
            return
        units = params[0]
        # transform = params[1] if len(params) > 1 else None
        # TODO: 支持组的变换（平移、缩放、旋转）

        # 递归渲染组内单元
        for unit in units:
            self._render_unit(unit, bounds)
