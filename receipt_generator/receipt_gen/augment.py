"""
Takes a clean rendered receipt image and makes it look like a phone photo
of a real receipt lying on a surface: slight perspective skew, creases,
uneven lighting, a soft shadow, sensor noise, focus blur and JPEG artifacts.
"""

import io
import random

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def _find_coeffs(source_pts, target_pts):
    matrix = []
    for p1, p2 in zip(source_pts, target_pts):
        matrix.append([p2[0], p2[1], 1, 0, 0, 0, -p1[0] * p2[0], -p1[0] * p2[1]])
        matrix.append([0, 0, 0, p2[0], p2[1], 1, -p1[1] * p2[0], -p1[1] * p2[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(source_pts, dtype=np.float64).reshape(8)
    res = np.linalg.solve(A, B)
    return res.tolist()


def _add_creases(img, n_creases=2, rng=random):
    """Darkens/lightens soft wavy horizontal bands to mimic paper folds,
    without drawing a hard line that would slice through printed text."""
    rgba = img.convert("RGBA")
    arr = np.asarray(rgba).astype(np.float64)
    h, w = arr.shape[0], arr.shape[1]

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    factor = np.ones((h, w), dtype=np.float64)

    for _ in range(n_creases):
        y0 = rng.uniform(h * 0.15, h * 0.85)
        band = rng.uniform(5, 11)
        depth = rng.uniform(0.08, 0.16)
        wavelength = rng.uniform(w * 1.5, w * 4.0)
        amplitude = rng.uniform(2, 8)
        phase = rng.uniform(0, 6.28)

        y_center = y0 + amplitude * np.sin(2 * np.pi * xx / wavelength + phase)
        dip = 1 - depth * np.exp(-0.5 * ((yy - y_center) / band) ** 2)
        hi_center = y_center + band * 1.6
        hi = 1 + (depth * 0.45) * np.exp(-0.5 * ((yy - hi_center) / (band * 0.9)) ** 2)
        factor *= dip * hi

    arr[:, :, 0] *= factor
    arr[:, :, 1] *= factor
    arr[:, :, 2] *= factor
    arr = np.clip(arr, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
    return out


def _perspective_warp(img, strength=0.06, rng=random):
    """Applies a mild random perspective skew. Input/output are RGBA."""
    w, h = img.size
    dx = int(w * strength)
    dy = int(h * strength)
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [
        (rng.randint(0, dx), rng.randint(0, dy)),
        (w - rng.randint(0, dx), rng.randint(0, dy)),
        (w - rng.randint(0, dx), h - rng.randint(0, dy)),
        (rng.randint(0, dx), h - rng.randint(0, dy)),
    ]
    coeffs = _find_coeffs(src, dst)
    return img.transform((w, h), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC)


def _procedural_background(size, rng=random):
    """A simple procedural surface texture (desk/table/worktop) behind the receipt."""
    w, h = size
    palette = rng.choice([
        (60, 45, 35),     # dark wood
        (150, 120, 90),   # light wood
        (90, 90, 92),     # grey worktop
        (210, 205, 195),  # pale countertop
        (40, 40, 44),     # dark surface
    ])
    base = np.zeros((h, w, 3), dtype=np.float64)
    for c in range(3):
        base[:, :, c] = palette[c]
    noise = rng.uniform(8, 18)
    grain = np.random.normal(0, noise, (h, w, 1))
    base = base + grain
    # Subtle large-scale streaks (wood-grain-ish) using a low-frequency sine field
    xx = np.linspace(0, rng.uniform(3, 8), w)
    streak = (np.sin(xx) * rng.uniform(4, 10))[None, :, None]
    base = base + streak
    base = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(base, mode="RGB")


def _drop_shadow(rgba_img, blur_radius=14, offset=(10, 14), opacity=120):
    w, h = rgba_img.size
    shadow = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    alpha = rgba_img.split()[-1]
    solid = Image.new("RGBA", rgba_img.size, (0, 0, 0, opacity))
    solid.putalpha(alpha.point(lambda a: int(a * opacity / 255)))
    shadow.paste(solid, (30 + offset[0], 30 + offset[1]), solid)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    return shadow


def _lighting_gradient(size, rng=random):
    """A smooth uneven-lighting multiplier field (simulates a single light source)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    cx, cy = rng.uniform(0, w), rng.uniform(-h * 0.3, h * 0.5)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = dist / dist.max()
    strength = rng.uniform(0.25, 0.45)
    field = 1.0 + strength * (0.5 - dist)
    field = np.clip(field, 0.55, 1.35)
    return field


def _vignette(size, rng=random):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    cx, cy = w / 2, h / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = dist / dist.max()
    strength = rng.uniform(0.15, 0.35)
    field = 1.0 - strength * (dist ** 2)
    return np.clip(field, 0.6, 1.0)


def make_photographed(clean_img, rng_seed=None, jpeg_quality=None):
    rng = random.Random(rng_seed)
    np.random.seed(rng_seed)

    receipt = clean_img.convert("RGBA")

    # 1. Creases on the flat paper before any geometric warp.
    receipt = _add_creases(receipt, n_creases=rng.randint(1, 3), rng=rng)

    # 2. Slight overall rotation (camera/paper not perfectly aligned).
    angle = rng.uniform(-4.5, 4.5)
    receipt = receipt.rotate(angle, expand=True, resample=Image.BICUBIC)

    # 3. Mild perspective skew.
    receipt = _perspective_warp(receipt, strength=rng.uniform(0.02, 0.07), rng=rng)

    # 4. Compose onto a procedural background, larger than the receipt with margin.
    margin = rng.randint(50, 110)
    canvas_w = receipt.width + margin * 2
    canvas_h = receipt.height + margin * 2
    background = _procedural_background((canvas_w, canvas_h), rng=rng)
    canvas = background.convert("RGBA")

    paste_x = rng.randint(margin // 2, margin + margin // 2)
    paste_y = rng.randint(margin // 2, margin + margin // 2)

    shadow = _drop_shadow(receipt)
    canvas.alpha_composite(shadow, (paste_x - 30, paste_y - 30))
    canvas.alpha_composite(receipt, (paste_x, paste_y))

    composite = canvas.convert("RGB")
    arr = np.asarray(composite).astype(np.float64)

    # 5. Uneven lighting + vignette.
    light = _lighting_gradient(composite.size, rng=rng)
    vig = _vignette(composite.size, rng=rng)
    factor = (light * vig)[:, :, None]
    arr = arr * factor

    # 6. Sensor noise.
    noise_sigma = rng.uniform(2.0, 7.0)
    arr = arr + np.random.normal(0, noise_sigma, arr.shape)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    composite = Image.fromarray(arr, mode="RGB")

    # 7. Slight focus blur.
    blur_radius = rng.uniform(0.3, 1.4)
    composite = composite.filter(ImageFilter.GaussianBlur(blur_radius))

    # 8. Mild colour/contrast jitter (white balance variation).
    composite = ImageOps.autocontrast(composite, cutoff=rng.uniform(0, 1.5))

    # 9. JPEG round-trip to bake in compression artifacts.
    quality = jpeg_quality or rng.randint(55, 85)
    buf = io.BytesIO()
    composite.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    final = Image.open(buf).convert("RGB")

    return final
