"""
配置文件 - DSL 类型定义、主题常量
"""

# ============================================
# DSL 类型码定义（14 种）
# ============================================

# 类型码 -> (名称, 描述)
PRIMITIVE_TYPES = {
    # 基础图形
    'P':    ('Point',        '点状纹理'),
    'L':    ('Line',         '线段/折线'),
    'R':    ('Rect',         '矩形'),
    'RR':   ('RoundedRect',  '圆角矩形'),
    'C':    ('Circle',       '圆形'),
    'E':    ('Ellipse',      '椭圆'),
    'G':    ('Polygon',      '多边形'),
    'A':    ('Arc',          '弧形'),

    # 曲线
    'Q':    ('Quadratic',    '二次贝塞尔'),
    'B':    ('Cubic',        '三次贝塞尔'),
    'PATH': ('CompoundPath', '复合路径'),

    # 装饰
    'RG':   ('Ring',         '圆环'),

    # 文字
    'T':    ('Text',         '文字'),

    # 组合
    'GR':   ('Group',        '组/容器'),
}

# 类型码列表（用于校验）
VALID_TYPE_CODES = set(PRIMITIVE_TYPES.keys())


# ============================================
# Style 结构定义
# ============================================

def make_style(
    fill=None,
    stroke=None,
    stroke_width=1.0,
    cap='round',
    join='round',
    gradient=None,
    opacity=1.0,
    blend_with=None,
    z=0,
):
    """
    创建样式对象

    参数:
        fill: RGB 元组 (r, g, b) 或 None（不填充）
        stroke: RGB 元组 (r, g, b) 或 None（不描边）
        stroke_width: 线宽
        cap: 线端样式 'round' | 'butt' | 'square'
        join: 连接样式 'round' | 'miter' | 'bevel'
        gradient: 渐变定义字典或 None
        opacity: 不透明度 0.0-1.0（需配合 blend_with 预混色）
        blend_with: 背景色 RGB 元组（opacity < 1 时必须提供）
        z: z-order 层级
    """
    return {
        'fill': fill,
        'stroke': stroke,
        'stroke_width': stroke_width,
        'cap': cap,
        'join': join,
        'gradient': gradient,
        'opacity': opacity,
        'blend_with': blend_with,
        'z': z,
    }


def make_text_style(
    font_family='Microsoft YaHei',
    font_size=16,
    font_weight='normal',
    align='center',
    color=None,
    z=0,
):
    """
    创建文字样式

    参数:
        font_family: 字体名称（需提供回退列表）
        font_size: 字号
        font_weight: 'normal' | 'bold'
        align: 'left' | 'center' | 'right'
        color: 文字颜色 RGB
        z: z-order
    """
    return {
        'font_family': font_family,
        'font_size': font_size,
        'font_weight': font_weight,
        'align': align,
        'color': color,
        'z': z,
    }


# ============================================
# Transform 结构定义
# ============================================

def make_transform(
    translate=None,
    scale=None,
    rotate=None,
    pivot=None,
):
    """
    创建变换对象

    执行顺序：局部点 → 缩放 → 旋转 → 平移 → 映射到 bounds

    参数:
        translate: [dx, dy] 平移
        scale: [sx, sy] 缩放
        rotate: 旋转角度（度）
        pivot: [px, py] 变换枢轴点（归一化坐标）
    """
    return {
        'translate': translate,
        'scale': scale,
        'rotate': rotate,
        'pivot': pivot,
    }


# ============================================
# 渐变定义
# ============================================

def linear_gradient(stops, angle=0, steps=36):
    """
    创建线性渐变

    参数:
        stops: 颜色断点列表 [[(r,g,b), position], ...]
               position: 0.0-1.0
        angle: 渐变角度（度）0=左到右，90=上到下
        steps: 渐变步数
    """
    return {
        'type': 'linear',
        'stops': stops,
        'angle': angle,
        'steps': steps,
    }


def radial_gradient(stops, center=None, steps=32):
    """
    创建径向渐变

    参数:
        stops: 颜色断点列表 [[(r,g,b), position], ...]
               position: 0.0-1.0
        center: 圆心位置 [x, y]，归一化坐标，默认 [0.5, 0.5]
        steps: 渐变步数
    """
    return {
        'type': 'radial',
        'stops': stops,
        'center': center if center else [0.5, 0.5],
        'steps': steps,
    }


# ============================================
# 中国传统配色
# ============================================

def rgb(r, g, b):
    """创建 RGB 颜色"""
    return (r, g, b)


COLORS = {
    # 城市主题色
    '北京红': rgb(201, 48, 44),
    '天津褐': rgb(139, 69, 19),
    '扬州青': rgb(46, 139, 87),
    '苏州蓝': rgb(65, 105, 225),
    '杭州绿': rgb(107, 142, 35),

    # 通用色
    '墨黑':   rgb(26, 26, 26),
    '宣纸白': rgb(245, 240, 220),
    '古铜金': rgb(184, 134, 11),
    '青灰':   rgb(112, 128, 144),

    # 食物色
    '烤鸭红': rgb(139, 69, 19),
    '月饼金': rgb(218, 165, 32),
    '包子白': rgb(255, 250, 240),
    '粽子绿': rgb(46, 139, 87),
    '茶汤绿': rgb(143, 188, 143),
}


# ============================================
# 主题配置
# ============================================

THEME = {
    'colors': COLORS,

    'spacing': {
        'xs': 5,
        'sm': 10,
        'md': 20,
        'lg': 40,
        'xl': 60,
    },

    'font': {
        'title': 36,
        'heading': 24,
        'body': 16,
        'caption': 12,
    },

    'canvas': {
        'width': 1200,
        'height': 800,
        'background': COLORS['宣纸白'],
        'margin': 40,
    },

    # 字体回退列表
    'font_families': {
        'default': ['Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'sans-serif'],
        'title': ['STKaiti', 'KaiTi', 'Microsoft YaHei', 'sans-serif'],
    },
}


# ============================================
# 画布常量
# ============================================

CANVAS_WIDTH = THEME['canvas']['width']
CANVAS_HEIGHT = THEME['canvas']['height']
CANVAS_MARGIN = THEME['canvas']['margin']
CANVAS_BG = THEME['canvas']['background']
