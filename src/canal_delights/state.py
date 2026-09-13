"""
状态机 - 管理应用状态和转换
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Set


class Mode(Enum):
    """应用模式"""
    INTRO = auto()        # 开场卷轴
    LOADING = auto()      # 首次音频与场景预热
    MAP = auto()          # 运河地图
    CITY = auto()         # 城市场景
    FOOD_DETAIL = auto()  # 美食详情
    ATLAS = auto()        # 美食图鉴
    SETTINGS = auto()     # 设置
    FINALE = auto()       # 终章长卷


@dataclass
class AppState:
    """应用状态"""
    mode: Mode = Mode.INTRO
    current_city: int = 0  # 0-4 对应五城
    current_food: int = 0  # 0-3 对应每城四道美食
    atlas_page: int = 0    # 0 为总览，1-5 为城市页
    visited_cities: Set[int] = field(default_factory=set)
    discovered_foods: Set[str] = field(default_factory=set)  # "city_food" 格式
    stamped_cities: Set[int] = field(default_factory=set)
    help_open: bool = False
    transition_locked: bool = False

    def can_go_back(self) -> bool:
        """是否可以返回上一级"""
        return self.mode in [Mode.MAP, Mode.CITY, Mode.FOOD_DETAIL, Mode.ATLAS, Mode.SETTINGS]

    def is_all_stamped(self) -> bool:
        """是否五城全部盖章"""
        return len(self.stamped_cities) >= 5

    def get_food_key(self) -> str:
        """获取当前美食的唯一标识"""
        return f"{self.current_city}_{self.current_food}"


class StateMachine:
    """状态机 - 管理状态转换"""

    def __init__(self, state: AppState, city_count: int = 5, food_count: int = 4):
        self.state = state
        self.city_count = city_count
        self.food_count = food_count

    def next_city(self):
        """下一个城市"""
        if self.state.mode == Mode.MAP and not self.state.transition_locked:
            self.state.current_city = (self.state.current_city + 1) % self.city_count

    def prev_city(self):
        """上一个城市"""
        if self.state.mode == Mode.MAP and not self.state.transition_locked:
            self.state.current_city = (self.state.current_city - 1) % self.city_count

    def enter_city(self):
        """进入城市"""
        if self.state.mode == Mode.MAP and not self.state.transition_locked:
            self.state.mode = Mode.CITY
            self.state.visited_cities.add(self.state.current_city)
            self.state.current_food = 0

    def next_food(self):
        """下一道美食"""
        if self.state.mode == Mode.CITY and not self.state.transition_locked:
            self.state.current_food = (self.state.current_food + 1) % self.food_count

    def prev_food(self):
        """上一道美食"""
        if self.state.mode == Mode.CITY and not self.state.transition_locked:
            self.state.current_food = (self.state.current_food - 1) % self.food_count

    def open_food(self):
        """打开美食详情"""
        if self.state.mode == Mode.CITY and not self.state.transition_locked:
            self.state.mode = Mode.FOOD_DETAIL

    def complete_tasting(self):
        """完成品鉴"""
        if self.state.mode == Mode.FOOD_DETAIL and not self.state.transition_locked:
            food_key = self.state.get_food_key()
            self.state.discovered_foods.add(food_key)

            # 四道菜全部发现后，给城市盖章。
            city = self.state.current_city
            if all(f"{city}_{index}" in self.state.discovered_foods
                   for index in range(self.food_count)):
                self.state.stamped_cities.add(city)

            self.state.mode = Mode.CITY

    def back(self):
        """返回上一级"""
        if self.state.transition_locked:
            return

        if self.state.mode == Mode.FOOD_DETAIL:
            self.state.mode = Mode.CITY
        elif self.state.mode == Mode.CITY:
            self.state.mode = Mode.MAP
        elif self.state.mode == Mode.ATLAS:
            self.state.mode = Mode.MAP
        elif self.state.mode == Mode.SETTINGS:
            self.state.mode = Mode.MAP
        elif self.state.mode == Mode.MAP:
            self.state.mode = Mode.INTRO

    def open_atlas(self):
        """从地图打开图鉴。"""
        if self.state.mode == Mode.MAP and not self.state.transition_locked:
            self.state.mode = Mode.ATLAS
            self.state.atlas_page = 0

    def turn_atlas(self, direction: int):
        """翻动图鉴，页码限制在总览与五个城市页之间。"""
        if self.state.mode == Mode.ATLAS and not self.state.transition_locked:
            self.state.atlas_page = max(
                0, min(self.city_count, self.state.atlas_page + direction),
            )

    def open_settings(self):
        """从地图打开设置。"""
        if self.state.mode == Mode.MAP and not self.state.transition_locked:
            self.state.mode = Mode.SETTINGS

    def start_journey(self):
        """开始旅程"""
        if self.state.mode == Mode.INTRO and not self.state.transition_locked:
            self.state.mode = Mode.MAP

    def start_loading(self):
        if self.state.mode == Mode.INTRO and not self.state.transition_locked:
            self.state.mode = Mode.LOADING

    def finish_loading(self):
        if self.state.mode == Mode.LOADING and not self.state.transition_locked:
            self.state.mode = Mode.MAP

    def go_to_finale(self):
        """进入终章"""
        if self.state.mode == Mode.MAP and self.state.is_all_stamped():
            self.state.mode = Mode.FINALE

    def return_from_finale(self):
        """从终章返回"""
        if self.state.mode == Mode.FINALE:
            self.state.mode = Mode.MAP

    def toggle_help(self):
        """切换帮助"""
        self.state.help_open = not self.state.help_open
