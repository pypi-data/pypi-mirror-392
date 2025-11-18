import hashlib
import inspect
import math
import re
import os
import plistlib
from typing import Union
from urllib.parse import urlparse, unquote

import pygame
import requests
import validators
from PIL import Image  # 导入PIL库的Image模块,用于加载gif图片
from tqdm import tqdm

__debug_level = {1: "提示", 2: "警告", 3: "错误"}
__debug_color = {2: "\033[33m", 3: "\033[31m"}
__DE_BUG__ = False
__level = [1]  # 打印哪些等级的信息？等级详细见__debug_level
# 函数调用栈，如果写了这个，那么仅限于在__function_name里面的名字会被打印debug，不会打印其它函数的调试信息
__function_name = ["__load_src"]

__MAX_CACHE_SIZE__ = 4e9  # 缓存大小,最大限制为4G，如果超出了4G，则删除部分缓存
# 缓存  {图片名字(png): {对象: 图片对象, 访问次数: 1}, 图片名字(gif): {对象: {1: 图片对象, 2: 图片对象, ...}, 访问次数: 1}}
__cache__ = {}  # 对于png和gif图片缓存，采用不同方式缓存


def __printf_debug(tips: str): print(tips + "\033[0m")


def debug(tip: str, level: int = 1, code: int = None):
    if not __DE_BUG__: return None
    else:
        if not __level: return None
        frame = inspect.currentframe().f_back  # 获取调用当前函数的帧对象
        _color = __debug_color.get(level)
        _message = f"{_color if _color else ''}【{__debug_level[level]}】"
        if level in __level:
            _message += (f"从第{frame.f_lineno}行处，调用此函数的函数名为：{frame.f_code.co_name}\t"
                         f"{__debug_level[level]}信息：{tip}")
            if code:
                _message += f"错误代码：{code}，请您联系开发者咨询！"
            if not __function_name:
                __printf_debug(_message)
            else:
                if frame.f_code.co_name in __function_name:
                    __printf_debug(_message)


def __count_cache_size__() -> int:
    # 计算缓存大小
    _img_size = 0
    for item in __cache__.values():
        obj = item['object']
        if isinstance(obj, dict):
            # 如果是字典（以前GIF缓存模式），遍历字典中的Surface
            for surf in obj.values():
                _img_size += pygame.image.tostring(surf, "RGBA").__sizeof__()
        elif isinstance(obj, list):
            # 如果是列表（新的GIF缓存模式），遍历列表中的每个Surface
            for surf in obj:
                _img_size += pygame.image.tostring(surf, "RGBA").__sizeof__()
        else:
            # 否则单一Surface的情况
            _img_size += pygame.image.tostring(obj, "RGBA").__sizeof__()

    debug(f"当前缓存大小：{_img_size} / {__MAX_CACHE_SIZE__}")
    return _img_size


def __del_cache__():
    """当缓存大于最大限制时，删除部分缓存，按访问次数排序删除"""
    while __count_cache_size__() > __MAX_CACHE_SIZE__:
        # 按访问次数排序
        sorted_cache = sorted(__cache__.items(), key=lambda x: x[1]['visit'])
        # 删除访问次数最少的
        if sorted_cache:
            del_item = sorted_cache[0][0]
            del __cache__[del_item]
            debug(f"当前图片的缓存超出最大缓存大小：{__MAX_CACHE_SIZE__}，删除缓存：{del_item}")


def custom_sort_key(key):
    # 如果键是数字（正则匹配以数字开头），按数字排序
    if re.match(r'^\d+', key):
        return int(re.match(r'^\d+', key).group())
    # 否则按字母ASCII码排序
    return key


def load_picture(dic_name: str, dic_data: pygame.Surface | list[pygame.Surface]):
    global __cache__
    __cache__[dic_name] = {"object": dic_data, "visit": 1}
    size = __count_cache_size__()
    if size > __MAX_CACHE_SIZE__:
        __del_cache__()
    debug(f"加载{dic_name}成功，当前缓存大小为{size}")


