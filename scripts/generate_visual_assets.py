from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONSET = ASSETS / "SysGuard.iconset"
ICON_PNG = ASSETS / "SysGuard.png"
ICON_ICNS = ASSETS / "SysGuard.icns"
DMG_BG = ASSETS / "dmg-background.png"


def ensure_dirs():
    ASSETS.mkdir(exist_ok=True)
    ICONSET.mkdir(exist_ok=True)


def hex_rgba(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def create_base_icon(size):
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    bg_top = hex_rgba("#0b1730")
    bg_bottom = hex_rgba("#07101d")
    for y in range(size):
        mix = y / max(1, size - 1)
        color = tuple(
            int(bg_top[index] * (1 - mix) + bg_bottom[index] * mix)
            for index in range(3)
        ) + (255,)
        draw.line((0, y, size, y), fill=color)

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (size * 0.12, size * 0.08, size * 0.92, size * 0.82),
        fill=hex_rgba("#38bdf8", 90),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.06))
    image.alpha_composite(glow)

    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    margin = int(size * 0.08)
    radius = int(size * 0.22)
    card_draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=radius,
        fill=hex_rgba("#0f1b2e", 245),
        outline=hex_rgba("#24486a", 255),
        width=max(2, size // 128),
    )
    image.alpha_composite(card)

    accent = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent)
    accent_draw.rounded_rectangle(
        (margin, margin, size - margin, margin + size * 0.26),
        radius=radius,
        fill=hex_rgba("#173c56", 95),
    )
    accent = accent.filter(ImageFilter.GaussianBlur(size * 0.02))
    image.alpha_composite(accent)

    shield = [
        (size * 0.50, size * 0.18),
        (size * 0.72, size * 0.27),
        (size * 0.72, size * 0.52),
        (size * 0.66, size * 0.69),
        (size * 0.50, size * 0.82),
        (size * 0.34, size * 0.69),
        (size * 0.28, size * 0.52),
        (size * 0.28, size * 0.27),
    ]
    shield_shadow = [(x, y + size * 0.015) for x, y in shield]
    draw.polygon(shield_shadow, fill=hex_rgba("#02060c", 110))
    draw.polygon(shield, fill=hex_rgba("#4fd7ff"), outline=hex_rgba("#b6f1ff"), width=max(3, size // 96))

    inner = [
        (size * 0.50, size * 0.27),
        (size * 0.64, size * 0.33),
        (size * 0.64, size * 0.50),
        (size * 0.60, size * 0.62),
        (size * 0.50, size * 0.70),
        (size * 0.40, size * 0.62),
        (size * 0.36, size * 0.50),
        (size * 0.36, size * 0.33),
    ]
    draw.polygon(inner, fill=hex_rgba("#0f2338"))

    eye_box = (size * 0.34, size * 0.39, size * 0.66, size * 0.58)
    draw.ellipse(eye_box, fill=hex_rgba("#d8f8ff"))
    pupil_box = (size * 0.44, size * 0.43, size * 0.56, size * 0.55)
    draw.ellipse(pupil_box, fill=hex_rgba("#0d5b84"))
    shine_box = (size * 0.485, size * 0.455, size * 0.525, size * 0.495)
    draw.ellipse(shine_box, fill=hex_rgba("#9aeaff"))

    pulse_color = hex_rgba("#8cecff", 150)
    width = max(3, size // 110)
    draw.arc((size * 0.18, size * 0.24, size * 0.82, size * 0.88), start=215, end=325, fill=pulse_color, width=width)
    draw.arc((size * 0.22, size * 0.29, size * 0.78, size * 0.84), start=220, end=320, fill=hex_rgba("#58cfff", 100), width=width)

    return image


def save_icon_assets():
    base = create_base_icon(1024)
    base.save(ICON_PNG)
    base.save(ICON_ICNS)
    icon_sizes = [16, 32, 128, 256, 512]

    for size in icon_sizes:
        image = base.resize((size, size), Image.Resampling.LANCZOS)
        image.save(ICONSET / f"icon_{size}x{size}.png")
        image.resize((size * 2, size * 2), Image.Resampling.LANCZOS).save(
            ICONSET / f"icon_{size}x{size}@2x.png"
        )


def save_dmg_background():
    width, height = 1600, 1000
    image = Image.new("RGBA", (width, height), hex_rgba("#08111d"))
    draw = ImageDraw.Draw(image)

    top = hex_rgba("#0c1730")
    bottom = hex_rgba("#07101a")
    for y in range(height):
        mix = y / max(1, height - 1)
        color = tuple(
            int(top[index] * (1 - mix) + bottom[index] * mix)
            for index in range(3)
        ) + (255,)
        draw.line((0, y, width, y), fill=color)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((80, 40, 720, 640), fill=hex_rgba("#0ea5e9", 65))
    overlay_draw.ellipse((940, 120, 1520, 760), fill=hex_rgba("#38bdf8", 38))
    overlay = overlay.filter(ImageFilter.GaussianBlur(70))
    image.alpha_composite(overlay)

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        (88, 86, width - 88, height - 92),
        radius=42,
        fill=hex_rgba("#0d1828", 220),
        outline=hex_rgba("#23415f", 255),
        width=3,
    )
    image.alpha_composite(panel)

    draw = ImageDraw.Draw(image)
    draw.text((140, 128), "SysGuard", fill=hex_rgba("#edf5ff"))
    draw.text((142, 182), "Drag the app into Applications to install.", fill=hex_rgba("#93b2cc"))
    draw.text((142, 226), "Native macOS security console", fill=hex_rgba("#5fd5ff"))
    draw.rounded_rectangle((210, 370, 620, 760), radius=46, outline=hex_rgba("#2d5677"), width=4)
    draw.rounded_rectangle((980, 370, 1390, 760), radius=46, outline=hex_rgba("#2d5677"), width=4)
    draw.text((335, 780), "SysGuard.app", fill=hex_rgba("#edf5ff"))
    draw.text((1060, 780), "Applications", fill=hex_rgba("#edf5ff"))
    image.save(DMG_BG)


def main():
    ensure_dirs()
    save_icon_assets()
    save_dmg_background()


if __name__ == "__main__":
    main()
