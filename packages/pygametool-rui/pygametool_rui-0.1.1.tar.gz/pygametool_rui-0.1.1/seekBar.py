import pygame
from PygameTool import text


class SeekBar:
    def __init__(self, x: int = None, y: int = None, w: int = None, h: int = None,
                 color: tuple | str = "DeepSkyBlue", circle_color: tuple | str = "Cyan",
                 air_color: tuple | str = "LightCyan",
                 Min: int = 0, Max: int = 100, value: int = None, radius: int = 4, **kwargs):
        """
        一个拖动条类
        :param x: 拖动条左上角的x坐标
        :param y: 拖动条左上角的y坐标
        :param w: 拖动条的宽度
        :param h: 拖动条的高度
        :param color: 拖动条的颜色，如1 - 100，值为50，将前面的50设为color颜色，后面的50不填色
        :param circle_color: 拖动条的圆点的颜色
        :param air_color: 拖动条的空白区域的颜色
        :param Min: 拖动条的最小值
        :param Max: 拖动条的最大值
        :param value: 拖动条的值，默认为(Min + Max) // 2
        :param radius: 拖动条的圆点的半径
        :param kwargs: Text类的参数，用于绘制拖动条的值
        """
        self.x = x or 100  # 默认值
        self.y = y or 100
        self.w = w or 200
        self.h = h or 10
        self.color = color
        self.circle_color = circle_color
        self.air_color = air_color
        self.Min = Min
        self.Max = Max
        self.radius = radius
        self.value = value or (Min + Max) // 2  # 初始值为中间值
        # Text会自动过滤不需要的，不能使用的参数
        self.value_draw = text.Text(self.value, self.x + self.w + 7, self.y - self.h / 2, **kwargs)
        self.dragging = False  # 是否正在拖动

    def set_pos(self, x: int | float = None, y: int | float = None, centerX: bool = False, centerY: bool = False):
        """设置位置(左上角)"""
        self.x = x or self.x
        self.y = y or self.y
        if centerX:  # 如果要居中，那么将进行位置调整
            self.x = self.x - self.w / 2
        if centerY:  # 如果要居中，那么将进行位置调整
            self.y = self.y - self.h / 2
        self.value_draw.pos(self.x + self.w + 7, self.y - self.h / 2)
        self.value_draw.change_text(self.value)

    def handle_event(self, event: pygame.event.Event):
        """
        处理事件，例如鼠标点击和拖动
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_x, mouse_y = event.pos
                if self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h:
                    self.dragging = True  # 开始拖动
                    self.update_value(mouse_x)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False  # 停止拖动

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                self.update_value(mouse_x)

    def update_value(self, mouse_x):
        """
        根据鼠标位置更新值
        """
        relative_x = mouse_x - self.x
        if relative_x < 0:
            relative_x = 0
        elif relative_x > self.w:
            relative_x = self.w
        self.value = int(self.Min + (relative_x / self.w) * (self.Max - self.Min))
        self.value_draw.pos(self.x + self.w + 7, self.y - self.h / 2)
        self.value_draw.change_text(self.value)

    def draw(self, window: pygame.Surface):
        """
        绘制拖动条
        """
        # 绘制圆角背景条
        pygame.draw.rect(window, self.air_color, (self.x, self.y, self.w, self.h), border_radius=self.radius)

        # 绘制圆角前景条（已拖动的部分）
        filled_width = int((self.value - self.Min) / (self.Max - self.Min) * self.w)
        if filled_width > 0:  # 确保我们有东西可以绘制
            pygame.draw.rect(window, self.color, (self.x, self.y, filled_width, self.h), border_radius=self.radius)

        # 绘制圆圈（小圆）和值文本
        circle_center = (self.x + filled_width, self.y + self.h // 2)
        pygame.draw.circle(window, self.circle_color, circle_center, self.h // 2 + 4)
        self.value_draw.draw(window)


__all__ = ["SeekBar"]
