# -*- coding: utf-8 -*-
"""
贪吃蛇游戏 (Snake Game)
一个使用 Python 和 Pygame 开发的经典贪吃蛇游戏，支持简体中文界面。
"""

import pygame
import random
import sys
import json
import os
import math

# 初始化 pygame
pygame.init()

# 颜色定义 (使用柔和、美观的配色)
COLOR_BG = (20, 20, 30)           # 深蓝灰色背景
COLOR_SNAKE_HEAD = (100, 220, 100)  # 浅绿色蛇头
COLOR_SNAKE_BODY = (60, 180, 60)    # 绿色蛇身
COLOR_FOOD = (255, 100, 100)        # 红色食物
COLOR_GRID = (40, 40, 50)           # 网格线颜色
COLOR_TEXT = (255, 255, 255)        # 白色文字
COLOR_SCORE = (255, 215, 0)         # 金色分数
COLOR_BUTTON = (70, 130, 180)       # 按钮颜色
COLOR_BUTTON_HOVER = (100, 160, 210)  # 按钮悬停颜色

# 游戏配置
CELL_SIZE = 25                       # 每个格子大小
GRID_WIDTH = 24                      # 网格宽度（格子数）
GRID_HEIGHT = 20                     # 网格高度（格子数）
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT + 60  # 额外空间用于显示分数

# 难度配置
DIFFICULTY_SETTINGS = {
    "简单": {"fps": 8, "color": (100, 200, 100)},
    "中等": {"fps": 12, "color": (200, 180, 100)},
    "困难": {"fps": 18, "color": (200, 100, 100)},
}
DEFAULT_DIFFICULTY = "中等"

# 游戏模式配置
GAME_MODES = {
    "经典": {"desc": "经典模式，撞墙或自身游戏结束", "color": (100, 200, 100)},
    "限时": {"desc": "限时60秒，挑战最高分", "time": 60, "color": (200, 180, 100)},
    "无尽": {"desc": "无墙壁，蛇穿墙而过", "color": (200, 100, 100)},
}
DEFAULT_GAME_MODE = "经典"

# 皮肤配置
SKINS = {
    "翠绿": {"head": (100, 220, 100), "body": (60, 180, 60), "food": (255, 100, 100), "color": (100, 200, 100)},
    "深蓝": {"head": (100, 150, 255), "body": (60, 100, 200), "food": (255, 200, 100), "color": (100, 150, 255)},
    "紫罗兰": {"head": (180, 100, 255), "body": (140, 60, 200), "food": (255, 255, 100), "color": (180, 100, 255)},
    "金色": {"head": (255, 200, 100), "body": (200, 150, 50), "food": (255, 100, 100), "color": (255, 200, 100)},
    "火焰": {"head": (255, 100, 50), "body": (200, 50, 0), "food": (100, 255, 100), "color": (255, 100, 50)},
}
DEFAULT_SKIN = "翠绿"

FPS = 10  # 默认值，会根据难度动态调整

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 数据持久化相关
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_data.json")

# 排行榜每页显示数量
LEADERBOARD_PAGE_SIZE = 5


def load_game_data():
    """加载游戏数据"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 确保排行榜数据结构存在
                if "leaderboards" not in data:
                    data["leaderboards"] = {
                        "经典": [],
                        "限时": [],
                        "无尽": []
                    }
                return data
    except Exception as e:
        print(f"加载数据失败：{e}")
    return {
        "high_scores": {"经典": 0, "限时": 0, "无尽": 0},
        "leaderboards": {"经典": [], "限时": [], "无尽": []}
    }


def save_game_data(data):
    """保存游戏数据"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据失败：{e}")

# 中文字体（尝试使用系统字体）
CHINESE_FONTS = [
    'SimHei',           # 黑体 (Windows)
    'Microsoft YaHei',  # 微软雅黑 (Windows)
    'PingFang SC',      # 苹方 (macOS)
    'Heiti SC',         # 黑体简 (macOS)
    'WenQuanYi Micro Hei',  # 文泉驿 (Linux)
    'Noto Sans CJK SC',     # 思源黑体
    'fonts/wqy-microhei.ttc',  # 备用字体文件
]

