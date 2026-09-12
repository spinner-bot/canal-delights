"""
变换Gallery - 展示Transform效果

运行：python examples/transform_gallery.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canal_delights.core.engine import DrawingEngine
from canal_delights.core.renderer import DrawingDataParser
from canal_delights.config import rgb, make_style, make_transform


def create_gallery_data():
    """创建变换展示数据"""
    items = []

    # 原始图形
    items.append(['R', [0.1, 0.7, 0.08, 0.06], make_style(fill=rgb(200, 200, 200))])
    items.append(['T', [0.14, 0.65, '原始'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 平移
    items.append(['R', [0.1, 0.7, 0.08, 0.06],
                  make_style(fill=rgb(255, 100, 100), transform=make_transform(translate=[0.15, 0]))])
    items.append(['T', [0.29, 0.65, '平移'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 缩放
    items.append(['R', [0.1, 0.7, 0.08, 0.06],
                  make_style(fill=rgb(100, 255, 100), transform=make_transform(scale=[1.5, 1.5]))])
    items.append(['T', [0.44, 0.65, '缩放'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 旋转
    items.append(['R', [0.1, 0.7, 0.08, 0.06],
                  make_style(fill=rgb(100, 100, 255), transform=make_transform(rotate=45))])
    items.append(['T', [0.59, 0.65, '旋转45°'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 组合变换
    items.append(['R', [0.1, 0.7, 0.08, 0.06],
                  make_style(fill=rgb(255, 255, 100),
                           transform=make_transform(translate=[0.3, 0], rotate=30, scale=[0.8, 0.8]))])
    items.append(['T', [0.74, 0.65, '组合'], {'font_size': 10, 'color': rgb(50, 50, 50)}])

    # 标题
    items.append(['T', [0.5, 0.95, 'Transform Gallery'], {'font_size': 18, 'color': rgb(50, 50, 50)}])

    return items


def main():
    print("=" * 50)
    print("  Transform Gallery")
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
