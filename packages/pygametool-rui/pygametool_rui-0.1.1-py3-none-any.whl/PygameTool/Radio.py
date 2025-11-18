import pygame
from PygameTool import Text


import pygame
import inspect


class Radio:
    queues = {}

    def __init__(self, window: pygame.Surface, x: int = None, y: int = None, size: int = 23,
                 is_center: bool = False, num_queue: int = 1, txt: str = "", text_offset: int = 10,
                 func: callable = None, **kwargs):
        """
        一个单选框类
        :param window: 传入的窗口
        :param x: 单选框的x位置
        :param y: 单选框的y位置
        :param size: 单选框的大小
        :param is_center: 是否以x,y为中心点
        :param num_queue: 单选框的队列，同一个队列内的单选框只能有一个选中
        :param txt: 单选框旁边的文字
        :param text_offset: 文字距离单选框的偏移量
        :param func: 要调用的函数
        :param kwargs: 传递给函数的关键字参数，当你需要调用点击事件后，会自动传入需要的全部参数,否则此项无效
            请你尽可能在编写功能函数的时候，不写kwargs之前的任何参数，如果有必要，你可以在handle函数当中接收**kwargs
        """
        self.window = window
        self.x = x
        self.y = y
        self.size = size
        self.is_center = is_center
        self.num_queue = num_queue
        self.is_selected = False
        self.text_offset = text_offset

        self.func = func
        self.kwargs = kwargs

        if self.is_center:
            self.x -= self.size // 2
            self.y -= self.size // 2

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.inner_circle_radius = self.size // 4
        self.text = Text(txt, self.x + self.size + self.text_offset, self.y, is_center=is_center)

        # Add this radio button to the appropriate queue
        if num_queue not in Radio.queues:
            Radio.queues[num_queue] = []
        Radio.queues[num_queue].append(self)

    def draw(self, window: pygame.Surface = None):
        if not window:
            window = self.window
        pygame.draw.circle(window, (0, 0, 0), (self.x + self.size // 2, self.y + self.size // 2), self.size // 2, 2)
        if self.is_selected:
            pygame.draw.circle(window, (0, 0, 0), (self.x + self.size // 2, self.y + self.size // 2),
                               self.inner_circle_radius)
        self.text.pos(self.x + self.size + self.text_offset, self.y)
        self.text.draw(window)

    def handle_event(self, _event, **kwargs):
        if not kwargs:  # 如果没有传递kwargs，那么使用self.kwargs
            kwargs = self.kwargs
        if _event.type == pygame.MOUSEBUTTONDOWN and _event.button == 1:
            if self.rect.collidepoint(_event.pos):
                if self.func:
                    # 筛选kwargs，使其仅包含self.func接受的参数
                    sig = inspect.signature(self.func)
                    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
                        # 如果func接受**kwargs，则传递所有kwargs
                        self.func(**kwargs)
                    else:
                        accepted_params = sig.parameters.keys()
                        filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_params}
                        self.func(**filtered_kwargs)
                self.select()
                return "click"  # 如果点击了单选框，则返回"click"

    def select(self):
        # Deselect all other radio buttons in the same queue
        for radio in Radio.queues[self.num_queue]:
            radio.is_selected = False
        self.is_selected = True


class SelectionBox:
    def __init__(self, window: pygame.Surface, x: int | float = None, y: int | float = None, size: int = 20,
                 is_center: bool = True, style: str = "circle"):
        """
        一个选择框类
        :param window: 传入的窗口
        :param x: 选择框的x位置
        :param y: 选择框的y位置
        :param size: 选择框的大小
        :param is_center: 是否以x,y为中心点
        :param style: 选择框的样式，目前支持circle和triangle以及rectangle
        """
        self.window = window
        self.x = x
        self.y = y
        self.size = size
        self.is_center = is_center
        self.style = style
        self.is_selected = False

        if self.is_center:
            self.x -= self.size // 2
            self.y -= self.size // 2

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self):
        if self.style == "rectangle":
            pygame.draw.rect(self.window, (0, 0, 0), self.rect, 2)
            if self.is_selected:
                pygame.draw.rect(self.window, (0, 0, 0),
                                 (self.x + self.size // 4, self.y + self.size // 4, self.size // 2, self.size // 2))
        elif self.style == "triangle":
            points = [(self.x + self.size // 2, self.y), (self.x + self.size, self.y + self.size),
                      (self.x, self.y + self.size)]
            pygame.draw.polygon(self.window, (0, 0, 0), points, 2)
            if self.is_selected:
                inner_points = [(self.x + self.size // 2, self.y + self.size // 4),
                                (self.x + self.size * 3 // 4, self.y + self.size * 3 // 4),
                                (self.x + self.size // 4, self.y + self.size * 3 // 4)]
                pygame.draw.polygon(self.window, (0, 0, 0), inner_points)
        else:  # 默认样式为圆形，如果传入的样式系统不能正确的识别，则默认为圆形
            pygame.draw.circle(self.window, (0, 0, 0), (self.x + self.size // 2, self.y + self.size // 2),
                               self.size // 2, 2)
            if self.is_selected:
                pygame.draw.circle(self.window, (0, 0, 0), (self.x + self.size // 2, self.y + self.size // 2),
                                   self.size // 4)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.is_selected:
                    self.deselect()
                else:
                    self.select()

    def select(self):
        self.is_selected = True
        self.on_select()

    def deselect(self):
        self.is_selected = False
        self.on_deselect()

    def on_select(self):
        """这里写选择时的代码，在类创建的时候，需要自己手动重写，这里只提供一个空方法"""

    def on_deselect(self):
        """这里写取消选择时的代码, 在类创建的时候，需要自己手动重写，这里只提供一个空方法"""


__all__ = ["Radio", "SelectionBox"]
