"""
渐变Gallery - 展示渐变填充效果

运行：python examples/gradient_gallery.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canal_delights.core.engine import DrawingEngine
from canal_delights.core.renderer import DrawingDataParser
from canal_delights.config import rgb, make_style, linear_gradient, radial_gradient


def create_gallery_data():
    """创建渐变展示数据"""
    items = []

    # 线性渐变示例
    gradients = [
        ("水平", linear_gradient([[rgb(255,0,0), 0.0], [rgb(0,0,255), 1.0]], angle=0)),
        ("垂直", linear_gradient([[rgb(0,255,0), 0.0], [rgb(255,255,0), 1.0]], angle=90)),
        ("45度", linear_gradient([[rgb(255,0,255), 0.0], [rgb(0,255,255), 1.0]], angle=45)),
        ("三色", linear_gradient([[rgb(255,0,0), 0.0], [rgb(0,255,0), 0.5], [rgb(0,0,255), 1.0]], angle=0)),
    ]

    y_start = 0.8
    for i, (name, grad) in enumerate(gradients):
        x = 0.1 + i * 0.2
        items.append(['C', [x, y_start, 0.08], make_style(gradient=grad)])
        items.append(['T', [x, y_start - 0.12, name], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 径向渐变示例
    radial_grads = [
        ("中心", radial_gradient([[rgb(255,255,0), 0.0], [rgb(255,0,0), 1.0]])),
        ("偏移", radial_gradient([[rgb(0,255,0), 0.0], [rgb(0,0,255), 1.0]], center=[0.3, 0.3])),
    ]

    y_start = 0.5
    for i, (name, grad) in enumerate(radial_grads):
        x = 0.2 + i * 0.3
        items.append(['C', [x, y_start, 0.1], make_style(gradient=grad)])
        items.append(['T', [x, y_start - 0.15, name], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 标题
    items.append(['T', [0.5, 0.95, '渐变填充 Gallery'], {'font_size': 18, 'color': rgb(50, 50, 50)}])

    return items


def main():
    print("=" * 50)
    print("  渐变填充 Gallery")
    print("=" * 50)

    engine = DrawingEngine(1000, 800)
    parser = DrawingDataParser(engine)

    bounds = (0, 0, 1000, 800)
    data = create_gallery_data()

    print("渲染中...")
    parser.parse(data, bounds)
    engine.update()

    print("\n完成！关闭窗口退出...")
    engine.exitonclick()


if __name__ == '__main__':
    main()
