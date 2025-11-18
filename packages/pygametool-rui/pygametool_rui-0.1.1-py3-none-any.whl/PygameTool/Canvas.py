import pygame


class Canvas:
    """
    画布类，用于管理屏幕上的精灵和文本，并处理滚动功能。
    可以设置画布的位置和大小，并在内容超出画布高度时启用滚动条。
    支持多个画布实例，只有被点击的画布才会响应鼠标滚轮事件进行滚动。
    """
    # 类变量，用于跟踪当前激活的画布实例
    active_canvas = None

    def __init__(self, screen: pygame.Surface, x: float = 0, y: float = 0, w: float = None, h: float = None, speed: float = 20):
        """
        初始化画布
        :param screen: Pygame 的主屏幕 Surface 对象
        :param x: 画布左上角的 X 坐标，默认为 0
        :param y: 画布左上角的 Y 坐标，默认为 0
        :param w: 画布的宽度，如果不提供，则使用屏幕的宽度
        :param h: 画布的高度，如果不提供，则使用屏幕的高度
        :param speed: 滚动速度，默认为 20
        """
        self.screen = screen  # 主屏幕 Surface
        self.x = int(x)  # 画布左上角的 X 坐标
        self.y = int(y)  # 画布左上角的 Y 坐标
        self.w = int(w) if w is not None else screen.get_width()  # 画布宽度
        self.h = int(h) if h is not None else screen.get_height()  # 画布高度
        self.speed = speed  # 滚动速度

        self.element = []  # 元素列表，可以是精灵或文本
        self.dropdown_elements = []  # 下拉列表元素
        self.elements = []  # 储存全部的元素
        self.scroll_offset = 0  # 当前滚动偏移量
        self.max_height = 0  # 内容的最大高度

        self.scroll_enabled = False  # 是否启用滚动
        self.max_scroll = 0  # 最大滚动偏移量

    def addSprite(self, sprite):
        """
        添加一个精灵或文本到画布中，并更新滚动范围。
        :param sprite: 要添加的精灵或文本对象
        """
        # 判断是否为下拉列表元素
        if hasattr(sprite, 'is_open') and hasattr(sprite, 'selected_index'):
            self.dropdown_elements.append(sprite)
        else:
            self.element.append(sprite)

        # 存储元素的原始 y 坐标，以便在滚动时调整
        sprite.orig_y = int(sprite.y)
        if hasattr(sprite, 'rect'):
            sprite.orig_rect_y = int(sprite.rect.y)
        else:
            sprite.orig_rect_y = None

        # 更新内容的最大高度
        if hasattr(sprite, 'h'):
            sprite_bottom = sprite.y + sprite.h
        else:
            sprite_bottom = sprite.y

        sprite_bottom = int(sprite_bottom)
        if sprite_bottom > self.max_height:
            self.max_height = sprite_bottom

        # 计算内容高度相对于画布的位置
        content_height = self.max_height - self.y

        # 检查是否需要启用滚动
        if content_height > self.h:
            self.scroll_enabled = True
            self.max_scroll = content_height - self.h  # 最大滚动偏移量
        else:
            self.scroll_enabled = False
            self.max_scroll = 0

        # 更新
        self.elements = self.element + self.dropdown_elements  # 更新全部的元素

    def handle_event(self, event):
        """
        处理 Pygame 事件，包括鼠标点击和滚轮事件。
        只有当画布被点击后，才会响应鼠标滚轮事件进行滚动。
        :param event: Pygame 事件
        """
        # 先处理下拉列表的事件，确保它们能够正常响应
        for dropdown in self.elements:
            if hasattr(dropdown, 'handle_event'):
                dropdown.handle_event(event)

        # 处理鼠标点击事件，以确定激活的画布
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # 检查鼠标点击是否在当前画布区域内
            if self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h:
                Canvas.active_canvas = self  # 设置当前画布为激活状态
            else:
                # 如果点击不在当前画布区域，且当前画布是激活状态，则取消激活
                if Canvas.active_canvas == self:
                    Canvas.active_canvas = None

        # 仅当当前画布是激活状态时，处理滚轮事件
        if self.scroll_enabled and Canvas.active_canvas == self:
            if event.type == pygame.MOUSEWHEEL:
                # 确认鼠标指针在画布区域内
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if not (self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h):
                    return  # 如果鼠标不在画布区域内，忽略滚轮事件

                # 计算滚动的差值
                # event.y > 0 表示滚轮向上滚动，内容向下移动，scroll_offset 减少
                # event.y < 0 表示滚轮向下滚动，内容向上移动，scroll_offset 增加
                delta_scroll = int(-event.y * self.speed)  # 反方向

                # 计算新的滚动偏移量，限制在 0 和 max_scroll 之间
                new_scroll_offset = self.scroll_offset + delta_scroll

                # 限制 scroll_offset
                if new_scroll_offset < 0:
                    new_scroll_offset = 0
                elif new_scroll_offset > self.max_scroll:
                    new_scroll_offset = self.max_scroll

                # 计算实际 delta_scroll after clamping
                delta_scroll = new_scroll_offset - self.scroll_offset
                self.scroll_offset = new_scroll_offset

                # 调整所有元素的位置
                all_elements = self.element + self.dropdown_elements
                for element in all_elements:
                    # 根据 delta_scroll 更新元素的 y 坐标
                    # 滚动向上（scroll_offset 增加）时，元素 y 需要减小
                    # 滚动向下（scroll_offset 减少）时，元素 y 需要增加
                    element.y = element.orig_y - self.scroll_offset
                    if hasattr(element, 'rect') and element.rect is not None:
                        element.rect.y = element.orig_rect_y - self.scroll_offset
                    if hasattr(element, "pos"):  # 对于有 pos 方法的元素（如 Text 类），调用 pos 更新位置
                        element.pos()

    def draw(self):
        """
        绘制画布上的所有元素（精灵和文本等元素）。
        只绘制在画布区域内的部分。
        先绘制普通元素，再绘制下拉列表元素，确保下拉列表在最上层。
        """
        # 保存当前的剪裁区域
        previous_clip = self.screen.get_clip()

        # 设置新的剪裁区域为画布的区域
        canvas_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.screen.set_clip(canvas_rect)

        # 先绘制普通元素
        for element in self.element:
            element.draw(self.screen)  # 元素的 draw 方法应根据其当前的 x, y 位置绘制

        # 恢复之前的剪裁区域，让下拉列表可以超出画布范围
        self.screen.set_clip(previous_clip)

        # 再绘制下拉列表元素，确保它们在最上层且不受画布剪裁限制
        for element in self.dropdown_elements:
            element.draw(self.screen)

    def set_position(self, x: float, y: float):
        """
        设置画布的位置。
        :param x: 画布左上角的新的 X 坐标
        :param y: 画布左上角的新的 Y 坐标
        """
        # 计算画布移动的偏移量
        delta_x = int(x - self.x)
        delta_y = int(y - self.y)

        self.x = int(x)
        self.y = int(y)

        # 更新所有元素的位置
        all_elements = self.element + self.dropdown_elements
        for element in all_elements:
            element.x += delta_x
            element.y += delta_y
            if hasattr(element, 'rect') and element.rect is not None:
                element.rect.x += delta_x
                element.rect.y += delta_y

    def set_size(self, w: float, h: float):
        """
        设置画布的大小。
        :param w: 画布的新的宽度
        :param h: 画布的新的高度
        """
        self.w = int(w)
        self.h = int(h)

        # 重新计算是否需要启用滚动
        content_height = self.max_height - self.y

        if content_height > self.h:
            self.scroll_enabled = True
            self.max_scroll = content_height - self.h  # 最大滚动偏移量
        else:
            self.scroll_enabled = False
            self.max_scroll = 0

    def clear(self):
        """
        清空画布上的所有元素。
        """
        self.element.clear()
        self.dropdown_elements.clear()
        self.scroll_offset = 0
        self.max_height = 0
        self.scroll_enabled = False
        self.max_scroll = 0


__all__ = ['Canvas']
