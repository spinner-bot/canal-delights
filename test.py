import os
import random
import time
import msvcrt
from enum import Enum


# ============================================================
# 配置
# ============================================================

WIDTH = 30
HEIGHT = 16

INITIAL_SPEED = 0.13
MIN_SPEED = 0.055

INITIAL_LIVES = 3

EMPTY = "  "
WALL = "##"
HEAD = "● "
BODY = "■ "
FOOD = "★ "


# ============================================================
# 游戏状态
# ============================================================

class GameState(Enum):
    MENU = 1
    READY = 2
    RUNNING = 3
    PAUSED = 4
    DEAD = 5
    GAME_OVER = 6
    EXIT = 7


# ============================================================
# 控制台
# ============================================================

def init_console():
    """
    初始化终端：
    1. Windows 开启 ANSI
    2. 清屏
    3. 隐藏光标
    """
    os.system("")
    print("\033[2J", end="")
    print("\033[?25l", end="", flush=True)


def restore_console():
    """程序退出时恢复光标"""
    print("\033[?25h", end="", flush=True)


def clear_frame():
    """
    光标移动到左上角。
    后续内容覆盖旧画面，而不是继续向下打印。
    """
    print("\033[H", end="")


def render(lines):
    """
    一次性绘制完整画面，减少闪烁。
    同时清理旧帧残留内容。
    """
    clear_frame()

    content = "\n".join(lines)

    # \033[J = 清除光标之后的内容
    print(content + "\033[J", end="", flush=True)


# ============================================================
# 输入
# ============================================================

def read_key():
    """
    非阻塞读取一个按键。
    没有按键时返回 None。
    """
    if not msvcrt.kbhit():
        return None

    key = msvcrt.getch()

    # 方向键等特殊键会返回两个字节
    if key in (b"\x00", b"\xe0"):
        if msvcrt.kbhit():
            msvcrt.getch()
        return None

    try:
        return key.decode("utf-8").lower()
    except UnicodeDecodeError:
        return None


def wait_key(valid_keys):
    """
    阻塞等待指定按键。
    """
    while True:
        key = read_key()

        if key in valid_keys:
            return key

        time.sleep(0.02)


# ============================================================
# 游戏数据
# ============================================================

