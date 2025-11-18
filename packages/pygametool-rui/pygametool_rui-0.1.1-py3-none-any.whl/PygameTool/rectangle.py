import pygame
import PygameTool.functool


class Rectangle:
    def __init__(self, x: float = None, y: float = None, w: float = None, h: float = None, fillet: int = 0,
                 color: tuple[int, int, int] | str = (0, 0, 0), is_center: bool = True):
        """
        一个矩形类，用于绘制矩形
        :param x: 矩形的X坐标，如果is_center为True，就以中心点为准
        :param y: 矩形的Y坐标，如果is_center为True，就以中心点为准
        :param w: 矩形的宽度
        :param h: 矩形的高度
        :param fillet: 矩形的圆角半径，如果为0，就是直角矩形
        :param color: 矩形的颜色，可传入颜色或者RGB元组
        :param is_center: 是否以中心点为准
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fillet = fillet
        self.color = PygameTool.functool.hex_to_rgb(color)
        self.is_center = is_center

        # 如果is_center为True，则矩形中心的坐标为(x, y)
        if is_center:
            self.rect_x = x - w / 2
            self.rect_y = y - h / 2
            self.rect_center = (x, y)
        else:
            self.rect_x = x
            self.rect_y = y
            self.rect_center = (x + w / 2, y + h / 2)  # 矩形的中心坐标

        self.__update_rect()

    def __update_rect(self):
        """更新矩形的位置，包括大小变化或者颜色等变化，都会调用这个方法"""
        if self.is_center:  # 如果is_center为True，则矩形中心的坐标为(x, y)
            self.rect_x = self.x - self.w / 2
            self.rect_y = self.y - self.h / 2
        else:
            self.rect_x = self.x
            self.rect_y = self.y

        self.pygame_rect = pygame.Rect(self.rect_x, self.rect_y, self.w, self.h)  # 生成一个矩形对象

    def change_pos(self, x=None, y=None):
        """
        改变矩形的位置
        :param x: 传入X坐标，如果x为None，就不改变
        :param y: 传入Y坐标，如果y为None，就不改变
        :return: None
        """
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.__update_rect()

    def change_size(self, size=None):
        """更改矩形的大小，如果传入的是一个浮点数，就是缩放比例，如果传入的是一个元组，就是宽和高"""
        if size is not None:
            if isinstance(size, float) or isinstance(size, int):
                self.w *= size
                self.h *= size
            elif isinstance(size, tuple) and len(size) == 2:
                self.w, self.h = size
        self.__update_rect()

    def change_color(self, color: tuple[int, int, int] | str = (0, 0, 0)):
        """更改矩形的颜色,如果不传入颜色，就不改变"""
        if color is not None:
            self.color = PygameTool.functool.hex_to_rgb(color)
        self.__update_rect()

    def change_fillet(self, fillet: int = None):
        """更改矩形的圆角半径，如果不传入圆角半径，就不改变"""
        if fillet is not None:
            self.fillet = fillet
        self.__update_rect()

    def change_alpha(self, alpha: int = None):
        if alpha is not None:
            self.color = (self.color[0], self.color[1], self.color[2], alpha)
        self.__update_rect()

    def hover(self) -> bool:
        """判断鼠标是否在矩形内"""
        return pygame.Rect.collidepoint(self.pygame_rect, pygame.mouse.get_pos())

    def draw(self, window: pygame.surface):
        """绘制矩形,如果圆角半径为0，就是直角矩形"""
        if self.fillet > 0:
            pygame.draw.rect(window, self.color, self.pygame_rect, border_radius=self.fillet)
        else:
            pygame.draw.rect(window, self.color, self.pygame_rect)

    def stroke(self, window, color: tuple = None, width: int = 1):
        """绘制矩形的边框"""
        if color is None:
            color = self.color
        if self.fillet > 0:
            pygame.draw.rect(window, color, self.pygame_rect, width, border_radius=self.fillet)
        else:
            pygame.draw.rect(window, color, self.pygame_rect, width)


def rectangle_mask(image: pygame.Surface, rectangle: Rectangle) -> pygame.Surface:
    # 创建一个与图片大小相同的透明遮罩表面
    mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    # 使用Rectangle类绘制遮罩
    rectangle.draw(mask)
    # 将遮罩转换为仅包含alpha通道的黑白图
    mask_alpha = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    mask_alpha.fill((0, 0, 0, 0))  # 全透明
    # 将白色区域（遮罩区域）转换为白色不透明，其他区域保持透明
    for y in range(mask.get_height()):
        for x in range(mask.get_width()):
            color = mask.get_at((x, y))
            if color[:3] == rectangle.color[:3]:  # 判断颜色是否匹配
                mask_alpha.set_at((x, y), (255, 255, 255, 255))
    # 应用遮罩
    masked_image = image.copy()
    masked_image.blit(mask_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return masked_image


__all__ = ["Rectangle", "rectangle_mask"]
