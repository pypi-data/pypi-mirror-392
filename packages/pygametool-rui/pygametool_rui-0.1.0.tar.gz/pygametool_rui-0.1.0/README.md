# PygameTool

一个基于 `pygame` 的常用组件合集，覆盖文字渲染、按钮/单选框、输入框/下拉框、滚动画布、图形绘制、精灵管理、音频管理、消息弹窗等。专注“拿来即用”，与原生 `pygame` 事件循环无缝配合。

## 安装

```
pip install PygameTool
```

## 环境与导入

- Python ≥ 3.10（类型语法使用 `int | float`）
- `import PygameTool` 不会创建窗口或初始化音频/Tk；按需在你的程序里调用：
  - `pygame.init(); pygame.display.set_mode(...)`
  - 音频按需初始化，由 `MusicManager` 的内部懒加载完成
  - Tk 根窗口按需创建，由 `messageBox.show_message(...)` 首次调用时创建

## 快速开始

```
import pygame
from PygameTool import Text, Canvas

pygame.init()
screen = pygame.display.set_mode((640, 480))

text = Text("Hello PygameTool", x=50, y=50, font_size=28)
canvas = Canvas(screen)
canvas.addSprite(text)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        canvas.handle_event(event)
    screen.fill((30, 30, 30))
    canvas.draw()
    pygame.display.flip()

pygame.quit()
```

## 组件总览

- `Text`：多行文本、自动换行、行距、居中/非居中、字体/大小/加粗/斜体/背景色
- `Button`：可配置文字/边框/圆角/透明背景，点击回调
- `Radio`：单选框，支持队列分组互斥、文字偏移、点击回调
- `InputBox`：占位符、密码模式、数字限制、居中/左对齐、剪贴板、重复按键处理、回车回调
- `DropDown`：下拉选择（与 `Canvas`/事件循环协作）
- `SeekBar`：拖动条，最小/最大值、当前值显示、颜色配置
- `Rectangle`/`Circle`/`Line`：常见图形绘制，支持颜色字符串/HEX 自动转 RGB
- `Canvas`：限定区域绘制与滚动，裁剪绘制、只在激活画布内响应滚轮
- `Sprite`：图片加载与绘制，支持居中/缩放/遮罩/动画（GIF 帧控制等）
- `Scrollbar`/`starfield`：滚动条、星空效果（与 `Canvas`/绘制配合）
- `MusicManager`：音频懒加载、播放/暂停/恢复/停止、唯一键管理、定时播放、播放序列
- `messageBox`：基于 Tk 的消息弹窗，支持单/双按钮与自定义回调
- `functool`：颜色名/HEX 转 RGB、构造参数过滤等工具函数

## 常用示例

### 按钮与单选框

```
import pygame
from PygameTool import Button, Radio

pygame.init()
screen = pygame.display.set_mode((480, 360))

def on_click():
    print("clicked!")

btn = Button(screen, x=240, y=60, w=150, h=40, text="点我", func=on_click)
radio1 = Radio(screen, x=100, y=140, num_queue=1, txt="选项A")
radio2 = Radio(screen, x=180, y=140, num_queue=1, txt="选项B")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 按钮/单选框通常各自有事件处理方法（如 click/handle），根据你的实现调用
    screen.fill((240, 240, 240))
    btn.draw()
    radio1.draw()
    radio2.draw()
    pygame.display.flip()
```

### 输入框与拖动条

```
import pygame
from PygameTool import InputBox, SeekBar

pygame.init()
screen = pygame.display.set_mode((600, 400))

ibox = InputBox(x=50, y=60, w=260, h=38, placeholder="输入文本...")
bar = SeekBar(x=50, y=140, w=260, h=12, Min=0, Max=100, value=50, color="DeepSkyBlue")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ibox.handle_event(event)
        # bar 的拖动在其内部处理，通常只需传递事件或在更新时调用其方法
    screen.fill((255, 255, 255))
    ibox.draw(screen)
    bar.draw(screen)
    pygame.display.flip()
```

### 图形与精灵

```
import pygame
from PygameTool import Rectangle, Circle, Line, Sprite

pygame.init()
screen = pygame.display.set_mode((640, 480))

rect = Rectangle(200, 100, 120, 60, fillet=10, color="#00AAFF", is_center=True)
circle = Circle(420, 120, 40, width=3, color="purple", fillColor="#FFEE88")
line = Line(60, 200, 580, 200, width=2, color="orange")
sprite = Sprite("./example.png", x=320, y=340, is_center=True, scale=0.5)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((28, 28, 28))
    rect.draw(screen)
    circle.draw(screen)
    line.draw(screen)
    sprite.draw(screen)
    pygame.display.flip()
```

### 音频与消息弹窗

```
from PygameTool import MusicManager, messageBox

key = MusicManager.play_sound("click.wav", voice=0.6, times=1)
is_yes = messageBox.show_message("继续操作吗？", title="提示", ok_button="确定", cancel_button="取消")
if is_yes:
    print("用户选择：确定")
```

## 事件循环与滚动画布

- 在 `Canvas` 中添加的元素（精灵/文本/下拉等），通过 `canvas.handle_event(event)` 传递事件；
- 只有点击激活的画布会响应滚轮滚动；绘制时自动裁剪到画布区域；
- 下拉元素绘制在最顶层，避免被裁剪；超出画布区域也可显示。

## 颜色输入规则

- 支持颜色名（如 `"red"`、`"orange"`）、HEX（如 `"#00AAFF"`）、RGB 元组（如 `(0, 170, 255)`）；
- 所有颜色输入会通过 `functool.hex_to_rgb(...)` 标准化为 RGB。

## 目录说明

- `PygameTool/dist/`：本地构建产物（wheel 与 sdist），用于上传 PyPI；不影响开发与使用。
- `PygameTool/PygameTool.egg-info/`：构建时自动生成的包元数据目录；正常现象，无需手动维护。
- 正式发布时仅上传 `dist/*`；源仓库中这两个目录可保留或忽略，不会影响 `pip install` 与 `import`。

## 许可

MIT License