class PvrCczLoader:
    def __init__(self, src: str, plist: str = None, returnType: str = "gif", serialNumberName: str | int = None,
                 auto_sort: bool = False):
        """
        创建适用于PvrCcz格式的加载器
        :param src: 传入图片的路径
        :param plist: plist文件路径，使用plist解析图片
        :param returnType: 分为：
            gif: 认为传入的图片是一系列frame，可以方便Sprite类使用
            png: 返回单一的图片，需要结合serialNumberName参数来使用
        :param serialNumberName: 当returnType为png时，指定要获取的frame名称
        :param auto_sort: 当auto_sort为True时，自动对图片进行排序，默认为False
        """
        self.src = src
        self.plist = plist or src.rsplit('.', 1)[0] + ".plist"
        self.returnType = returnType
        self.serialNumberName = serialNumberName
        self.auto_sort = auto_sort

        # 加载plist信息
        with open(self.plist, 'rb') as f:
            plist_data = plistlib.load(f)

        self.frames = plist_data["frames"]

        cache_name = f"_load_pvr_{self.src}"
        # 加载整张图
        if cache_name in __cache__:
            self.sprite_sheet = __cache__[cache_name]['object'].copy()
            __cache__[cache_name]['visit'] += 1
            debug(f"从缓存当中加载{cache_name}成功")
        else:
            img = pygame.image.load(self.src).convert_alpha()
            __cache__[cache_name] = {"object": img, "visit": 1}
            self.sprite_sheet = img

        self.sprites = self._load_sprites()  # 加载图片

    @staticmethod
    def _parse_texture_rect(rect_str):
        match = re.match(r"\{\{(\d+),(\d+)},\{(\d+),(\d+)}}", rect_str)
        if match:
            return tuple(map(int, match.groups()))
        else:
            raise ValueError("无效的纹理矩形字符串：%s" % rect_str)

    def _load_sprites(self) -> dict[str, pygame.Surface]:
        sprites = {}
        for image_name, frame_data in self.frames.items():
            texture_rect_str = frame_data['textureRect']
            x, y, width, height = self._parse_texture_rect(texture_rect_str)
            rotated = frame_data.get('textureRotated', False)

            if rotated:
                # 当rotated = True时，先用对调的(width, height)截取
                sub_surface = self.sprite_sheet.subsurface(pygame.Rect((x, y), (height, width)))
                # 再旋转90度使之复原
                sub_surface = pygame.transform.rotate(sub_surface, 90)
            else:
                sub_surface = self.sprite_sheet.subsurface(pygame.Rect((x, y), (width, height)))

            sprites[image_name] = sub_surface

        # 给sprites进行排序，如果图片名字是数字，按数字顺序，如果图片名字不是数字的时候，按阿斯克码排序
        if self.auto_sort:
            sprites = dict(sorted(sprites.items(), key=lambda x: custom_sort_key(x[0])))
        return sprites

    def get_image(self):
        """
        根据returnType返回处理后的图片对象或对象列表。
        对png类型，根据serialNumberName返回对应Surface；
        对gif类型，返回所有frames的Surface列表。
        """
        # 缓存key，将影响图片唯一性的属性全部纳入key
        cache_key = (self.src, self.plist, self.returnType, self.serialNumberName)

        # 如果缓存中已有
        if cache_key in __cache__:
            __cache__[cache_key]['visit'] += 1
            # print(f"从缓存中加载{cache_key}成功")
            return __cache__[cache_key]['object'].copy()

        if self.returnType == "png":
            if isinstance(self.serialNumberName, str):  # 如果self.serialNumberName是字符串
                for key, value in self.sprites.items():
                    if key == self.serialNumberName:
                        result = value
            elif isinstance(self.serialNumberName, int):  # 如果self.serialNumberName是整数
                result = list(self.sprites.values())[self.serialNumberName]
            else:
                raise ValueError("serialNumberName未指定或在plist中未找到")
        elif self.returnType == "gif":
            # 返回所有frame的列表
            result = list(self.sprites.values())
        else:
            raise ValueError("无效的returnType，请选择 'png' 或 'gif' ")

        # 存入缓存并设置访问次数
        __cache__[cache_key] = {
            'object': result,
            'visit': 1
        }

        return result


