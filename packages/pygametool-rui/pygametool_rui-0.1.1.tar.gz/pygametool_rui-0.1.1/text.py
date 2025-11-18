import pygame
from PygameTool import functool


class Text:
    @functool.filter_kwargs  # 过滤掉不需要的参数，只要有用的参数
    def __init__(self, text, x: int | float = None, y: int | float = None, Tcolor="black", font_size: float | int = 20,
                 font_name="kaiti",
                 is_center=False, antialias=True, bg_color=None, bold=False, italic=False,
                 max_width=None, line_spacing=5):
        """
        对于文字的一些操作,下面的Rectangle类会调用这个类以达到显示文字的效果
        :param text: 当前文字的文字
        :param x: 文字的x坐标
        :param y: 文字的y坐标
        :param Tcolor: 文字的颜色,可以传入颜色的字符串，也可以传入颜色的元组，还有16进制的颜色，会自动转换成元组，如果不传入，那么就是黑色
        :param font_size: 文字的大小，默认是20
        :param font_name: 文字的字体，默认是微软雅黑
        :param is_center: 是否居中
        :param antialias: 是否抗锯齿
        :param bg_color: 背景颜色，默认是None，如果不是None，那么就会有背景颜色
        :param bold: 是否加粗
        :param italic: 是否斜体
        :param max_width: 最大宽度，如果超过这个宽度，那么就会换行
        :param line_spacing: 行间距，默认是5
        """
        self.text = str(text)  # 将传入的文字强行转换成字符串
        self.x = x if x is not None else 100  # 如果没有传入x，默认在100的位置
        self.y = y if y is not None else 100  # 如果没有传入y，默认在100的位置
        self.Tcolor = Tcolor
        self.bold = bold
        self.font_size = font_size
        self.font_name = font_name
        self.is_center = is_center
        self.antialias = antialias
        self.italic = italic

        if bg_color:
            self.bg_color = bg_color  # 将背景颜色转换成元组
        else:
            self.bg_color = None

        self.font = pygame.font.SysFont(self.font_name, self.font_size, bold=self.bold, italic=self.italic)  # 创建字体对象
        self.text_surface = self.font.render(self.text, self.antialias, self.Tcolor, self.bg_color)  # 创建文字对象
        self.text_rect = self.text_surface.get_rect()
        if self.is_center:
            self.text_rect.center = self.x, self.y
        else:
            self.text_rect.x, self.text_rect.y = self.x, self.y

        self.w, self.h = self.text_rect.width, self.text_rect.height  # 获取文字的宽度和高度
        self.trueAltitude = self.text_rect.height

        self.max_width = max_width  # 新增：最大允许宽度（超过则换行）
        self.line_spacing = line_spacing  # 新增：行间距
        self.lines = []  # 存储分割后的多行文本
        self._split_text()  # 分割文本到多行
        # print(f"创建了一个文字对象，文字是{self.text}， 颜色是{self.Tcolor}，背景颜色是{bg_color}")

    def __text_pos_update(self):
        if self.is_center:
            self.text_rect.center = self.x, self.y
        else:
            self.text_rect.x, self.text_rect.y = self.x, self.y

    def __text_update(self):  # __ 开头的方法是私有方法，只能在类内部调用，这个方法是用来更新文字的，不需要外部调用
        self.text = str(self.text)
        self.font = pygame.font.SysFont(self.font_name, self.font_size, bold=self.font.get_bold(), italic=self.font.get_italic())
        self.text_surface = self.font.render(self.text, True, self.Tcolor, self.bg_color)
        self.text_rect = self.text_surface.get_rect()
        self.__text_pos_update()
        self.w, self.h = self.text_rect.width, self.text_rect.height  # 重新获取文字的宽度和高度
        self._split_text()  # 更新时重新分割文本

    def _split_text(self):
        """将长文本分割为多行（根据max_width自动换行和\n强制换行）"""
        if self.max_width is None and '\n' not in self.text:
            self.lines = [self.text]
            return

        # 首先按\n分割文本
        paragraphs = self.text.split('\n')
        self.lines = []

        for paragraph in paragraphs:
            # 如果段落为空（连续的\n），添加空行
            if not paragraph:
                self.lines.append('')
                continue

            # 如果没有最大宽度限制，直接添加整段
            if self.max_width is None:
                self.lines.append(paragraph)
                continue

            # 处理需要按宽度换行的段落
            words = paragraph.split(' ')
            current_line = []
            current_width = 0

            for word in words:
                # 计算单词宽度
                word_surface = self.font.render(word, True, self.Tcolor, self.bg_color)
                word_width = word_surface.get_width()

                # 判断是否需要换行
                if current_width + word_width > self.max_width:
                    self.lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width + self.font.size(' ')[0] if current_line else 0  # 加上空格宽度

            # 添加段落的最后一行
            if current_line:
                self.lines.append(' '.join(current_line))

        self.trueAltitude = self.font.get_height() * len(self.lines) + self.line_spacing * (
                    len(self.lines) - 1)  # 更新真实高度

    def change_text(self, text):
        """改变文字"""
        self.text = text
        self.__text_update()

    def change_color(self, color: str):
        """改变颜色"""
        self.Tcolor = color
        self.__text_update()

    def change_font_size(self, font_size: int):
        """改变字体大小"""
        self.font_size = font_size
        self.__text_update()

    def change_font_name(self, font_name: str):
        """改变字体"""
        self.font_name = font_name
        self.__text_update()

    def change_is_center(self, is_center: bool):
        """改变是否居中"""
        self.is_center = is_center
        self.__text_update()

    def change_bold(self, bold: bool):
        """改变是否加粗"""
        self.font.set_bold(bold)
        self.__text_update()

    def change_italic(self, italic: bool):
        """改变是否斜体"""
        self.font.set_italic(italic)
        self.__text_update()

    def change_bg_color(self, bg_color: str):
        """改变背景颜色"""
        self.bg_color = bg_color
        self.__text_update()

    def pos(self, x=None, y=None):
        """
        改变位置
        :param x:  x坐标
        :param y: y坐标
        :return: None
        """
        self.x = x or self.x  # 调整文字的x坐标，如果没有传入x，那么就不改变x坐标，使用原来的x坐标
        self.y = y or self.y  # 调整文字的y坐标，如果没有传入y，那么就不改变y坐标，使用原来的y坐标
        self.__text_pos_update()

    def click(self, pos: tuple[int | float, int | float] = None) -> bool:
        """
        判断是否点击
        :param pos: 鼠标的位置，如果没有传入，那么就使用当前鼠标的位置
        :return:
        """
        if pos is None:
            pos = pygame.mouse.get_pos()
        return self.text_rect.collidepoint(pos)

    def draw(self, window: pygame.surface):
        """绘制多行文本"""
        y_offset = 0
        line_height = self.font.get_height() + self.line_spacing

        for line in self.lines:
            line_surface = self.font.render(line, self.antialias, self.Tcolor, self.bg_color)
            line_rect = line_surface.get_rect()

            if self.is_center:
                line_rect.center = (self.x, self.y + y_offset)
            else:
                line_rect.topleft = (self.x, self.y + y_offset)

            window.blit(line_surface, line_rect)
            y_offset += line_height


pygame.font.init()
__all__ = ["Text"]
