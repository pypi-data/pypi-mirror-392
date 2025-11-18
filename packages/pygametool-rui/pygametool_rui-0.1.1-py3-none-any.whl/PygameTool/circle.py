import pygame

# 假设 hex_to_rgb 和相关字典都在此导入
from PygameTool.functool import hex_to_rgb


class Circle:
    def __init__(self, x: int | float = None, y: int | float = None, r: int | float = None, width: int | float = 1,
                 color: str | tuple[int | float, int | float, int | float] = "black",
                 fillColor: str | tuple[int | float, int | float, int | float] | None = None):
        self.x = x or 100
        self.y = y or 100
        self.radius = r or 100
        self.width = width
        self.color = self.process_color(color)
        self.fillColor = self.process_color(fillColor) if fillColor else None

    @staticmethod
    def process_color(color):
        if color is None:
            return None  # 如果颜色没有指定，则返回 None
        rgb_color = hex_to_rgb(color)
        if isinstance(rgb_color, tuple) and len(rgb_color) == 3:
            return rgb_color
        else:
            raise ValueError("颜色格式不正确或无法识别")

    def draw(self, surface: pygame.Surface):
        # 如果 fillColor 被指定，则先填充圆形
        if self.fillColor:
            pygame.draw.circle(
                surface,
                self.fillColor,
                (int(self.x), int(self.y)),
                int(self.radius),
                0  # 0 表示填充整个圆
            )
        # 绘制圆形的边缘
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            int(self.radius),
            int(self.width)
        )
