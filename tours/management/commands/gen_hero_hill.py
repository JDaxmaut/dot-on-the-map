"""
python manage.py gen_hero_hill [--out static/img/hero-hills-magenta.webp]

Собирает hero-изображение «холмы» математически (градиент + слоистые
гауссовы холмы), палитра от #000000 до #d81696. Воспроизводит композицию
hero-hills.webp, но не использует его пиксели.
"""
import numpy as np
from django.core.management.base import BaseCommand
from PIL import Image

W = 2560
H = 1760
SCALE = 2
TOP = np.array([216, 22, 150], dtype=np.float32)    # #d81696
BOTTOM = np.array([0, 0, 0], dtype=np.float32)      # #000000


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hill_top(u, base, peaks):
    v = np.full_like(u, base, dtype=np.float32)
    for c, amp, w in peaks:
        v -= amp * np.exp(-((u - c) / w) ** 2)
    return v


def build_layers(u):
    return np.stack(
        [
            hill_top(
                u, 0.57,
                [(0.14, 0.20, 0.09), (0.46, 0.15, 0.11), (0.63, 0.09, 0.06), (0.86, 0.17, 0.09)],
            ),
            hill_top(
                u, 0.65,
                [(0.03, 0.14, 0.08), (0.30, 0.12, 0.09), (0.55, 0.16, 0.11), (0.79, 0.10, 0.07)],
            ),
            hill_top(
                u, 0.73,
                [(0.18, 0.10, 0.09), (0.42, 0.07, 0.06), (0.70, 0.12, 0.09), (0.93, 0.08, 0.07)],
            ),
            hill_top(
                u, 0.81,
                [(0.10, 0.06, 0.08), (0.35, 0.05, 0.09), (0.60, 0.08, 0.08), (0.88, 0.05, 0.06)],
            ),
            hill_top(
                u, 0.89,
                [(0.25, 0.05, 0.10), (0.55, 0.06, 0.09), (0.81, 0.04, 0.08)],
            ),
        ]
    )


def render():
    sw, sh = W * SCALE, H * SCALE
    u = np.linspace(0, 1, sw, dtype=np.float32)
    y = np.arange(sh, dtype=np.float32)
    tops = build_layers(u) * float(H * SCALE)  # (5, sw) в пикселях хайреза

    coverage = np.zeros((sh, sw), dtype=np.float32)
    feather = 5.0
    for top_line in tops:
        z = np.clip((y[:, None] - top_line[None, :]) / feather, -40.0, 40.0)
        coverage += 1.0 / (1.0 + np.exp(-z))

    colors = [
        TOP * 0.75,   # h=0 (низ неба)
        TOP * 0.58,   # h=1
        TOP * 0.44,   # h=2
        TOP * 0.33,   # h=3
        TOP * 0.24,   # h=4
        TOP * 0.16,   # h=5
    ]
    lut = np.stack([c / 255.0 for c in colors], axis=1)  # (3, 6)

    sky_bottom = colors[0] / 255.0
    sky_f = smoothstep(0.0, 0.72, y / float(sh)) * 0.85 + 0.15

    alpha = smoothstep(0.0, 1.0, coverage)
    img = np.empty((sh, sw, 3), dtype=np.float32)
    for ch in range(3):
        sky_plane = (TOP[ch] / 255.0) * (1 - sky_f) + sky_bottom[ch] * sky_f
        sky_plane = sky_plane[:, None] * (1.0 + 0.035 * u[None, :])
        hill_plane = np.interp(coverage.ravel(), np.arange(6, dtype=np.float32),
                               lut[ch]).reshape(sh, sw)
        img[..., ch] = (1 - alpha) * sky_plane + alpha * hill_plane

    bf = smoothstep(0.86, 1.0, y / float(sh))
    img = img * (1 - bf[:, None, None] * 0.85) + (BOTTOM / 255.0)[None, None, :] * bf[:, None, None] * 0.85

    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(img).resize((W, H), Image.LANCZOS)


class Command(BaseCommand):
    help = "Генерирует математический холмистый hero с палитрой #000000 → #d81696"

    def add_arguments(self, parser):
        parser.add_argument("--out", default="static/img/hero-hills-magenta.webp")

    def handle(self, *args, **options):
        pil = render()
        pil.save(options["out"], quality=90, method=6)
        self.stdout.write(self.style.SUCCESS(f"saved {options['out']}"))