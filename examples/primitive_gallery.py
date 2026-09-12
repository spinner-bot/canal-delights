"""
Primitive Gallery - 展示所有 14 种基本图形类型

运行：python examples/primitive_gallery.py
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canal_delights.core.engine import DrawingEngine
from canal_delights.core.renderer import DrawingDataParser
from canal_delights.config import rgb, make_style, linear_gradient


def create_gallery_data():
    """创建展示所有 14 种 primitive 的数据"""

    # 布局：4 列 x 4 行
    cell_w = 0.22
    cell_h = 0.20
    margin = 0.03

    items = []

    def cell_pos(col, row):
        x = margin + col * (cell_w + margin)
        y = 0.95 - row * (cell_h + margin) - cell_h
        return x, y

    # 第 1 行
    x, y = cell_pos(0, 0)
    items.append(['P', [x + 0.1, y + 0.1, 0.03], make_style(fill=rgb(255, 0, 0))])
    items.append(['T', [x + 0.1, y + 0.02, 'P: Point'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(1, 0)
    items.append(['L', [[x + 0.02, y + 0.05], [x + 0.18, y + 0.15], [x + 0.18, y + 0.05]], make_style(stroke=rgb(0, 100, 200), stroke_width=2)])
    items.append(['T', [x + 0.1, y + 0.02, 'L: Line'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(2, 0)
    items.append(['R', [x + 0.03, y + 0.05, 0.14, 0.10], make_style(fill=rgb(100, 200, 100))])
    items.append(['T', [x + 0.1, y + 0.02, 'R: Rect'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(3, 0)
    items.append(['RR', [x + 0.03, y + 0.05, 0.14, 0.10, 0.02], make_style(fill=rgb(200, 150, 100))])
    items.append(['T', [x + 0.1, y + 0.02, 'RR: Rounded'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 第 2 行
    x, y = cell_pos(0, 1)
    items.append(['C', [x + 0.1, y + 0.1, 0.07], make_style(fill=rgb(255, 200, 0))])
    items.append(['T', [x + 0.1, y + 0.02, 'C: Circle'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(1, 1)
    items.append(['E', [x + 0.1, y + 0.1, 0.08, 0.05], make_style(fill=rgb(150, 100, 200))])
    items.append(['T', [x + 0.1, y + 0.02, 'E: Ellipse'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(2, 1)
    items.append(['G', [[x + 0.05, y + 0.05], [x + 0.15, y + 0.05], [x + 0.1, y + 0.16]], make_style(fill=rgb(200, 50, 50))])
    items.append(['T', [x + 0.1, y + 0.02, 'G: Polygon'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(3, 1)
    items.append(['A', [x + 0.1, y + 0.1, 0.06, 0, 270], make_style(stroke=rgb(0, 150, 150), stroke_width=2)])
    items.append(['T', [x + 0.1, y + 0.02, 'A: Arc'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 第 3 行
    x, y = cell_pos(0, 2)
    items.append(['Q', [[x + 0.02, y + 0.05], [x + 0.1, y + 0.18], [x + 0.18, y + 0.05]], make_style(stroke=rgb(200, 100, 0), stroke_width=2)])
    items.append(['T', [x + 0.1, y + 0.02, 'Q: Quadratic'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(1, 2)
    items.append(['B', [[x + 0.02, y + 0.05], [x + 0.05, y + 0.18], [x + 0.15, y + 0.18], [x + 0.18, y + 0.05]], make_style(stroke=rgb(100, 0, 200), stroke_width=2)])
    items.append(['T', [x + 0.1, y + 0.02, 'B: Cubic'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(2, 2)
    items.append(['PATH', [
        ['M', x + 0.02, y + 0.05],
        ['L', x + 0.1, y + 0.16],
        ['L', x + 0.18, y + 0.05],
        ['Z'],
    ], make_style(fill=rgb(50, 150, 100))])
    items.append(['T', [x + 0.1, y + 0.02, 'PATH: Path'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(3, 2)
    items.append(['RG', [x + 0.1, y + 0.1, 0.04, 0.07], make_style(fill=rgb(100, 100, 200))])
    items.append(['T', [x + 0.1, y + 0.02, 'RG: Ring'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 第 4 行
    x, y = cell_pos(0, 3)
    items.append(['T', [x + 0.05, y + 0.12, 'Hello'], {'font_size': 16, 'color': rgb(200, 50, 100)}])
    items.append(['T', [x + 0.1, y + 0.02, 'T: Text'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(1, 3)
    items.append(['GR', [
        ['C', [0.08, 0.08, 0.03], make_style(fill=rgb(255, 100, 100))],
        ['C', [0.12, 0.08, 0.03], make_style(fill=rgb(100, 255, 100))],
        ['C', [0.10, 0.12, 0.03], make_style(fill=rgb(100, 100, 255))],
    ], {'transform': {'translate': [x, y]}}])
    items.append(['T', [x + 0.1, y + 0.02, 'GR: Group'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 渐变展示
    x, y = cell_pos(2, 3)
    items.append(['C', [x + 0.1, y + 0.1, 0.07], make_style(gradient=linear_gradient([
        [rgb(255, 0, 0), 0.0],
        [rgb(255, 255, 0), 0.5],
        [rgb(0, 255, 0), 1.0],
    ], angle=45))])
    items.append(['T', [x + 0.1, y + 0.02, 'Linear Gradient'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    x, y = cell_pos(3, 3)
    items.append(['C', [x + 0.1, y + 0.1, 0.07], make_style(gradient={
        'type': 'radial',
        'stops': [[rgb(255, 255, 200), 0.0], [rgb(255, 100, 0), 1.0]],
        'center': [0.4, 0.4],
        'steps': 32,
    })])
    items.append(['T', [x + 0.1, y + 0.02, 'Radial Gradient'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 标题
    items.append(['T', [0.5, 0.98, 'Primitive Gallery - 14 种基本图形'], {'font_size': 20, 'color': rgb(50, 50, 50)}])

    return items


def main():
    """运行 Gallery"""
    print("=" * 50)
    print("  Primitive Gallery")
    print("  展示所有 14 种基本图形类型")
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
