import pygame


class dropDown:
    def __init__(self, x, y, width, height, data: list, font_name="华文新魏", max_show=5,
                 radius=10, border_color=(0, 0, 0), item_border_color=(150, 150, 150)):
        """
        初始化下拉菜单，接收菜单位置、大小、数据、字体和每页显示项数。
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = data  # 下拉菜单的内容
        self.font_name = font_name  # 字体
        self.max_show = max_show  # 每页显示的最大数据项数
        self.radius = radius
        self.is_open = False  # 下拉菜单是否展开
        self.text = ""  # 当前选中的选项
        self.selected_index = None  # 当前选择的选项
        self.font = pygame.font.SysFont(self.font_name, 24)
        self.bg_color = (255, 255, 255)  # 背景颜色
        self.text_color = (0, 0, 0)  # 文字颜色
        self.hover_color = (200, 200, 255)  # 悬停项高亮颜色
        self.border_color = border_color  # 下拉框边框颜色
        self.item_border_color = item_border_color  # 子项的边框颜色
        self.dropdown_height = self.height * max_show  # 展开时的高度
        self.is_hovering = None  # 当前悬停项的索引
        self.symbol = '∨'  # 下拉框右侧符号
        self.symbol_rect = pygame.Rect(self.x + self.width - 30, self.y + 5, 30, 30)  # 符号点击区域
        self.scroll_offset = 0  # 滚动偏移量，控制当前可显示的选项区域

    def load_data(self):
        """加载数据，默认已经在初始化时传入，后续可扩展为动态加载"""
        pass

    def get_text(self) -> str:
        """获取当前选中的选项"""
        print("返回当前值：", self.text)
        return self.text

    def handle_event(self, event):
        """处理鼠标点击事件和选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if event.button == 1:
                # 检查点击的是不是下拉菜单区域
                if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                    self.is_open = not self.is_open  # 切换菜单展开或收起状态
                    self.symbol = '∧' if self.symbol == '∨' else '∨'

                # 如果菜单已展开，检查是否选择了某一项
                if self.is_open:
                    item_height = self.height
                    for i, item in enumerate(self.data[self.scroll_offset:self.scroll_offset + self.max_show]):
                        item_rect = pygame.Rect(self.x + 10, self.y + item_height, self.width - 20, 40)  # 子项矩形比下拉框小
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_index = i + self.scroll_offset
                            self.text = item
                            self.is_open = False  # 选择后关闭菜单
                            self.symbol = '∧'
                            break
                        item_height += 40

        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 判断当前悬停的是哪个项
            if self.is_open:
                item_height = self.height
                self.is_hovering = None
                for i, item in enumerate(self.data[self.scroll_offset:self.scroll_offset + self.max_show]):
                    item_rect = pygame.Rect(self.x + 10, self.y + item_height, self.width - 20, 40)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.is_hovering = i
                    item_height += 40

        if event.type == pygame.MOUSEWHEEL:
            """处理鼠标滚轮事件"""
            if self.is_open:
                if event.y > 0:  # 滚轮向上，选择上一个项
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                elif event.y < 0:  # 滚轮向下，选择下一个项
                    if self.scroll_offset + self.max_show < len(self.data):
                        self.scroll_offset += 1

    def draw(self, screen):
        """绘制下拉菜单"""
        # 创建一个临时surface用于绘制下拉菜单
        if self.is_open:
            # 计算需要的surface高度
            dropdown_total_height = self.height + min(len(self.data), self.max_show) * 40
            temp_surface = pygame.Surface((self.width, dropdown_total_height), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # 透明背景
        else:
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # 透明背景

        # 绘制下拉框背景和圆角
        pygame.draw.rect(temp_surface, self.bg_color, (0, 0, self.width, self.height), border_radius=self.radius)
        pygame.draw.rect(temp_surface, self.border_color, (0, 0, self.width, self.height), 2, border_radius=self.radius)

        # 绘制当前选中的项
        if self.selected_index is not None:
            selected_text = self.font.render(self.data[self.selected_index], True, self.text_color)
        else:
            selected_text = self.font.render('请选择...', True, self.text_color)
        temp_surface.blit(selected_text, (5, 5))

        # 绘制右侧符号
        symbol_text = self.font.render(self.symbol, True, self.text_color)
        temp_surface.blit(symbol_text, (self.width - 30, 5))

        # 如果菜单展开，绘制每一项
        if self.is_open:
            item_height = self.height
            for i, item in enumerate(self.data[self.scroll_offset:self.scroll_offset + self.max_show]):
                item_rect = pygame.Rect(10, item_height, self.width - 20, 40)

                # 判断是否为悬停项，悬停项高亮显示
                if self.is_hovering == i:
                    pygame.draw.rect(temp_surface, self.hover_color, item_rect)
                else:
                    pygame.draw.rect(temp_surface, self.bg_color, item_rect)
                pygame.draw.rect(temp_surface, self.item_border_color, item_rect, 2)

                item_text = self.font.render(item, True, self.text_color)
                temp_surface.blit(item_text, (15, item_height + 5))

                item_height += 40

        # 将临时surface绘制到屏幕上
        screen.blit(temp_surface, (self.x, self.y))
