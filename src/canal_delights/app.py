"""
应用主类 - 协调所有模块
"""

from .state import AppState, StateMachine, Mode
from .core.engine import DrawingEngine
from .core.renderer import DrawingDataParser
from .config import rgb, CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG
from .content.catalog import get_city, get_food
from .content.foods.prototype import get_food_drawing


class App:
    """应用主类"""

    def __init__(self):
        self.engine = DrawingEngine(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.parser = DrawingDataParser(self.engine)
        self.state = AppState()
        self.machine = StateMachine(self.state)
        self.bounds = (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    def run(self):
        """运行应用"""
        print("=" * 50)
        print("  运河四季·美食绘卷")
        print("=" * 50)
        print()
        print("操作说明:")
        print("  INTRO: Enter/点击 开始旅程")
        print("  MAP:   ←/→ 选择城市, Enter 进入")
        print("  CITY:  ←/→ 选择美食, Enter 查看")
        print("  DETAIL: Enter 完成品鉴")
        print("  Esc:   返回上一级")
        print("  H:     帮助")
        print()

        # 绑定键盘事件
        self.engine.screen.onkey(self.on_enter, 'Return')
        self.engine.screen.onkey(self.on_enter, 'KP_Enter')
        self.engine.screen.onkey(self.on_escape, 'Escape')
        self.engine.screen.onkey(self.on_left, 'Left')
        self.engine.screen.onkey(self.on_right, 'Right')
        self.engine.screen.onkey(self.on_help, 'h')
        self.engine.screen.onkey(self.on_help, 'H')

        # 鼠标点击
        self.engine.screen.onclick(self.on_click)

        self.engine.listen()
        self.render()
        self.engine.mainloop()

    def render(self):
        """渲染当前帧"""
        self.engine.clear()

        # 绘制背景
        self.draw_background()

        # 根据模式绘制内容
        if self.state.mode == Mode.INTRO:
            self.draw_intro()
        elif self.state.mode == Mode.MAP:
            self.draw_map()
        elif self.state.mode == Mode.CITY:
            self.draw_city()
        elif self.state.mode == Mode.FOOD_DETAIL:
            self.draw_food_detail()
        elif self.state.mode == Mode.FINALE:
            self.draw_finale()

        # 绘制帮助覆盖层
        if self.state.help_open:
            self.draw_help()

        # 绘制状态提示
        self.draw_status()

        self.engine.update()

    def draw_background(self):
        """绘制背景"""
        data = [
            ['R', [0, 0, 1, 1], {'fill': CANVAS_BG}],
        ]
        self.parser.parse(data, self.bounds)

    def draw_intro(self):
        """绘制开场"""
        data = [
            # 标题
            ['T', [0.5, 0.6, '运河四季'], {'font_size': 48, 'color': rgb(139, 69, 19)}],
            ['T', [0.5, 0.5, '美食绘卷'], {'font_size': 36, 'color': rgb(139, 69, 19)}],
            # 副标题
            ['T', [0.5, 0.35, '一河通南北，五味见四时'], {'font_size': 18, 'color': rgb(100, 100, 100)}],
            # 提示
            ['T', [0.5, 0.2, '按 Enter 或点击开始'], {'font_size': 14, 'color': rgb(150, 150, 150)}],
        ]
        self.parser.parse(data, self.bounds)

    def draw_map(self):
        """绘制地图"""
        cities = ['北京', '天津', '扬州', '苏州', '杭州']
        colors = [rgb(201, 48, 44), rgb(139, 69, 19), rgb(46, 139, 87),
                  rgb(65, 105, 225), rgb(107, 142, 35)]

        # 标题
        data = [
            ['T', [0.5, 0.9, '运河地图'], {'font_size': 28, 'color': rgb(50, 50, 50)}],
        ]

        # 城市节点
        for i, (city, color) in enumerate(zip(cities, colors)):
            x = 0.15 + i * 0.175
            y = 0.5

            # 城市圆圈
            fill_color = color if i == self.state.current_city else rgb(200, 200, 200)
            data.append(['C', [x, y, 0.05], {'fill': fill_color}])

            # 城市名
            data.append(['T', [x, y - 0.08, city], {'font_size': 14, 'color': rgb(50, 50, 50)}])

            # 印章标记
            if i in self.state.stamped_cities:
                data.append(['T', [x, y + 0.02, '✓'], {'font_size': 20, 'color': rgb(255, 0, 0)}])

        # 进度
        progress = f"已游览: {len(self.state.visited_cities)}/5  已盖章: {len(self.state.stamped_cities)}/5"
        data.append(['T', [0.5, 0.15, progress], {'font_size': 12, 'color': rgb(100, 100, 100)}])

        self.parser.parse(data, self.bounds)

    def draw_city(self):
        """绘制城市场景"""
        city_data = get_city(self.state.current_city)
        city = city_data['name']

        data = [
            # 城市标题
            ['T', [0.5, 0.85, f'{city}·食味'], {'font_size': 32, 'color': rgb(50, 50, 50)}],
        ]

        # 两道美食
        for i in range(2):
            food_data = city_data['foods'][i]
            x = 0.3 + i * 0.4
            y = 0.5

            # 占位圆
            color = rgb(200, 200, 200) if i != self.state.current_food else rgb(255, 200, 100)
            data.append(['C', [x, y, 0.1], {'fill': color}])

            # 美食名
            data.append(['T', [x, y - 0.15, food_data['name']], {'font_size': 14, 'color': rgb(50, 50, 50)}])

        # 提示
        data.append(['T', [0.5, 0.2, '←/→ 选择  Enter 查看  Esc 返回'],
                    {'font_size': 12, 'color': rgb(150, 150, 150)}])

        self.parser.parse(data, self.bounds)

    def draw_food_detail(self):
        """绘制美食详情"""
        city_data = get_city(self.state.current_city)
        food_data = get_food(self.state.current_city, self.state.current_food)
        city_name = city_data['name']

        data = [
            # 标题
            ['T', [0.5, 0.85, f'{city_name}·{food_data["name"]}'], {'font_size': 28, 'color': rgb(50, 50, 50)}],
            # 节气
            ['T', [0.5, 0.78, food_data['season']], {'font_size': 14, 'color': rgb(150, 150, 150)}],
        ]

        # 添加食物绘图数据
        food_drawing = get_food_drawing(city_data['id'], food_data['id'])
        data.extend(food_drawing)

        # 描述
        data.extend([
            ['T', [0.5, 0.25, food_data['story']], {'font_size': 14, 'color': rgb(100, 100, 100)}],
            # 食材
            ['T', [0.5, 0.2, f'食材：{"、".join(food_data["ingredients"])}'], {'font_size': 12, 'color': rgb(150, 150, 150)}],
            # 提示
            ['T', [0.5, 0.15, 'Enter 完成品鉴'], {'font_size': 12, 'color': rgb(150, 150, 150)}],
        ])

        self.parser.parse(data, self.bounds)

    def draw_finale(self):
        """绘制终章"""
        data = [
            ['T', [0.5, 0.7, '运河四季·人间五味'], {'font_size': 36, 'color': rgb(139, 69, 19)}],
            ['T', [0.5, 0.55, '五城印章已全部收集'], {'font_size': 18, 'color': rgb(100, 100, 100)}],
            ['T', [0.5, 0.4, '🏮 🏮 🏮 🏮 🏮'], {'font_size': 24, 'color': rgb(255, 0, 0)}],
            ['T', [0.5, 0.25, '一河通南北，五味见四时'], {'font_size': 16, 'color': rgb(150, 150, 150)}],
            ['T', [0.5, 0.15, 'Enter 重新游览'], {'font_size': 12, 'color': rgb(150, 150, 150)}],
        ]

        self.parser.parse(data, self.bounds)

    def draw_help(self):
        """绘制帮助覆盖层"""
        data = [
            # 半透明背景（用灰色模拟）
            ['R', [0.2, 0.2, 0.6, 0.6], {'fill': rgb(240, 240, 240)}],
            # 帮助内容
            ['T', [0.5, 0.72, '操作帮助'], {'font_size': 24, 'color': rgb(50, 50, 50)}],
            ['T', [0.5, 0.62, 'Enter - 确认/进入'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.56, '←/→ - 选择'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.5, 'Esc - 返回上一级'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.44, 'H - 帮助'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.34, '按 H 或 Esc 关闭'], {'font_size': 12, 'color': rgb(150, 150, 150)}],
        ]

        self.parser.parse(data, self.bounds)

    def draw_status(self):
        """绘制状态提示"""
        mode_names = {
            Mode.INTRO: '开场',
            Mode.MAP: '地图',
            Mode.CITY: '城市',
            Mode.FOOD_DETAIL: '详情',
            Mode.FINALE: '终章',
        }
        mode_name = mode_names.get(self.state.mode, '未知')
        data = [
            ['T', [0.95, 0.05, f'[{mode_name}]'], {'font_size': 10, 'color': rgb(180, 180, 180), 'align': 'right'}],
        ]
        self.parser.parse(data, self.bounds)

    # 事件处理
    def on_enter(self):
        """Enter 键"""
        if self.state.help_open:
            self.machine.toggle_help()
            self.render()
            return

        if self.state.mode == Mode.INTRO:
            self.machine.start_journey()
        elif self.state.mode == Mode.MAP:
            self.machine.enter_city()
        elif self.state.mode == Mode.CITY:
            self.machine.open_food()
        elif self.state.mode == Mode.FOOD_DETAIL:
            self.machine.complete_tasting()
        elif self.state.mode == Mode.FINALE:
            self.machine.return_from_finale()

        self.render()

    def on_escape(self):
        """Esc 键"""
        if self.state.help_open:
            self.machine.toggle_help()
        else:
            self.machine.back()
        self.render()

    def on_left(self):
        """左方向键"""
        if self.state.help_open:
            return

        if self.state.mode == Mode.MAP:
            self.machine.prev_city()
        elif self.state.mode == Mode.CITY:
            self.machine.prev_food()

        self.render()

    def on_right(self):
        """右方向键"""
        if self.state.help_open:
            return

        if self.state.mode == Mode.MAP:
            self.machine.next_city()
        elif self.state.mode == Mode.CITY:
            self.machine.next_food()

        self.render()

    def on_help(self):
        """H 键"""
        self.machine.toggle_help()
        self.render()

    def on_click(self, x, y):
        """鼠标点击"""
        if self.state.help_open:
            self.machine.toggle_help()
            self.render()
            return

        if self.state.mode == Mode.INTRO:
            self.machine.start_journey()
            self.render()


def main():
    """主程序入口"""
    app = App()
    app.run()


if __name__ == '__main__':
    main()
