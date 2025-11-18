import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class MessageBox:
    def __init__(self,
                 message: str = "提示信息",
                 ok_f: Optional[Callable] = None,
                 cancel_f: Optional[Callable] = None,
                 title: str = "提示",
                 ok_button: str = "确定",
                 cancel_button: str = "取消"):
        """
        初始化 MessageBox 类。

        :param message: 默认显示的提示信息
        :param ok_f: 默认点击“确定”时调用的回调函数
        :param cancel_f: 默认点击“取消”时调用的回调函数
        :param title: 默认弹窗标题
        :param ok_button: 默认确定按钮文字
        :param cancel_button: 默认取消按钮文字
        """
        self.default_message = message
        self.default_ok_f = ok_f
        self.default_cancel_f = cancel_f
        self.default_title = title
        self.default_ok_button = ok_button
        self.default_cancel_button = cancel_button
        self.result = None
        self.root = None

    def on_close(self):
        """处理窗口关闭事件，默认为取消操作。"""
        self.result = False
        if hasattr(self, 'popup'):
            self.popup.destroy()
        if self.root:
            self.root.quit()

    def _ensure_root(self):
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def handle_confirm(self):
        """处理确定按钮点击事件。"""
        if self.current_ok_f:
            self.current_ok_f()
        self.result = True
        self.popup.destroy()
        self.root.quit()

    def handle_cancel(self):
        """处理取消按钮点击事件。"""
        if self.current_cancel_f:
            self.current_cancel_f()
        self.result = False
        self.popup.destroy()
        self.root.quit()

    def show_message(self,
                     message: Optional[str] = None,
                     title: Optional[str] = None,
                     ok_f: Optional[Callable] = None,
                     cancel_f: Optional[Callable] = None,
                     ok_button: Optional[str] = None,
                     cancel_button: Optional[str] = None,
                     single_button: bool = False) -> Optional[bool]:
        """
        显示消息弹窗，并等待用户选择。

        :param message: 显示的提示信息。如果不传，则使用初始化时的默认值。
        :param title: 弹窗标题。如果不传，则使用初始化时的默认值。
        :param ok_f: 点击“确定”时调用的回调函数。如果不传，则使用初始化时的默认值。
        :param cancel_f: 点击“取消”时调用的回调函数。如果不传，则使用初始化时的默认值。
        :param ok_button: 确定按钮文字。如果不传，则使用初始化时的默认值。
        :param cancel_button: 取消按钮文字。如果不传，则使用初始化时的默认值。
        :param single_button: 是否只显示一个按钮（确定）
        :return: 用户的选择，True 表示确定，False 表示取消，None 表示未选择
        """
        # 使用传入的参数或默认值
        self.current_message = message if message is not None else self.default_message
        self.current_title = title if title is not None else self.default_title
        self.current_ok_f = ok_f if ok_f is not None else self.default_ok_f
        self.current_cancel_f = cancel_f if cancel_f is not None else self.default_cancel_f
        self.current_ok_button = ok_button if ok_button is not None else self.default_ok_button
        self.current_cancel_button = cancel_button if cancel_button is not None else self.default_cancel_button

        self._ensure_root()
        self.result = None

        # 创建一个新的窗口作为弹窗
        self.popup = tk.Toplevel(self.root)
        self.popup.title(self.current_title)
        self.popup.geometry("300x150")
        self.popup.resizable(False, False)

        # 设置弹窗在主窗口中央
        self.popup.transient(self.root)
        self.popup.grab_set()

        # 提示信息标签
        label = ttk.Label(self.popup, text=self.current_message, font=("Arial", 12), wraplength=280)
        label.pack(pady=20)

        # 按钮框架
        button_frame = ttk.Frame(self.popup)
        button_frame.pack(pady=10)

        # 确定按钮
        confirm_button = ttk.Button(button_frame, text=self.current_ok_button, command=self.handle_confirm)
        confirm_button.pack(side="left", padx=10)

        if not single_button:
            # 取消按钮
            cancel_button = ttk.Button(button_frame, text=self.current_cancel_button, command=self.handle_cancel)
            cancel_button.pack(side="right", padx=10)

        # 等待窗口关闭
        self.root.wait_window(self.popup)

        return self.result

    def __del__(self):
        """确保在对象销毁时正确退出 Tkinter。"""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"捕获到异常：{e}")


messageBox = MessageBox()

__all__ = ["messageBox"]