class SnakeGame:

    def __init__(self):
        self.state = GameState.MENU

        self.snake = []
        self.food = None
        self.direction = "right"

        self.score = 0
        self.lives = INITIAL_LIVES

        self.speed = INITIAL_SPEED

    # --------------------------------------------------------
    # 初始化游戏
    # --------------------------------------------------------

    def new_game(self):
        """
        完整的新游戏：
        分数、生命全部重置。
        """
        self.score = 0
        self.lives = INITIAL_LIVES
        self.speed = INITIAL_SPEED

        self.reset_round()

        self.state = GameState.READY

    def reset_round(self):
        """
        重置当前这一条命。

        注意：
        不重置 score 和 lives。
        """
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]

        self.direction = "right"
        self.food = self.create_food()

    # --------------------------------------------------------
    # 食物
    # --------------------------------------------------------

    def create_food(self):
        while True:
            food = (
                random.randint(1, WIDTH - 2),
                random.randint(1, HEIGHT - 2),
            )

            if food not in self.snake:
                return food

    # --------------------------------------------------------
    # 移动
    # --------------------------------------------------------

    def change_direction(self, key):
        """
        根据 WASD 改变方向。
        禁止直接反方向移动。
        """

        if key == "w" and self.direction != "down":
            self.direction = "up"

        elif key == "s" and self.direction != "up":
            self.direction = "down"

        elif key == "a" and self.direction != "right":
            self.direction = "left"

        elif key == "d" and self.direction != "left":
            self.direction = "right"

    def move(self):
        x, y = self.snake[0]

        if self.direction == "up":
            y -= 1

        elif self.direction == "down":
            y += 1

        elif self.direction == "left":
            x -= 1

        elif self.direction == "right":
            x += 1

        new_head = (x, y)

        self.snake.insert(0, new_head)

        # 吃到食物
        if new_head == self.food:
            self.score += 10

            self.food = self.create_food()

            # 分数越高速度越快
            self.speed = max(
                MIN_SPEED,
                INITIAL_SPEED - self.score * 0.0005,
            )

            # 不删除尾部，相当于增长
        else:
            self.snake.pop()

    # --------------------------------------------------------
    # 死亡判断
    # --------------------------------------------------------

    def collided(self):
        x, y = self.snake[0]

        # 撞墙
        if (
            x <= 0
            or x >= WIDTH - 1
            or y <= 0
            or y >= HEIGHT - 1
        ):
            return True

        # 撞自己
        if self.snake[0] in self.snake[1:]:
            return True

        return False

    # --------------------------------------------------------
    # 生命周期：死亡
    # --------------------------------------------------------

    def die(self):
        """
        当前生命结束。
        """
        self.lives -= 1

        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            self.state = GameState.DEAD

    # --------------------------------------------------------
    # 生命周期：复活
    # --------------------------------------------------------

    def revive(self):
        """
        复活。

        当前 lives 已经在死亡时扣除，
        所以这里只重新生成蛇。
        """
        if self.lives <= 0:
            return

        self.reset_round()
        self.state = GameState.READY

    # ========================================================
    # 绘制
    # ========================================================

    def board_lines(self):
        snake_set = set(self.snake)

        lines = []

        for y in range(HEIGHT):

            line = ""

            for x in range(WIDTH):

                if (
                    x == 0
                    or x == WIDTH - 1
                    or y == 0
                    or y == HEIGHT - 1
                ):
                    line += WALL

                elif self.snake and (x, y) == self.snake[0]:
                    line += HEAD

                elif (x, y) in snake_set:
                    line += BODY

                elif (x, y) == self.food:
                    line += FOOD

                else:
                    line += EMPTY

            lines.append(line)

        return lines

    def draw_game(self):
        lines = [
            "========== Python 贪吃蛇 ==========",
            "",
            f"分数：{self.score:<5}   生命：{'♥ ' * self.lives}",
            "",
        ]

        lines += self.board_lines()

        lines += [
            "",
            "WASD：移动    P：暂停    Q：返回菜单",
        ]

        render(lines)

    # ========================================================
    # 各状态界面
    # ========================================================

    def show_menu(self):
        lines = [
            "",
            "==========================================",
            "",
            "              PYTHON 贪吃蛇",
            "",
            "==========================================",
            "",
            "",
            "              [ Enter ] 开始游戏",
            "",
            "              [ Q ]     退出游戏",
            "",
            "",
            "控制：",
            "",
            "    W / A / S / D       移动",
            "    P                   暂停 / 继续",
            "    Q                   返回菜单",
            "",
            "==========================================",
        ]

        render(lines)

    def show_ready(self):
        lines = [
            "========== Python 贪吃蛇 ==========",
            "",
            f"分数：{self.score:<5}   生命：{'♥ ' * self.lives}",
            "",
        ]

        lines += self.board_lines()

        lines += [
            "",
            "------------------------------------------",
            "",
            "               准备开始",
            "",
            "             SPACE  开始移动",
            "",
            "             Q      返回菜单",
            "",
            "------------------------------------------",
        ]

        render(lines)

    def show_paused(self):
        lines = [
            "========== Python 贪吃蛇 ==========",
            "",
            f"分数：{self.score:<5}   生命：{'♥ ' * self.lives}",
            "",
        ]

        lines += self.board_lines()

        lines += [
            "",
            "==========================================",
            "",
            "                 已暂停",
            "",
            "              P 继续游戏",
            "              Q 返回菜单",
            "",
            "==========================================",
        ]

        render(lines)

    def show_dead(self):
        lines = [
            "========== Python 贪吃蛇 ==========",
            "",
            f"分数：{self.score:<5}   剩余生命：{'♥ ' * self.lives}",
            "",
        ]

        lines += self.board_lines()

        lines += [
            "",
            "==========================================",
            "",
            "               你死掉了！",
            "",
            f"             剩余生命：{self.lives}",
            "",
            "              R     复活",
            "              Enter 新游戏",
            "              Q     返回菜单",
            "",
            "==========================================",
        ]

        render(lines)

    def show_game_over(self):
        lines = [
            "",
            "==========================================",
            "",
            "                GAME OVER",
            "",
            "==========================================",
            "",
            f"                最终得分",
            "",
            f"                   {self.score}",
            "",
            "",
            "              Enter 重新开始",
            "",
            "              Q     返回菜单",
            "",
            "==========================================",
        ]

        render(lines)

    # ========================================================
    # 状态处理
    # ========================================================

    def handle_menu(self):
        self.show_menu()

        key = wait_key(["\r", "q"])

        if key == "\r":
            self.new_game()

        elif key == "q":
            self.state = GameState.EXIT

    def handle_ready(self):
        self.show_ready()

        while self.state == GameState.READY:

            key = read_key()

            if key == " ":
                self.state = GameState.RUNNING

            elif key == "q":
                self.state = GameState.MENU

            time.sleep(0.02)

    def handle_running(self):
        """
        真正的游戏循环。
        """

        self.draw_game()

        while self.state == GameState.RUNNING:

            frame_start = time.perf_counter()

            # ------------------------------
            # 获取这一帧期间所有键盘输入
            # ------------------------------

            while msvcrt.kbhit():

                key = read_key()

                if key is None:
                    continue

                if key in ("w", "a", "s", "d"):
                    self.change_direction(key)

                elif key == "p":
                    self.state = GameState.PAUSED
                    return

                elif key == "q":
                    self.state = GameState.MENU
                    return

            # ------------------------------
            # 移动
            # ------------------------------

            self.move()

            # ------------------------------
            # 判断死亡
            # ------------------------------

            if self.collided():

                self.draw_game()

                # 短暂停顿一下，让玩家看见死亡位置
                time.sleep(0.35)

                self.die()

                return

            # ------------------------------
            # 绘制
            # ------------------------------

            self.draw_game()

            # ------------------------------
            # 控制帧率
            # ------------------------------

            elapsed = time.perf_counter() - frame_start

            sleep_time = self.speed - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    def handle_paused(self):
        self.show_paused()

        while self.state == GameState.PAUSED:

            key = read_key()

            if key == "p":
                self.state = GameState.RUNNING

            elif key == "q":
                self.state = GameState.MENU

            time.sleep(0.02)

    def handle_dead(self):
        self.show_dead()

        while self.state == GameState.DEAD:

            key = read_key()

            if key == "r":
                self.revive()

            elif key == "\r":
                self.new_game()

            elif key == "q":
                self.state = GameState.MENU

            time.sleep(0.02)

    def handle_game_over(self):
        self.show_game_over()

        while self.state == GameState.GAME_OVER:

            key = read_key()

            if key == "\r":
                self.new_game()

            elif key == "q":
                self.state = GameState.MENU

            time.sleep(0.02)

    # ========================================================
    # 游戏主生命周期
    # ========================================================

    def run(self):

        while self.state != GameState.EXIT:

            if self.state == GameState.MENU:
                self.handle_menu()

            elif self.state == GameState.READY:
                self.handle_ready()

            elif self.state == GameState.RUNNING:
                self.handle_running()

            elif self.state == GameState.PAUSED:
                self.handle_paused()

            elif self.state == GameState.DEAD:
                self.handle_dead()

            elif self.state == GameState.GAME_OVER:
                self.handle_game_over()


# ============================================================
# Main
# ============================================================

def main():

    init_console()

    try:
        game = SnakeGame()
        game.run()

    finally:
        restore_console()

        # 清屏并把光标移回左上角
        print("\033[2J\033[H", end="")

        print("游戏已退出。")


if __name__ == "__main__":
    main()