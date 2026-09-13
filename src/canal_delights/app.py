"""
应用主类 - 协调所有模块
"""

import math
import threading

from .state import AppState, StateMachine, Mode
from .core.backend import RenderMode, create_engine
from .core.animation import AnimationClock, SceneTransition
from .core.navigation import (
    BoatPhysics, CITY_POINTS, ROUTE_SEGMENTS, readable_boat_pose,
    route_point, route_tangent,
)
from .core.splash import SplashSystem
from .core.music import ScorePlayer
from .core.sound_effects import EffectPlayer
from .core.renderer import DrawingDataParser
from .config import linear_gradient, rgb, CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG
from .content.catalog import get_all_cities, get_city, get_food
from .content.scenes import FOOD_POSITIONS, get_city_scene
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
            self.engine.screen, fps=30 if self.engine.mode_name == 'accelerated' else 10,
        )
        self.boat = BoatPhysics()
        self.splash = SplashSystem(limit=36 if self.engine.mode_name == 'accelerated' else 10)
        self.transition = SceneTransition()
        self.move_direction = 0
        self.animation_phase = 0.0
        self._splash_elapsed = 0.0
        self._pressed_nav = None
        self.book_turn = 0.0
        self.master_volume = .72
        self.effects_volume = .82
        self.music = ScorePlayer(volume=self.master_volume)
        self.effects = EffectPlayer(volume=self.effects_volume)
        self.audio_enabled = True
        self._loading_started = False
        self._loading_progress = 0.0
        self._loading_target = 0.0
        self._loading_complete = False
        self._loading_finished_transition = False
        self._loading_label = '正在加载……'

    def run(self):
        """运行应用"""
        print("=" * 50)
        print("  运河风物志 Canal Delights")
        print("=" * 50)
        print()
        print("操作说明:")
        print("  INTRO: Enter/点击 开始旅程")
        print("  MAP:   按住 ←/→ 驾船, 靠近城市后 Enter 探索")
        print("  CITY:  ←/→ 选择美食, Enter 查看")
        print("  DETAIL: Enter 完成品鉴")
        print("  ATLAS: ←/→ 翻页，B 打开/关闭图鉴")
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
        self.engine.screen.onkey(self.on_atlas, 'b')
        self.engine.screen.onkey(self.on_atlas, 'B')

        # 鼠标点击
        self.engine.screen.onclick(self.on_click)
        self.engine.on_motion(self.on_motion)
        self.engine.on_pointer_press(self.on_pointer_press)
        self.engine.on_pointer_release(self.on_pointer_release)

        self.engine.listen()
        self.render()
        self.animations.add(self.on_animation_frame)
        try:
            self.engine.mainloop()
        finally:
            self.music.stop()
            self.effects.stop()

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
        elif self.state.mode == Mode.LOADING:
            self.draw_loading()
        elif self.state.mode == Mode.MAP:
            self.draw_map()
        elif self.state.mode == Mode.CITY:
            self.draw_city()
        elif self.state.mode == Mode.FOOD_DETAIL:
            self.draw_food_detail()
        elif self.state.mode == Mode.ATLAS:
            self.draw_atlas()
        elif self.state.mode == Mode.SETTINGS:
            self.draw_settings()
        elif self.state.mode == Mode.FINALE:
            self.draw_finale()

        if self.state.mode not in (Mode.INTRO, Mode.LOADING):
            self.draw_back_button()

        # 绘制帮助覆盖层
        if self.state.help_open:
            self.draw_help()

        # 绘制状态提示
        self.draw_status()

        if self.transition.active:
            self.draw_transition()

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

    def _food_medallion(self, cx, cy, city_id, food_id, selected=False):
        """Small, recognisable food illustration used by the city selection."""
        rim = rgb(184, 134, 11) if selected else rgb(190, 180, 155)
        data = [
            ['E', [cx, cy - .065, .115, .028], {'fill': rgb(216, 205, 178)}],
            ['C', [cx, cy, .105], {'fill': rgb(250, 248, 240), 'stroke': rim, 'stroke_width': 2}],
        ]
        drawing = get_food_drawing(city_id, food_id)
        if drawing:
            data.append(['GR', drawing, {'transform': {
                'scale': [.52, .52], 'translate': [cx - .5, cy - .45],
                'pivot': [.5, .45],
            }}])
        return data

    @staticmethod
    def _wrapped_lines(text, width=24):
        """Wrap Chinese prose without requiring whitespace between words."""
        return [text[index:index + width] for index in range(0, len(text), width)]

    @staticmethod
    def _inside(nx, ny, bounds):
        x, y, width, height = bounds
        return x <= nx <= x + width and y <= ny <= y + height

    def _preview_layout(self, city_index):
        """Size to wrapped copy and place beside the associated marker."""
        marker_x, marker_y = CITY_POINTS[city_index]
        lines = self._wrapped_lines(get_city(city_index)['description'], 18)
        width = .38
        height = .17 + .022 * len(lines)
        x = max(.045, min(.955 - width, marker_x - width / 2))
        above_y = marker_y + .075
        y = above_y if above_y + height <= .95 else marker_y - height - .075
        button = (x + width - .115, y + .018, .090, .050)
        return x, y, width, height, button

    @staticmethod
    def _city_thumbnail(city_id, cx, cy, theme, phase):
        """Small city silhouettes that avoid scaling full-scene gradients."""
        sway = .003 * math.sin(phase * 1.5)
        data = [
            ['E', [cx, cy - .035, .065, .012], {'fill': rgb(183, 211, 204)}],
            ['B', [[cx-.065,cy-.025],[cx-.025,cy-.012],[cx+.025,cy-.038],[cx+.065,cy-.020]],
             {'stroke': rgb(112, 169, 175), 'stroke_width': 2}],
        ]
        if city_id == 'beijing':
            data += [
                ['R', [cx-.045,cy-.025,.09,.050], {'fill': rgb(174, 72, 54)}],
                ['G', [[cx-.060,cy+.025],[cx+.060,cy+.025],[cx+.040,cy+.050],[cx-.040,cy+.050]], {'fill': theme}],
                ['R', [cx-.010,cy-.025,.020,.035], {'fill': rgb(80, 48, 35)}],
            ]
        elif city_id == 'tianjin':
            data += [
                ['C', [cx,cy+.010,.047], {'stroke': theme, 'stroke_width': 2}],
                ['L', [[cx-.035,cy-.025],[cx,cy+.010],[cx+.035,cy-.025]], {'stroke': theme, 'stroke_width': 2}],
                ['L', [[cx-.047,cy+.010],[cx+.047,cy+.010]], {'stroke': theme, 'stroke_width': 1}],
                ['L', [[cx,cy-.037],[cx,cy+.057]], {'stroke': theme, 'stroke_width': 1}],
            ]
        elif city_id == 'yangzhou':
            data += [
                ['B', [[cx-.060,cy-.025],[cx-.032,cy+.045],[cx+.010,cy+.045],[cx+.040,cy-.025]], {'stroke': rgb(210, 203, 178), 'stroke_width': 6}],
                ['B', [[cx-.057,cy-.025],[cx-.030,cy+.037],[cx+.008,cy+.037],[cx+.037,cy-.025]], {'stroke': theme, 'stroke_width': 1}],
                ['L', [[cx+.048,cy-.030],[cx+.048+sway,cy+.055]], {'stroke': rgb(77, 112, 67), 'stroke_width': 2}],
            ]
        elif city_id == 'suzhou':
            data += [
                ['R', [cx-.055,cy-.025,.11,.055], {'fill': rgb(237, 232, 213), 'stroke': rgb(61, 66, 65), 'stroke_width': 1}],
                ['G', [[cx-.065,cy+.030],[cx+.065,cy+.030],[cx+.045,cy+.052],[cx-.045,cy+.052]], {'fill': rgb(61, 66, 65)}],
                ['B', [[cx-.015,cy-.025],[cx+.010,cy+.025],[cx+.045,cy+.025],[cx+.065,cy-.025]], {'stroke': rgb(61, 66, 65), 'stroke_width': 2}],
            ]
        else:
            data += [
                ['B', [[cx-.065,cy-.005],[cx-.035,cy+.045],[cx,cy+.010],[cx+.040,cy+.050]], {'stroke': rgb(105, 145, 97), 'stroke_width': 10}],
                ['R', [cx+.020,cy-.025,.025,.072], {'fill': rgb(190, 158, 99), 'stroke': theme, 'stroke_width': 1}],
                ['G', [[cx+.012,cy+.047],[cx+.053,cy+.047],[cx+.043,cy+.060],[cx+.022,cy+.060]], {'fill': rgb(91, 67, 45)}],
            ]
        return data

    def draw_intro(self):
        """绘制开场"""
        bob = math.sin(self.animation_phase * 2.2) * .004
        data = [
            ['B', [[.08,.29],[.28,.45],[.60,.13],[.91,.31]], {'stroke': rgb(102, 155, 167), 'stroke_width': 28}],
            ['B', [[.08,.29],[.28,.45],[.60,.13],[.91,.31]], {'stroke': rgb(188, 222, 221), 'stroke_width': 3}],
            ['G', [[.17,.31+bob],[.23,.36+bob],[.29,.31+bob]], {'fill': rgb(102, 63, 37)}],
            ['L', [[.23,.36+bob],[.23,.43+bob]], {'stroke': rgb(82, 57, 38), 'stroke_width': 2}],
            ['G', [[.23,.42+bob],[.28,.39+bob],[.23,.36+bob]], {'fill': rgb(201, 48, 44)}],
            ['B', [[.13,.278-bob],[.19,.265+bob],[.26,.27-bob],[.33,.275]], {'stroke': rgb(198, 222, 215), 'stroke_width': 2}],
            # 标题
            ['T', [0.5, 0.59, '运河风物志'], {'font_size': 46, 'font_weight': 'bold', 'color': rgb(139, 69, 19)}],
            ['T', [0.5, 0.515, 'Canal Delights'], {'font_size': 24, 'color': rgb(164, 121, 62)}],
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

    def draw_loading(self):
        """One-time animated preheating screen shown before the first map."""
        wave_x = .08 * math.sin(self.animation_phase * 2.2)
        progress = max(0., min(1., self._loading_progress))
        data = [
            ['T', [.50, .68, '正在展开运河长卷'], {'font_size': 27, 'font_weight': 'bold', 'color': rgb(73, 60, 46)}],
            ['T', [.50, .625, '资源加载中，请耐心等待'], {'font_size': 11, 'color': rgb(139, 109, 72)}],
            ['B', [[.17,.46],[.27,.49+wave_x*.10],[.39,.45-wave_x*.08],[.50,.46]], {
                'stroke': rgb(89, 154, 161), 'stroke_width': 5,
            }],
            ['B', [[.50,.46],[.61,.49+wave_x*.06],[.73,.45-wave_x*.08],[.83,.46]], {
                'stroke': rgb(89, 154, 161), 'stroke_width': 5,
            }],
            ['RR', [.25, .34, .50, .028, .014], {'fill': rgb(214, 202, 174), 'stroke': rgb(174, 137, 82), 'stroke_width': 1}],
            ['RR', [.25, .34, .50*progress, .028, .014], {'fill': rgb(70, 145, 132)}],
            ['T', [.50, .385, self._loading_label], {'font_size': 8, 'color': rgb(164, 143, 113)}],
            ['T', [.50, .285, f'{round(progress*100)}%'], {'font_size': 17, 'font_weight': 'bold', 'color': rgb(89, 112, 84)}],
        ]
        self.parser.parse(data, self.bounds)

    def _start_first_loading(self):
        self.machine.start_loading()
        if self._loading_started:
            return
        self._loading_started = True
        threading.Thread(target=self._prepare_first_journey, name='canal-loader', daemon=True).start()

    def _enter_journey(self):
        """Route later visits directly to the map after the one-time preload."""
        if self._loading_complete:
            self.machine.start_journey()
        else:
            self._start_first_loading()

    def _prepare_first_journey(self):
        try:
            self._loading_label = '正在加载交互音效……'
            self._loading_target = .16
            self.effects.prepare()
            self._loading_label = '正在加载清新风背景音乐……'
            self._loading_target = .38
            self.music.prepare()
            self._loading_label = '正在完成首次初始化……'
        except Exception:
            # Audio availability must never strand the user on the loader.
            self.audio_enabled = False
            self.music.set_enabled(False)
            self.effects.set_enabled(False)
            self._loading_label = '音频初始化不可用，正在以静音模式进入……'
        finally:
            self._loading_target = 1.0
            self._loading_complete = True

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
            ['R', [.034, .043, .932, .914], {'gradient': linear_gradient([
                [rgb(239, 230, 205), 0.0], [rgb(250, 244, 225), .48], [rgb(226, 218, 192), 1.0],
            ], angle=25, steps=12 if self.engine.mode_name == 'accelerated' else 6), 'z': -20}],
            ['PATH', route_commands, {'stroke': rgb(94, 155, 170), 'stroke_width': 40}],
            ['PATH', route_commands, {'stroke': rgb(181, 220, 220), 'stroke_width': 27}],
            ['PATH', route_commands, {'stroke': rgb(226, 242, 235), 'stroke_width': 3}],
            ['T', [0.5, 0.9, '京杭大运河'], {'font_size': 28, 'color': rgb(50, 50, 50)}],
            ['T', [0.5, 0.845, '驾一叶轻舟，循水寻味'], {'font_size': 13, 'color': rgb(122, 101, 75)}],
        ]

        # Low-contrast brocade and water-line motifs give the map depth without
        # competing with the route or behaving like free-floating particles.
        pattern = rgb(218, 204, 170)
        for index in range(6):
            y = .18 + index * .115
            offset = .012 * math.sin(self.animation_phase * .55 + index)
            data.append(['B', [[.07, y], [.28, y + .045 + offset], [.68, y - .035], [.94, y + .010]],
                         {'stroke': pattern, 'stroke_width': 1, 'z': -10}])
        for x, y in ((.10,.76),(.88,.76),(.13,.15),(.88,.17)):
            data.extend([
                ['A', [x, y, .040, 15, 165], {'stroke': rgb(207, 186, 143), 'stroke_width': 2, 'z': -10}],
                ['A', [x + .050, y, .032, 20, 160], {'stroke': rgb(207, 186, 143), 'stroke_width': 2, 'z': -10}],
            ])

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

        boat_x, boat_y = route_point(self.boat.position)
        tangent_x, tangent_y = route_tangent(self.boat.position)
        direction = 1 if self.boat.velocity >= 0 else -1
        boat_angle, boat_flipped = readable_boat_pose(
            (tangent_x, tangent_y), direction, (CANVAS_WIDTH, CANVAS_HEIGHT),
        )
        bob = math.sin(self.animation_phase * 5) * .003
        wake_strength = min(1.0, abs(self.boat.velocity) / .12)
        tail_x = boat_x - tangent_x * direction * (.035 + .025 * wake_strength)
        tail_y = boat_y - tangent_y * direction * (.035 + .025 * wake_strength)
        normal_x, normal_y = -tangent_y, tangent_x
        if wake_strength > .05:
            data.extend([
                ['B', [[boat_x, boat_y - .016],
                       [tail_x + normal_x*.020, tail_y + normal_y*.020],
                       [tail_x + normal_x*.035, tail_y + normal_y*.035],
                       [tail_x - tangent_x*direction*.035, tail_y - tangent_y*direction*.035]],
                 {'stroke': rgb(226, 241, 233), 'stroke_width': 2}],
                ['B', [[boat_x, boat_y - .016],
                       [tail_x - normal_x*.020, tail_y - normal_y*.020],
                       [tail_x - normal_x*.035, tail_y - normal_y*.035],
                       [tail_x - tangent_x*direction*.035, tail_y - tangent_y*direction*.035]],
                 {'stroke': rgb(134, 184, 187), 'stroke_width': 2}],
            ])
        data.extend(self.splash.drawing_data())
        data.append(['GR', [
            ['E', [boat_x, boat_y - .018 + bob, .050, .012], {'fill': rgb(111, 170, 181)}],
            ['G', [[boat_x - .047, boat_y + bob], [boat_x + .047, boat_y + bob],
                   [boat_x + .030, boat_y - .025 + bob], [boat_x - .030, boat_y - .025 + bob]],
             {'fill': rgb(115, 65, 38), 'stroke': rgb(72, 45, 31), 'stroke_width': 1}],
            ['L', [[boat_x, boat_y + bob], [boat_x, boat_y + .060 + bob]],
             {'stroke': rgb(75, 49, 33), 'stroke_width': 2}],
            ['G', [[boat_x + .002, boat_y + .055 + bob], [boat_x + .002, boat_y + .012 + bob],
                   [boat_x + .040, boat_y + .025 + bob]], {'fill': rgb(201, 48, 44)}],
        ], {'transform': {
            'scale': [-1, 1] if boat_flipped else [1, 1],
            'rotate': boat_angle, 'pivot': [boat_x, boat_y],
        }}])

        # Side controls behave like a compact physical throttle.
        left_hover = self.hovered_item == ('nav', -1)
        right_hover = self.hovered_item == ('nav', 1)
        left_pressed = self._pressed_nav == -1
        right_pressed = self._pressed_nav == 1
        data.extend([
            ['RR', [.055, .39, .075, .10, .025], {'fill': rgb(105, 57, 35) if left_pressed else (rgb(139, 69, 19) if left_hover else rgb(224, 207, 170)), 'stroke': rgb(164, 121, 62), 'stroke_width': 3 if left_pressed else 2}],
            ['T', [.092, .418, '‹'], {'font_size': 26, 'color': rgb(255, 248, 229) if left_hover else rgb(91, 63, 39)}],
            ['RR', [.87, .39, .075, .10, .025], {'fill': rgb(105, 57, 35) if right_pressed else (rgb(139, 69, 19) if right_hover else rgb(224, 207, 170)), 'stroke': rgb(164, 121, 62), 'stroke_width': 3 if right_pressed else 2}],
            ['T', [.907, .418, '›'], {'font_size': 26, 'color': rgb(255, 248, 229) if right_hover else rgb(91, 63, 39)}],
            ['RR', [.835, .865, .110, .060, .018], {
                'fill': rgb(139, 69, 19) if self.hovered_item == ('settings', 0) else rgb(232, 218, 187),
                'stroke': rgb(164, 121, 62), 'stroke_width': 1,
            }],
            ['T', [.890, .883, '设置'], {'font_size': 11, 'font_weight': 'bold',
                                        'color': rgb(255, 248, 229) if self.hovered_item == ('settings', 0) else rgb(91, 63, 39)}],
        ])

        # A compact open-book silhouette: leather rim, layered pages, page
        # rules and a cinnabar bookmark.  It floats instead of sitting inside
        # another generic rectangular button.
        atlas_hover = self.hovered_item == ('atlas', 0)
        lift = (.008 if atlas_hover else 0) + .002 * math.sin(self.animation_phase * 1.6)
        rim = rgb(221, 174, 83) if atlas_hover else rgb(166, 104, 55)
        data.extend([
            ['E', [.125, .055 + lift, .088, .014], {'fill': rgb(193, 175, 139)}],
            ['G', [[.043,.072+lift],[.117,.061+lift],[.125,.071+lift],
                   [.133,.061+lift],[.207,.072+lift],[.197,.169+lift],
                   [.139,.159+lift],[.125,.148+lift],[.111,.159+lift],[.053,.169+lift]], {
                'fill': rgb(119, 61, 43), 'stroke': rim, 'stroke_width': 3 if atlas_hover else 2,
            }],
            ['G', [[.054,.083+lift],[.119,.073+lift],[.119,.151+lift],
                   [.110,.158+lift],[.063,.162+lift]], {
                'fill': rgb(251, 241, 210), 'stroke': rgb(213, 180, 119), 'stroke_width': 1,
            }],
            ['G', [[.131,.073+lift],[.196,.083+lift],[.187,.162+lift],
                   [.140,.158+lift],[.131,.151+lift]], {
                'fill': rgb(247, 233, 195), 'stroke': rgb(213, 180, 119), 'stroke_width': 1,
            }],
            ['L', [[.125,.071+lift],[.125,.150+lift]], {'stroke': rgb(132, 84, 51), 'stroke_width': 2}],
            ['G', [[.166,.156+lift],[.180,.158+lift],[.177,.105+lift],
                   [.171,.112+lift],[.165,.104+lift]], {'fill': rgb(188, 50, 43)}],
            ['L', [[.068,.137+lift],[.108,.132+lift]], {'stroke': rgb(210, 190, 151), 'stroke_width': 1}],
            ['L', [[.066,.120+lift],[.108,.116+lift]], {'stroke': rgb(210, 190, 151), 'stroke_width': 1}],
            ['L', [[.142,.132+lift],[.185,.137+lift]], {'stroke': rgb(207, 184, 143), 'stroke_width': 1}],
            ['L', [[.142,.116+lift],[.184,.120+lift]], {'stroke': rgb(207, 184, 143), 'stroke_width': 1}],
            ['RR', [.094, .078 + lift, .062, .030, .010], {
                'fill': rgb(218, 177, 94) if atlas_hover else rgb(229, 203, 145),
                'stroke': rgb(139, 69, 19), 'stroke_width': 1,
            }],
            ['T', [.125, .085 + lift, '图鉴'], {'font_size': 9, 'font_weight': 'bold',
                                              'color': rgb(105, 57, 35)}],
        ])

        if nearby_city is not None:
            city_data = get_city(nearby_city)
            explore_hover = self.hovered_item == ('explore', nearby_city)
            card_x, card_y, card_w, card_h, explore_bounds = self._preview_layout(nearby_city)
            marker_x, marker_y = CITY_POINTS[nearby_city]
            card_above = card_y > marker_y
            stem_y = card_y if card_above else card_y + card_h
            data.extend([
                ['G', [[marker_x - .018, stem_y], [marker_x + .018, stem_y],
                       [marker_x, marker_y + (.052 if card_above else -.052)]],
                 {'fill': rgb(250, 245, 225), 'stroke': city_data['theme'], 'stroke_width': 1, 'z': 99}],
                ['RR', [card_x, card_y, card_w, card_h, .022], {'fill': rgb(250, 245, 225), 'stroke': city_data['theme'], 'stroke_width': 2, 'z': 100}],
            ])
            # A lightweight animated silhouette avoids scaling full-scene
            # gradients, which would be expensive in pure Turtle mode.
            thumb_x, thumb_y = card_x + .075, card_y + card_h / 2
            data.append(['GR', self._city_thumbnail(
                city_data['id'], thumb_x, thumb_y, city_data['theme'], self.animation_phase,
            ), {'z': 101}])
            copy_x = card_x + .145
            top = card_y + card_h
            data.extend([
                ['T', [copy_x, top - .045, city_data['name']], {'font_size': 17, 'font_weight': 'bold', 'align': 'left', 'color': rgb(55, 48, 39), 'z': 102}],
                ['T', [copy_x, top - .078, city_data['cuisine']], {'font_size': 9, 'align': 'left', 'color': city_data['theme'], 'z': 102}],
                ['RR', [*explore_bounds, .014], {'fill': city_data['theme'] if explore_hover else rgb(219, 190, 130), 'stroke': city_data['theme'], 'stroke_width': 1, 'z': 102}],
                ['T', [explore_bounds[0] + explore_bounds[2] / 2, explore_bounds[1] + .013, '探索'], {'font_size': 10, 'font_weight': 'bold', 'color': rgb(255, 250, 235) if explore_hover else rgb(75, 54, 35), 'z': 103}],
            ])
            for line_index, line in enumerate(self._wrapped_lines(city_data['description'], 18)):
                data.append(['T', [copy_x, top - .108 - line_index * .022, line], {
                    'font_size': 8, 'align': 'left', 'color': rgb(120, 105, 83), 'z': 102,
                }])

        self.parser.parse(data, self.bounds)

    def draw_city(self):
        """绘制城市场景"""
        city_data = get_city(self.state.current_city)
        city = city_data['name']

        theme = city_data['theme']
        data = get_city_scene(
            city_data['id'], theme, self.animation_phase,
            gradient_steps=10 if self.engine.mode_name == 'accelerated' else 5,
        )
        data.append(['T', [0.5, 0.86, f'{city} · 城市食景'], {
            'font_size': 30, 'font_weight': 'bold', 'color': rgb(50, 50, 50),
        }])
        data.append(['T', [0.5, 0.815, f"{city_data['cuisine']} · 寻访四道时味"], {
            'font_size': 11, 'color': rgb(130, 112, 85),
        }])

        # 四道美食
        for i, food_data in enumerate(city_data['foods']):
            x, y = FOOD_POSITIONS[city_data['id']][i]

            hovered = self.hovered_item == ('food', i)
            highlighted = i == self.state.current_food or hovered
            medallion = self._food_medallion(
                x, y, city_data['id'], food_data['id'], highlighted,
            )
            scale = .84 if hovered else .74
            data.append(['GR', medallion, {'transform': {
                'scale': [scale, scale], 'pivot': [x, y],
            }}])

            # 美食名
            data.append(['T', [x, y - 0.105, food_data['name']], {'font_size': 12, 'color': rgb(50, 50, 50)}])
            if f'{self.state.current_city}_{i}' in self.state.discovered_foods:
                data.append(['C', [x + .075, y + .070, .023], {'fill': rgb(176, 45, 39), 'stroke': rgb(246, 220, 160), 'stroke_width': 1}])
                data.append(['T', [x + .075, y + .061, '✓'], {'font_size': 10, 'color': rgb(255, 246, 224)}])

        # 提示
        data.append(['T', [0.5, 0.12, '悬浮预览 · 点击探索 · ←/→ 切换'],
                    {'font_size': 12, 'color': rgb(150, 150, 150)}])

        self.parser.parse(data, self.bounds)

    def draw_food_detail(self):
        """绘制美食详情"""
        city_data = get_city(self.state.current_city)
        food_data = get_food(self.state.current_city, self.state.current_food)
        city_name = city_data['name']

        theme = city_data['theme']
        detail_bob = .004 * math.sin(self.animation_phase * 1.7)
        data = [
            # Upper area: illustration 3/10, introduction 7/10.
            ['RR', [.065, .53, .27, .31, .025], {'fill': rgb(250, 246, 230), 'stroke': theme, 'stroke_width': 2}],
            ['RR', [.365, .53, .57, .31, .025], {'fill': rgb(247, 240, 217), 'stroke': rgb(215, 192, 147), 'stroke_width': 1}],
            ['T', [.405, .775, f'{city_name} · {food_data["name"]}'], {'font_size': 25, 'font_weight': 'bold', 'align': 'left', 'color': rgb(52, 44, 34)}],
            ['T', [.405, .727, city_data['cuisine']], {'font_size': 11, 'align': 'left', 'color': theme}],

            # Lower area: story occupies roughly 60% of the content height.
            ['RR', [.065, .135, .87, .35, .025], {'fill': rgb(242, 232, 203), 'stroke': rgb(204, 173, 116), 'stroke_width': 1}],
            ['T', [.105, .420, '食味小记'], {'font_size': 19, 'font_weight': 'bold', 'align': 'left', 'color': theme}],
            ['RR', [.745, .175, .15, .065, .018], {'fill': theme if self.hovered_item == ('taste', 0) else rgb(222, 196, 142), 'stroke': theme, 'stroke_width': 1}],
            ['T', [.82, .194, '完成品鉴'], {'font_size': 12, 'font_weight': 'bold', 'color': rgb(255, 249, 234) if self.hovered_item == ('taste', 0) else rgb(75, 55, 36)}],
        ]

        for index, line in enumerate(self._wrapped_lines(food_data['intro'], 25)[:3]):
            data.append(['T', [.405, .674 - index * .043, line], {
                'font_size': 12, 'align': 'left', 'color': rgb(91, 76, 56),
            }])
        for index, line in enumerate(self._wrapped_lines(food_data['story'], 38)[:4]):
            data.append(['T', [.105, .360 - index * .048, line], {
                'font_size': 12, 'align': 'left', 'color': rgb(79, 68, 53),
            }])

        # 添加食物绘图数据
        food_drawing = get_food_drawing(city_data['id'], food_data['id'])
        data.append(['GR', food_drawing, {
            'transform': {'scale': [.60, .60], 'translate': [-.30, .255 + detail_bob], 'pivot': [.5, .45]},
        }])

        self.parser.parse(data, self.bounds)

    def draw_atlas(self):
        """绘制带翻页反馈的动漫风格美食图鉴。"""
        cities = get_all_cities()
        page = self.state.atlas_page
        lift = .004 * math.sin(self.animation_phase * 1.4)
        data = [
            ['E', [.50, .135 + lift, .39, .035], {'fill': rgb(188, 169, 132)}],
            ['RR', [.105, .17 + lift, .79, .66, .035], {
                'fill': rgb(112, 56, 42), 'stroke': rgb(190, 139, 67), 'stroke_width': 3,
            }],
            ['G', [[.13,.20+lift],[.495,.185+lift],[.495,.79+lift],[.14,.805+lift]], {
                'fill': rgb(249, 240, 211), 'stroke': rgb(208, 181, 124), 'stroke_width': 2,
            }],
            ['G', [[.505,.185+lift],[.87,.20+lift],[.86,.805+lift],[.505,.79+lift]], {
                'fill': rgb(247, 235, 202), 'stroke': rgb(208, 181, 124), 'stroke_width': 2,
            }],
            ['B', [[.50,.19+lift],[.485,.39+lift],[.515,.60+lift],[.50,.795+lift]], {
                'stroke': rgb(148, 104, 62), 'stroke_width': 3,
            }],
            ['T', [.50, .865, '京杭大运河 · 美食图鉴'], {
                'font_size': 27, 'font_weight': 'bold', 'color': rgb(85, 55, 39),
            }],
        ]

        if page == 0:
            discovered = len(self.state.discovered_foods)
            data.extend([
                ['T', [.19, .735 + lift, '行旅总览'], {'font_size': 22, 'font_weight': 'bold', 'align': 'left', 'color': rgb(139, 69, 19)}],
                ['T', [.19, .685 + lift, f'已收录 {discovered} / 20 道运河风味'], {'font_size': 12, 'align': 'left', 'color': rgb(110, 91, 68)}],
                ['T', [.56, .735 + lift, '五城印记'], {'font_size': 22, 'font_weight': 'bold', 'align': 'left', 'color': rgb(139, 69, 19)}],
            ])
            for index, city in enumerate(cities):
                column = 0 if index < 3 else 1
                row = index if index < 3 else index - 3
                x = .19 if column == 0 else .56
                y = .60 - row * .145 + lift
                count = sum(f'{index}_{food}' in self.state.discovered_foods for food in range(4))
                data.extend([
                    ['C', [x + .025, y + .018, .025], {'fill': city['theme'] if count == 4 else rgb(205, 195, 172)}],
                    ['T', [x + .065, y + .013, city['name']], {'font_size': 14, 'font_weight': 'bold', 'align': 'left', 'color': rgb(69, 57, 45)}],
                    ['T', [x + .21, y + .013, f'{count}/4'], {'font_size': 11, 'align': 'right', 'color': city['theme']}],
                    ['R', [x + .065, y - .018, .145, .010], {'fill': rgb(222, 211, 185)}],
                    ['R', [x + .065, y - .018, .145 * count / 4, .010], {'fill': city['theme']}],
                ])
        else:
            city_index = page - 1
            city = cities[city_index]
            data.extend([
                ['T', [.18, .735 + lift, city['name']], {'font_size': 28, 'font_weight': 'bold', 'align': 'left', 'color': city['theme']}],
                ['T', [.18, .690 + lift, city['cuisine']], {'font_size': 11, 'align': 'left', 'color': rgb(99, 81, 61)}],
            ])
            for index, line in enumerate(self._wrapped_lines(city['description'], 23)[:2]):
                data.append(['T', [.55, .735 - index * .035 + lift, line], {
                    'font_size': 10, 'align': 'left', 'color': rgb(110, 91, 68),
                }])
            positions = ((.27,.54),(.43,.37),(.62,.54),(.78,.37))
            for food_index, (food, (x, y)) in enumerate(zip(city['foods'], positions)):
                found = f'{city_index}_{food_index}' in self.state.discovered_foods
                medallion = self._food_medallion(
                    x, y + lift, city['id'], food['id'], found,
                )
                data.append(['GR', medallion, {'transform': {
                    'scale': [.52, .52], 'pivot': [x, y + lift],
                }}])
                data.append(['T', [x, y - .072 + lift, food['name'] if found else '尚未品鉴'], {
                    'font_size': 11, 'font_weight': 'bold' if found else 'normal',
                    'color': city['theme'] if found else rgb(156, 146, 124),
                }])
                data.append(['T', [x, y - .102 + lift, '已收录 ✓' if found else '沿运河继续寻味'], {
                    'font_size': 8, 'color': rgb(113, 101, 79),
                }])

        prev_disabled = page == 0
        next_disabled = page == len(cities)
        prev_hover = self.hovered_item == ('atlas_nav', -1) and not prev_disabled
        next_hover = self.hovered_item == ('atlas_nav', 1) and not next_disabled
        data.extend([
            ['RR', [.20, .105, .12, .055, .018], {'fill': rgb(139, 69, 19) if prev_hover else (rgb(224, 216, 196) if prev_disabled else rgb(218, 190, 137)), 'stroke': rgb(167, 120, 62), 'stroke_width': 1}],
            ['T', [.26, .121, '‹ 上一页'], {'font_size': 10, 'color': rgb(255, 248, 229) if prev_hover else rgb(105, 80, 56)}],
            ['T', [.50, .123, f'{page + 1} / {len(cities) + 1}'], {'font_size': 10, 'color': rgb(136, 117, 88)}],
            ['RR', [.68, .105, .12, .055, .018], {'fill': rgb(139, 69, 19) if next_hover else (rgb(224, 216, 196) if next_disabled else rgb(218, 190, 137)), 'stroke': rgb(167, 120, 62), 'stroke_width': 1}],
            ['T', [.74, .121, '下一页 ›'], {'font_size': 10, 'color': rgb(255, 248, 229) if next_hover else rgb(105, 80, 56)}],
        ])

        if abs(self.book_turn) > .025:
            amount = min(1.0, abs(self.book_turn))
            edge = .50 + (.34 * amount if self.book_turn > 0 else -.34 * amount)
            data.append(['G', [[.50,.205+lift],[edge,.23+lift],[edge,.77+lift],[.50,.79+lift]], {
                'fill': rgb(238, 224, 190), 'stroke': rgb(188, 150, 91), 'stroke_width': 2, 'z': 200,
            }])
        self.parser.parse(data, self.bounds)

    def draw_settings(self):
        """绘制设置页；主音量连接代码演奏，音效接口保持预留。"""
        pulse = .006 * math.sin(self.animation_phase * 1.8)
        accelerated = self.engine.mode_name == 'accelerated'
        acceleration_available = self.engine.supports_acceleration
        toggle_hover = self.hovered_item == ('acceleration', 0) and acceleration_available
        audio_hover = self.hovered_item == ('audio_enabled', 0)
        data = [
            ['T', [.50, .865, '设置'], {'font_size': 30, 'font_weight': 'bold', 'color': rgb(67, 54, 42)}],
            ['T', [.50, .820, '画面与声音'], {'font_size': 11, 'color': rgb(137, 113, 79)}],
            ['E', [.50, .185, .315, .025], {'fill': rgb(201, 185, 151)}],
            ['RR', [.19, .20 + pulse, .62, .56, .032], {
                'fill': rgb(247, 238, 211), 'stroke': rgb(173, 126, 67), 'stroke_width': 2,
            }],
            ['T', [.255, .675 + pulse, '渲染性能'], {'font_size': 17, 'font_weight': 'bold', 'align': 'left', 'color': rgb(73, 60, 46)}],
            ['T', [.255, .632 + pulse, '加速模式'], {'font_size': 14, 'align': 'left', 'color': rgb(82, 68, 52)}],
            ['T', [.255, .598 + pulse, '关闭后使用纯 Turtle 绘制，帧率会相应降低'], {'font_size': 9, 'align': 'left', 'color': rgb(135, 117, 91)}],
            ['RR', [.655, .617 + pulse, .095, .052, .026], {
                'fill': rgb(54, 142, 104) if accelerated else rgb(190, 183, 165),
                'stroke': rgb(35, 112, 81) if toggle_hover else rgb(151, 135, 106),
                'stroke_width': 3 if toggle_hover else 1,
            }],
            ['C', [.722 if accelerated else .682, .643 + pulse, .020], {
                'fill': rgb(255, 250, 233) if acceleration_available else rgb(216, 208, 189),
            }],
            ['L', [[.24,.555+pulse],[.76,.555+pulse]], {'stroke': rgb(213, 193, 153), 'stroke_width': 1}],
            ['T', [.255, .510 + pulse, '音频设置'], {'font_size': 17, 'font_weight': 'bold', 'align': 'left', 'color': rgb(73, 60, 46)}],
            ['T', [.545, .510 + pulse, '总开关'], {'font_size': 11, 'align': 'left', 'color': rgb(91, 74, 55)}],
            ['RR', [.655, .484 + pulse, .095, .046, .023], {
                'fill': rgb(54, 142, 104) if self.audio_enabled else rgb(190, 183, 165),
                'stroke': rgb(35, 112, 81) if audio_hover else rgb(151, 135, 106),
                'stroke_width': 2 if audio_hover else 1,
            }],
            ['C', [.721 if self.audio_enabled else .684, .507 + pulse, .017], {'fill': rgb(255, 250, 233)}],
        ]

        for label, value, y, key in (
            ('音乐音量', self.master_volume, .435, 'master_volume'),
            ('音效', self.effects_volume, .335, 'effects_volume'),
        ):
            hovered = self.hovered_item == (key, 0)
            knob_x = .43 + .30 * value
            data.extend([
                ['T', [.255, y + .004 + pulse, label], {'font_size': 12, 'align': 'left', 'color': rgb(91, 74, 55)}],
                ['RR', [.43, y + pulse, .30, .012, .006], {'fill': rgb(211, 200, 174)}],
                ['RR', [.43, y + pulse, .30 * value, .012, .006], {'fill': rgb(173, 126, 67)}],
                ['C', [knob_x, y + .006 + pulse, .015 if hovered else .012], {
                    'fill': rgb(139, 69, 19) if hovered else rgb(181, 129, 65),
                    'stroke': rgb(255, 246, 220), 'stroke_width': 2,
                }],
                ['T', [.765, y + .001 + pulse, f'{round(value * 100)}%'], {
                    'font_size': 10, 'align': 'right', 'color': rgb(118, 98, 72),
                }],
            ])
        status = '已启用 Canvas 批量渲染' if accelerated else '当前使用纯 Turtle 渲染'
        if not acceleration_available:
            status += '（命令行兼容模式）'
        data.extend([
            ['T', [.50, .272 + pulse, status], {'font_size': 10, 'color': rgb(119, 97, 70)}],
        ])
        self.parser.parse(data, self.bounds)

    def draw_back_button(self):
        """Global back affordance shared by every non-intro scene."""
        hovered = self.hovered_item == ('back', 0)
        data = [
            ['RR', [.055, .875, .105, .060, .018], {
                'fill': rgb(139, 69, 19) if hovered else rgb(232, 218, 187),
                'stroke': rgb(164, 121, 62), 'stroke_width': 1,
            }],
            ['T', [.108, .892, '‹ 返回'], {'font_size': 11, 'font_weight': 'bold',
                                          'color': rgb(255, 248, 229) if hovered else rgb(91, 63, 39)}],
        ]
        self.parser.parse(data, self.bounds)

    def draw_transition(self):
        """A scroll-closing transition shared by all scene changes."""
        cover = self.transition.cover
        if cover <= 0:
            return
        half = .5 * cover
        data = [
            ['R', [0, 0, half, 1], {'fill': rgb(232, 218, 184), 'z': 900}],
            ['R', [1 - half, 0, half, 1], {'fill': rgb(232, 218, 184), 'z': 900}],
            ['L', [[half, .03], [half, .97]], {'stroke': rgb(169, 124, 65), 'stroke_width': 3, 'z': 910}],
            ['L', [[1 - half, .03], [1 - half, .97]], {'stroke': rgb(169, 124, 65), 'stroke_width': 3, 'z': 910}],
        ]
        if cover > .84:
            data.append(['T', [.5, .49, '京杭大运河'], {'font_size': 18, 'color': rgb(126, 82, 48), 'z': 920}])
        self.parser.parse(data, self.bounds)

    def draw_finale(self):
        """绘制终章"""
        lantern_bob = .008 * math.sin(self.animation_phase * 1.8)
        data = [
            ['T', [0.5, 0.7, '运河四季·人间五味'], {'font_size': 36, 'color': rgb(139, 69, 19)}],
            ['T', [0.5, 0.55, '五城印章已全部收集'], {'font_size': 18, 'color': rgb(100, 100, 100)}],
            ['T', [0.5, 0.4 + lantern_bob, '🏮  🏮  🏮  🏮  🏮'], {'font_size': 24, 'color': rgb(201, 48, 44)}],
            ['B', [[.22,.34-lantern_bob],[.39,.37],[.62,.32+lantern_bob],[.78,.35]], {'stroke': rgb(218, 190, 130), 'stroke_width': 2}],
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
            ['T', [0.5, 0.44, '鼠标长按 / ←→ - 驾船或翻页'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.38, 'B - 打开/关闭美食图鉴'], {'font_size': 14, 'color': rgb(80, 80, 80)}],
            ['T', [0.5, 0.30, '按 H 或 Esc 关闭'], {'font_size': 12, 'color': rgb(150, 150, 150)}],
        ]

        self.parser.parse(data, self.bounds)

    def draw_status(self):
        """绘制状态提示"""
        mode_names = {
            Mode.INTRO: '开场',
            Mode.LOADING: '加载',
            Mode.MAP: '地图',
            Mode.CITY: '城市',
            Mode.FOOD_DETAIL: '详情',
            Mode.ATLAS: '图鉴',
            Mode.SETTINGS: '设置',
            Mode.FINALE: '终章',
        }
        mode_name = mode_names.get(self.state.mode, '未知')
        data = [
            ['T', [0.95, 0.05, f'[{mode_name}]'], {'font_size': 10, 'color': rgb(180, 180, 180), 'align': 'right'}],
        ]
        self.parser.parse(data, self.bounds)

    # 事件处理
    def begin_transition(self, action):
        """Lock input and change scene at the covered midpoint."""
        if self.transition.active:
            return
        self.move_direction = 0
        self._pressed_nav = None
        self.state.transition_locked = True

        def switch_scene():
            # StateMachine intentionally rejects transitions while locked, so
            # unlock only for the atomic midpoint scene change.
            self.state.transition_locked = False
            action()
            self.state.transition_locked = True
            self.hovered_item = None

        self.transition.start(switch_scene)

    def on_enter(self):
        """Enter 键"""
        if self.state.transition_locked:
            return
        if self.state.help_open:
            self.machine.toggle_help()
            self.render()
            return

        if self.state.mode == Mode.INTRO:
            self.effects.play('key')
            self.begin_transition(self._enter_journey)
        elif self.state.mode == Mode.MAP:
            if self.state.is_all_stamped():
                self.begin_transition(self.machine.go_to_finale)
            elif self.boat.nearby_city() is not None:
                self.state.current_city = self.boat.nearby_city()
                self.effects.play('fresh')
                self.begin_transition(self.machine.enter_city)
        elif self.state.mode == Mode.CITY:
            self.effects.play('scroll')
            self.begin_transition(self.machine.open_food)
        elif self.state.mode == Mode.FOOD_DETAIL:
            self.effects.play('stamp')
            self.begin_transition(self.machine.complete_tasting)
        elif self.state.mode == Mode.ATLAS:
            self._turn_atlas(1)
        elif self.state.mode == Mode.FINALE:
            self.begin_transition(self.machine.return_from_finale)

        self.render()

    def on_escape(self):
        """Esc 键"""
        if self.state.help_open:
            self.machine.toggle_help()
        elif self.state.mode == Mode.FINALE:
            self.begin_transition(self.machine.return_from_finale)
        elif self.state.mode != Mode.INTRO:
            self.effects.play('scroll' if self.state.mode in (Mode.ATLAS, Mode.FOOD_DETAIL) else 'key')
            self.begin_transition(self.machine.back)
        self.render()

    def on_left(self):
        """左方向键"""
        if self.state.help_open or self.state.transition_locked:
            return

        if self.state.mode == Mode.MAP:
            self.move_direction = -1
        elif self.state.mode == Mode.CITY:
            self.machine.prev_food()
            self.render()
        elif self.state.mode == Mode.ATLAS:
            self._turn_atlas(-1)

    def on_right(self):
        """右方向键"""
        if self.state.help_open or self.state.transition_locked:
            return

        if self.state.mode == Mode.MAP:
            self.move_direction = 1
        elif self.state.mode == Mode.CITY:
            self.machine.next_food()
            self.render()
        elif self.state.mode == Mode.ATLAS:
            self._turn_atlas(1)

    def on_direction_release(self):
        self.move_direction = 0

    def _turn_atlas(self, direction):
        previous = self.state.atlas_page
        self.machine.turn_atlas(direction)
        if self.state.atlas_page != previous:
            self.effects.play('page')
            self.book_turn = float(direction)
            self.render()

    def on_animation_frame(self, delta_seconds):
        """Drive restrained vector motion, boat physics and transitions."""
        self.animation_phase += delta_seconds
        was_transitioning = self.transition.active
        self.transition.step(delta_seconds)
        if abs(self.book_turn) > .001:
            self.book_turn *= math.exp(-7.5 * delta_seconds)
        else:
            self.book_turn = 0.0
        if was_transitioning and not self.transition.active:
            self.state.transition_locked = False

        if self.state.mode == Mode.LOADING:
            ceiling = self._loading_target if self._loading_complete else min(self._loading_target + .42, .92)
            self._loading_progress += (ceiling - self._loading_progress) * min(1., delta_seconds * 2.6)
            if self._loading_complete and self._loading_progress >= .985 and not self._loading_finished_transition:
                self._loading_finished_transition = True
                if self.audio_enabled:
                    self.music.start()
                self.begin_transition(self.machine.finish_loading)

        if self.state.mode == Mode.MAP:
            moved = self.boat.step(self.move_direction, delta_seconds)
            self.splash.step(delta_seconds)
            self._splash_elapsed += delta_seconds
            if moved and abs(self.boat.velocity) > .018 and self._splash_elapsed >= .075:
                x, y = route_point(self.boat.position)
                self.splash.emit(
                    x, y - .018,
                    1 if self.boat.velocity >= 0 else -1,
                    2 if self.engine.mode_name == 'accelerated' else 1,
                )
                self._splash_elapsed = 0.0
            nearby = self.boat.nearby_city()
            if nearby is not None:
                self.state.current_city = nearby
            self.effects.set_water_level(abs(self.boat.velocity) / self.boat.max_speed)
        else:
            self.effects.set_water_level(0)
        self.render()
        return True

    def on_help(self):
        """H 键"""
        if self.state.transition_locked:
            return
        self.machine.toggle_help()
        self.render()

    def on_atlas(self):
        """B toggles the atlas from either side of the map."""
        if self.state.transition_locked or self.state.help_open:
            return
        if self.state.mode == Mode.MAP:
            self.effects.play('scroll')
            self.begin_transition(self.machine.open_atlas)
        elif self.state.mode == Mode.ATLAS:
            self.effects.play('scroll')
            self.begin_transition(self.machine.back)
        self.render()

    def _toggle_acceleration(self):
        """Switch renderer implementation while preserving application state."""
        if not self.engine.supports_acceleration:
            return
        self.engine.set_acceleration(self.engine.mode_name != 'accelerated')
        self._background_rendered = False
        accelerated = self.engine.mode_name == 'accelerated'
        self.animations.set_fps(30 if accelerated else 10)
        self.splash.limit = 36 if accelerated else 10
        self.splash.drops = self.splash.drops[-self.splash.limit:]

    def _set_volume(self, setting, nx):
        value = max(0.0, min(1.0, (nx - .43) / .30))
        if setting == 'master_volume':
            self.master_volume = value
            self.music.set_volume(value)
        else:
            self.effects_volume = value
            self.effects.set_volume(value)

    def _toggle_audio(self):
        self.audio_enabled = not self.audio_enabled
        self.music.set_enabled(self.audio_enabled)
        self.effects.set_enabled(self.audio_enabled)

    def on_motion(self, x, y):
        """Update semantic hover state without redrawing for every pixel."""
        nx, ny = x / CANVAS_WIDTH, y / CANVAS_HEIGHT
        hovered = None

        if self.state.transition_locked:
            return
        if not self.state.help_open and self.state.mode != Mode.INTRO and .045 <= nx <= .17 and .86 <= ny <= .95:
            hovered = ('back', 0)
        elif not self.state.help_open and self.state.mode == Mode.INTRO:
            if .35 <= nx <= .65 and .14 <= ny <= .26:
                hovered = ('start', 0)
        elif not self.state.help_open and self.state.mode == Mode.MAP:
            if .825 <= nx <= .955 and .85 <= ny <= .94:
                hovered = ('settings', 0)
            elif .04 <= nx <= .21 and .05 <= ny <= .17:
                hovered = ('atlas', 0)
            else:
                nearby = self.boat.nearby_city()
                if nearby is not None and self._inside(
                    nx, ny, self._preview_layout(nearby)[-1],
                ):
                    hovered = ('explore', nearby)
                elif .045 <= nx <= .14 and .37 <= ny <= .51:
                    hovered = ('nav', -1)
                elif .86 <= nx <= .955 and .37 <= ny <= .51:
                    hovered = ('nav', 1)
        elif not self.state.help_open and self.state.mode == Mode.CITY:
            city_id = get_city(self.state.current_city)['id']
            for index, (px, py) in enumerate(FOOD_POSITIONS[city_id]):
                if (px - nx) ** 2 + (py - ny) ** 2 <= .010:
                    hovered = ('food', index)
                    break
        elif not self.state.help_open and self.state.mode == Mode.FOOD_DETAIL:
            if .73 <= nx <= .91 and .16 <= ny <= .25:
                hovered = ('taste', 0)
        elif not self.state.help_open and self.state.mode == Mode.ATLAS:
            if .19 <= nx <= .33 and .09 <= ny <= .17 and self.state.atlas_page > 0:
                hovered = ('atlas_nav', -1)
            elif .67 <= nx <= .81 and .09 <= ny <= .17 and self.state.atlas_page < 5:
                hovered = ('atlas_nav', 1)
        elif not self.state.help_open and self.state.mode == Mode.SETTINGS:
            if .64 <= nx <= .77 and .47 <= ny <= .54:
                hovered = ('audio_enabled', 0)
            elif (.64 <= nx <= .77 and .60 <= ny <= .69
                    and self.engine.supports_acceleration):
                hovered = ('acceleration', 0)
            elif .40 <= nx <= .75 and .40 <= ny <= .48:
                hovered = ('master_volume', 0)
            elif .40 <= nx <= .75 and .30 <= ny <= .38:
                hovered = ('effects_volume', 0)

        self.engine.set_cursor('hand2' if hovered is not None else '')
        if hovered != self.hovered_item:
            self.hovered_item = hovered
            self.render()

    def on_click(self, x, y):
        """鼠标点击"""
        if self.state.transition_locked:
            return
        if self.state.help_open:
            self.effects.play('key')
            self.machine.toggle_help()
            self.render()
            return

        nx, ny = x / CANVAS_WIDTH, y / CANVAS_HEIGHT
        if self.state.can_go_back() and .045 <= nx <= .17 and .86 <= ny <= .95:
            self.effects.play('scroll' if self.state.mode in (Mode.ATLAS, Mode.FOOD_DETAIL) else 'key')
            if self.state.mode == Mode.FINALE:
                self.begin_transition(self.machine.return_from_finale)
            else:
                self.begin_transition(self.machine.back)
        elif self.state.mode == Mode.INTRO:
            if .35 <= nx <= .65 and .14 <= ny <= .26:
                self.effects.play('key')
                self.begin_transition(self._enter_journey)
        elif self.state.mode == Mode.MAP:
            if .825 <= nx <= .955 and .85 <= ny <= .94:
                self.effects.play('key')
                self.begin_transition(self.machine.open_settings)
            elif .04 <= nx <= .21 and .05 <= ny <= .17:
                self.effects.play('scroll')
                self.begin_transition(self.machine.open_atlas)
            else:
                nearby = self.boat.nearby_city()
                if nearby is not None and self._inside(
                    nx, ny, self._preview_layout(nearby)[-1],
                ):
                    self.state.current_city = nearby
                    self.effects.play('fresh')
                    self.begin_transition(self.machine.enter_city)
                elif .045 <= nx <= .14 and .37 <= ny <= .51:
                    self.effects.play('key')
                    self.boat.nudge(-1)
                elif .86 <= nx <= .955 and .37 <= ny <= .51:
                    self.effects.play('key')
                    self.boat.nudge(1)
        elif self.state.mode == Mode.CITY:
            city_id = get_city(self.state.current_city)['id']
            for index, (px, py) in enumerate(FOOD_POSITIONS[city_id]):
                if (px - nx) ** 2 + (py - ny) ** 2 <= .010:
                    self.state.current_food = index
                    self.effects.play('scroll')
                    self.begin_transition(self.machine.open_food)
                    break
        elif self.state.mode == Mode.FOOD_DETAIL:
            if .73 <= nx <= .91 and .16 <= ny <= .25:
                self.effects.play('stamp')
                self.begin_transition(self.machine.complete_tasting)
        elif self.state.mode == Mode.ATLAS:
            if .19 <= nx <= .33 and .09 <= ny <= .17:
                self._turn_atlas(-1)
            elif .67 <= nx <= .81 and .09 <= ny <= .17:
                self._turn_atlas(1)
        elif self.state.mode == Mode.SETTINGS:
            if .64 <= nx <= .77 and .47 <= ny <= .54:
                self.effects.play('key')
                self._toggle_audio()
            elif .64 <= nx <= .77 and .60 <= ny <= .69:
                self.effects.play('key')
                self._toggle_acceleration()
            elif .40 <= nx <= .75 and .40 <= ny <= .48:
                self._set_volume('master_volume', nx)
            elif .40 <= nx <= .75 and .30 <= ny <= .38:
                self._set_volume('effects_volume', nx)
        self.render()

    def on_pointer_press(self, x, y):
        """Turn map arrows into continuous press-and-hold throttles."""
        if self.state.mode != Mode.MAP or self.state.help_open or self.state.transition_locked:
            return
        nx, ny = x / CANVAS_WIDTH, y / CANVAS_HEIGHT
        nearby = self.boat.nearby_city()
        if nearby is not None and self._inside(
            nx, ny, self._preview_layout(nearby)[-1],
        ):
            # The floating Explore button intentionally wins when the Suzhou
            # card overlaps the forward throttle.
            return
        direction = 0
        if .045 <= nx <= .14 and .37 <= ny <= .51:
            direction = -1
        elif .86 <= nx <= .955 and .37 <= ny <= .51:
            direction = 1
        if direction:
            self._pressed_nav = direction
            self.move_direction = direction
            self.hovered_item = ('nav', direction)
            self.render()

    def on_pointer_release(self, _x, _y):
        if self._pressed_nav is not None:
            self._pressed_nav = None
            self.move_direction = 0
            self.render()


def main(argv=None):
    """主程序入口"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description='运河风物志 Canal Delights')
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
