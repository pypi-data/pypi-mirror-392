import pygame


class Button:
    def __init__(self, window: pygame.Surface, x: int | float = None, y: int | float = None, w: int | float = None,
                 h: int | float = None, text: str = None,
                 font_name: str = 'kaiti', font_size: int = 20, font_color: str | tuple[int, int, int] = 'black',
                 background_color: str = 'white',
                 border_color: str = 'black',
                 border_width: int = 1, border_radius: int = 0, is_center: bool = True,
                 func: callable = None):
        """
        一个按钮类
        :param window: 传入的窗口
        :param x: 按钮的x位置
        :param y: 按钮的y位置
        :param w: 按钮的宽度
        :param h: 按钮的高度
        :param text: 按钮上的文字
        :param font_name: 字体名称
        :param font_size: 字体大小
        :param font_color: 字体颜色
        :param background_color: 按钮背景颜色,transparent表示透明
        :param border_color: 按钮边框颜色
        :param border_width: 按钮边框宽度
        :param border_radius: 按钮边框圆角半径
        :param is_center: 是否以x,y为中心点
        :param func: 按钮点击后的函数
        """
        self.window = window
        self.x = x or window.get_width() // 2
        self.y = y or window.get_height() // 2
        self.w = w or 150
        self.h = h or 50
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.background_color = background_color.lower() if type(background_color) is str else background_color  # 背景颜色
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.is_center = is_center
        self.func = func

        if self.is_center:
            self.x -= self.w // 2
            self.y -= self.h // 2

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.font = pygame.font.SysFont(self.font_name, self.font_size)

    def set_pos(self, x=None, y=None):
        x_none, y_none = x, y
        x = x or self.x
        y = y or self.y
        if self.is_center:
            if x_none:
                self.x = x - self.w // 2
            if y_none:
                self.y = y - self.h // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def click(self, mouse: tuple = None):
        """
        检查鼠标点击是否在按钮范围内
        """
        if mouse is None:
            mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            return self.__function()

    def __function(self):
        """点击按钮后的函数调用"""
        if self.func:
            return self.func()
        return True

    def draw(self, screen: pygame.Surface = None):
        """
        绘制按钮
        """
        if screen is None:
            screen = self.window
        if self.background_color != "transparent":  # 如果背景颜色不为透明，就绘制背景
            pygame.draw.rect(screen, self.background_color, self.rect, border_radius=self.border_radius)  # 绘制背景
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width,
                         border_radius=self.border_radius)  # 绘制边框

        if self.text:
            text_surf = self.font.render(self.text, True, self.font_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def suspension(self, mouse=None):
        """判断鼠标悬停"""
        return self.rect.collidepoint(mouse if mouse else pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.click(event.pos)

    def main(self, events):
        """
        主逻辑
        """
        for event in events:
            self.handle_event(event)
        self.draw()


__all__ = ["Button"]
