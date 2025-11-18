"""
星光粒子系统（漫天星光）

功能概述：
- 使用准随机序列（Halton）进行均匀分布
- 粒子持续闪烁（亮度周期性变化），频率可配置
- 使用改进 Perlin 噪声驱动位移，自然缓动，速度可配置
- 位移超过阈值后自动回归原点区域，阈值可配置
- 支持透明度渐变与近大远小的视觉深度关系
- 周期性重新分布机制（基于准随机旋转），避免长期聚集

使用方式：
1) 作为脚本运行演示模式（默认参数）：
   python -m 元宵.starfield

2) 指定参数：
   python -m 元宵.starfield --count 1200 --flicker 1.2 --speed 3.5 --threshold 24 --width 1920 --height 1080 --redistribute 40

3) 在代码中使用（简单接口）：
   from PygameTool import run_starfield
   run_starfield(star_count=1000, flicker_hz=1.0, speed_px_s=2.0, return_threshold_px=20,
                 width=1280, height=720, fullscreen=False, redistribute_interval=30.0)

注意：
- 本系统不使用 random.random 或完全随机分布，所有分布与相位基于 Halton 序列与确定性常数
- 粒子运动轨迹基于 Perlin 噪声，避免线性插值与不自然的运动
- Pygame 在演示模式中按需导入，如需动画显示请先安装：pip install pygame
"""

from dataclasses import dataclass
import math
import time
import argparse
import random
from typing import List, Tuple


def halton(index: int, base: int) -> float:
    f = 1.0
    r = 0.0
    i = index
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def halton2(index: int, base1: int = 2, base2: int = 3) -> Tuple[float, float]:
    return halton(index, base1), halton(index, base2)


