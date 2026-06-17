from __future__ import annotations

import csv
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "outputs" / "public_healthcare_lakehouse_workshop"
ASSETS = WORKSHOP / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

WIDTH = 1600
HEIGHT = 900


def rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


pixels = bytearray(WIDTH * HEIGHT * 3)


def set_px(x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        idx = (y * WIDTH + x) * 3
        pixels[idx : idx + 3] = bytes(color)


def fill_rect(x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    row = bytes(color) * max(0, x1 - x0)
    for yy in range(y0, y1):
        start = (yy * WIDTH + x0) * 3
        pixels[start : start + len(row)] = row


def stroke_rect(x: int, y: int, w: int, h: int, color: tuple[int, int, int], thickness: int = 2) -> None:
    fill_rect(x, y, w, thickness, color)
    fill_rect(x, y + h - thickness, w, thickness, color)
    fill_rect(x, y, thickness, h, color)
    fill_rect(x + w - thickness, y, thickness, h, color)


def draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int], thickness: int = 4) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        fill_rect(x - thickness // 2, y - thickness // 2, thickness, thickness, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def write_png(path: Path) -> None:
    scanlines = bytearray()
    for y in range(HEIGHT):
        scanlines.append(0)
        start = y * WIDTH * 3
        scanlines.extend(pixels[start : start + WIDTH * 3])

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(png)


for y in range(HEIGHT):
    for x in range(WIDTH):
        gx = x / WIDTH
        gy = y / HEIGHT
        base = (
            int(19 + 12 * gx + 18 * gy),
            int(45 + 39 * gx + 16 * gy),
            int(41 + 29 * gx + 34 * gy),
        )
        set_px(x, y, base)

fill_rect(0, 0, WIDTH, 96, rgb("#152f2e"))
fill_rect(0, HEIGHT - 92, WIDTH, 92, rgb("#172625"))
fill_rect(102, 144, 1396, 620, rgb("#f7fbfa"))
stroke_rect(102, 144, 1396, 620, rgb("#d5e2df"), 3)
fill_rect(102, 144, 1396, 62, rgb("#ffffff"))
fill_rect(134, 166, 208, 18, rgb("#cf2e2e"))
fill_rect(1210, 163, 116, 20, rgb("#284d48"))
fill_rect(1340, 163, 116, 20, rgb("#e15f3f"))

panel_border = rgb("#d9e5e1")
panel_bg = rgb("#ffffff")
muted = rgb("#edf4f2")
green = rgb("#0f766e")
mint = rgb("#34a853")
amber = rgb("#f4a62a")
coral = rgb("#e15f3f")
ink = rgb("#233330")

cards = [(134, 236, 282, 104), (440, 236, 282, 104), (746, 236, 282, 104), (1052, 236, 282, 104)]
for idx, (x, y, w, h) in enumerate(cards):
    fill_rect(x, y, w, h, panel_bg)
    stroke_rect(x, y, w, h, panel_border, 2)
    fill_rect(x + 24, y + 24, 82 + idx * 12, 12, muted)
    fill_rect(x + 24, y + 54, 144, 18, [green, coral, amber, mint][idx])
    fill_rect(x + 188, y + 34, 56, 46, rgb("#e8f2ef"))

fill_rect(134, 376, 586, 300, panel_bg)
stroke_rect(134, 376, 586, 300, panel_border, 2)
fill_rect(164, 408, 184, 16, ink)
points = [(174, 596), (238, 570), (302, 582), (366, 530), (430, 544), (494, 492), (558, 510), (622, 462), (682, 480)]
for a, b in zip(points, points[1:]):
    draw_line(a[0], a[1], b[0], b[1], green, 7)
for x, y in points:
    fill_rect(x - 7, y - 7, 14, 14, coral)
for i, h in enumerate([78, 104, 58, 138, 116, 82, 152, 96]):
    fill_rect(176 + i * 58, 648 - h, 26, h, rgb("#b4ded5"))
    fill_rect(206 + i * 58, 648 - int(h * 0.72), 26, int(h * 0.72), amber)

fill_rect(752, 376, 582, 300, panel_bg)
stroke_rect(752, 376, 582, 300, panel_border, 2)
fill_rect(782, 408, 208, 16, ink)
districts = [
    (805, 462, 92, 92, rgb("#9bd7cf")),
    (910, 436, 128, 104, rgb("#e15f3f")),
    (1054, 462, 112, 128, rgb("#f4a62a")),
    (854, 570, 134, 72, rgb("#34a853")),
    (1002, 560, 132, 84, rgb("#7fb8dd")),
]
for x, y, w, h, color in districts:
    fill_rect(x, y, w, h, color)
    stroke_rect(x, y, w, h, rgb("#ffffff"), 5)

legend_x = 1190
for i, color in enumerate([green, mint, amber, coral]):
    fill_rect(legend_x, 460 + i * 42, 22, 22, color)
    fill_rect(legend_x + 34, 464 + i * 42, 86, 10, muted)

fill_rect(116, 780, 1368, 16, rgb("#cf2e2e"))
fill_rect(116, 796, 928, 12, rgb("#f4a62a"))
fill_rect(116, 812, 1228, 12, rgb("#34a853"))

with (WORKSHOP / "data" / "curated" / "fact_district_health_week.csv").open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

max_pressure = max(float(row["public_health_pressure_index"]) for row in rows)
top = max(rows, key=lambda row: float(row["public_health_pressure_index"]))

accent = int(min(255, 80 + max_pressure * 1.3))
fill_rect(1390, 786, 62, 38, (accent, 75, 58))
fill_rect(1458, 786, 18, 38, rgb("#ffffff"))

write_png(ASSETS / "public-health-dashboard-preview.png")
print(f"Created {ASSETS / 'public-health-dashboard-preview.png'} using peak pressure district {top['district_name']}.")
