import pygame
import pyperclip
from typing import Optional, Callable
from PygameTool.functool import hex_to_rgb


class InputBox:
    def __init__(self, x: float = 100, y: float = 100, w: float = 200, h: float = 40, radius: int = 5,
                 placeholder='', bg_color="#FFFFFF", border_color="#000000",
                 text_color="#000000", placeholder_color="#A9A9A9",
                 digit: bool = False, password: bool = False,
                 is_box_centered: bool = True, is_text_centered: bool = False,
                 font_size: int = 24, font_name="SimHei", padding: int = 10, editable: bool = True,
                 on_enter: Optional[Callable] = None, clear_on_enter: bool = True):
        """
        输入框
        :param x: 输入框的x坐标
        :param y: 输入框的y坐标
        :param w: 输入框的宽度
        :param h: 输入框的高度
        :param radius: 输入框的圆角半径
        :param placeholder: 当输入框为空时显示的提示文字
        :param bg_color: 输入框的背景颜色
        :param border_color: 输入框的边框颜色
        :param text_color: 输入框内文字的颜色
        :param placeholder_color: 提示文字的颜色
        :param digit: 是否为数字输入框
        :param password: 是否为密码输入（以●显示文本内容）
        :param is_box_centered: 输入框的x、y是否为中心坐标
        :param is_text_centered: 文本是否居中显示在输入框内
        :param font_size: 输入框内文字的大小
        :param font_name: 输入框内文字的字体
        :param padding: 文本与输入框边界的内边距
        :param editable: 是否可编辑
        """
        self.w, self.h = w, h
        self.x, self.y = x, y
        self.radius = radius
        self.is_box_centered = is_box_centered
        self.is_text_centered = is_text_centered
        self.font_name = font_name
        self.editable = editable  # 控制是否可编辑文本
        self.on_enter = on_enter
        self.clear_on_enter = clear_on_enter

        # 设置矩形位置
        if self.is_box_centered:
            self.rect = pygame.Rect(0, 0, w, h)
            self.rect.center = (x, y)
        else:
            self.rect = pygame.Rect(x, y, w, h)

        self.color_inactive = hex_to_rgb(border_color)
        self.color_active = (0, 128, 255)
        self.color = self.color_inactive
        self.bg_color = hex_to_rgb(bg_color)
        self.text_color = hex_to_rgb(text_color)
        self.placeholder_color = hex_to_rgb(placeholder_color)
        self.placeholder = placeholder
        self.text = ''
        self.active = False
        self.digit = digit
        self.password = password
        self.font_size = font_size
        if self.password:
            self.font = pygame.font.SysFont(font_name, self.font_size // 2)  # 密码显示的圈要小一圈，不然看的很奇怪
        else:
            self.font = pygame.font.SysFont(font_name, self.font_size)
        self.P_font = pygame.font.SysFont(font_name, self.font_size)  # 为空的时候，显示的文本，与密码的字符分开
        self.padding = padding

        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_position = 0  # 光标在文本中的位置（字符索引）
        self.text_offset = 0      # 文本偏移量，用于裁剪显示

        initial_delay = 150
        repeat_delay = 100

        # 用于处理连续按键
        self.backspace_held = False
        self.backspace_initial_delay = initial_delay  # 退格按键的初始延迟
        self.backspace_repeat_delay = repeat_delay    # 退格按键的重复延迟
        self.last_backspace_time = 0

        # 处理左右方向键的连续按压
        self.left_key_held = False
        self.left_key_initial_delay = initial_delay    # 毫秒
        self.left_key_repeat_delay = repeat_delay      # 毫秒
        self.last_left_key_time = 0
        self.right_key_held = False
        self.right_key_initial_delay = initial_delay   # 毫秒
        self.right_key_repeat_delay = repeat_delay     # 毫秒
        self.last_right_key_time = 0

        # 启用 Pygame 的文本输入事件
        pygame.key.start_text_input()

        self._update_text_surface()

    def _update_text_surface(self):
        """更新文本表面并调整文本偏移量以确保光标可见"""
        display_text = self.text
        if self.password:
            display_text = '●' * len(self.text)
        self.txt_surface = self.font.render(display_text, True, self.text_color)
        if not self.text and not self.active:
            self.txt_surface = self.P_font.render(self.placeholder, True, self.placeholder_color)

        # 更新文本宽度
        self.text_width = self.txt_surface.get_width()
        self.box_inner_width = self.rect.width - 2 * self.padding

        # 计算光标在像素中的位置
        if self.password:
            # 计算密码模式下的光标位置
            cursor_pixel = self.font.size('●' * self.cursor_position)[0]
        else:
            cursor_pixel = self.font.size(self.text[:self.cursor_position])[0]

        # 调整文本偏移量以确保光标可见
        if cursor_pixel - self.text_offset > self.box_inner_width:
            self.text_offset = cursor_pixel - self.box_inner_width
        elif cursor_pixel - self.text_offset < 0:
            self.text_offset = cursor_pixel - self.box_inner_width // 2
            if self.text_offset < 0:
                self.text_offset = 0

        # 确保text_offset不超出文本宽度
        if self.text_width - self.text_offset < self.box_inner_width:
            self.text_offset = max(self.text_width - self.box_inner_width, 0)

    def change_password_mode(self, mode: bool = False):
        if mode == self.password:
            return
        self.password = mode
        if self.password:
            self.font = pygame.font.SysFont(self.font_name, self.font_size // 2)  # 密码显示的圈要小一圈，不然看的很奇怪
        else:
            self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self._update_text_surface()

    def handle_event(self, event):
        """处理事件，包括鼠标点击和键盘输入"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not self.editable:
                    return
                # 检测是否点击在输入框内
                if self.rect.collidepoint(event.pos):
                    self.active = True
                    self.color = self.color_active
                    # 设置光标位置到点击位置
                    self.set_cursor_position(event.pos[0])
                    pygame.key.set_repeat(0)  # 禁用键盘重复输入
                    pygame.key.set_text_input_rect(self.rect.inflate(-self.padding * 2, -self.padding * 2))
                else:
                    self.active = False
                    self.color = self.color_inactive
                    pygame.key.set_repeat(500, 50)  # 启用键盘重复输入
                self._update_text_surface()

        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    if self.on_enter:
                        try:
                            self.on_enter(self.text)
                        except TypeError:
                            self.on_enter()
                    if self.clear_on_enter:
                        self.text = ''
                        self.cursor_position = 0
                        self._update_text_surface()

                elif event.key == pygame.K_BACKSPACE:
                    # 退格键删除操作
                    if self.cursor_position > 0:  # 确保不超出文本范围
                        # 删除光标前的一个字符
                        self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
                        self.cursor_position -= 1
                        self._update_text_surface()
                    self.backspace_held = True
                    self.last_backspace_time = pygame.time.get_ticks()

                elif event.key == pygame.K_DELETE:
                    if self.cursor_position < len(self.text):
                        # 删除光标后的一个字符
                        self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]
                        self._update_text_surface()

                elif event.key == pygame.K_LEFT:
                    if self.cursor_position > 0:
                        self.cursor_position -= 1
                        self._update_text_surface()
                    self.left_key_held = True
                    self.last_left_key_time = pygame.time.get_ticks()

                elif event.key == pygame.K_RIGHT:
                    if self.cursor_position < len(self.text):
                        self.cursor_position += 1
                        self._update_text_surface()
                    self.right_key_held = True
                    self.last_right_key_time = pygame.time.get_ticks()

                elif event.key == pygame.K_HOME:
                    self.cursor_position = 0
                    self._update_text_surface()

                elif event.key == pygame.K_END:
                    self.cursor_position = len(self.text)
                    self._update_text_surface()

                elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:  # 复制文本到剪贴板，ctrl + c
                    pyperclip.copy(self.text)

                elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:  # 全选文本，ctrl + a
                    self.select_all_text()

                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:  # 粘贴文本，ctrl + v
                    if self.editable:  # 确保粘贴操作仅在可编辑的输入框上进行
                        paste_text = pyperclip.paste()  # 获取剪贴板中的文本
                        self.text = self.text[:self.cursor_position] + paste_text + self.text[self.cursor_position:]
                        self.cursor_position += len(paste_text)
                        self._update_text_surface()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:  # 释放退格键
                self.backspace_held = False
            if event.key == pygame.K_RIGHT:
                self.right_key_held = False
            if event.key == pygame.K_LEFT:
                self.left_key_held = False

        elif event.type == pygame.TEXTINPUT:
            if self.active:
                if self.digit:
                    if event.text.isdigit():
                        self.text = self.text[:self.cursor_position] + event.text + self.text[self.cursor_position:]
                        self.cursor_position += len(event.text)
                        self._update_text_surface()
                else:
                    self.text = self.text[:self.cursor_position] + event.text + self.text[self.cursor_position:]
                    self.cursor_position += len(event.text)
                    self._update_text_surface()

        # 处理退格键连续删除的时间逻辑
        if self.backspace_held:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_backspace_time >= self.backspace_initial_delay:
                if current_time - self.last_backspace_time >= self.backspace_initial_delay + self.backspace_repeat_delay:
                    if self.cursor_position > 0:
                        self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
                        self.cursor_position -= 1
                        self._update_text_surface()
                        self.last_backspace_time = current_time

        # 处理左右方向键的连续移动
        if self.left_key_held:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_left_key_time >= self.left_key_initial_delay:
                if current_time - self.last_left_key_time >= self.left_key_initial_delay + self.left_key_repeat_delay:
                    if self.cursor_position > 0:
                        self.cursor_position -= 1
                        self._update_text_surface()
                        self.last_left_key_time = current_time

        if self.right_key_held:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_right_key_time >= self.right_key_initial_delay:
                if current_time - self.last_right_key_time >= self.right_key_initial_delay + self.right_key_repeat_delay:
                    if self.cursor_position < len(self.text):
                        self.cursor_position += 1
                        self._update_text_surface()
                        self.last_right_key_time = current_time

    def select_all_text(self):
        """选中输入框中的所有文本"""
        self.cursor_position = len(self.text)

    def set_cursor_position(self, mouse_x):
        """根据鼠标点击位置设置光标位置"""
        relative_x = mouse_x - self.rect.x - self.padding + self.text_offset
        pos = 0
        accumulated_width = 0
        for i, char in enumerate(self.text):
            char_display = '●' if self.password else char
            char_width = self.font.size(char_display)[0]
            if accumulated_width + char_width / 2 >= relative_x:
                pos = i
                break
            accumulated_width += char_width
        else:
            pos = len(self.text)
        self.cursor_position = pos
        self._update_text_surface()

    def set_position(self, x, y, is_center=None):
        """设置输入框的位置
        :param x: 新的x坐标
        :param y: 新的y坐标
        :param is_center: 是否以中心点设置。如果为None，则使用初始化时的is_box_centered
        """
        if is_center is None:
            is_center = self.is_box_centered

        if is_center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)
        self._update_text_surface()

    def get_text(self, strip: bool = True, strip_message: str = " \n\t") -> str | int:
        """获取输入框中的文本"""
        if strip:
            self.text.strip(strip_message)
        # 如果是数字，返回数字格式
        if self.digit and self.text.isdigit():
            return int(self.text)
        return self.text

    def set_text(self, text: str):
        self.text = text
        self._update_text_surface()

    def set_placeholder(self, placeholder: str) -> None:
        self.placeholder = str(placeholder)
        self._update_text_surface()

    def update(self):
        """更新光标状态和处理连续按键"""
        self.cursor_counter += 1
        if self.cursor_counter >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_counter = 0

        current_time = pygame.time.get_ticks()

        # 处理退格键的连续删除
        if self.backspace_held:
            if current_time - self.last_backspace_time >= self.backspace_initial_delay:
                if current_time - self.last_backspace_time >= self.backspace_initial_delay + self.backspace_repeat_delay:
                    if self.cursor_position > 0:
                        self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
                        self.cursor_position -= 1
                        self._update_text_surface()
                        self.last_backspace_time = current_time

        # 处理左方向键的连续移动
        if self.left_key_held:
            if current_time - self.last_left_key_time >= self.left_key_initial_delay:
                if current_time - self.last_left_key_time >= self.left_key_initial_delay + self.left_key_repeat_delay:
                    if self.cursor_position > 0:
                        self.cursor_position -= 1
                        self._update_text_surface()
                        self.last_left_key_time = current_time

        # 处理右方向键的连续移动
        if self.right_key_held:
            if current_time - self.last_right_key_time >= self.right_key_initial_delay:
                if current_time - self.last_right_key_time >= self.right_key_initial_delay + self.right_key_repeat_delay:
                    if self.cursor_position < len(self.text):
                        self.cursor_position += 1
                        self._update_text_surface()
                        self.last_right_key_time = current_time

    def draw(self, window: pygame.Surface):
        """绘制输入框，包括背景、边框、文本和光标"""
        # 绘制背景
        pygame.draw.rect(window, self.bg_color, self.rect, border_radius=self.radius)
        # 绘制边框
        pygame.draw.rect(window, self.color, self.rect, 2, border_radius=self.radius)

        # 设置裁剪区域，确保文本不超出输入框
        clip_rect = pygame.Rect(self.rect.x + self.padding, self.rect.y,
                                self.rect.width - 2 * self.padding, self.rect.height)
        window.set_clip(clip_rect)

        # 绘制文本
        if self.is_text_centered and not self.text:
            text_rect = self.txt_surface.get_rect(center=self.rect.center)
            window.blit(self.txt_surface, text_rect)
        else:
            if self.password:
                display_text = '●' * len(self.text)
            else:
                display_text = self.text
            text_to_display = display_text
            if self.text or self.active:
                # Render text up to the current view
                rendered_text = self.font.render(text_to_display, True, self.text_color)
                if self.is_text_centered:
                    text_rect = rendered_text.get_rect(center=self.rect.center)
                    window.blit(rendered_text, text_rect)
                else:
                    window.blit(rendered_text, (self.rect.x + self.padding - self.text_offset,
                                                self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
            else:
                window.blit(self.txt_surface, (self.rect.x + self.padding - self.text_offset,
                                               self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))

        window.set_clip(None)  # 取消裁剪

        # 绘制光标
        if self.active and self.cursor_visible:
            # 计算光标位置
            if self.password:
                cursor_text = '●' * self.cursor_position
            else:
                cursor_text = self.text[:self.cursor_position]
            cursor_x = self.rect.x + self.padding + self.font.size(cursor_text)[0] - self.text_offset
            cursor_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
            cursor_height = self.txt_surface.get_height()
            # 确保光标不超出输入框
            cursor_x = max(self.rect.x + self.padding, min(cursor_x, self.rect.x + self.rect.width - self.padding))
            pygame.draw.line(window, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    @staticmethod
    def stop_text_input():
        """停止文本输入事件"""
        pygame.key.stop_text_input()


__all__ = ["InputBox"]
