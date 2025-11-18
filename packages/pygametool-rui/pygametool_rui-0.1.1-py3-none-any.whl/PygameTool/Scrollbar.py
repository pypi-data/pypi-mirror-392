import pygame
from PygameTool import functool


class Scrollbar:
    @functool.filter_kwargs  # 过滤掉不需要的参数，只要有用的参数
    def __init__(self, screen: pygame.Surface, x: int = 0, y: int = 0, width: int = None, height: int = None,
                 scrollBarColor=None, sliderColor=None):
        """
        滚动条
        :param screen: 传入绘图表面
        :param x: 传入滚动条位置x
        :param y: 传入滚动条位置y
        :param width: 传入滚动条宽度，不写默认10
        :param height: 传入滚动条高度，不写默认100
        :param scrollBarColor: 传入滚动条颜色，不写或不能识别默认橙色，可传入字符串，或者RGB元组，同时也可以传入中文颜色名(支持少量中文)
        :param sliderColor: 传入滑块颜色，不写或不能识别默认橙色，可传入字符串，或者RGB元组，同时也可以传入中文颜色名(支持少量中文)
        """
        self.screen = screen
        self.width = width or 10
        self.height = height or 100
        self.position = (x, y)
        self.scrollBarColor = functool.hex_to_rgb(scrollBarColor) if scrollBarColor else (200, 200, 200)
        self.sliderColor = functool.hex_to_rgb(sliderColor) if sliderColor else (150, 150, 150)

        self.scroll = 0
        self.bar_height = height  # 初始滑块高度等于滚动条总高度
        self.dragging = False

    def update(self, content_height, container_height):
        """ 更新滚动条的滑块高度，基于内容高度和容器高度 """
        if content_height > container_height:
            # 如果内容高度大于容器高度，计算滑块的高度
            self.bar_height = max(30, container_height * (container_height / content_height))
        else:
            # 如果内容没有超出容器，滑块高度与滚动条高度一致
            self.bar_height = self.height

    def handle_event(self, event):
        """ 处理输入事件，调整滚动位置 """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if (self.position[0] <= event.pos[0] <= self.position[0] + self.width and
                        self.position[1] + self.scroll <= event.pos[1] <= self.position[1] + self.scroll +
                        self.bar_height):
                    self.dragging = True
            elif event.button == 4:
                self.scroll = max(self.scroll - 10, 0)
            elif event.button == 5:
                self.scroll = min(self.scroll + 10, self.height - self.bar_height)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.scroll = min(max(event.pos[1] - self.position[1] - self.bar_height // 2, 0),
                              self.height - self.bar_height)

    def draw(self, screen: pygame.Surface):
        if self.height > self.bar_height:  # 仅当滑块高度小于滚动条高度时绘制
            pygame.draw.rect(screen, self.scrollBarColor, (self.position[0], self.position[1], self.width, self.height))
            pygame.draw.rect(screen, self.sliderColor, (self.position[0], self.position[1] + self.scroll, self.width,
                                                        self.bar_height))

    def get_scroll(self):
        """ 获取当前滚动的比例 """
        if self.height - self.bar_height > 0:
            return self.scroll / (self.height - self.bar_height)
        return 0


class ScrollableArea:
    def __init__(self, screen, x=0, y=0, width=None, height=None, **kwargs):
        self.screen = screen
        self.position = (x, y)
        self.width = width or 300
        self.height = height or 600
        self.content = []
        self.scrollbar = Scrollbar(screen, self.position[0] + self.width, self.position[1], 20, self.height, **kwargs)

    def add_sprite(self, sprite):
        if (not hasattr(sprite, 'x') or not hasattr(sprite, 'y') or not hasattr(sprite, 'w') or not hasattr(sprite, 'h') or
                not hasattr(sprite, "draw")):
            print('添加失败，请确保精灵类有x、y、w、h属性以及draw方法！')
            return False
        self.content.append(sprite)
        self.update_scrollbar()  # 更新滚动条状态

    def count_content_height(self):
        MaxH = 0
        for sprite in self.content:
            MaxH = max(MaxH, sprite.y + sprite.h)
        return MaxH

    def update_scrollbar(self):
        content_height = self.count_content_height()
        self.scrollbar.update(content_height, self.height)

    def handle_event(self, event):
        self.scrollbar.handle_event(event)

    def draw(self):
        """ 绘制滚动区域和所有内容 """
        self.screen.set_clip(pygame.Rect(self.position, (self.width, self.height)))  # 限制绘图区域
        scroll_offset = self.scrollbar.get_scroll() * (self.count_content_height() - self.height)
        for sprite in self.content:
            original_y = sprite.y  # 保存原始y位置
            sprite.y -= scroll_offset  # 调整y位置根据滚动
            sprite.draw(self.screen)  # 调用sprite的draw方法，该方法应处理sprite的x和y
            sprite.y = original_y  # 恢复原始y位置
        self.screen.set_clip(None)  # 移除绘图限制
        self.scrollbar.draw()  # 绘制滚动条


__all__ = ["ScrollableArea"]
