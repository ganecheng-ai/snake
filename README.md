# 贪吃蛇游戏 (Snake Game)

一个使用 Python 和 Pygame 开发的经典贪吃蛇游戏，支持简体中文界面。

## 功能特性

- 🎮 经典贪吃蛇游戏玩法
- 🖥️ 精美的游戏画面
- 🇨🇳 简体中文界面支持
- 🏆 计分系统和最高分持久化保存
- ⌨️ 流畅的键盘控制
- 💾 自动保存最高分记录
- 🔊 音效支持（吃食物、撞墙、游戏结束音效）
- 🎚️ 三种难度等级可选（简单、中等、困难）
- ✨ 食物脉冲动画特效

## 系统要求

- Python 3.8+
- Pygame 2.0+

## 安装和运行

### 从源码运行

```bash
# 安装依赖
pip install pygame

# 运行游戏
python game/snake_game.py
```

### 下载可执行文件

访问 [Releases](https://github.com/ganecheng-ai/snake/releases) 页面下载适合你操作系统的版本：
- Windows: `.exe` 文件
- Linux: `.tar.gz` 或 `.AppImage`
- macOS: `.dmg` 文件

## 游戏操作

| 按键 | 功能 |
|------|------|
| ↑ / W | 向上移动 |
| ↓ / S | 向下移动 |
| ← / A | 向左移动 |
| → / D | 向右移动 |
| P | 暂停/继续 |
| R | 重新开始 |
| ESC | 退出游戏 |

## 难度选择

在游戏主菜单可以选择难度：

| 难度 | 速度 | 适合人群 |
|------|------|----------|
| 简单 | 慢速 | 新手玩家 |
| 中等 | 正常 | 普通玩家 |
| 困难 | 快速 | 挑战玩家 |

## 游戏规则

1. 控制蛇移动吃到食物
2. 每吃一个食物，蛇身增长一节
3. 撞到墙壁或自身则游戏结束
4. 尽可能获得更高的分数

## 开发

### 本地开发

```bash
git clone git@github.com:ganecheng-ai/snake.git
cd snake
pip install pygame
python game/snake_game.py
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