class URLImageLoader:
    """URL图片加载器"""
    def __init__(self, download_folder: str = 'downloads'):
        self.download_folder = download_folder
        # 确保下载文件夹存在
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    @staticmethod
    def _generate_filename(url: str) -> str:
        """根据URL生成MD5哈希值作为文件名，并尝试智能地识别文件扩展名"""
        parsed_url = urlparse(unquote(url))  # 对URL进行解码
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        # 识别常见的图片文件扩展名，否则默认使用.png
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            endswith = ext
        else:
            endswith = '.png'
        # 生成MD5哈希值作为文件名
        name = hashlib.md5(url.encode('utf-8')).hexdigest()[:6] + endswith
        debug(f"下载文件名：{name}")
        return name

    @staticmethod
    def _download_with_progress(url: str, path: str):
        """使用tqdm显示下载进度条"""
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(path, 'wb') as file, tqdm(
                desc=path,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

    def download_image(self, url: str) -> Union[str, None]:
        """下载图片，返回本地存储路径"""
        filename = self._generate_filename(url)
        path = os.path.join(self.download_folder, filename)
        if os.path.exists(path):  # 文件已存在则直接返回
            debug(f"文件{path}已存在！直接返回文件路径！")
            return path
        try:
            self._download_with_progress(url, path)
            return path
        except Exception as e:
            debug(f"下载{url}时出错，错误提示: {e}", 2, 404)
            return None

    def load_image(self, url: str, flipOver: str = "") -> pygame.Surface:
        """
        下载或从缓存(本地文件)加载图片，返回pygame Surface对象。
        支持通过flipOver参数进行翻转：
        - flipOver = 'horizontal' 进行水平翻转
        - flipOver = 'vertical'   进行垂直翻转
        - flipOver = ''           不翻转
        """
        path = self.download_image(url)
        if path:
            try:
                image = pygame.image.load(path)
                # 根据flipOver参数决定是否翻转
                flipOver = flipOver.lower()
                if flipOver == "horizontal":
                    image = pygame.transform.flip(image, True, False)
                elif flipOver == "vertical":
                    image = pygame.transform.flip(image, False, True)
                return image
            except pygame.error as e:
                debug(f"加载图像{path}时出错，错误提示：{e}", 2, 101)

        # 加载失败返回一个白色背景图像作为回退
        surface = pygame.Surface((100, 100))
        surface.fill((255, 255, 255))
        return surface


class Sprite(pygame.sprite.Sprite):
    load_url_picture = URLImageLoader()  # 加载图片的URL下载器

    def __init__(self, src: pygame.Surface | str, x: float = 100, y: float = 100, w: float = None, h: float = None,
                 scale: float = 1.0, is_center: bool = True, mask_draw: bool = False, **kwargs):
        """
        精灵类
        :param src: 图片路径或图片对象
        :param x: 图片的x坐标
        :param y: 图片的y坐标
        :param w: 图片的宽度，传入后，会优先进先使用传入的宽高，如果不传入，则使用图片的宽高
        :param h: 图片的高度，传入后，会优先进先使用传入的宽高，如果不传入，则使用图片的宽高
        :param scale: 图片的缩放倍数，只能等比缩放，如果同时传入宽高，那么此参数无效
        :param is_center: 是否居中，如果居中，那么x，y坐标会自动变为图片的中心坐标
        :param mask_draw: 是否采用遮罩形式来绘制图片，默认为False
        :param kwargs: 可以额外传入的参数
            alpha: 图片的透明度，0-255，默认为255
            frame_duration：动画帧间隔时间，单位毫秒，仅对于GIF图片有效，默认值：100ms/fps
            gif_count: GIF图片播放的轮次，-1为无限循环，写上次数后，如果图片播放完毕，会删除这个角色回收，默认值：-1
                注意：图片回收仅对pygame的group有效
            mask_shape: 遮罩形式，支持圆形或者矩形，默认为圆形，参数("circle", "rectangle", "custom")，需要先支持遮罩
            mask_rect_radius: 传入的矩形遮罩圆角，需要遮罩形式为rectangle
            mask_custom_shap: 遮罩形状，如果传入了这个选项，会使用传入的形状作为遮罩形状，请确保类型一定是pygame.Surface,否则此项无效
            flipOver: 是否进行翻转，支持两个参数：水平翻转(Horizontal)、垂直翻转(Vertical)，参数("Horizontal", "Vertical")
            pvrCcz: 是否是pvr图片，是的话表示可能是一个多序列帧结合的png，单独写读取来得到图片
        """
        super().__init__()
        # print(__cache__)
        self.frame_duration = kwargs.get("frame_duration", 100)  # 图片帧间隔时间，单位毫秒，默认为100毫秒/帧
        self.flipOver = kwargs.get("flipOver", "")  # 图片翻转，支持两个参数：水平翻转(Horizontal)、垂直翻转(Vertical)
        self.gif_count = kwargs.get("gif_count", -1)  # 写了次数后，次数到了，图片播放完毕后，删除这个角色并回收
        self.is_pvr = kwargs.get("pvrCcz", False)  # 是否是pvr图片，是的话表示可能是一个多序列帧结合的png，单独写读取来得到图片
        self.kwargs = kwargs  # 其它参数

        self.is_center = is_center  # 是否居中
        self.is_gif = False  # 是否是GIF图片
        self.mask_draw = mask_draw  # 是否采用遮罩形式来绘制图片
        self.convert_alpha = False

        self.angle = 0  # 图片的旋转角度，初始在0度，与图片面朝方向有关
        self.facingAngle = kwargs.get("facingAngle", 0)  # 图片面向的角度，与图片的旋转角度有关
        self.alpha = kwargs.get("alpha", 255)  # 图片的透明度,范围为0-255，其中0为完全透明，255为完全不透明，默认255

        self.name = src if isinstance(src, str) else None
        self.original_image = src if isinstance(src, pygame.Surface) \
            else self.__load_src(src)  # 如果是图片路径则加载图片，否则认为是图片对象
        self.scaled_image = self.original_image.copy()
        self.image = self.scaled_image

        self.mask = pygame.mask.from_surface(self.image)  # 图片的蒙版，用于精确像素级碰撞检测

        self.x, self.y = x, y
        self.w, self.h = self.original_image.get_width(), self.original_image.get_height()
        self.scale = scale if not w and not h else 1.0  # 图片的缩放倍数，传入了宽高，那么缩放倍数无效
        # 如果大小有变化，直接调用一次缩放
        if w or h:
            self.set_size((w or self.w, h or self.h))
        elif self.scale != 1.0:  # 如果同时传入了缩放倍数和大小，那么就取大小参数，此时，缩放倍数无效
            self.set_size(self.scale)
        self.rect = self.image.get_rect()
        self.__update_rect_x_y()

        if self.mask_draw:  # 采用遮罩的模式来绘制图片，当采用遮罩绘制后，会转换绘制图片，此时draw只绘制遮罩区域
            self._load_mask(**kwargs)

        self.audio_update = kwargs.get("update", False)  # gif图片是否绘制就自己更新

        self.moving_to = None  # 移动的目标坐标
        self.edge = 0  # 碰到窗口边缘的次数，加上这个参数，方便让角色碰到边缘n次后消失3

        if not self.is_gif:  # 是GIF已经被缓存好了图片的帧，这里如果在加载完毕后不是GIF，那么就保存图片的帧
            if not self.convert_alpha:
                try:
                    self.image = self.scaled_image.convert_alpha()  # 转换为带alpha通道的图片
                    self.convert_alpha = True
                except Exception as e:
                    debug(f"图片{src}转换为alpha通道失败，错误提示：{e}", 2, 103)

        debug(f"角色创建成功，图片名字：{self.name}, 位置：{self.x}, {self.y}，宽高：{self.w}, {self.h}")

    @staticmethod
    def __flip_resource(resource, flipOver: str):
        """对加载的资源进行翻转处理"""
        horizontal = (flipOver == "horizontal")
        vertical = (flipOver == "vertical")

        # 如果缓存当中存在翻转的图片，那么直接返回，否则就生成新的图片，并缓存起来
        cache_key = f"{flipOver}_{resource}"
        if cache_key in __cache__:
            return __cache__[cache_key]

        if isinstance(resource, list):
            # GIF帧列表翻转
            return [pygame.transform.flip(frame, horizontal, vertical) for frame in resource]
        else:
            # 单张Surface翻转
            return pygame.transform.flip(resource, horizontal, vertical)

    def __update_rect_x_y(self, x: int | float = None, y: int | float = None, mask_update: bool = False):
        """更新rect的x，y坐标"""
        if self.is_center:
            self.rect.center = x or self.x, y or self.y
        else:
            self.rect.x, self.rect.y = x or self.x, y or self.y
        # 重新生成mask
        if mask_update:
            self.mask = pygame.mask.from_surface(self.image)

    def __load_url(self, src: str) -> pygame.Surface:
        """传入图片路径，返回图片对象"""
        if validators.url(src):
            return self.load_url_picture.load_image(src)

    def __load_gif(self, src: str) -> pygame.Surface:
        self.is_gif = True
        self.frames_index = 0
        self.last_frame_update_time = pygame.time.get_ticks()

        if src in __cache__ and isinstance(__cache__[src]['object'], list):
            self.frames = __cache__[src]['object'].copy()
            __cache__[src]['visit'] += 1
            debug(f"从缓存中加载GIF：{src}，访问次数：{__cache__[src]['visit']}")
        else:
            image = Image.open(src)
            self.frames = []
            for frame_index in tqdm(range(image.n_frames), desc=f"加载{src}的GIF帧: "):
                image.seek(frame_index)
                frame = image.convert("RGBA")
                frame_pygame = pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA')
                self.frames.append(frame_pygame)

            __cache__[src] = {"object": self.frames, "visit": 1}
            debug(f"从文件中缓存GIF：{src}，总帧数：{len(self.frames)}")

        self.original_frames = self.frames.copy()
        self.frames_length = len(self.frames)
        return self.frames[0]

    def __load_pvr(self, src: str) -> pygame.Surface:
        returnType = self.kwargs.get("returnType", "gif")
        picture = PvrCczLoader(src, src.split(".")[0] + ".plist", returnType, self.kwargs.get("serialNumberName", ""),
                               auto_sort=self.kwargs.get("auto_sort", False))
        return picture.get_image()  # 获取图片，在PvrCczLoader里面会自动缓存，这里不必重新加载

    def __load_src(self, src: str, flipOver: str = "") -> pygame.Surface:
        global __cache__

        # 根据是否有翻转需求生成 flip_key
        flipOver = flipOver.lower() or self.flipOver.lower()
        if flipOver in ["horizontal", "vertical"]:
            flip_key = f"{src}|flip={flipOver}"
        else:
            flip_key = src

        # 如果缓存中有翻转或未翻转版本的资源，直接返回
        if flip_key in __cache__:
            __cache__[flip_key]['visit'] += 1
            debug(f"从缓存中加载图片：{flip_key}，此图片现访问次数：{__cache__[flip_key]['visit']}")
            cached_obj = __cache__[flip_key]['object'].copy()  # 拷贝对象，防止修改缓存对象
            return self.__handle_cached_object(cached_obj)

        # 缓存中没有对应版本的资源时，先尝试原始src（未翻转）的缓存
        # 如果 flip_key 就是 src，说明不需要翻转；如果 flip_key != src，表示需要翻转，此时先取原始资源
        original_cached_obj = None
        if src in __cache__:
            __cache__[src]['visit'] += 1
            debug(f"从缓存中加载图片：{src}，此图片现访问次数：{__cache__[src]['visit']}")
            original_cached_obj = __cache__[src]['object'].copy()
        else:
            # 原始资源不在缓存中则加载
            if validators.url(src):
                original_cached_obj = self.__load_url(src)
            elif not os.path.exists(src):
                debug(f"图片路径{src}不存在，", 2, 100)
                ima = pygame.Surface((100, 100))
                ima.fill((255, 255, 255))
                original_cached_obj = ima
            elif self.is_pvr:
                original_cached_obj = self.__load_pvr(src)
            elif src.lower().endswith((".png", ".jpg")):
                image = pygame.image.load(src)
                debug(f"从文件当中加载图片{src}，图片大小：{image.get_size()}")
                original_cached_obj = image
                # 加载后立即缓存原版资源
                __cache__[src] = {"object": original_cached_obj, "visit": 1}
                # 检查缓存大小，必要时进行清理
                if __count_cache_size__() > __MAX_CACHE_SIZE__:
                    __del_cache__()
                    debug(f"缓存大小超过最大限制的{__MAX_CACHE_SIZE__}，自动清理缓存...")
            elif src.lower().endswith(".gif"):
                # 加载GIF帧列表
                original_cached_obj = self.__load_gif(src)
                # __load_gif 已经对 __cache__ 写入了原版frames
            else:
                # 处理其他不支持的格式，同样返回一个占位白色图像
                debug(f"未识别的图片格式{src}", 2, 100)
                ima = pygame.Surface((100, 100))
                ima.fill((255, 255, 255))
                original_cached_obj = ima
                __cache__[src] = {"object": original_cached_obj, "visit": 1}

        # 此时original_cached_obj为原版资源(单张图片或帧列表)
        # 如果需要翻转，则在这里对original_cached_obj进行翻转
        if flipOver in ["horizontal", "vertical"]:
            flipped_obj = self.__flip_resource(original_cached_obj, flipOver)
            __cache__[flip_key] = {"object": flipped_obj, "visit": 1}
            return self.__handle_cached_object(flipped_obj)
        else:
            # 不需要翻转，直接返回原始资源
            if src not in __cache__:  # 如果原始资源之前没有入缓存（如URL加载时），则在这里入缓存
                __cache__[src] = {"object": original_cached_obj, "visit": 1}
            return self.__handle_cached_object(original_cached_obj)

    def __handle_cached_object(self, cached_obj):
        """根据缓存的对象类型，初始化GIF属性或返回单帧Surface"""
        if isinstance(cached_obj, list):
            # GIF帧列表
            self.is_gif = True
            self.frames = cached_obj
            self.frames_index = 0
            self.last_frame_update_time = pygame.time.get_ticks()
            self.frames_length = len(self.frames)
            self.original_frames = self.frames.copy()
            return self.frames[0]
        else:
            # 单张Surface
            return cached_obj

    def _load_mask(self, **kwargs):
        if not self.convert_alpha:
            self.image = self.image.convert_alpha()
            self.MImage = self.image.copy()  # 转换为alpha格式
            self.convert_alpha = True
        else:
            self.MImage = self.scaled_image.copy()
        mask_surface = pygame.Surface(self.scaled_image.get_size(), pygame.SRCALPHA)  # 创建一个与图片大小相同的透明蒙版
        mask_surface.fill((0, 0, 0, 0))
        center = (self.scaled_image.get_width() // 2, self.scaled_image.get_height() // 2)
        shape = kwargs.get("mask_shape").lower()
        if not shape:
            debug("没有找到遮罩类型，不支持遮罩，已经正常处理... ...")
            return  # 如果没有指定遮罩类型，则不进行遮罩处理
        if shape == "rectangle":  # 绘制矩形蒙版
            radius = kwargs.get("mask_rect_radius", 0)
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, self.MImage.get_width(),
                             self.MImage.get_height()), border_radius=radius)
            debug(f"遮罩参数: {mask_surface}, rect: {self.MImage.get_size()}, 圆角半径: {radius}")
        elif shape == "custom" and kwargs.get("mask_custom_shap"):
            mask_surface = kwargs.get("mask_custom_shap")
            # 检查mask_surface是不是pygame.Surface类型，如果不是，遮罩无效
            if not isinstance(mask_surface, pygame.Surface):
                debug("自定义遮罩必须是pygame.Surface类型，遮罩无效")
                return
        else:
            radius = min(self.image.get_width(), self.image.get_height()) // 2
            debug(f"{'不支持类型，' if shape != 'circle' else ''}使用圆形遮罩", 2, 102)
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), center, radius)
        self.MImage.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # 应用蒙版

    def rotation(self, angle: int | float = None, pivot: tuple = None) -> None:
        """
        围绕指定pivot点进行旋转。pivot是全局坐标中的一个固定点，不会随着图片变化而改变。
        :param angle: 要旋转的角度（度）。正数为逆时针旋转, 负数则顺时针。
        :param pivot: 用于旋转的基准点(全局坐标), 图片将围绕此点旋转。若不传, 使用图片中心点。
        """
        if angle is None or angle == 0:
            return

        if pivot is None:
            # 如果没有指定pivot，就默认以图片当前中心为参考点
            pivot = self.rect.center

        # 获取当前图片中心点(全局坐标)
        old_center = self.rect.center
        # 计算pivot到图片中心的偏移向量
        offset = pygame.math.Vector2(old_center[0] - pivot[0], old_center[1] - pivot[1])

        # 更新累计旋转角度
        self.angle += angle

        if not self.is_gif:
            self.image = pygame.transform.rotate(self.scaled_image, self.angle)
        else:
            self.frames = [pygame.transform.rotate(frame, self.angle) for frame in self.original_frames]
            self.image = self.frames[self.frames_index]
        # 计算新的中心位置
        offset = offset.rotate(angle)
        new_center = (pivot[0] + offset.x, pivot[1] + offset.y)
        self.rect = self.image.get_rect(center=new_center)

        self.__update_rect_x_y(mask_update=True)  # 更新rect_x和rect_y

    def move_to(self, x: int | float = None, y: int | float = None,
                timeConsumption: float = 1, fps: int | float = None) -> None:
        """
        在timeConsumption时间内，将图片移动到x，y位置, 单位：秒
        :param x: 传入的x坐标，不传入，那么默认为原x位置不变
        :param y: 传入的y坐标，不传入，那么默认为原y位置不变
        :param timeConsumption: 移动的时间，单位为秒
        :param fps: 每秒帧数
        :return: None
        """
        if not fps:  # 如果没传入fps，那么默认为pygame.time.get_ticks()
            fps = pygame.time.get_ticks()  # 获取每秒帧数
        total_frames = timeConsumption * fps  # 在指定时间内需要的总帧数
        x, y = x or self.x, y or self.y  # 如果没有传入x和y，那么默认为原x或者y位置不变
        if self.is_center:  # 如果图片是居中模式，那么计算中心点的偏移量
            dx = (x - self.rect.centerx) / total_frames  # 每帧在x方向上移动的距离
            dy = (y - self.rect.centery) / total_frames  # 每帧在y方向上移动的距离
        else:  # 否则，计算左上角的偏移量
            dx = (x - self.rect.x) / total_frames
            dy = (y - self.rect.y) / total_frames
        self.moving_to = {'target': (x, y), 'frames_left': total_frames, 'dx': dx, 'dy': dy}  # 设置移动的目标
        debug(f"图片将从({self.x}, {self.y})移动到({x}, {y})，移动需要时间：{timeConsumption}秒，每秒帧数：{fps}")

    def move_in_direction(
            self,
            window: pygame.Surface = None,
            speed: Union[float, int] = 1.0,
            rebound: bool = False,
            direction_source=None,
    ):
        """
        根据当前的角度移动精灵，并根据参数决定是否在碰到边缘时反弹。
        如果传入 direction_source，则按该对象的面向方向移动。
        如果窗口为None，不执行边缘检测。

        :param window: 窗口Surface对象，用于获取边缘位置，如果为None，则不进行边缘检测。
        :param speed: 每帧移动的速度，以像素为单位。
        :param rebound: 如果为True，在碰到边缘时反弹。
        :param direction_source: 用于指定移动方向的对象，如果为None或者传入的对象没有angle属性，则使用自身的角度。
        """

        def calculate_angle(sprite, mouse_pos):
            dx = mouse_pos[0] - sprite.x
            dy = sprite.y - mouse_pos[1]  # 反转y轴
            angle = math.degrees(math.atan2(dy, dx))
            angle %= 360
            return angle
        # 确定使用哪个角度，如果传入的direction_source没有angle方法，或者什么都没有传入，则使用自己的angle
        if direction_source is None or not hasattr(direction_source, 'angle'):
            current_angle = (self.facingAngle + self.angle) % 360
        else:
            current_angle = direction_source.angle

        # 计算移动的x和y增量
        dx = math.cos(math.radians(current_angle)) * speed
        dy = -math.sin(math.radians(current_angle)) * speed  # pygame的y轴向下

        self.x += dx
        self.y += dy

        if window is not None and rebound:
            # 获取精灵矩形的边界
            left, top, right, bottom = self.rect.left, self.rect.top, self.rect.right, self.rect.bottom

            # 检查是否碰到窗口的边缘，并相应地调整位置和角度
            if left + dx < 0 or right + dx > window.get_width():
                self.edge += 1  # 记录一次反弹
                self.angle = 180 - self.angle  # 水平边界反弹
                self.x = max(self.rect.width / 2, min(self.x, window.get_width() - self.rect.width / 2))  # 防止移出窗口

            if top + dy < 0 or bottom + dy > window.get_height():
                self.edge += 1
                self.angle = -self.angle  # 垂直边界反弹
                self.y = max(self.rect.height / 2, min(self.y, window.get_height() - self.rect.height / 2))  # 防止移出窗口

            # 确保角度在0-360度之间
            self.angle %= 360

        # 根据新的self.x和self.y更新rect的位置
        if self.is_center:
            self.rect.center = (self.x, self.y)
        else:
            self.rect.x, self.rect.y = self.x, self.y

    def face_towards(self, target_surface: pygame.Surface = None, window: pygame.Surface = None, direction: float = 0, limit: tuple[float, float] = None):
        """
        使角色面向给定的Surface对象的方向，如果没有给定Surface对象，则面向鼠标指针的方向。
        :param target_surface: 需要面向的Surface对象，如果为None，则面向鼠标指针。
        :param window: 当前的窗口Surface对象，用于获取鼠标位置，仅当target_surface为None时需要。
        :param direction: 初始的方向，默认为0度，可以为负数。
        :param limit: 限制角度的范围，例如(-75, 75)表示限制在-75到75度之间，不传入默认不限制。
        """
        if target_surface is not None:
            # 计算目标Surface的中心点坐标
            target_rect = target_surface.get_rect()
            target_x, target_y = target_rect.centerx, target_rect.centery
        elif window is not None:
            # 获取鼠标当前的位置
            target_x, target_y = pygame.mouse.get_pos()
        else:
            return  # 如果没有给定Surface也没有给定window，则不执行任何操作

        # 计算角色中心到目标点的向量
        dx = target_x - self.x
        dy = target_y - self.y

        angle_radians = math.atan2(-dy, dx)  # pygame的y轴向下，所以这里用-dy，使用atan2反正切函数，计算角度
        angle_degrees = math.degrees(angle_radians)  # 使用degrees函数将弧度转换为度

        # 应用方向调整
        angle_degrees += direction

        # 规范化角度到(-180, 180]
        angle_degrees = (angle_degrees + 180) % 360 - 180

        if limit:
            min_limit, max_limit = limit

            # 规范化限制范围到(-360, 360)
            min_limit = (min_limit + 360) if min_limit < -360 else (min_limit - 360 if min_limit > 360 else min_limit)
            max_limit = (max_limit + 360) if max_limit < -360 else (max_limit - 360 if max_limit > 360 else max_limit)

            # 规范化角度和限制范围到(-180, 180]
            min_limit = (min_limit + 180) % 360 - 180
            max_limit = (max_limit + 180) % 360 - 180

            if min_limit <= max_limit:
                # 简单范围，如(-75, 75)
                if angle_degrees < min_limit:
                    angle_degrees = min_limit
                elif angle_degrees > max_limit:
                    angle_degrees = max_limit
            else:
                if max_limit < angle_degrees < min_limit:
                    # 选择离当前角度最近的边界
                    dist_to_min = abs(angle_degrees - min_limit)
                    dist_to_max = abs(angle_degrees - max_limit)
                    if dist_to_min < dist_to_max:
                        angle_degrees = min_limit
                    else:
                        angle_degrees = max_limit
        self.angle = angle_degrees

    def _flip_image(self, flip_type: str, src: str = None) -> None:
        """
        私有方法，用于处理图像翻转逻辑。
        :param flip_type: 翻转类型，'horizontal' 或 'vertical'
        :param src: 可选，图像源
        """
        size = self.w, self.h
        try:
            if self.flipOver.lower() == flip_type:
                # 如果已经是指定翻转类型，则恢复原图
                self.__load_src(src or self.name, "NULL")
            else:
                # 应用指定的翻转
                self.__load_src(src or self.name, flip_type)
            self.set_size(size)
        except Exception as e:
            if not self.is_gif:
                debug(f"错误提示{e}\n, 原图片翻转失败，尝试重新翻转 ... ...", 2)
                try:
                    if flip_type == "horizontal":
                        flipped = pygame.transform.flip(self.scaled_image, True, False)
                    else:
                        flipped = pygame.transform.flip(self.scaled_image, False, True)
                    self.set_size(size, flipped)
                    self.mask = pygame.mask.from_surface(self.image)
                except Exception as e:
                    debug(f"错误提示{e}\n, 翻转失败，请检查图片是否正确，此次翻转无效 ... ...")
                    return
            else:
                debug(f"翻转{flip_type.upper()} GIF图片出现了未知错误，已停止翻转 ... ...")
                return

    def horizontalFlip(self, src: str = None) -> None:
        """
        水平翻转图像。
        :param src: 可选，图像源
        """
        self._flip_image("horizontal", src)
        self.flipOver = "horizontal"

    def verticalFlip(self, src: str = None) -> None:
        """
        垂直翻转图像。
        :param src: 可选，图像源
        """
        self._flip_image("vertical", src)
        self.flipOver = "vertical"

    def set_img(self, img: pygame.Surface | str = None, only_src: bool = True, **kwargs):
        if not img:
            return
        new_surface = img if isinstance(img, pygame.Surface) else self.__load_src(img)  # 新的图

        # -- 关键：把 original_image / scaled_image 都更新 --
        self.original_image = new_surface
        self.scaled_image = new_surface.copy()
        self.image = self.scaled_image
        self.mask = pygame.mask.from_surface(self.image)  # 如果你需要蒙版进行碰撞

        # 如果你原本的代码还有“是否使用蒙版绘制”的逻辑，就继续
        if self.mask_draw:
            self._load_mask(**kwargs)

        # 这里看你需求，如果要保持旧的大小和位置就执行，否则就不要动
        if only_src:
            self.set_size((kwargs.get("w", self.w), kwargs.get("h", self.h)))
            self.set_pos(kwargs.get("x", self.x), kwargs.get("y", self.y))

    def set_pos(self, x: int | float = None, y: int | float = None) -> None:
        """
        设置图片的位置，如果没有传入x和y，那么默认为原x或者y位置不变
        :param x: 传入的x坐标
        :param y: 传入的y坐标
        :return: None
        """
        self.x, self.y = x or self.x, y or self.y
        self.__update_rect_x_y(x, y)

    def set_alpha(self, alpha: int | float) -> None:
        """设置图片的透明度，范围为0-255，其中0为完全透明，255为完全不透明"""
        self.alpha = max(0, min(255, int(alpha)))  # 设置透明度,使用max和min可以确保透明度在0-255之间，不允许小于0，不允许大于255
        self.image.set_alpha(self.alpha)
        self.original_image.set_alpha(self.alpha)

    def set_size(self, size: tuple[int | float, int | float] | float | int, image=None) -> None:
        """
        图片的缩放
        :param size: 传入元组或者一个数字(小数、整数)，如果传入元组，表示缩放的大小，如果传入一个数字，表示缩放的比例(等比)
        :param image: 基于什么图片缩放,仅支持非GIF图片
        :return: None
        """

        def __size():
            # 根据size类型决定如何缩放
            if isinstance(size, tuple):
                self.frames[i] = pygame.transform.scale(frame, size)
            elif isinstance(size, float) or isinstance(size, int):
                # 计算每一帧的缩放大小进行缩放
                frame_size = frame.get_size()
                new_w = int(frame_size[0] * size)
                new_h = int(frame_size[1] * size)
                self.frames[i] = pygame.transform.scale(frame, (new_w, new_h))

        # 如果缩放倍数是1，表示不缩放
        if isinstance(size, float) or isinstance(size, int):
            if size == 1:
                return
        # 如果传入的宽高不变，那么不缩放
        # if isinstance(size, tuple) and size == (self.w, self.h):
        #     return

        debug(f"正在缩放图片... 参数：{size}, 图片名字：{self.name}", 1)

        if self.is_gif:
            # 估算内存：每个像素 4 字节(RGBA)，累计所有帧的大小
            frames_count = len(self.frames)
            total_memory = 0
            for f in self.frames:
                w, h = f.get_size()
                total_memory += w * h * 4  # 4 字节每像素
            # print(f"图片内存估算为 {total_memory / 1024 / 1024:.2f} MB")

            # 判断是否显示进度条的条件
            # 同时满足：帧数>50 并且 总内存>100MB(100*1024*1024字节)
            show_progress = (frames_count > 50) and (total_memory > 102400 * 102400)

            if show_progress:
                # 使用tqdm显示进度条
                for i, frame in tqdm(enumerate(self.frames), desc=f"正在缩放GIF 图片：{self.name}", total=frames_count):
                    __size()
            else:
                # 不显示进度条，正常缩放
                for i, frame in enumerate(self.frames):
                    __size()

            # 对应的更新scale或者w和h
            if isinstance(size, float) or isinstance(size, int):
                self.scale = size
                self.w, self.h = int(self.w * self.scale), int(self.h * self.scale)
            else:
                self.w, self.h = size

            self.image = self.frames[self.frames_index]  # 更新当前显示帧为缩放后的帧
            self.rect = self.image.get_rect()  # 更新rect对象
        else:
            # 非GIF图片的缩放处理
            if isinstance(size, tuple):
                new_size = size
            elif isinstance(size, float) or isinstance(size, int):
                # 计算图片的缩放倍数
                new_size = (int(self.original_image.get_width() * size), int(self.original_image.get_height() * size))
            else:
                new_size = self.original_image.get_width(), int(self.original_image.get_height())
            # 进行缩放，保持 original_image 不变
            self.scaled_image = pygame.transform.scale(image or self.original_image, new_size)
            self.scale = size if isinstance(size, (float, int)) else 1.0
            self.w, self.h = new_size

            # 如果有旋转角度，先应用缩放，再旋转
            if self.angle != 0:
                self.image = pygame.transform.rotate(self.scaled_image, self.angle)
            else:
                self.image = self.scaled_image
            self.rect = self.image.get_rect()

        self.__update_rect_x_y(mask_update=True)  # 更新rect的位置,同时重置遮罩

    def collide_target(self, target) -> bool:
        """
        判断图片是否与目标碰撞,这个是一个简单的碰撞检测，检查的是图片的rect和目标角色的rect是否碰撞
        :param target: 目标角色
        :return: bool
        """
        return self.rect.colliderect(target.rect)

    def mask_collide_target(self, target) -> bool:
        """
        像素碰撞检测
        :param target: 目标角色
        :return: bool
        """
        # 假设self.mask和target.mask都是有效的pygame.mask.Mask对象
        offset_x = target.rect.left - self.rect.left
        offset_y = target.rect.top - self.rect.top
        return self.mask.overlap(target.mask, (offset_x, offset_y)) is not None

    def click(self, key: int = 0, warning: bool = False, error: bool = False) -> bool:
        """
        返回角色是否已经被鼠标点击了
        :param key: 鼠标的键码，0表示鼠标左键，1表示鼠标中键，2表示鼠标右键
        :param warning: 是否在键码错误的情况下警告，通常用于debug
        :param error: 是否在键码错误的情况下报错，通常不应该发生
        :return: bool
        """
        if error and key not in [0, 1, 2]:
            debug(f"无效的键码{key}，键码应该在0-2之间", 3)
            raise KeyError
        if warning and key not in [0, 1, 2]:
            debug(f"无效的键码{key}，键码应该在0-2之间", 2)
        key = max(0, min(2, int(key)))  # 将键码限制在0-2之间
        return self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[key]

    def hover(self) -> bool:
        """返回鼠标是否在角色的上方"""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def hover_mask(self) -> bool:
        """判断鼠标是否精确悬浮在了图片上"""
        mouse_pos = pygame.mouse.get_pos()  # 获取鼠标当前的位置,并用于计算鼠标位置相对于图片的坐标

        # 如果图片居中，要根据图片实际的矩形位置来调整鼠标的相对位置
        if self.is_center:
            offset_x = mouse_pos[0] - (self.rect.x + self.rect.width / 2)
            offset_y = mouse_pos[1] - (self.rect.y + self.rect.height / 2)
        else:
            offset_x = mouse_pos[0] - self.rect.x
            offset_y = mouse_pos[1] - self.rect.y

        # 检查鼠标的相对位置是否在遮罩的范围内，避免越界错误
        if 0 <= offset_x < self.mask.get_size()[0] and 0 <= offset_y < self.mask.get_size()[1]:
            # 使用遮罩检查鼠标是否悬浮在图片的非透明部分
            return self.mask.get_at((int(offset_x), int(offset_y))) != 0
        return False

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        # 如果是GIF图片，那么需要更新帧
        if self.is_gif and pygame.time.get_ticks() - self.last_frame_update_time > self.frame_duration:
            self.last_frame_update_time = pygame.time.get_ticks()  # 更新上一帧更新的时间
            self.frames_index = (self.frames_index + 1) % self.frames_length  # 更新当前帧
            self.image = self.frames[self.frames_index]  # 更新当前帧图片
            self.rect = self.image.get_rect()  # 获取新帧的rect

            # 保持位置不变，根据is_center设置正确的位置
            if self.is_center:
                self.rect.center = (self.x, self.y)
            else:
                self.rect.x, self.rect.y = self.x, self.y

            if self.frames_index == 0:
                self.gif_count -= 1
                if self.gif_count == 0:  # 如果GIF图片播放结束，那么回收这个图片，删除此类
                    self.kill()  # 回收，注意，回收仅对于pygame的group有效，其它无效
                    debug(f"GIF帧结束，因此角色已经开启了播放回收，该角色回收完毕！")

        if self.moving_to:
            if self.moving_to['frames_left'] > 1:
                # 实时更新self.x和self.y，然后基于它们更新rect.center
                self.x += self.moving_to['dx']
                self.y += self.moving_to['dy']
                self.moving_to['frames_left'] -= 1
            else:
                # 最后一步，确保self.x和self.y与目标位置完全匹配
                self.x, self.y = self.moving_to['target']
                self.moving_to = None  # 清除移动目标，移动完成

        # 更新rect.center以反映self.x和self.y的最新值
        self.__update_rect_x_y()

    def draw(self, window: pygame.Surface):
        if self.mask_draw:
            window.blit(self.MImage, self.rect)
        else:
            window.blit(self.image, self.rect)


__all__ = ["Sprite", "load_picture", "PvrCczLoader"]
