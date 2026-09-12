"""
配置文件 - 主题、类型系统、常量定义
"""

# ============================================
# 基本单元类型定义
# ============================================

# 类型码: (名称, 参数说明, 是否支持渐变填充)
UNIT_TYPES = {
    # 基础图形
    'P':  ('point',      'x, y, size, color', False),
    'L':  ('line',       'x1, y1, x2, y2, color, width', False),
    'C':  ('circle',     'x, y, r, fill_style', True),
    'E':  ('ellipse',    'x, y, rx, ry, fill_style', True),
    'R':  ('rect',       'x, y, w, h, fill_style, radius?', True),
    'G':  ('polygon',    'points[], fill_style', True),
    'A':  ('arc',        'x, y, r, start_angle, end_angle, color, width', False),

    # 高级图形
    'B':  ('bezier',     'control_points[], color, width', False),
    'Q':  ('quadratic',  'p0, p1, p2, color, width', False),  # 二次贝塞尔

    # 装饰
    'RG': ('ring',       'x, y, r_inner, r_outer, fill_style', True),  # 圆环
    'PG': ('path',       'commands[], fill_style', True),  # 复合路径 (M/L/C/Z)

    # 文字
    'T':  ('text',       'x, y, text, size, color, font?, align?', False),

    # 组合
    'GR': ('group',      'units[], transform?', False),
}

# ============================================
# 颜色系统 - RGB256
# ============================================

def rgb(r, g, b):
    """创建 RGB 颜色"""
    return (r, g, b)

def rgba(r, g, b, a):
    """创建 RGBA 颜色（带透明度）"""
    return (r, g, b, a)

# 中国传统配色
COLORS = {
    # 城市主题色
    '北京红': rgb(201, 48, 44),      # #C9302C
    '天津褐': rgb(139, 69, 19),      # #8B4513
    '扬州青': rgb(46, 139, 87),      # #2E8B57
    '苏州蓝': rgb(65, 105, 225),     # #4169E1
    '杭州绿': rgb(107, 142, 35),     # #6B8E23

    # 通用色
    '墨黑':   rgb(26, 26, 26),       # #1A1A1A
    '宣纸白': rgb(245, 245, 220),    # #F5F5DC
    '古铜金': rgb(184, 134, 11),     # #B8860B
    '青灰':   rgb(112, 128, 144),    # #708090

    # 食物色
    '烤鸭红': rgb(139, 69, 19),
    '月饼金': rgb(218, 165, 32),
    '包子白': rgb(255, 250, 240),
    '粽子绿': rgb(46, 139, 87),
    '茶汤绿': rgb(143, 188, 143),
}

# ============================================
# 渐变系统
# ============================================

def linear_gradient(color_stops, angle=0):
    """
    创建线性渐变

    参数:
        color_stops: 颜色断点列表 [(color, position%), ...]
                    position: 0-100 的整数或浮点数
        angle: 渐变角度（度）
               0 = 从左到右
               90 = 从上到下
               180 = 从右到左
               270 = 从下到上

    示例:
        # 从红到蓝的水平渐变
        linear_gradient([(RED, 0), (BLUE, 100)], angle=0)

        # 三色渐变，45度角
        linear_gradient([(RED, 0), (YELLOW, 50), (GREEN, 100)], angle=45)
    """
    return {
        'type': 'linear',
        'stops': color_stops,  # [(color, pos%), ...]
        'angle': angle
    }

def radial_gradient(color_stops, center=(0.5, 0.5)):
    """
    创建径向渐变

    参数:
        color_stops: 颜色断点列表 [(color, position%), ...]
        center: 圆心位置 (x%, y%)，默认中心
    """
    return {
        'type': 'radial',
        'stops': color_stops,
        'center': center
    }

# 预设渐变
GRADIENTS = {
    '烤鸭光泽': linear_gradient([
        (rgb(139, 69, 19), 0),    # 深棕
        (rgb(205, 92, 92), 40),   # 红褐
        (rgb(255, 140, 0), 70),   # 橙黄
        (rgb(205, 92, 92), 100),  # 红褐
    ], angle=45),

    '月饼金黄': radial_gradient([
        (rgb(255, 215, 0), 0),    # 金黄中心
        (rgb(218, 165, 32), 60),  # 深金
        (rgb(184, 134, 11), 100), # 古铜边缘
    ]),

    '粽子翠绿': linear_gradient([
        (rgb(34, 139, 34), 0),    # 深绿
        (rgb(50, 205, 50), 50),   # 亮绿
        (rgb(34, 139, 34), 100),  # 深绿
    ], angle=90),

    '茶汤清澈': linear_gradient([
        (rgb(144, 238, 144), 0),  # 浅绿
        (rgb(60, 179, 113), 100), # 中绿
    ], angle=180),

    '包子蒸汽': radial_gradient([
        (rgb(255, 255, 255), 0),  # 白色中心
        (rgb(245, 245, 245), 70), # 浅灰
        (rgb(220, 220, 220), 100),# 灰色边缘
    ]),
}

# ============================================
# 填充样式统一格式
# ============================================

def solid(color):
    """纯色填充"""
    return {'type': 'solid', 'color': color}

def gradient(gradient_def):
    """渐变填充"""
    return {'type': 'gradient', 'gradient': gradient_def}

# ============================================
# 主题配置
# ============================================

THEME = {
    'colors': COLORS,
    'gradients': GRADIENTS,

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
    }
}
