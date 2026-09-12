"""
绘图数据解析器 - 将声明式 DSL 数据转换为实际绘制

职责：
- 校验 DSL schema
- 转换坐标（归一化 → 绝对）
- 应用 Transform
- 解析 Style
- 分发到 engine 绘制
- 不负责业务状态
"""

from typing import List, Tuple, Optional, Any

from .engine import DrawingEngine
from .geometry import (
    normalized_to_absolute,
    normalized_size_to_absolute,
    normalized_points_to_absolute,
    apply_transform,
    transform_points,
)
from .styles import validate_rgb, parse_style, interpolate_gradient_stops
from ..config import VALID_TYPE_CODES, CANVAS_BG


# 类型别名
Bounds = Tuple[float, float, float, float]  # (left, bottom, width, height)
DrawingData = List[list]


class DSLValidationError(Exception):
    """DSL 校验错误"""
    def __init__(self, index: int, type_code: str, message: str):
        self.index = index
        self.type_code = type_code
        self.message = message
        super().__init__(f"Item {index} ({type_code}): {message}")


class DrawingDataParser:
    """
    绘图数据解析器

    职责：
    - 校验 DSL schema
    - 坐标转换和变换
    - 分发到 engine 绘制
    """

    def __init__(self, engine: DrawingEngine):
        self.engine = engine
        self.background = CANVAS_BG

    def parse(
        self,
        data: DrawingData,
        bounds: Bounds,
        parent_transform: Optional[dict] = None,
    ):
        """
        解析并渲染绘图数据

        参数:
            data: 绘图数据列表
            bounds: 绘制区域 (left, bottom, width, height)
            parent_transform: 父级变换（用于 Group 嵌套）
        """
        if not data:
            return

        # 校验并收集所有项
        items = []
        for i, unit in enumerate(data):
            try:
                parsed = self._validate_and_parse(unit, i)
                items.append(parsed)
            except DSLValidationError as e:
                # 记录错误但继续处理其他项
                print(f"DSL 校验警告: {e}")
                continue

        # 按 z-order 排序（稳定排序）
        items.sort(key=lambda x: x.get('style', {}).get('z', 0))

        # 渲染
        for item in items:
            self._render_item(item, bounds, parent_transform)

    def _validate_and_parse(self, unit: Any, index: int) -> dict:
        """校验并解析单个单元"""
        if not isinstance(unit, (list, tuple)) or len(unit) < 2:
            raise DSLValidationError(index, '?', f"无效格式，需要 [type, geometry, ...]")

        type_code = unit[0]

        if type_code not in VALID_TYPE_CODES:
            raise DSLValidationError(index, type_code, f"未知类型码: {type_code}")

        geometry = unit[1]
        style = unit[2] if len(unit) > 2 else {}

        # 校验 geometry
        self._validate_geometry(type_code, geometry, index)

        return {
            'type': type_code,
            'geometry': geometry,
            'style': style if isinstance(style, dict) else {},
            'index': index,
        }

    def _validate_geometry(self, type_code: str, geometry: Any, index: int):
        """校验 geometry 格式"""
        validators = {
            'P': self._validate_point,
            'L': self._validate_line,
            'R': self._validate_rect,
            'RR': self._validate_rounded_rect,
            'C': self._validate_circle,
            'E': self._validate_ellipse,
            'G': self._validate_polygon,
            'A': self._validate_arc,
            'Q': self._validate_quadratic,
            'B': self._validate_bezier,
            'PATH': self._validate_path,
            'RG': self._validate_ring,
            'T': self._validate_text,
            'GR': self._validate_group,
        }

        validator = validators.get(type_code)
        if validator:
            validator(geometry, index)

    def _validate_point(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 3:
            raise DSLValidationError(idx, 'P', "需要 [x, y, size]")

    def _validate_line(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 2:
            raise DSLValidationError(idx, 'L', "需要点列表 [[x,y], ...]")

    def _validate_rect(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 4:
            raise DSLValidationError(idx, 'R', "需要 [x, y, w, h]")

    def _validate_rounded_rect(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 5:
            raise DSLValidationError(idx, 'RR', "需要 [x, y, w, h, radius]")

    def _validate_circle(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 3:
            raise DSLValidationError(idx, 'C', "需要 [cx, cy, r]")

    def _validate_ellipse(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 4:
            raise DSLValidationError(idx, 'E', "需要 [cx, cy, rx, ry]")

    def _validate_polygon(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 3:
            raise DSLValidationError(idx, 'G', "需要至少 3 个点")

    def _validate_arc(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 5:
            raise DSLValidationError(idx, 'A', "需要 [cx, cy, r, start, end]")

    def _validate_quadratic(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 3:
            raise DSLValidationError(idx, 'Q', "需要 3 个控制点")

    def _validate_bezier(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 4:
            raise DSLValidationError(idx, 'B', "需要 4 个控制点")

    def _validate_path(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)):
            raise DSLValidationError(idx, 'PATH', "需要命令列表")

    def _validate_ring(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 4:
            raise DSLValidationError(idx, 'RG', "需要 [cx, cy, r_inner, r_outer]")

    def _validate_text(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)) or len(geo) < 3:
            raise DSLValidationError(idx, 'T', "需要 [x, y, text]")

    def _validate_group(self, geo: Any, idx: int):
        if not isinstance(geo, (list, tuple)):
            raise DSLValidationError(idx, 'GR', "需要子元素列表")

    # ============================================
    # 渲染方法
    # ============================================

    def _render_item(self, item: dict, bounds: Bounds, parent_transform: Optional[dict]):
        """渲染单个项"""
        type_code = item['type']
        geometry = item['geometry']
        style = item['style']

        # 处理 transform
        transform = style.get('transform', parent_transform)

        # 分发到具体渲染方法
        renderers = {
            'P': self._render_point,
            'L': self._render_line,
            'R': self._render_rect,
            'RR': self._render_rounded_rect,
            'C': self._render_circle,
            'E': self._render_ellipse,
            'G': self._render_polygon,
            'A': self._render_arc,
            'Q': self._render_quadratic,
            'B': self._render_bezier,
            'PATH': self._render_path,
            'RG': self._render_ring,
            'T': self._render_text,
            'GR': self._render_group,
        }

        renderer = renderers.get(type_code)
        if renderer:
            renderer(geometry, style, bounds, transform)

    def _resolve_style(self, style: dict) -> dict:
        """解析样式，处理预混色"""
        return parse_style(style, self.background)

    def _get_fill_and_stroke(self, style: dict):
        """获取填充和描边颜色"""
        resolved = self._resolve_style(style)

        fill = resolved.get('fill')
        stroke = resolved.get('stroke')
        stroke_width = resolved.get('stroke_width', 1.0)
        gradient = resolved.get('gradient')

        # 如果有渐变，填充为 None（由渐变处理）
        if gradient:
            fill = None

        return fill, stroke, stroke_width, gradient

    def _transform_point(self, point: tuple, bounds: Bounds, transform: Optional[dict]) -> tuple:
        """转换单个点"""
        if transform:
            point = apply_transform(point, transform, bounds)
        return normalized_to_absolute(point[0], point[1], bounds)

    def _transform_points(self, points: list, bounds: Bounds, transform: Optional[dict]) -> list:
        """转换点列表"""
        if transform:
            points = transform_points(points, transform, bounds)
        return normalized_points_to_absolute(points, bounds)

    def _transform_size(self, size: float, bounds: Bounds) -> float:
        """转换尺寸"""
        return normalized_size_to_absolute(size, bounds)

    # ============================================
    # 各类型渲染
    # ============================================

    def _render_point(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染点: [x, y, size]"""
        x, y = self._transform_point((geo[0], geo[1]), bounds, transform)
        size = self._transform_size(geo[2], bounds)

        fill, stroke, _, _ = self._get_fill_and_stroke(style)
        color = fill or stroke or (0, 0, 0)

        self.engine.draw_point(x, y, max(1, size), color)

    def _render_line(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染线: [[x,y], ...]"""
        points = self._transform_points(geo, bounds, transform)

        _, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        color = stroke or (0, 0, 0)

        self.engine.draw_polyline(points, color, max(1, stroke_width), close=False)

    def _render_rect(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染矩形: [x, y, w, h]"""
        x = self._transform_size(geo[0], bounds)
        y = self._transform_size(geo[1], bounds)
        w = self._transform_size(geo[2], bounds)
        h = self._transform_size(geo[3], bounds)

        # 应用变换
        if transform:
            abs_points = [(bounds[0] + x, bounds[1] + y),
                          (bounds[0] + x + w, bounds[1] + y),
                          (bounds[0] + x + w, bounds[1] + y + h),
                          (bounds[0] + x, bounds[1] + y + h)]
            norm_points = [((p[0] - bounds[0]) / bounds[2],
                            (p[1] - bounds[1]) / bounds[3])
                           for p in abs_points]
            points = self._transform_points(norm_points, bounds, transform)
            self._render_polygon_with_style(points, style, bounds, None)
            return

        abs_x = bounds[0] + x
        abs_y = bounds[1] + y

        fill, stroke, stroke_width, gradient = self._get_fill_and_stroke(style)

        if gradient:
            points = [(abs_x, abs_y), (abs_x + w, abs_y),
                      (abs_x + w, abs_y + h), (abs_x, abs_y + h)]
            self.engine.draw_gradient_fill(points, gradient, bounds)
            if stroke:
                self.engine.draw_polyline(points, stroke, stroke_width, close=True)
        else:
            self.engine.draw_rect(abs_x, abs_y, w, h, fill, stroke, stroke_width)

    def _render_rounded_rect(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染圆角矩形: [x, y, w, h, radius]"""
        x = self._transform_size(geo[0], bounds)
        y = self._transform_size(geo[1], bounds)
        w = self._transform_size(geo[2], bounds)
        h = self._transform_size(geo[3], bounds)
        r = self._transform_size(geo[4], bounds)

        abs_x = bounds[0] + x
        abs_y = bounds[1] + y
        abs_r = r

        fill, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        self.engine.draw_rounded_rect(abs_x, abs_y, w, h, abs_r, fill, stroke, stroke_width)

    def _render_circle(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染圆形: [cx, cy, r]"""
        cx, cy = self._transform_point((geo[0], geo[1]), bounds, transform)
        r = self._transform_size(geo[2], bounds)

        fill, stroke, stroke_width, gradient = self._get_fill_and_stroke(style)

        if gradient:
            # 用多边形近似圆形来做渐变
            from .geometry import sample_ellipse
            points = sample_ellipse(cx, cy, r, r)
            self.engine.draw_gradient_fill(points, gradient, bounds)
            if stroke:
                self.engine.draw_polyline(points, stroke, stroke_width, close=True)
        else:
            self.engine.draw_circle(cx, cy, r, fill, stroke, stroke_width)

    def _render_ellipse(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染椭圆: [cx, cy, rx, ry]"""
        cx, cy = self._transform_point((geo[0], geo[1]), bounds, transform)
        rx = self._transform_size(geo[2], bounds)
        ry = self._transform_size(geo[3], bounds)

        fill, stroke, stroke_width, gradient = self._get_fill_and_stroke(style)

        if gradient:
            from .geometry import sample_ellipse
            points = sample_ellipse(cx, cy, rx, ry)
            self.engine.draw_gradient_fill(points, gradient, bounds)
            if stroke:
                self.engine.draw_polyline(points, stroke, stroke_width, close=True)
        else:
            self.engine.draw_ellipse(cx, cy, rx, ry, fill, stroke, stroke_width)

    def _render_polygon(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染多边形: [[x,y], ...]"""
        points = self._transform_points(geo, bounds, transform)
        self._render_polygon_with_style(points, style, bounds, transform)

    def _render_polygon_with_style(self, points: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """用样式渲染多边形"""
        fill, stroke, stroke_width, gradient = self._get_fill_and_stroke(style)

        if gradient:
            self.engine.draw_gradient_fill(points, gradient, bounds)
            if stroke:
                self.engine.draw_polyline(points, stroke, stroke_width, close=True)
        else:
            self.engine.draw_polygon(points, fill, stroke, stroke_width)

    def _render_arc(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染弧形: [cx, cy, r, start, end]"""
        cx, cy = self._transform_point((geo[0], geo[1]), bounds, transform)
        r = self._transform_size(geo[2], bounds)
        start = geo[3]
        end = geo[4]

        _, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        color = stroke or (0, 0, 0)

        self.engine.draw_arc(cx, cy, r, start, end, color, max(1, stroke_width))

    def _render_quadratic(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染二次贝塞尔: [[p0], [p1], [p2]]"""
        p0 = self._transform_point(tuple(geo[0]), bounds, transform)
        p1 = self._transform_point(tuple(geo[1]), bounds, transform)
        p2 = self._transform_point(tuple(geo[2]), bounds, transform)

        _, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        color = stroke or (0, 0, 0)

        self.engine.draw_quadratic(p0, p1, p2, color, max(1, stroke_width))

    def _render_bezier(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染三次贝塞尔: [[p0], [p1], [p2], [p3]]"""
        points = self._transform_points(geo, bounds, transform)

        _, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        color = stroke or (0, 0, 0)

        self.engine.draw_bezier(points, color, max(1, stroke_width))

    def _render_path(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染复合路径: [['M', x, y], ['L', x, y], ...]"""
        # 转换路径命令中的坐标
        commands = []
        for cmd in geo:
            if not cmd:
                continue

            op = cmd[0]

            if op == 'M' and len(cmd) >= 3:
                pt = self._transform_point((cmd[1], cmd[2]), bounds, transform)
                commands.append(['M', pt[0], pt[1]])

            elif op == 'L' and len(cmd) >= 3:
                pt = self._transform_point((cmd[1], cmd[2]), bounds, transform)
                commands.append(['L', pt[0], pt[1]])

            elif op == 'Q' and len(cmd) >= 5:
                p1 = self._transform_point((cmd[1], cmd[2]), bounds, transform)
                p2 = self._transform_point((cmd[3], cmd[4]), bounds, transform)
                commands.append(['Q', p1[0], p1[1], p2[0], p2[1]])

            elif op == 'C' and len(cmd) >= 7:
                p1 = self._transform_point((cmd[1], cmd[2]), bounds, transform)
                p2 = self._transform_point((cmd[3], cmd[4]), bounds, transform)
                p3 = self._transform_point((cmd[5], cmd[6]), bounds, transform)
                commands.append(['C', p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]])

            elif op == 'Z':
                commands.append(['Z'])

        fill, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        self.engine.draw_path(commands, fill, stroke, max(1, stroke_width))

    def _render_ring(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染圆环: [cx, cy, r_inner, r_outer]"""
        cx, cy = self._transform_point((geo[0], geo[1]), bounds, transform)
        r_inner = self._transform_size(geo[2], bounds)
        r_outer = self._transform_size(geo[3], bounds)

        fill, stroke, stroke_width, _ = self._get_fill_and_stroke(style)
        self.engine.draw_ring(cx, cy, r_inner, r_outer, fill, stroke, stroke_width)

    def _render_text(self, geo: list, style: dict, bounds: Bounds, transform: Optional[dict]):
        """渲染文字: [x, y, text]"""
        x, y = self._transform_point((geo[0], geo[1]), bounds, transform)
        text = geo[2]

        # 文字样式
        font_family = style.get('font_family', 'Microsoft YaHei')
        font_size = style.get('font_size', 16)
        font_weight = style.get('font_weight', 'normal')
        align = style.get('align', 'center')
        color = style.get('color', (0, 0, 0))

        # 字号直接使用，不做转换
        abs_size = max(8, font_size)

        self.engine.draw_text(text, x, y, abs_size, color, font_family, align, font_weight)

    def _render_group(self, geo: list, style: dict, bounds: Bounds, parent_transform: Optional[dict]):
        """渲染组: [children]"""
        # 获取组的变换
        group_transform = style.get('transform')

        # 组合父变换和组变换
        if parent_transform and group_transform:
            from .geometry import compose_transforms
            combined = compose_transforms(parent_transform, group_transform)
        else:
            combined = group_transform or parent_transform

        # 递归渲染子元素
        self.parse(geo, bounds, combined)
