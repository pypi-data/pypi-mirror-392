import pygame
from pathlib import Path
import time


def ensure_mixer():
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"pygame.mixer init failed: {e}")


def stop_all_sounds():
    ensure_mixer()
    pygame.mixer.stop()


class SoundManager:
    def __init__(self):
        self.sound_library = {}
        # 使用字典存储每个文件路径对应的键和通道
        self.channels = {}
        # 用于生成唯一键的计数器
        self.key_counters = {}
        # 用于记录播放顺序，方便停止最近播放的声音
        self.play_order = []
        # 序列播放队列
        self.sequence_queue = []
        self.current_sound_channel = None
        # 调度播放列表，存储 (scheduled_time, path, voice, times)
        self.scheduled_plays = []

    def load_sound(self, path):
        """ 加载声音文件到声音库 """
        try:
            ensure_mixer()
            if isinstance(path, str):
                path = Path(path)
            elif not isinstance(path, Path):
                raise TypeError("path must be a string or a Path object")

            if path not in self.sound_library:
                self.sound_library[path] = pygame.mixer.Sound(path)
            # 初始化该文件的键计数器
            if path not in self.key_counters:
                self.key_counters[path] = 0
        except pygame.error as e:
            print(f"Error loading sound from {path}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def generate_unique_key(self, path):
        """ 生成唯一键 """
        if isinstance(path, str):
            path = Path(path)
        unique_key = f"{path.stem}_{self.key_counters[path]}"
        self.key_counters[path] += 1
        return unique_key

    def play_sound(self, path, voice: float = 1.0, times: int = 1):
        """
        播放单个声音文件
        :param path: 传入声音文件路径，可以是字符串或 Path 对象
        :param voice: 传入声音大小（0-100）
        :param times: 传入播放次数，如果为0表示无限循环播放
        :return: 返回唯一键
        """
        # 确定路径对象
        if isinstance(path, str):
            actual_path = Path(path)
        elif isinstance(path, Path):
            actual_path = path
        else:
            raise TypeError("path must be a string or a Path object")

        ensure_mixer()
        # 加载声音（如果尚未加载）
        if actual_path not in self.sound_library:
            self.load_sound(actual_path)

        sound = self.sound_library.get(actual_path)
        if sound:
            # 生成唯一键
            unique_key = self.generate_unique_key(actual_path)
            # 计算 loops 参数
            loops = times - 1 if times > 0 else -1
            # 播放声音
            channel = sound.play(loops)
            if channel:
                # 设置音量，确保在0.0到1.0之间
                voice = max(0.0, min(voice / 100 if voice > 1 else voice, 1.0))
                channel.set_volume(voice)
                # 存储键与通道的映射
                if actual_path not in self.channels:
                    self.channels[actual_path] = {}
                self.channels[actual_path][unique_key] = channel
                # 记录播放顺序
                self.play_order.append((actual_path, unique_key))
                return unique_key
        return None

    def schedule_play_sound(self, path, voice: float = 1.0, times: int = 1, delay: float = 1.0):
        """
        调度在延时后播放声音
        :param path: 声音文件路径，可以是字符串或 Path 对象
        :param voice: 声音大小
        :param times: 播放次数，0表示无限循环
        :param delay: 延时（秒）
        """
        scheduled_time = time.time() + delay
        self.scheduled_plays.append((scheduled_time, path, voice, times))
        print(f"Scheduled to play {path} in {delay} seconds.")

    def stop_sound(self, path, unique_key: str = None):
        """
        停止单个声音文件
        :param path: 声音文件路径，可以是字符串或 Path 对象
        :param unique_key: 唯一键，如果不提供则停止最近播放的该文件声音
        """
        ensure_mixer()
        actual_path = path if isinstance(path, Path) else Path(path)
        # print(f"字典：{self.channels}，传入的path：{path}，类型：{type(path)}，传入的unique_key：{unique_key}")
        if actual_path in self.channels and self.channels[actual_path]:
            if unique_key:
                # 停止指定键的声音
                channel = self.channels[actual_path].get(unique_key)
                if channel:
                    channel.stop()
                    del self.channels[actual_path][unique_key]
                    # 从播放顺序中移除
                    if (actual_path, unique_key) in self.play_order:
                        self.play_order.remove((actual_path, unique_key))
            else:
                # 停止最近播放的声音
                for i in range(len(self.play_order)-1, -1, -1):
                    p, k = self.play_order[i]
                    if p == actual_path:
                        channel = self.channels[actual_path].get(k)
                        if channel:
                            channel.stop()
                            del self.channels[actual_path][k]
                            self.play_order.pop(i)
                            break

    def stop_last_sound(self):
        """
        停止最近播放的任意声音
        """
        if self.play_order:
            path, unique_key = self.play_order.pop()
            if path in self.channels and unique_key in self.channels[path]:
                self.channels[path][unique_key].stop()
                del self.channels[path][unique_key]

    def pause_sound(self, path, unique_key: str = None):
        """ 暂停单个声音 """
        ensure_mixer()
        actual_path = path if isinstance(path, Path) else Path(path)
        if actual_path in self.channels and self.channels[actual_path]:
            if unique_key:
                channel = self.channels[actual_path].get(unique_key)
                if channel:
                    channel.pause()
            else:
                for i in range(len(self.play_order)-1, -1, -1):
                    p, k = self.play_order[i]
                    if p == actual_path:
                        channel = self.channels[actual_path].get(k)
                        if channel:
                            channel.pause()
                            break

    def recovery_sound(self, path, unique_key: str = None):
        """ 恢复单个暂停的声音 """
        ensure_mixer()
        actual_path = path if isinstance(path, Path) else Path(path)
        if actual_path in self.channels and self.channels[actual_path]:
            if unique_key:
                channel = self.channels[actual_path].get(unique_key)
                if channel:
                    channel.unpause()
            else:
                for i in range(len(self.play_order)-1, -1, -1):
                    p, k = self.play_order[i]
                    if p == actual_path:
                        channel = self.channels[actual_path].get(k)
                        if channel:
                            channel.unpause()
                            break

    def play_sounds_in_sequence(self, path_list: list):
        """ 按顺序播放一系列声音 """
        self.sequence_queue = path_list.copy()
        self._play_next_in_sequence()

    def _play_next_in_sequence(self):
        """ 播放序列中的下一个声音 """
        if self.sequence_queue:
            next_sound_path = self.sequence_queue.pop(0)
            self.play_sound(next_sound_path)
        else:
            self.current_sound_channel = None

    def is_playing(self, path, unique_key: str = None) -> bool:
        """
        检查指定的音乐是否正在播放。

        :param path: 声音文件路径，可以是字符串或 Path 对象。
        :param unique_key: 可选的唯一键，如果提供，则检查特定的声音是否正在播放。
        :return: 如果指定的声音正在播放，返回 True；否则返回 False。
        """
        ensure_mixer()
        # 将路径转换为 Path 对象
        actual_path = path if isinstance(path, Path) else Path(path)

        # 检查路径是否在 channels 字典中
        if actual_path not in self.channels:
            return False

        # 如果提供了 unique_key，检查特定的声音是否在播放
        if unique_key:
            channel = self.channels[actual_path].get(unique_key)
            if channel:
                return channel.get_busy()
            return False

        # 如果没有提供 unique_key，检查该路径下是否有任何声音在播放
        for channel in self.channels[actual_path].values():
            if channel.get_busy():
                return True
        return False

    def handle_event(self, event: pygame.event.Event):
        """ 处理声音播放结束事件 """
        if event.type == pygame.USEREVENT and self.current_sound_channel == event.channel:
            self._play_next_in_sequence()

    def update(self):
        """ 更新声音管理器状态 """
        current_time = time.time()
        # 处理调度播放
        for scheduled in self.scheduled_plays[:]:
            scheduled_time, path, voice, times = scheduled
            if current_time >= scheduled_time:
                self.play_sound(path, voice, times)
                self.scheduled_plays.remove(scheduled)

        # 如果有序列播放
        if self.current_sound_channel and not self.current_sound_channel.get_busy():
            self._play_next_in_sequence()


MusicManager = SoundManager()  # 音乐管理器，其他窗口可以用这个管理器播放音乐
__all__ = ['MusicManager', 'stop_all_sounds']

if __name__ == '__main__':
    pygame.init()
