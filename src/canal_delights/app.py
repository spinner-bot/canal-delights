"""
应用主类 - 协调所有模块
"""

import math

from .state import AppState, StateMachine, Mode
from .core.backend import RenderMode, create_engine
from .core.animation import AnimationClock
from .core.navigation import BoatPhysics, CITY_POINTS, ROUTE_SEGMENTS, route_point, route_tangent
from .core.particles import ParticleSystem
from .core.renderer import DrawingDataParser
from .config import rgb, CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG
from .content.catalog import get_city, get_food
from .content.foods.prototype import get_food_drawing


class App:
    """应用主类"""

    def __init__(self, render_mode=RenderMode.ACCELERATED):
        self.engine = create_engine(render_mode, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.parser = DrawingDataParser(self.engine)
        self.state = AppState()
        self.machine = StateMachine(self.state)
        self.bounds = (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        self._background_rendered = False
        self.hovered_item = None
        self.animations = AnimationClock(
            self.engine.screen, fps=30 if self.engine.mode_name == 'accelerated' else 15,
        )
        self.boat = BoatPhysics()
        self.particles = ParticleSystem(limit=72 if self.engine.mode_name == 'accelerated' else 18)
        self.move_direction = 0
        self.animation_phase = 0.0
        self._splash_elapsed = 0.0

    def run(self):
        """运行应用"""
        print("=" * 50)
        print("  运河四季·美食绘卷")
        print("=" * 50)
        print()
        print("操作说明:")
        print("  INTRO: Enter/点击 开始旅程")
        print("  MAP:   按住 ←/→ 驾船, 靠近城市后 Enter 探索")
        print("  CITY:  ←/→ 选择美食, Enter 查看")
        print("  DETAIL: Enter 完成品鉴")
        print("  Esc:   返回上一级")
        print("  H:     帮助")
        print(f"  渲染:  {self.engine.mode_name}")
        print()

        # 绑定键盘事件
        self.engine.screen.onkey(self.on_enter, 'Return')
        self.engine.screen.onkey(self.on_enter, 'KP_Enter')
        self.engine.screen.onkey(self.on_escape, 'Escape')
        self.engine.screen.onkeypress(self.on_left, 'Left')
        self.engine.screen.onkeypress(self.on_right, 'Right')
        self.engine.screen.onkeyrelease(self.on_direction_release, 'Left')
        self.engine.screen.onkeyrelease(self.on_direction_release, 'Right')
        self.engine.screen.onkey(self.on_help, 'h')
        self.engine.screen.onkey(self.on_help, 'H')

        # 鼠标点击
        self.engine.screen.onclick(self.on_click)
        self.engine.on_motion(self.on_motion)

        self.engine.listen()
        self.render()
        self.animations.add(self.on_animation_frame)
        self.engine.mainloop()

    def render(self):
        """渲染当前帧"""
        # The paper is static and lives on its own retained layer.  Interaction
        # only clears content, which is essential for smooth animation later.
        if not self._background_rendered:
            self.engine.set_layer('background')
            self.draw_background()
            self._background_rendered = True

        self.engine.clear('content')
        self.engine.set_layer('content')

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
            # paper fibres and an understated double border make every scene
            # read as one scroll instead of a white application window.
            ['R', [0.018, 0.025, 0.964, 0.95], {'stroke': rgb(164, 121, 62), 'stroke_width': 3}],
            ['R', [0.032, 0.041, 0.936, 0.918], {'stroke': rgb(218, 187, 126), 'stroke_width': 1}],
        ]
        for x, y in ((.10,.13),(.22,.84),(.39,.09),(.67,.88),(.88,.18),(.92,.72)):
            data.append(['E', [x, y, .035, .006], {'fill': rgb(237, 228, 204)}])
        self.parser.parse(data, self.bounds)

    def _food_medallion(self, cx, cy, food_id, selected=False):
        """Small, recognisable food illustration used by the city selection."""
        rim = rgb(184, 134, 11) if selected else rgb(190, 180, 155)
        data = [
            ['E', [cx, cy - .065, .115, .028], {'fill': rgb(216, 205, 178)}],
            ['C', [cx, cy, .105], {'fill': rgb(250, 248, 240), 'stroke': rim, 'stroke_width': 2}],
        ]
        golden = rgb(205, 133, 35)
        if food_id in ('roast_duck', 'lion_head', 'west_lake_fish', 'squirrel_fish'):
            data += [['E', [cx, cy, .073, .040], {'fill': rgb(159, 75, 37)}],
                     ['G', [[cx + .065, cy], [cx + .10, cy + .035], [cx + .10, cy - .035]], {'fill': rgb(125, 57, 30)}],
                     ['L', [[cx - .04, cy + .015], [cx + .04, cy + .015]], {'stroke': golden, 'stroke_width': 2}]]
        elif food_id in ('baozi', 'soup_dumpling'):
            data += [['C', [cx, cy, .067], {'fill': rgb(255, 248, 229), 'stroke': rgb(210, 194, 164), 'stroke_width': 1}],
                     ['C', [cx, cy + .02, .014], {'fill': rgb(221, 195, 157)}]]
            for offset in (-.04, -.02, .02, .04):
                data.append(['L', [[cx, cy + .02], [cx + offset, cy - .035]], {'stroke': rgb(218, 202, 174), 'stroke_width': 1}])
        elif food_id == 'longjing_tea':
            data += [['RR', [cx - .055, cy - .035, .11, .07, .012], {'fill': rgb(237, 246, 223), 'stroke': rgb(102, 135, 63), 'stroke_width': 2}],
                     ['E', [cx, cy - .005, .044, .015], {'fill': rgb(143, 180, 92)}]]
        elif food_id == 'osmanthus_cake':
            data += [['RR', [cx - .065, cy - .040, .13, .08, .012], {'fill': rgb(255, 237, 189), 'stroke': golden, 'stroke_width': 1}]]
            for dx, dy in ((-.03,.01), (0,.02), (.03,-.01)):
                data.append(['C', [cx + dx, cy + dy, .009], {'fill': rgb(226, 159, 30)}])
        else:  # mooncake and mahua
            data += [['C', [cx, cy, .065], {'fill': golden, 'stroke': rgb(159, 102, 28), 'stroke_width': 2}],
                     ['RG', [cx, cy, .035, .050], {'stroke': rgb(240, 193, 79), 'stroke_width': 2}]]
        return data

    def draw_intro(self):
        """绘制开场"""
        data = [
            ['B', [[.08,.29],[.28,.45],[.60,.13],[.91,.31]], {'stroke': rgb(102, 155, 167), 'stroke_width': 28}],
            ['B', [[.08,.29],[.28,.45],[.60,.13],[.91,.31]], {'stroke': rgb(188, 222, 221), 'stroke_width': 3}],
            ['G', [[.17,.31],[.23,.36],[.29,.31]], {'fill': rgb(102, 63, 37)}],
            ['L', [[.23,.36],[.23,.43]], {'stroke': rgb(82, 57, 38), 'stroke_width': 2}],
            ['G', [[.23,.42],[.28,.39],[.23,.36]], {'fill': rgb(201, 48, 44)}],
            # 标题
            ['T', [0.5, 0.6, '运河四季'], {'font_size': 48, 'color': rgb(139, 69, 19)}],
            ['T', [0.5, 0.5, '美食绘卷'], {'font_size': 36, 'color': rgb(139, 69, 19)}],
            # 副标题
            ['T', [0.5, 0.35, '一河通南北，五味见四时'], {'font_size': 18, 'color': rgb(100, 100, 100)}],
            # 悬浮按钮
            ['RR', [.385, .155, .23, .075, .028], {
                'fill': rgb(201, 48, 44) if self.hovered_item == ('start', 0) else rgb(139, 69, 19),
                'stroke': rgb(225, 184, 105), 'stroke_width': 2,
            }],
            ['T', [0.5, 0.177, '启 程'], {'font_size': 15, 'font_weight': 'bold', 'color': rgb(255, 248, 229)}],
            ['T', [0.5, 0.12, 'Enter 或点击'], {'font_size': 10, 'color': rgb(150, 138, 116)}],
        ]
        self.parser.parse(data, self.bounds)

    def draw_map(self):
        """绘制地图"""
        cities = ['北京', '天津', '扬州', '苏州', '杭州']
        colors = [rgb(201, 48, 44), rgb(139, 69, 19), rgb(46, 139, 87),
                  rgb(65, 105, 225), rgb(107, 142, 35)]

        # 标题
        route_commands = [['M', *CITY_POINTS[0]]]
        for _, control_1, control_2, end in ROUTE_SEGMENTS:
            route_commands.append(['C', *control_1, *control_2, *end])

        nearby_city = self.boat.nearby_city()
        data = [
            ['PATH', route_commands, {'stroke': rgb(94, 155, 170), 'stroke_width': 40}],
            ['PATH', route_commands, {'stroke': rgb(181, 220, 220), 'stroke_width': 27}],
            ['PATH', route_commands, {'stroke': rgb(226, 242, 235), 'stroke_width': 3}],
            ['T', [0.5, 0.9, '运河地图'], {'font_size': 28, 'color': rgb(50, 50, 50)}],
            ['T', [0.5, 0.845, '驾一叶轻舟，循水寻味'], {'font_size': 13, 'color': rgb(122, 101, 75)}],
        ]

        # 城市节点
        for i, (city, color) in enumerate(zip(cities, colors)):
            x, y = CITY_POINTS[i]

            # Unified inverted-drop marker. Proximity, visited and stamped
            # states change its color without changing its visual language.
            active = i == nearby_city
            pulse = .004 * (1 + math.sin(self.animation_phase * 4)) if active else 0
            marker_fill = color if active else rgb(190, 190, 181)
            if i in self.state.visited_cities and not active:
                marker_fill = tuple(int((channel + 230) / 2) for channel in color)
            data.append(['C', [x, y + .018, .050 + pulse], {
                'fill': rgb(247, 241, 220), 'stroke': color if active else rgb(158, 151, 136), 'stroke_width': 2,
            }])
            data.append(['G', [[x - .034, y + .010], [x + .034, y + .010], [x, y - .050]], {'fill': marker_fill}])
            data.append(['C', [x, y + .020, .030], {'fill': marker_fill}])
            data.append(['C', [x, y + .020, .010], {'fill': rgb(247, 241, 220)}])

            # 城市名
            data.append(['T', [x, y - 0.08, city], {'font_size': 14, 'color': rgb(50, 50, 50)}])

            # 印章标记
            if i in self.state.stamped_cities:
                data.append(['T', [x, y + 0.02, '✓'], {'font_size': 20, 'color': rgb(255, 0, 0)}])

        # Boat and motion particles are regular scene data, so both rendering
        # modes present the same navigation state.
        data.extend(self.particles.drawing_data())
        boat_x, boat_y = route_point(self.boat.position)
        tangent_x, tangent_y = route_tangent(self.boat.position)
        boat_angle = math.degrees(math.atan2(tangent_y * CANVAS_HEIGHT, tangent_x * CANVAS_WIDTH))
        bob = math.sin(self.animation_phase * 5) * .003
        data.append(['GR', [
            ['E', [boat_x, boat_y - .018 + bob, .050, .012], {'fill': rgb(111, 170, 181)}],
            ['G', [[boat_x - .047, boat_y + bob], [boat_x + .047, boat_y + bob],
                   [boat_x + .030, boat_y - .025 + bob], [boat_x - .030, boat_y - .025 + bob]],
             {'fill': rgb(115, 65, 38), 'stroke': rgb(72, 45, 31), 'stroke_width': 1}],
            ['L', [[boat_x, boat_y + bob], [boat_x, boat_y + .060 + bob]],
             {'stroke': rgb(75, 49, 33), 'stroke_width': 2}],
            ['G', [[boat_x + .002, boat_y + .055 + bob], [boat_x + .002, boat_y + .012 + bob],
                   [boat_x + .040, boat_y + .025 + bob]], {'fill': rgb(201, 48, 44)}],
        ], {'transform': {'rotate': boat_angle, 'pivot': [boat_x, boat_y]}}])

        # Side controls behave like a compact physical throttle.
        left_hover = self.hovered_item == ('nav', -1)
        right_hover = self.hovered_item == ('nav', 1)
        data.extend([
            ['RR', [.055, .39, .075, .10, .025], {'fill': rgb(139, 69, 19) if left_hover else rgb(224, 207, 170), 'stroke': rgb(164, 121, 62), 'stroke_width': 2}],
            ['T', [.092, .418, '‹'], {'font_size': 26, 'color': rgb(255, 248, 229) if left_hover else rgb(91, 63, 39)}],
            ['RR', [.87, .39, .075, .10, .025], {'fill': rgb(139, 69, 19) if right_hover else rgb(224, 207, 170), 'stroke': rgb(164, 121, 62), 'stroke_width': 2}],
            ['T', [.907, .418, '›'], {'font_size': 26, 'color': rgb(255, 248, 229) if right_hover else rgb(91, 63, 39)}],
        ])

        if nearby_city is not None:
            city_data = get_city(nearby_city)
            explore_hover = self.hovered_item == ('explore', nearby_city)
            data.extend([
                ['RR', [.59, .69, .34, .145, .025], {'fill': rgb(250, 245, 225), 'stroke': city_data['theme'], 'stroke_width': 2}],
                ['T', [.625, .783, city_data['name']], {'font_size': 19, 'font_weight': 'bold', 'align': 'left', 'color': rgb(55, 48, 39)}],
                ['T', [.625, .737, f"{city_data['season']} · 两道时味待寻"], {'font_size': 11, 'align': 'left', 'color': rgb(120, 105, 83)}],
                ['RR', [.80, .713, .10, .052, .015], {'fill': city_data['theme'] if explore_hover else rgb(219, 190, 130), 'stroke': city_data['theme'], 'stroke_width': 1}],
                ['T', [.85, .727, '探索'], {'font_size': 11, 'font_weight': 'bold', 'color': rgb(255, 250, 235) if explore_hover else rgb(75, 54, 35)}],
            ])

        # Progress
        progress = f"已游览: {len(self.state.visited_cities)}/5  已盖章: {len(self.state.stamped_cities)}/5"
        data.append(['T', [0.5, 0.075, progress], {'font_size': 12, 'color': rgb(100, 100, 100)}])

        self.parser.parse(data, self.bounds)

    def draw_city(self):
        """绘制城市场景"""
        city_data = get_city(self.state.current_city)
        city = city_data['name']

        theme = city_data['theme']
        data = [
            ['R', [.08,.34,.84,.34], {'fill': rgb(236, 228, 201), 'stroke': theme, 'stroke_width': 1}],
            ['B', [[.09,.38],[.30,.46],[.52,.36],[.91,.43]], {'stroke': rgb(151, 194, 193), 'stroke_width': 17}],
            ['B', [[.09,.38],[.30,.46],[.52,.36],[.91,.43]], {'stroke': rgb(218, 235, 226), 'stroke_width': 2}],
            # 城市标题
            ['T', [0.5, 0.85, f'{city}·食味'], {'font_size': 32, 'color': rgb(50, 50, 50)}],
        ]

        # 两道美食
        for i in range(2):
            food_data = city_data['foods'][i]
            x = 0.3 + i * 0.4
            y = 0.5

            highlighted = i == self.state.current_food or self.hovered_item == ('food', i)
            data.extend(self._food_medallion(x, y, food_data['id'], highlighted))

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
            if self.state.is_all_stamped():
                self.machine.go_to_finale()
            elif self.boat.nearby_city() is not None:
                self.state.current_city = self.boat.nearby_city()
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
            self.move_direction = -1
        elif self.state.mode == Mode.CITY:
            self.machine.prev_food()
            self.render()

    def on_right(self):
        """右方向键"""
        if self.state.help_open:
            return

        if self.state.mode == Mode.MAP:
            self.move_direction = 1
        elif self.state.mode == Mode.CITY:
            self.machine.next_food()
            self.render()

    def on_direction_release(self):
        self.move_direction = 0

    def on_animation_frame(self, delta_seconds):
        """Drive ambient motion, boat physics and particles from one clock."""
        self.animation_phase += delta_seconds
        if self.state.mode == Mode.MAP:
            moved = self.boat.step(self.move_direction, delta_seconds)
            self.particles.step(delta_seconds)
            self._splash_elapsed += delta_seconds
            if moved and abs(self.boat.velocity) > .012 and self._splash_elapsed >= .065:
                x, y = route_point(self.boat.position)
                self.particles.emit_splash(
                    x, y - .018, 1 if self.boat.velocity >= 0 else -1,
                    3 if self.engine.mode_name == 'accelerated' else 1,
                )
                self._splash_elapsed = 0.0
            nearby = self.boat.nearby_city()
            if nearby is not None:
                self.state.current_city = nearby
        self.render()
        return True

    def on_help(self):
        """H 键"""
        self.machine.toggle_help()
        self.render()

    def on_motion(self, x, y):
        """Update semantic hover state without redrawing for every pixel."""
        nx, ny = x / CANVAS_WIDTH, y / CANVAS_HEIGHT
        hovered = None

        if not self.state.help_open and self.state.mode == Mode.INTRO:
            if .35 <= nx <= .65 and .14 <= ny <= .26:
                hovered = ('start', 0)
        elif not self.state.help_open and self.state.mode == Mode.MAP:
            if .045 <= nx <= .14 and .37 <= ny <= .51:
                hovered = ('nav', -1)
            elif .86 <= nx <= .955 and .37 <= ny <= .51:
                hovered = ('nav', 1)
            elif self.boat.nearby_city() is not None and .79 <= nx <= .91 and .70 <= ny <= .78:
                hovered = ('explore', self.boat.nearby_city())
        elif not self.state.help_open and self.state.mode == Mode.CITY:
            if .16 <= nx <= .44 and .36 <= ny <= .64:
                hovered = ('food', 0)
            elif .56 <= nx <= .84 and .36 <= ny <= .64:
                hovered = ('food', 1)

        self.engine.set_cursor('hand2' if hovered is not None else '')
        if hovered != self.hovered_item:
            self.hovered_item = hovered
            self.render()

    def on_click(self, x, y):
        """鼠标点击"""
        if self.state.help_open:
            self.machine.toggle_help()
            self.render()
            return

        if self.state.mode == Mode.INTRO:
            self.machine.start_journey()
        elif self.state.mode == Mode.MAP:
            nx, ny = x / CANVAS_WIDTH, y / CANVAS_HEIGHT
            if .045 <= nx <= .14 and .37 <= ny <= .51:
                self.boat.nudge(-1)
            elif .86 <= nx <= .955 and .37 <= ny <= .51:
                self.boat.nudge(1)
            elif self.boat.nearby_city() is not None and .79 <= nx <= .91 and .70 <= ny <= .78:
                self.state.current_city = self.boat.nearby_city()
                self.machine.enter_city()
        elif self.state.mode == Mode.CITY:
            # The two dishes are deliberately generous click targets.
            nx = x / CANVAS_WIDTH
            if .16 <= nx <= .44:
                self.state.current_food = 0
                self.machine.open_food()
            elif .56 <= nx <= .84:
                self.state.current_food = 1
                self.machine.open_food()
        elif self.state.mode == Mode.FOOD_DETAIL:
            self.machine.complete_tasting()
        self.render()


def main(argv=None):
    """主程序入口"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description='运河四季·美食绘卷')
    parser.add_argument(
        '--renderer', choices=[mode.value for mode in RenderMode],
        default=os.environ.get('CANAL_RENDERER', RenderMode.ACCELERATED.value),
        help='渲染后端：accelerated（默认）或 pure（纯 Turtle）',
    )
    args = parser.parse_args(argv)
    app = App(args.renderer)
    app.run()


if __name__ == '__main__':
    main()
