"""Image cleanup and marketplace export utilities for KarigarConnect."""

from __future__ import annotations

import io
import os
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    from rembg import remove
except ImportError:  # pragma: no cover - exercised when the optional AI package is absent
    remove = None


CANVAS_SIZE = 1200
BACKGROUND = (250, 248, 243, 255)


def _remove_background(image: Image.Image) -> Image.Image:
    """Use rembg when installed; otherwise preserve the photo with a clean canvas."""
    if remove is None or os.getenv("REMOVE_BACKGROUND", "true").lower() == "false":
        return image.convert("RGBA")

    source = io.BytesIO()
    image.save(source, format="PNG")
    result = remove(source.getvalue())
    return Image.open(io.BytesIO(result)).convert("RGBA")


def _add_soft_shadow(subject: Image.Image) -> Image.Image:
    alpha = subject.getchannel("A")
    shadow = Image.new("RGBA", subject.size, (50, 42, 32, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(28)).point(lambda value: value // 5))
    return shadow


def process_image(input_path: Path, output_path: Path) -> Path:
    """Clean an artisan photo and save a square, marketplace-ready JPEG."""
    image = ImageOps.exif_transpose(Image.open(input_path)).convert("RGB")
    image = ImageEnhance.Color(image).enhance(1.12)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.18)

    subject = _remove_background(image)
    subject.thumbnail((CANVAS_SIZE - 180, CANVAS_SIZE - 180), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND)
    left = (CANVAS_SIZE - subject.width) // 2
    top = (CANVAS_SIZE - subject.height) // 2
    shadow = _add_soft_shadow(subject)
    canvas.alpha_composite(shadow, (left, top + 18))
    canvas.alpha_composite(subject, (left, top))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "JPEG", quality=94, optimize=True, progressive=True)
    return output_path