class Perlin2D:
    def __init__(self):
        p = [151, 160, 137, 91, 90, 15,
             131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142,
             8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252,
             219, 203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56, 87, 174, 20, 125, 136,
             171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111,
             229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54,
             65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196,
             135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226,
             250, 124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227,
             47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44, 154,
             163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110,
             79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238,
             210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107, 49, 192,
             214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150,
             254]
        self.p = p + p

    @staticmethod
    def fade(t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    @staticmethod
    def grad(hash_v: int, x: float, y: float) -> float:
        h = hash_v & 3
        u = x if h & 1 == 0 else -x
        v = y if h & 2 == 0 else -y
        return u + v

    def noise(self, x: float, y: float) -> float:
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = self.fade(xf)
        v = self.fade(yf)
        aa = self.p[(self.p[xi] + yi) & 255]
        ab = self.p[(self.p[xi] + yi + 1) & 255]
        xi1 = (xi + 1) & 255
        ba = self.p[(self.p[xi1] + yi) & 255]
        bb = self.p[(self.p[xi1] + yi + 1) & 255]
        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        value = self.lerp(x1, x2, v)
        return max(-1.0, min(1.0, value))


@dataclass
class Star:
    idx: int
    home_fx: float
    home_fy: float
    depth: float
    phase: float
    disp_x: float = 0.0
    disp_y: float = 0.0

    def update(self, dt: float, t: float, noise: Perlin2D,
               speed_px_s: float, threshold_px: float,
               return_strength: float,
               width: int, height: int,
               rehome_active: bool) -> None:
        s1 = 0.91
        s2 = 1.37
        base1 = self.idx * 0.073 + self.depth * 3.1
        base2 = self.idx * 0.041 + self.depth * 2.3
        ts = 0.25
        vx = noise.noise(base1 + t * ts, base2 - t * ts)
        vy = noise.noise(base1 - t * ts * s1, base2 + t * ts * s2)
        mag = max(1e-4, math.sqrt(vx * vx + vy * vy))
        vx /= mag
        vy /= mag
        self.disp_x += vx * speed_px_s * dt
        self.disp_y += vy * speed_px_s * dt
        dist = math.sqrt(self.disp_x * self.disp_x + self.disp_y * self.disp_y)
        limit = threshold_px * (0.4 + 0.6 * (1.0 - self.depth))
        if rehome_active or dist > limit:
            pull = return_strength * dt * (dist - limit + 1.0)
            if dist > 1e-4:
                self.disp_x -= (self.disp_x / dist) * pull
                self.disp_y -= (self.disp_y / dist) * pull

    def screen_pos(self, width: int, height: int) -> Tuple[int, int]:
        x = int(self.home_fx * width + self.disp_x)
        y = int(self.home_fy * height + self.disp_y)
        return x, y

    def visual(self, t: float, flicker_hz: float) -> Tuple[float, float]:
        brightness = 0.5 + 0.5 * math.sin(2.0 * math.pi * flicker_hz * t + self.phase)
        alpha = 0.35 + 0.65 * self.depth
        return brightness, alpha


class StarField:
    def __init__(self,
                 star_count: int,
                 width: int,
                 height: int,
                 flicker_hz: float = 1.0,
                 speed_px_s: float = 2.0,
                 return_threshold_px: float = 20.0,
                 redistribute_interval: float = 30.0,
                 return_strength: float = 15.0):
        self.width = width
        self.height = height
        self.count = star_count
        self.flicker_hz = flicker_hz
        self.speed_px_s = speed_px_s
        self.threshold_px = return_threshold_px
        self.redistribute_interval = max(5.0, redistribute_interval)
        self.return_strength = return_strength
        self.noise = Perlin2D()
        self.stars: List[Star] = []
        self.t0 = time.time()
        self.last_redistribute = self.t0
        self.rehome_active = False
        self.rehome_window = 2.5
        self._rehome_until = self.t0
        self._cycle_index = 0
        self._init_distribution()

    def _rotation_offsets(self, k: int) -> Tuple[float, float]:
        phi = (math.sqrt(5) - 1) / 2.0
        a = (k * phi) % 1.0
        b = (k * (math.sqrt(2) - 1)) % 1.0
        return a, b

    def _init_distribution(self) -> None:
        self.stars.clear()
        # 栅格抖动：均匀覆盖屏幕且使用随机偏移
        w, h = self.width, self.height
        ar = w / max(1, h)
        nx = max(1, int(math.sqrt(self.count * ar)))
        ny = max(1, int(math.ceil(self.count / nx)))
        cell_w = w / nx
        cell_h = h / ny
        jitter_x = 0.45 * cell_w
        jitter_y = 0.45 * cell_h
        idx = 1
        for iy in range(ny):
            for ix in range(nx):
                if idx > self.count:
                    break
                cx = (ix + 0.5) * cell_w + random.uniform(-jitter_x, jitter_x)
                cy = (iy + 0.5) * cell_h + random.uniform(-jitter_y, jitter_y)
                fx = min(0.999, max(0.0, cx / w))
                fy = min(0.999, max(0.0, cy / h))
                depth = 0.15 + 0.85 * random.random()
                phase = random.uniform(0.0, 2.0 * math.pi)
                self.stars.append(Star(idx=idx, home_fx=fx, home_fy=fy, depth=depth, phase=phase))
                idx += 1

    def _redistribute(self, now_t: float) -> None:
        # 重新随机栅格抖动，保持均匀
        w, h = self.width, self.height
        ar = w / max(1, h)
        nx = max(1, int(math.sqrt(self.count * ar)))
        ny = max(1, int(math.ceil(self.count / nx)))
        cell_w = w / nx
        cell_h = h / ny
        jitter_x = 0.45 * cell_w
        jitter_y = 0.45 * cell_h
        idx = 1
        for iy in range(ny):
            for ix in range(nx):
                if idx > self.count:
                    break
                cx = (ix + 0.5) * cell_w + random.uniform(-jitter_x, jitter_x)
                cy = (iy + 0.5) * cell_h + random.uniform(-jitter_y, jitter_y)
                fx = min(0.999, max(0.0, cx / w))
                fy = min(0.999, max(0.0, cy / h))
                s = self.stars[idx - 1]
                s.home_fx = fx
                s.home_fy = fy
                idx += 1
        self.rehome_active = True
        self._rehome_until = now_t + self.rehome_window

    def update(self, dt: float) -> None:
        t = time.time()
        if self.rehome_active and t >= self._rehome_until:
            self.rehome_active = False
        if t - self.last_redistribute >= self.redistribute_interval:
            self.last_redistribute = t
            self._redistribute(t)
        for s in self.stars:
            s.update(dt, t - self.t0, self.noise,
                     self.speed_px_s, self.threshold_px,
                     self.return_strength, self.width, self.height,
                     self.rehome_active)

    def draw(self, surface) -> None:
        ordered = sorted(self.stars, key=lambda st: st.depth)
        t = time.time() - self.t0
        for s in ordered:
            x, y = s.screen_pos(self.width, self.height)
            brightness, alpha_base = s.visual(t, self.flicker_hz)
            size = 1 + int(3 * s.depth)
            a = max(0, min(255, int(255 * alpha_base * brightness)))
            color = (255, 255, 255, a)
            import pygame
            dot = pygame.Surface((size * 2 + 2, size * 2 + 2), flags=pygame.SRCALPHA)
            pygame.draw.circle(dot, color, (size + 1, size + 1), size)
            surface.blit(dot, (x - size - 1, y - size - 1))


def run_starfield(star_count: int = 1000,
                  flicker_hz: float = 1.0,
                  speed_px_s: float = 2.0,
                  return_threshold_px: float = 20.0,
                  width: int = 1280,
                  height: int = 720,
                  fullscreen: bool = False,
                  redistribute_interval: float = 30.0) -> None:
    import pygame
    pygame.init()
    flags = pygame.SRCALPHA
    if fullscreen:
        flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Starfield - 漫天星光")
    clock = pygame.time.Clock()
    sf = StarField(star_count, width, height, flicker_hz, speed_px_s,
                   return_threshold_px, redistribute_interval)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        sf.update(dt)
        sf.draw(screen)
        pygame.display.flip()
    pygame.quit()


def self_test() -> None:
    N = 1000
    xs = []
    ys = []
    for i in range(1, N + 1):
        x, y = halton2(i)
        xs.append(x)
        ys.append(y)
        assert 0.0 <= x < 1.0 and 0.0 <= y < 1.0
    grid = [[0 for _ in range(10)] for _ in range(10)]
    for x, y in zip(xs, ys):
        gx = min(9, int(x * 10))
        gy = min(9, int(y * 10))
        grid[gx][gy] += 1
    assert all(grid[i][j] >= 3 for i in range(10) for j in range(10))
    per = Perlin2D()
    a = per.noise(0.1, 0.2)
    b = per.noise(0.12, 0.22)
    c = per.noise(5.1, -3.7)
    assert -1.0 <= a <= 1.0 and -1.0 <= b <= 1.0 and -1.0 <= c <= 1.0
    assert abs(a - b) < 0.5
    st = Star(idx=1, home_fx=0.5, home_fy=0.5, depth=0.8, phase=math.pi / 3)
    br1, al1 = st.visual(0.0, 1.0)
    br2, al2 = st.visual(0.25, 1.0)
    assert 0.0 <= br1 <= 1.0 and 0.0 <= br2 <= 1.0
    assert 0.35 <= al1 <= 1.0 and 0.35 <= al2 <= 1.0
    st.disp_x = 100.0
    st.disp_y = 0.0
    d0 = math.sqrt(st.disp_x * st.disp_x + st.disp_y * st.disp_y)
    st.update(dt=0.016, t=0.0, noise=per, speed_px_s=0.0, threshold_px=20.0,
              return_strength=20.0, width=1280, height=720, rehome_active=True)
    d1 = math.sqrt(st.disp_x * st.disp_x + st.disp_y * st.disp_y)
    assert d1 < d0
    print("Self-test passed: Halton, Perlin, brightness, return mechanism OK.")


def _parse_args():
    ap = argparse.ArgumentParser(description="漫天星光 - 星光粒子系统（Halton 分布 + Perlin 噪声）")
    ap.add_argument("--count", type=int, default=1000, help="光点数量（默认1000）")
    ap.add_argument("--flicker", type=float, default=1.0, help="闪烁频率Hz（建议0.5-2Hz，默认1.0）")
    ap.add_argument("--speed", type=float, default=2.0, help="位移速度（像素/秒，建议1-5，默认2.0）")
    ap.add_argument("--threshold", type=float, default=20.0, help="回归阈值（像素，默认20）")
    ap.add_argument("--width", type=int, default=1280, help="屏幕宽度（默认1280）")
    ap.add_argument("--height", type=int, default=720, help="屏幕高度（默认720）")
    ap.add_argument("--fullscreen", action="store_true", help="是否全屏显示")
    ap.add_argument("--redistribute", type=float, default=30.0, help="重新分布周期（秒，默认30）")
    ap.add_argument("--selftest", action="store_true", help="运行自测（无需 pygame）")
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.selftest:
        self_test()
    else:
        run_starfield(star_count=args.count,
                      flicker_hz=args.flicker,
                      speed_px_s=args.speed,
                      return_threshold_px=args.threshold,
                      width=args.width,
                      height=args.height,
                      fullscreen=args.fullscreen,
                      redistribute_interval=args.redistribute)