def get_chinese_font(size):
    """获取支持中文的字体"""
    for font_name in CHINESE_FONTS:
        try:
            font = pygame.font.Font(font_name, size)
            # 测试是否能渲染中文字符
            test_render = font.render("测试", True, COLOR_TEXT)
            return font
        except:
            continue
    # 如果所有中文字体都失败，使用默认字体（可能无法显示中文）
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont('arial', size)


class SoundManager:
    """音效管理器 - 使用 pygame 合成器生成音效"""

    def __init__(self):
        self.enabled = True
        self.sample_rate = 22050
        try:
            pygame.mixer.init(self.sample_rate, -16, 1, 512)
            self.enabled = True
        except:
            self.enabled = False
            print("音效初始化失败，将静音运行")

    
    def create_eat_sound(self):
        """创建吃食物的音效 - 高音滴声"""
        if not self.enabled:
            return None
        duration = 0.1
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            # 使用正弦波生成高音滴声
            value = int(32767 * 0.3 * (1 - i/n_samples) * math.sin(2 * math.pi * 880 * t))
            samples.append(max(-32768, min(32767, value)))
        return pygame.sndarray.make_sound(pygame.sndarray.array(samples))

    def create_crash_sound(self):
        """创建撞墙的音效 - 低沉噪音"""
        if not self.enabled:
            return None
        duration = 0.3
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            noise = random.uniform(-0.5, 0.5)
            value = int(32767 * 0.4 * (1 - i/n_samples) * noise)
            samples.append(max(-32768, min(32767, value)))
        return pygame.sndarray.make_sound(pygame.sndarray.array(samples))

    def create_gameover_sound(self):
        """创建游戏结束的音效 - 下降音调"""
        if not self.enabled:
            return None
        duration = 0.5
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            # 频率从440Hz下降到200Hz
            freq = 440 * (1 - t/duration) + 200
            value = int(32767 * 0.3 * (1 - i/n_samples) * math.sin(2 * math.pi * freq * t))
            samples.append(max(-32768, min(32767, value)))
        return pygame.sndarray.make_sound(pygame.sndarray.array(samples))

    def create_button_click_sound(self):
        """创建按钮点击音效 - 清脆短音"""
        if not self.enabled:
            return None
        duration = 0.05
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            # 使用正弦波生成清脆短音
            value = int(32767 * 0.3 * math.sin(2 * math.pi * 1200 * t))
            samples.append(max(-32768, min(32767, value)))
        return pygame.sndarray.make_sound(pygame.sndarray.array(samples))


