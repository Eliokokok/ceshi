import pygame
import random
import math
import os

# 初始化 Pygame
pygame.init()

# 颜色定义（调整为更柔和的颜色）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (78, 201, 176)  # 柔和的青色
YELLOW = (242, 201, 76)  # 柔和的黄色
MAGENTA = (184, 61, 186)  # 柔和的品红
RED = (217, 87, 99)  # 柔和的红色
GREEN = (89, 196, 114)  # 柔和的绿色
BLUE = (69, 177, 232)  # 柔和的蓝色
ORANGE = (239, 149, 72)  # 柔和的橙色
BACKGROUND = (40, 44, 52)  # 深色背景

# 游戏设置
BLOCK_SIZE = 30  # 每个方块的大小
GRID_WIDTH = 10  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 20  # 游戏区域高度（以方块数计）

# 计算实际窗口大小
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # 额外空间用于显示下一个方块和分数
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

# 初始化字体
try:
    # 尝试加载思源黑体
    font_path = "C:\\Windows\\Fonts\\SourceHanSansSC-Regular.otf"  # Windows 默认字体路径
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\SourceHanSansCN-Regular.otf"  # 备选路径
    font = pygame.font.Font(font_path, 24)
except:
    # 如果找不到思源黑体，使用系统默认字体
    font = pygame.font.SysFont("microsoft yahei", 24)

# 游戏状态
score = 0
level = 1
lines_cleared = 0
paused = False

# 方块形状定义
SHAPES = {
    'I': [(0, 0), (-1, 0), (1, 0), (2, 0)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, 1)],
    'L': [(0, 0), (-1, 0), (1, 0), (1, 1)],
    'J': [(0, 0), (-1, 0), (1, 0), (-1, 1)],
    'S': [(0, 0), (-1, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (1, 0), (0, 1), (-1, 1)]
}

# 创建游戏网格（使用新的背景色）
grid = [[BACKGROUND for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


class Block:
    def __init__(self):
        self.shape = random.choice(list(SHAPES.keys()))
        self.color = random.choice([CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE])
        self.x = GRID_WIDTH // 2
        self.y = 0
        self.rotation = 0

    def rotate(self):
        # 保存当前位置，以便碰撞检测失败时恢复
        old_rotation = self.rotation

        # 更新旋转状态
        self.rotation = (self.rotation + 1) % 4

        # 如果发生碰撞，恢复原来的旋转状态
        if self.check_collision():
            self.rotation = old_rotation

    def get_rotated_coords(self):
        shape_coords = SHAPES[self.shape]
        if self.shape == 'O':  # O形方块不需要旋转
            return shape_coords

        rotated = []
        for x, y in shape_coords:
            # 旋转公式
            if self.rotation == 0:
                rotated.append((x, y))
            elif self.rotation == 1:
                rotated.append((-y, x))
            elif self.rotation == 2:
                rotated.append((-x, -y))
            else:  # rotation == 3
                rotated.append((y, -x))
        return rotated

    def draw(self):
        shape_coords = self.get_rotated_coords()
        for x, y in shape_coords:
            pos_x = (self.x + x) * BLOCK_SIZE
            pos_y = (self.y + y) * BLOCK_SIZE
            pygame.draw.rect(screen, self.color,
                             (pos_x, pos_y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def check_collision(self):
        shape_coords = self.get_rotated_coords()
        for x, y in shape_coords:
            new_x = self.x + x
            new_y = self.y + y
            if (new_x < 0 or new_x >= GRID_WIDTH or
                    new_y >= GRID_HEIGHT or
                    (new_y >= 0 and grid[new_y][new_x] != BACKGROUND)):
                return True
        return False

    def drop_to_bottom(self):
        """让方块直接落到底部"""
        while not self.check_collision():
            self.y += 1
        self.y -= 1  # 回退一步，因为最后一次移动导致了碰撞
        new_block()


def new_block():
    global current_block, score
    # 将当前方块固定到网格中
    shape_coords = current_block.get_rotated_coords()
    for x, y in shape_coords:
        grid_y = current_block.y + y
        grid_x = current_block.x + x
        if grid_y >= 0:
            grid[grid_y][grid_x] = current_block.color

    # 检查消行
    lines = check_lines()
    if lines > 0:
        score += (lines * 100) * level  # 根据消除的行数和当前等级计算分数
        update_level()

    # 创建新方块
    current_block = Block()
    if current_block.check_collision():
        global running
        running = False


def check_lines():
    lines_cleared = 0
    for y in range(GRID_HEIGHT):
        if all(color != BACKGROUND for color in grid[y]):
            del grid[y]
            grid.insert(0, [BACKGROUND for _ in range(GRID_WIDTH)])
            lines_cleared += 1
    return lines_cleared


def update_level():
    global level, lines_cleared, fall_speed
    lines_cleared += 1
    if lines_cleared >= level * 10:
        level += 1
        fall_speed = max(100, 1000 - (level - 1) * 100)  # 随等级提高加快下落速度


def draw_grid():
    # 绘制游戏区域背景
    pygame.draw.rect(screen, BACKGROUND,
                     (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))

    # 绘制边框
    pygame.draw.rect(screen, WHITE,
                     (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

    # 绘制网格内容
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != BACKGROUND:
                pygame.draw.rect(screen, grid[y][x],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                  BLOCK_SIZE - 1, BLOCK_SIZE - 1))


def draw_score():
    # 绘制分数面板背景
    panel_x = GRID_WIDTH * BLOCK_SIZE + 10
    panel_y = 30
    panel_width = SCREEN_WIDTH - panel_x - 10
    panel_height = 200
    pygame.draw.rect(screen, BACKGROUND,
                     (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE,
                     (panel_x, panel_y, panel_width, panel_height), 2)

    # 绘制文字（使用新字体）
    score_text = font.render(f'分数: {score}', True, WHITE)
    level_text = font.render(f'等级: {level}', True, WHITE)
    lines_text = font.render(f'消除: {lines_cleared}', True, WHITE)

    screen.blit(score_text, (panel_x + 20, panel_y + 20))
    screen.blit(level_text, (panel_x + 20, panel_y + 60))
    screen.blit(lines_text, (panel_x + 20, panel_y + 100))

    if paused:
        pause_text = font.render('已暂停', True, WHITE)
        screen.blit(pause_text, (panel_x + 20, panel_y + 140))


# 创建当前方块
current_block = Block()

# 游戏主循环
clock = pygame.time.Clock()
running = True
fall_time = 0
fall_speed = 1000  # 下落速度（毫秒）

while running:
    if not paused:
        # 计算下落时间
        fall_time += clock.get_rawtime()
        clock.tick()

        # 自动下落
        if fall_time >= fall_speed:
            current_block.y += 1
            if current_block.check_collision():
                current_block.y -= 1
                new_block()
            fall_time = 0

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # P键暂停
                paused = not paused
            if not paused:  # 只有在非暂停状态才处理其他按键
                if event.key == pygame.K_LEFT:
                    current_block.x -= 1
                    if current_block.check_collision():
                        current_block.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_block.x += 1
                    if current_block.check_collision():
                        current_block.x -= 1
                elif event.key == pygame.K_DOWN:  # 修改下方向键行为
                    current_block.drop_to_bottom()
                elif event.key == pygame.K_UP:
                    current_block.rotate()

    # 清空屏幕
    screen.fill(BACKGROUND)

    # 绘制游戏元素
    draw_grid()
    current_block.draw()
    draw_score()

    # 更新显示
    pygame.display.flip()

# 退出游戏
pygame.quit()
