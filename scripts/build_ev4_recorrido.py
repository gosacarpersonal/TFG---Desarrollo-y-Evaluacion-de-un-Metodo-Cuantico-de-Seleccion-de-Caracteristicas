"""EV4 - Recorrido del TFG.

Figura de apertura narrativa: nueve fases, embudo dimensional y Madelon como
caso limite. Se genera solo con Pillow para poder reconstruirla en entornos sin
matplotlib/numpy/pandas.
"""
from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures" / "10_memoria"
FIGS = ROOT / "Plantilla_Latex_GCD" / "tfgs" / "figs"

W, H = 3960, 2220
S = 3  # 300 dpi scale from a 1320x740 layout
BG = "#f7f4ef"
TEXT = "#3b3b3b"
MUTED = "#746f66"
GRID = "#ded7cc"
NEUTRAL = "#bdbdbd"
ACCENT = "#d95f5f"
SECONDARY = "#4f81bd"

FASES = [
    ("1", "Auditoría", "cruda"),
    ("2", "Preproc.", "conservador"),
    ("3", "Post-aud.", "fiel"),
    ("4", "Splits", "auditados"),
    ("5", "Selección", "12 selectores"),
    ("6", "Modelado", "4 modelos"),
    ("7", "Clásico", "veredicto"),
    ("8", "QFS", "simulación"),
    ("9", "Diagnóstico", "criterio/opt."),
]

FUNNEL = {
    "Breast Cancer": (30, 20, 10),
    "Customer Churn": (15, 15, 10),
    "Madelon": (500, 20, 10),
    "Olive 3": (8, 8, 5),
    "Olive 9": (8, 8, 5),
}
STAGES = ["Datos\ncrudos", "Envolvente\nQFS <=20", "Subconjunto\nfinal (k)"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F_TITLE = font(48, True)
F_SUB = font(30)
F_SECTION = font(32, True)
F_PHASE_NUM = font(30, True)
F_PHASE = font(25, True)
F_SMALL = font(22)
F_AXIS = font(28)
F_TICK = font(23)
F_ANNOT = font(27, True)
F_ANNOT_REG = font(26)


def xy(x: float, y: float) -> tuple[int, int]:
    return int(round(x)), int(round(y))


def draw_multiline_center(draw: ImageDraw.ImageDraw, pos: tuple[float, float], text: str, fnt, fill: str, spacing: int = 5) -> None:
    lines = text.split("\n")
    widths = [draw.textbbox((0, 0), line, font=fnt)[2] for line in lines]
    heights = [draw.textbbox((0, 0), line, font=fnt)[3] - draw.textbbox((0, 0), line, font=fnt)[1] for line in lines]
    total_h = sum(heights) + spacing * (len(lines) - 1)
    x, y = pos
    cursor = y - total_h / 2
    for line, width, height in zip(lines, widths, heights):
        draw.text((x - width / 2, cursor), line, font=fnt, fill=fill)
        cursor += height + spacing


def arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], fill: str, width: int = 5) -> None:
    sx, sy = start
    ex, ey = end
    draw.line([xy(sx, sy), xy(ex, ey)], fill=fill, width=width)
    angle = math.atan2(ey - sy, ex - sx)
    head = 18
    spread = 0.48
    p1 = (ex - head * math.cos(angle - spread), ey - head * math.sin(angle - spread))
    p2 = (ex - head * math.cos(angle + spread), ey - head * math.sin(angle + spread))
    draw.polygon([xy(ex, ey), xy(*p1), xy(*p2)], fill=fill)


def log_y(value: float, top: float, bottom: float, ymin: float = 4.0, ymax: float = 650.0) -> float:
    lv = math.log10(value)
    return bottom - (lv - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) * (bottom - top)


