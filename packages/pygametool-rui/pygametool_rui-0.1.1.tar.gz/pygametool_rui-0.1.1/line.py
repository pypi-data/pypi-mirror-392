import pygame
from PygameTool.functool import hex_to_rgb


class Line:
    def __init__(self, x1: int | float = 0, y1: int | float = 100, x2: int | float = 100, y2: int | float = 100,
                 width: int | float = 1,
                 color: str | tuple[int | float, int | float, int | float] = "orange"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.color = self.process_color(color)

    @staticmethod
    def process_color(color):
        # 使用 hex_to_rgb 函数处理颜色输入
        rgb_color = hex_to_rgb(color)
        if isinstance(rgb_color, tuple) and len(rgb_color) == 3:
            return rgb_color
        else:
            raise ValueError("颜色格式不正确或无法识别")

    def draw(self, surface: pygame.Surface):
        pygame.draw.line(
            surface,
            self.color,
            (int(self.x1), int(self.y1)),
            (int(self.x2), int(self.y2)),
            int(self.width)
        )


__all__ = ["Line"]
