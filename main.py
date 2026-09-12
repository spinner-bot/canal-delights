"""
运河四季·Turtle 美食绘卷
程序入口
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from core.engine import DrawingEngine
from core.renderer import DrawingDataParser
from config import rgb, solid, gradient, COLORS, linear_gradient


# ============================================
# 示例绘图数据
# ============================================

# 粽子
ZONGZI = [
    ['E', 0.5, 0.25, 0.25, 0.05, solid(rgb(100, 100, 100))],
    ['G', [[0.5, 0.2], [0.25, 0.8], [0.75, 0.8]], gradient(COLORS['粽子绿'])],
    ['E', 0.42, 0.45, 0.08, 0.18, solid(rgb(80, 180, 80))],
    ['L', 0.5, 0.25, 0.35, 0.75, rgb(30, 100, 30), 0.015],
    ['L', 0.5, 0.25, 0.65, 0.75, rgb(30, 100, 30), 0.015],
    ['B', [[0.35, 0.4], [0.5, 0.3], [0.65, 0.4]], rgb(139, 69, 19), 0.02],
    ['C', 0.5, 0.35, 0.03, solid(rgb(139, 69, 19))],
    ['T', 0.5, 0.92, '粽子', 0.05, COLORS['墨黑']],
]

# 月饼
MOONCAKE = [
    ['E', 0.5, 0.28, 0.28, 0.06, solid(rgb(120, 100, 80))],
    ['C', 0.5, 0.5, 0.3, gradient(COLORS['月饼金黄'])],
    ['RG', 0.5, 0.5, 0.25, 0.3, solid(rgb(184, 134, 11))],
    ['C', 0.5, 0.5, 0.1, solid(rgb(255, 215, 0))],
    ['C', 0.35, 0.5, 0.04, solid(rgb(205, 92, 92))],
    ['C', 0.65, 0.5, 0.04, solid(rgb(205, 92, 92))],
    ['C', 0.5, 0.35, 0.04, solid(rgb(205, 92, 92))],
    ['C', 0.5, 0.65, 0.04, solid(rgb(205, 92, 92))],
    ['T', 0.5, 0.92, '月饼', 0.05, COLORS['墨黑']],
]

# 烤鸭
ROAST_DUCK = [
    ['E', 0.5, 0.3, 0.35, 0.06, solid(rgb(100, 80, 60))],
    ['E', 0.5, 0.55, 0.3, 0.2, gradient(COLORS['烤鸭光泽'])],
    ['E', 0.4, 0.5, 0.08, 0.12, solid(rgb(255, 140, 0))],
    ['L', 0.2, 0.7, 0.8, 0.7, rgb(139, 69, 19), 0.02],
    ['C', 0.3, 0.75, 0.04, solid(rgb(34, 139, 34))],
    ['C', 0.7, 0.75, 0.04, solid(rgb(34, 139, 34))],
    ['R', 0.15, 0.8, 0.7, 0.08, solid(rgb(255, 250, 240))],
    ['T', 0.5, 0.95, '北京烤鸭', 0.05, COLORS['墨黑']],
]


def main():
    """主程序"""
    print("=" * 50)
    print("  运河四季·Turtle 美食绘卷")
    print("=" * 50)

    # 初始化引擎
    engine = DrawingEngine(1000, 700)
    parser = DrawingDataParser(engine)
    bounds = (0, 0, 1000, 700)

    # 绘制示例
    foods = [
        ('粽子', ZONGZI),
        ('月饼', MOONCAKE),
        ('北京烤鸭', ROAST_DUCK),
    ]

    current = 0
    food_names = [f[0] for f in foods]

    def show_food(index):
        engine.clear()
        name, data = foods[index]
        parser.parse(data, bounds)
        engine.update()
        print(f"当前展示: {name} ({index + 1}/{len(foods)})")

    def next_food():
        nonlocal current
        current = (current + 1) % len(foods)
        show_food(current)

    def prev_food():
        nonlocal current
        current = (current - 1) % len(foods)
        show_food(current)

    # 绑定键盘事件
    screen = engine.screen
    screen.onkey(next_food, 'Right')
    screen.onkey(next_food, 'space')
    screen.onkey(prev_food, 'Left')
    screen.onkey(lambda: screen.bye(), 'Escape')
    screen.listen()

    # 显示第一个
    show_food(current)

    print()
    print("操作说明:")
    print("  → / 空格 : 下一个")
    print("  ←       : 上一个")
    print("  ESC     : 退出")
    print()
    print("关闭窗口或按 ESC 退出...")

    screen.mainloop()


if __name__ == '__main__':
    main()
