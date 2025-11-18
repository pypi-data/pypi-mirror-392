# 工具函数
from inspect import signature

__color_dict = {"red": (255, 0, 0), "orange": (255, 128, 0), "yellow": (255, 255, 0), "green": (0, 255, 0),
                "cyan": (0, 255, 255), "blue": (0, 0, 255), "purple": (255, 0, 255), "white": (255, 255, 255),
                "black": (0, 0, 0), "gray": (128, 128, 128), "pink": (255, 192, 203), "brown": (165, 42, 42),
                "gold": (255, 215, 0), "silver": (192, 192, 192)}  # 颜色字典
__color_name = {"红色": "red", "橙色": "orange", "黄色": "yellow", "绿色": "green", "青色": "cyan", "蓝色": "blue",
                "紫色": "purple", "白色": "white", "黑色": "black", "灰色": "gray", "粉色": "pink", "棕色": "brown",
                "金色": "gold", "银色": "silver"}  # 颜色名字字典


def filter_kwargs(func):
    """过滤器，过滤掉不需要的参数，只要有用的参数"""
    def wrapper(*args, **kwargs):
        sig = signature(func)  # 获取函数的参数
        parameters = sig.parameters  # 获取函数的参数
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in parameters}  # 过滤掉不需要的参数
        return func(*args, **filtered_kwargs)  # 返回函数

    return wrapper  # 返回函数


def hex_to_rgb(color) -> tuple:
    """将十六进制数字、字母、元组解析，返回颜色对应的元组，默认返回橙色"""
    # 如果输入是元组，并且元素是整数，则直接返回该元组
    if isinstance(color, tuple) and all(isinstance(x, int) for x in color) and len(color) == 3:
        return color

    # 如果输入是字符串
    if isinstance(color, str):
        # 如果输入是十六进制颜色码
        if color.startswith("#"):
            hex_color = color.lstrip("#")
            length = len(hex_color)
            if length not in [3, 6]:
                return __color_dict.get("orange")
            factor = 2 if length == 6 else 1
            r = int(hex_color[0:factor], 16)
            g = int(hex_color[factor:factor * 2], 16)
            b = int(hex_color[factor * 2:factor * 3], 16)
            if factor == 1:
                r, g, b = r * 17, g * 17, b * 17
            return r, g, b

        # 如果输入是英文颜色名
        if color.lower() in __color_dict:
            return __color_dict[color.lower()]

        # 如果输入是中文颜色名
        if color in __color_name:
            english_name = __color_name[color]
            return __color_dict[english_name]

    # 如果其他类型，则返回默认颜色橙色
    return __color_dict.get("orange")


__all__ = ["hex_to_rgb", "filter_kwargs"]