class EffectManager:
    """特效管理器 - 处理视觉特效"""

    def __init__(self, screen_width, screen_height):
        self.food_pulse = 0
        self.food_pulse_dir = 1
        self.blur_surface = None
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        """更新特效状态"""
        self.food_pulse += 0.1 * self.food_pulse_dir
        if self.food_pulse > 1 or self.food_pulse < 0:
            self.food_pulse_dir *= -1

    def get_food_radius(self, base_radius):
        """获取带脉冲效果的食物半径"""
        return base_radius + self.food_pulse * 2

    def create_blur_surface(self, screen):
        """创建模糊背景 surface"""
        # 通过缩小再放大来模拟模糊效果
        small_size = (self.screen_width // 8, self.screen_height // 8)
        small_surface = pygame.transform.smoothscale(screen, small_size)
        self.blur_surface = pygame.transform.smoothscale(small_surface, (self.screen_width, self.screen_height))

    def get_blur_surface(self):
        """获取模糊背景 surface"""
        return self.blur_surface


class Snake:
    """蛇类"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置蛇的状态"""
        # 初始位置在屏幕中央
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False

    def change_direction(self, new_direction):
        """改变方向（防止 180 度转向）"""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.next_direction = new_direction

    def update(self):
        """更新蛇的位置"""
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_collision(self, game_mode="经典"):
        """检测碰撞（墙壁或自身）"""
        head = self.body[0]

        # 撞墙检测（无尽模式不检测撞墙）
        if game_mode != "无尽":
            if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
                return True

        # 撞自身检测
        if head in self.body[1:]:
            return True

        return False

    def wrap_around(self):
        """无尽模式：蛇穿墙而过"""
        head_x, head_y = self.body[0]
        new_x = head_x % GRID_WIDTH
        new_y = head_y % GRID_HEIGHT
        self.body[0] = (new_x, new_y)

    def eat(self):
        """吃到食物，蛇身增长"""
        self.grow = True


class Food:
    """食物类"""

    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        """在随机位置生成食物，避免出现在蛇身上"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if snake_body is None or (x, y) not in snake_body:
                self.position = (x, y)
                break


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏 - Snake Game")
        self.clock = pygame.time.Clock()
        self.font_large = get_chinese_font(48)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(24)
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        # 加载持久化的最高分
        game_data = load_game_data()
        self.high_scores = game_data.get("high_scores", {"经典": 0, "限时": 0, "无尽": 0})
        # 兼容旧版本数据
        if "high_score" in game_data and not self.high_scores.get("经典"):
            self.high_scores["经典"] = game_data["high_score"]
        self.selected_difficulty = DEFAULT_DIFFICULTY
        self.selected_game_mode = DEFAULT_GAME_MODE
        self.selected_skin = DEFAULT_SKIN
        self.state = "MENU"  # MENU, LEADERBOARD, PLAYING, PAUSED, GAME_OVER
        self.button_rect = None
        self.difficulty_buttons = []
        self.game_mode_buttons = []
        self.skin_buttons = []
        # 排行榜数据
        self.leaderboards = game_data.get("leaderboards", {"经典": [], "限时": [], "无尽": []})
        self.leaderboard_mode = DEFAULT_GAME_MODE
        self.leaderboard_back_button = None
        # 计时模式相关
        self.time_limit = 0
        self.time_remaining = 0
        self.start_time = 0
        # 初始化和创建音效
        self.sound_manager = SoundManager()
        self.sound_eat = self.sound_manager.create_eat_sound()
        self.sound_crash = self.sound_manager.create_crash_sound()
        self.sound_gameover = self.sound_manager.create_gameover_sound()
        self.sound_click = self.sound_manager.create_button_click_sound()
        # 特效管理器
        self.effect_manager = EffectManager(SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw_grid(self):
        """绘制背景网格"""
        self.screen.fill(COLOR_BG)
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 40), (x, SCREEN_HEIGHT))
        for y in range(40, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

    def draw_snake(self):
        """绘制蛇"""
        skin = SKINS[self.selected_skin]
        head_color = skin["head"]
        body_color = skin["body"]
        for i, (x, y) in enumerate(self.snake.body):
            color = head_color if i == 0 else body_color
            rect = pygame.Rect(
                x * CELL_SIZE + 2,
                y * CELL_SIZE + 42,  # 偏移以留出分数显示空间
                CELL_SIZE - 4,
                CELL_SIZE - 4
            )
            # 绘制圆角矩形
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            # 给蛇头添加眼睛
            if i == 0:
                eye_size = 4
                eye_offset = 6
                if self.snake.direction == RIGHT:
                    eye1_pos = (rect.right - eye_offset, rect.top + eye_offset)
                    eye2_pos = (rect.right - eye_offset, rect.bottom - eye_offset)
                elif self.snake.direction == LEFT:
                    eye1_pos = (rect.left + eye_offset, rect.top + eye_offset)
                    eye2_pos = (rect.left + eye_offset, rect.bottom - eye_offset)
                elif self.snake.direction == UP:
                    eye1_pos = (rect.left + eye_offset, rect.top + eye_offset)
                    eye2_pos = (rect.right - eye_offset, rect.top + eye_offset)
                else:  # DOWN
                    eye1_pos = (rect.left + eye_offset, rect.bottom - eye_offset)
                    eye2_pos = (rect.right - eye_offset, rect.bottom - eye_offset)
                pygame.draw.circle(self.screen, (255, 255, 255), eye1_pos, eye_size)
                pygame.draw.circle(self.screen, (255, 255, 255), eye2_pos, eye_size)

    def draw_food(self):
        """绘制食物"""
        skin = SKINS[self.selected_skin]
        food_color = skin["food"]
        x, y = self.food.position
        # 更新特效
        self.effect_manager.update()
        # 绘制圆形食物（带脉冲效果）
        center = (
            x * CELL_SIZE + CELL_SIZE // 2,
            y * CELL_SIZE + 42 + CELL_SIZE // 2
        )
        radius = self.effect_manager.get_food_radius(CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, food_color, center, int(radius))
        # 添加高光效果
        highlight_color = tuple(min(255, c + 50) for c in food_color)
        highlight_pos = (center[0] - 4, center[1] - 4)
        pygame.draw.circle(self.screen, highlight_color, highlight_pos, 4)
        # 添加外圈光晕效果
        glow_radius = int(radius + 4 + self.effect_manager.food_pulse * 3)
        pygame.draw.circle(self.screen, food_color, center, glow_radius, 2)

    def draw_score(self):
        """绘制分数"""
        high_score = self.high_scores.get(self.selected_game_mode, 0)
        if self.selected_game_mode == "限时":
            score_text = f"得分：{self.score}  |  剩余时间：{self.time_remaining}秒  |  最高分：{high_score}"
        else:
            score_text = f"得分：{self.score}  |  最高分：{high_score}"
        text_surface = self.font_small.render(score_text, True, COLOR_SCORE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 25))
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        """绘制主菜单"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 游戏标题
        title = self.font_large.render("贪吃蛇游戏", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
        self.screen.blit(title, title_rect)

        # 显示当前选择的游戏模式
        mode_color = GAME_MODES[self.selected_game_mode]["color"]
        mode_text = self.font_medium.render(f"当前模式：{self.selected_game_mode}", True, mode_color)
        mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140))
        self.screen.blit(mode_text, mode_rect)

        # 游戏模式选择按钮
        self.game_mode_buttons = []
        button_width = 100
        button_height = 40
        start_x = SCREEN_WIDTH // 2 - (len(GAME_MODES) * (button_width + 10)) // 2
        mouse_pos = pygame.mouse.get_pos()

        for i, (mode_name, settings) in enumerate(GAME_MODES.items()):
            btn_rect = pygame.Rect(
                start_x + i * (button_width + 10),
                SCREEN_HEIGHT // 2 - 100,
                button_width,
                button_height
            )
            self.game_mode_buttons.append((btn_rect, mode_name))
            btn_color = settings["color"]
            if btn_rect.collidepoint(mouse_pos):
                btn_color = tuple(min(255, c + 50) for c in btn_color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            mode_text = self.font_small.render(mode_name, True, COLOR_TEXT)
            text_rect = mode_text.get_rect(center=btn_rect.center)
            self.screen.blit(mode_text, text_rect)

        # 显示当前选择的难度
        diff_color = DIFFICULTY_SETTINGS[self.selected_difficulty]["color"]
        diff_text = self.font_medium.render(f"当前难度：{self.selected_difficulty}", True, diff_color)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(diff_text, diff_rect)

        # 难度选择按钮
        self.difficulty_buttons = []
        start_x = SCREEN_WIDTH // 2 - (len(DIFFICULTY_SETTINGS) * (button_width + 10)) // 2

        for i, (diff_name, settings) in enumerate(DIFFICULTY_SETTINGS.items()):
            btn_rect = pygame.Rect(
                start_x + i * (button_width + 10),
                SCREEN_HEIGHT // 2,
                button_width,
                button_height
            )
            self.difficulty_buttons.append((btn_rect, diff_name))
            btn_color = settings["color"]
            if btn_rect.collidepoint(mouse_pos):
                btn_color = tuple(min(255, c + 50) for c in btn_color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            diff_text = self.font_small.render(diff_name, True, COLOR_TEXT)
            text_rect = diff_text.get_rect(center=btn_rect.center)
            self.screen.blit(diff_text, text_rect)

        # 显示当前选择的皮肤
        skin_color = SKINS[self.selected_skin]["color"]
        skin_text = self.font_medium.render(f"当前皮肤：{self.selected_skin}", True, skin_color)
        skin_rect = skin_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(skin_text, skin_rect)

        # 皮肤选择按钮
        self.skin_buttons = []
        skin_button_width = 80
        start_x = SCREEN_WIDTH // 2 - (len(SKINS) * (skin_button_width + 5)) // 2

        for i, (skin_name, settings) in enumerate(SKINS.items()):
            btn_rect = pygame.Rect(
                start_x + i * (skin_button_width + 5),
                SCREEN_HEIGHT // 2 + 100,
                skin_button_width,
                button_height
            )
            self.skin_buttons.append((btn_rect, skin_name))
            btn_color = settings["color"]
            if btn_rect.collidepoint(mouse_pos):
                btn_color = tuple(min(255, c + 50) for c in btn_color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            skin_text = self.font_small.render(skin_name, True, COLOR_TEXT)
            text_rect = skin_text.get_rect(center=btn_rect.center)
            self.screen.blit(skin_text, text_rect)

        # 开始按钮
        self.button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 160,
            200,
            50
        )
        button_color = COLOR_BUTTON_HOVER if self.button_rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=10)

        start_text = self.font_medium.render("开始游戏", True, COLOR_TEXT)
        start_rect = start_text.get_rect(center=self.button_rect.center)
        self.screen.blit(start_text, start_rect)

        # 排行榜按钮
        self.leaderboard_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 80,
            SCREEN_HEIGHT // 2 + 220,
            160,
            40
        )
        lb_button_color = COLOR_BUTTON_HOVER if self.leaderboard_button.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(self.screen, lb_button_color, self.leaderboard_button, border_radius=10)

        lb_text = self.font_medium.render("排行榜", True, COLOR_TEXT)
        lb_rect = lb_text.get_rect(center=self.leaderboard_button.center)
        self.screen.blit(lb_text, lb_rect)

        # 操作说明
        instructions = [
            "方向键或 WASD 控制移动",
            "P 键暂停，R 键重新开始",
            "ESC 键退出"
        ]
        for i, inst in enumerate(instructions):
            inst_surface = self.font_small.render(inst, True, COLOR_TEXT)
            inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 280 + i * 30))
            self.screen.blit(inst_surface, inst_rect)

    def draw_pause(self):
        """绘制暂停界面"""
        # 使用模糊背景效果
        if self.effect_manager.blur_surface:
            self.screen.blit(self.effect_manager.blur_surface, (0, 0))
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render("游戏暂停", True, COLOR_TEXT)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)

        continue_text = self.font_small.render("按 P 键继续", True, COLOR_TEXT)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

    def draw_game_over(self):
        """绘制游戏结束界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        high_score = self.high_scores.get(self.selected_game_mode, 0)
        is_new_high_score = self.score >= high_score and self.score > 0

        game_over_text = self.font_large.render("游戏结束", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, game_over_rect)

        # 显示游戏模式
        mode_text = self.font_small.render(f"模式：{self.selected_game_mode}", True, GAME_MODES[self.selected_game_mode]["color"])
        mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(mode_text, mode_rect)

        score_text = self.font_medium.render(f"最终得分：{self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        if is_new_high_score:
            new_high_text = self.font_medium.render("新纪录！", True, (255, 215, 0))
            new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(new_high_text, new_high_rect)

        restart_text = self.font_small.render("按 R 键重新开始 或 点击按钮", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)

        # 重新开始按钮
        self.button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 110,
            200,
            50
        )
        mouse_pos = pygame.mouse.get_pos()
        button_color = COLOR_BUTTON_HOVER if self.button_rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=10)

        restart_btn_text = self.font_medium.render("重新开始", True, COLOR_TEXT)
        restart_btn_rect = restart_btn_text.get_rect(center=self.button_rect.center)
        self.screen.blit(restart_btn_text, restart_btn_rect)

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_l:
                        self.state = "LEADERBOARD"
                    elif event.key == pygame.K_ESCAPE:
                        return False

                elif self.state == "LEADERBOARD":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "PLAYING":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.change_direction(UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.change_direction(DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.change_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_p:
                        # 暂停前创建模糊背景
                        self.effect_manager.create_blur_surface(self.screen)
                        self.state = "PAUSED"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "PAUSED":
                    if event.key == pygame.K_p:
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # 检查游戏模式按钮点击
                if self.state == "MENU":
                    for btn_rect, mode_name in self.game_mode_buttons:
                        if btn_rect.collidepoint(mouse_pos):
                            self.selected_game_mode = mode_name
                            if self.sound_click:
                                self.sound_click.play()
                            break
                    # 检查难度按钮点击
                    for btn_rect, diff_name in self.difficulty_buttons:
                        if btn_rect.collidepoint(mouse_pos):
                            self.selected_difficulty = diff_name
                            if self.sound_click:
                                self.sound_click.play()
                            break
                    # 检查皮肤按钮点击
                    for btn_rect, skin_name in self.skin_buttons:
                        if btn_rect.collidepoint(mouse_pos):
                            self.selected_skin = skin_name
                            if self.sound_click:
                                self.sound_click.play()
                            break
                    # 检查开始按钮点击
                    if self.button_rect and self.button_rect.collidepoint(mouse_pos):
                        self.start_game()
                    # 检查排行榜按钮点击
                    if self.leaderboard_button and self.leaderboard_button.collidepoint(mouse_pos):
                        self.state = "LEADERBOARD"
                        if self.sound_click:
                            self.sound_click.play()
                elif self.state == "LEADERBOARD":
                    # 检查模式选择按钮
                    if hasattr(self, 'mode_buttons'):
                        for btn_rect, mode_name in self.mode_buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                self.leaderboard_mode = mode_name
                                if self.sound_click:
                                    self.sound_click.play()
                                break
                    # 检查返回按钮
                    if self.leaderboard_back_button and self.leaderboard_back_button.collidepoint(mouse_pos):
                        self.state = "MENU"
                        if self.sound_click:
                            self.sound_click.play()
                elif self.state == "GAME_OVER":
                    if self.button_rect and self.button_rect.collidepoint(mouse_pos):
                        self.start_game()

        return True

    def start_game(self):
        """开始新游戏"""
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.state = "PLAYING"
        # 根据难度设置 FPS
        global FPS
        FPS = DIFFICULTY_SETTINGS[self.selected_difficulty]["fps"]
        # 初始化限时模式计时器
        if self.selected_game_mode == "限时":
            self.time_limit = GAME_MODES["限时"]["time"]
            self.time_remaining = self.time_limit
            self.start_time = pygame.time.get_ticks()
        else:
            self.time_remaining = 0

    def update(self):
        """更新游戏状态"""
        if self.state != "PLAYING":
            return

        # 更新限时模式计时器
        if self.selected_game_mode == "限时":
            elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
            self.time_remaining = max(0, self.time_limit - elapsed)
            # 时间到，游戏结束
            if self.time_remaining <= 0:
                self.end_game()
                return

        self.snake.update()

        # 无尽模式：蛇穿墙
        if self.selected_game_mode == "无尽":
            self.snake.wrap_around()

        # 检测吃食物
        if self.snake.body[0] == self.food.position:
            self.snake.eat()
            self.score += 10
            if self.score > self.high_scores.get(self.selected_game_mode, 0):
                self.high_scores[self.selected_game_mode] = self.score
            self.food.spawn(self.snake.body)
            # 播放吃食物音效
            if self.sound_eat:
                self.sound_eat.play()

        # 检测碰撞（经典模式和限时模式）
        if self.snake.check_collision(self.selected_game_mode):
            # 播放撞墙音效
            if self.sound_crash:
                self.sound_crash.play()
            self.end_game()

    def end_game(self):
        """结束游戏"""
        # 保存最高分
        high_score = self.high_scores.get(self.selected_game_mode, 0)
        if self.score >= high_score and self.score > 0:
            self.high_scores[self.selected_game_mode] = self.score
        # 添加到排行榜
        self.add_to_leaderboard(self.selected_game_mode, self.score)
        save_game_data({"high_scores": self.high_scores, "leaderboards": self.leaderboards})
        self.state = "GAME_OVER"
        # 播放游戏结束音效
        if self.sound_gameover:
            self.sound_gameover.play()

    def add_to_leaderboard(self, mode, score):
        """添加分数到排行榜"""
        if score <= 0:
            return
        leaderboard = self.leaderboards.get(mode, [])
        # 添加新分数（包含日期）
        from datetime import datetime
        entry = {
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "difficulty": self.selected_difficulty
        }
        leaderboard.append(entry)
        # 按分数排序，保留前10名
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.leaderboards[mode] = leaderboard[:10]

    def draw_leaderboard(self):
        """绘制排行榜界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 标题
        title = self.font_large.render("排行榜", True, COLOR_SCORE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # 游戏模式选择按钮
        mode_buttons = []
        button_width = 100
        button_height = 35
        start_x = SCREEN_WIDTH // 2 - (len(GAME_MODES) * (button_width + 10)) // 2
        mouse_pos = pygame.mouse.get_pos()

        for i, (mode_name, settings) in enumerate(GAME_MODES.items()):
            btn_rect = pygame.Rect(
                start_x + i * (button_width + 10),
                90,
                button_width,
                button_height
            )
            mode_buttons.append((btn_rect, mode_name))
            btn_color = settings["color"]
            if self.leaderboard_mode == mode_name:
                btn_color = tuple(min(255, c + 50) for c in btn_color)
            elif btn_rect.collidepoint(mouse_pos):
                btn_color = tuple(min(255, c + 30) for c in btn_color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            mode_text = self.font_small.render(mode_name, True, COLOR_TEXT)
            text_rect = mode_text.get_rect(center=btn_rect.center)
            self.screen.blit(mode_text, text_rect)

        self.mode_buttons = mode_buttons

        # 显示排行榜
        leaderboard = self.leaderboards.get(self.leaderboard_mode, [])
        y_offset = 150

        # 表头
        header_text = self.font_small.render("排名    分数    难度    日期", True, COLOR_TEXT)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(header_text, header_rect)
        y_offset += 40

        # 分隔线
        pygame.draw.line(self.screen, COLOR_GRID, (50, y_offset - 10), (SCREEN_WIDTH - 50, y_offset - 10), 2)

        if not leaderboard:
            no_data_text = self.font_medium.render("暂无记录", True, COLOR_TEXT)
            no_data_rect = no_data_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 50))
            self.screen.blit(no_data_text, no_data_rect)
        else:
            for i, entry in enumerate(leaderboard[:LEADERBOARD_PAGE_SIZE]):
                # 排名颜色
                if i == 0:
                    rank_color = (255, 215, 0)  # 金色
                elif i == 1:
                    rank_color = (192, 192, 192)  # 银色
                elif i == 2:
                    rank_color = (205, 127, 50)  # 铜色
                else:
                    rank_color = COLOR_TEXT

                rank_text = f"  {i + 1}      {entry['score']}      {entry['difficulty']}      {entry['date']}"
                entry_surface = self.font_small.render(rank_text, True, rank_color)
                entry_rect = entry_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(entry_surface, entry_rect)
                y_offset += 35

        # 返回按钮
        self.leaderboard_back_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 80,
            SCREEN_HEIGHT - 80,
            160,
            45
        )
        button_color = COLOR_BUTTON_HOVER if self.leaderboard_back_button.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(self.screen, button_color, self.leaderboard_back_button, border_radius=10)

        back_text = self.font_medium.render("返回", True, COLOR_TEXT)
        back_rect = back_text.get_rect(center=self.leaderboard_back_button.center)
        self.screen.blit(back_text, back_rect)

    def draw(self):
        """绘制游戏画面"""
        self.draw_grid()
        self.draw_score()
        self.draw_food()
        self.draw_snake()

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "LEADERBOARD":
            self.draw_leaderboard()
        elif self.state == "PAUSED":
            self.draw_pause()
        elif self.state == "GAME_OVER":
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