def build() -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text(xy(240, 110), "Nueve fases convierten cinco problemas distintos en un diagnóstico QFS", font=F_TITLE, fill=TEXT)
    draw.text(
        xy(240, 185),
        "De los datos crudos al subconjunto cuántico; Madelon es el caso límite y el veredicto final es diagnóstico",
        font=F_SUB,
        fill=MUTED,
    )

    # Phase ribbon
    draw.text(xy(240, 315), "El recorrido completo: nueve fases encadenadas", font=F_SECTION, fill=TEXT)
    ribbon_left, ribbon_right = 240, 3720
    box_gap = 24
    box_w = (ribbon_right - ribbon_left - box_gap * (len(FASES) - 1)) / len(FASES)
    box_h = 164
    y_box = 430
    for i, (num, title, sub) in enumerate(FASES):
        x0 = ribbon_left + i * (box_w + box_gap)
        x1 = x0 + box_w
        color = NEUTRAL if i < 7 else (SECONDARY if i == 7 else ACCENT)
        fill = color if i >= 7 else "#e4e2de"
        outline = color if i >= 7 else "#e4e2de"
        draw.rounded_rectangle([xy(x0, y_box), xy(x1, y_box + box_h)], radius=28, fill=fill, outline=outline, width=1)
        if i < 7:
            # soften classical phases
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rounded_rectangle([xy(x0, y_box), xy(x1, y_box + box_h)], radius=28, fill=(255, 255, 255, 80))
            img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
            draw = ImageDraw.Draw(img)
        cx = (x0 + x1) / 2
        draw.text(xy(cx - draw.textlength(num, font=F_PHASE_NUM) / 2, y_box + 28), num, font=F_PHASE_NUM, fill=TEXT)
        draw.text(xy(cx - draw.textlength(title, font=F_PHASE) / 2, y_box + 69), title, font=F_PHASE, fill=TEXT)
        draw.text(xy(cx - draw.textlength(sub, font=F_SMALL) / 2, y_box + box_h + 30), sub, font=F_SMALL, fill=MUTED)
        if i < len(FASES) - 1:
            arrow(draw, (x1 + 6, y_box + box_h / 2), (x1 + box_gap - 8, y_box + box_h / 2), MUTED, width=3)

    # Chart frame
    left, right = 310, 3720
    top, bottom = 900, 1990
    x_positions = [820, 1930, 3040]
    ticks = [5, 10, 20, 50, 100, 200, 500]

    for tick in ticks:
        y = log_y(tick, top, bottom)
        draw.line([xy(left, y), xy(right, y)], fill=GRID, width=2)
        label = str(tick)
        draw.text(xy(left - 70 - draw.textlength(label, font=F_TICK), y - 14), label, font=F_TICK, fill=MUTED)
    draw.line([xy(left, top), xy(left, bottom)], fill="#d6d0c5", width=3)
    draw.line([xy(left, bottom), xy(right, bottom)], fill="#d6d0c5", width=3)

    # Axis labels
    y_label = "Variables predictoras (escala log)"
    label_img = Image.new("RGBA", (520, 60), (0, 0, 0, 0))
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((0, 0), y_label, font=F_AXIS, fill=TEXT)
    label_img = label_img.rotate(90, expand=True)
    img.paste(label_img, (110, 1180), label_img)
    draw = ImageDraw.Draw(img)
    for x, stage in zip(x_positions, STAGES):
        draw_multiline_center(draw, (x, bottom + 70), stage, F_AXIS, MUTED, spacing=3)

    # Funnel lines
    for name, vals in FUNNEL.items():
        is_madelon = name == "Madelon"
        color = ACCENT if is_madelon else "#cfcfcb"
        width = 11 if is_madelon else 7
        radius = 19 if is_madelon else 12
        points = [(x, log_y(v, top, bottom)) for x, v in zip(x_positions, vals)]
        for a, b in zip(points, points[1:]):
            draw.line([xy(*a), xy(*b)], fill=color, width=width)
        for x, y in points:
            draw.ellipse([xy(x - radius, y - radius), xy(x + radius, y + radius)], fill=color, outline=BG, width=4)
        if is_madelon:
            draw.text(xy(points[-1][0] + 45, points[-1][1] - 20), name, font=F_ANNOT, fill=ACCENT)
        else:
            label = f"{name} ({vals[0]})"
            draw.text(xy(points[0][0] - 45 - draw.textlength(label, font=F_SMALL), points[0][1] - 14), label, font=F_SMALL, fill=MUTED)

    # Narrative annotations
    draw.text(xy(1210, 935), "Madelon: 500 variables,\nsolo 13 con señal real (FDR)\n-> reducir no es opcional", font=F_ANNOT, fill=ACCENT, spacing=5)
    arrow(draw, (1190, 975), (840, log_y(500, top, bottom) + 8), ACCENT, width=5)
    draw.text(xy(1960, 1510), "Todas convergen a 5-10 variables:\nla envolvente de un átomo por variable", font=F_ANNOT_REG, fill=TEXT, spacing=6)
    arrow(draw, (2500, 1575), (3035, log_y(10, top, bottom) - 10), MUTED, width=4)

    OUT.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    png = OUT / "ev4_recorrido_tfg.png"
    pdf = OUT / "ev4_recorrido_tfg.pdf"
    img.save(png, dpi=(300, 300))
    img.save(pdf, "PDF", resolution=300)
    shutil.copy2(png, FIGS / png.name)
    print(f"EV4 built: {png}")


if __name__ == "__main__":
    build()
