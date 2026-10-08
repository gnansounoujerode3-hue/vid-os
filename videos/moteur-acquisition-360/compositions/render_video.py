#!/usr/bin/env python3
"""Create a deterministic, text-led 9:16 marketing video for Moteur d'Acquisition 360°.

The product panels are explicitly illustrative: they use the public site's feature copy,
not screenshots or an assumed exact UI. All visuals and the instrumental score are generated
locally. Requires Pillow and imageio-ffmpeg.
"""
from __future__ import annotations

import math
import os
import struct
import subprocess
import sys
import time
import wave
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from imageio_ffmpeg import get_ffmpeg_exe

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
AUDIO = ROOT / "audio"
RENDERS = ROOT / "renders"
SNAPSHOTS = ROOT / "snapshots"

W, H = 1080, 1920
FPS = 30
DURATION = 34.0
TOTAL_FRAMES = int(FPS * DURATION)
SR = 48000

# The dark base is the exact PWA theme_color; accent colors are restrained production choices,
# not verified app tokens (the public page's CSS and screenshot were not available).
BG_HEX = "#0A0B0E"
BG = (10, 11, 14)
SURFACE = (19, 22, 29)
SURFACE_2 = (24, 28, 36)
BORDER = (50, 57, 68)
WHITE = (245, 246, 242)
MUTED = (164, 171, 180)
DIM = (105, 113, 124)
MINT = (190, 244, 120)
LILAC = (183, 169, 255)

SCENES = [
    (0.0, 4.0, "Partout"),
    (4.0, 7.7, "Le défi"),
    (7.7, 12.0, "Qualification"),
    (12.0, 16.2, "Tableau de bord"),
    (16.2, 20.3, "Contenu"),
    (20.3, 24.4, "Prospection"),
    (24.4, 28.0, "Le système"),
    (28.0, 34.0, "Essai gratuit"),
]

FONT_REGULAR_PATH = ASSETS / "InstrumentSans-Regular.ttf"
FONT_BOLD_PATH = ASSETS / "InstrumentSans-Bold.ttf"
FONT_MONO_PATH = ASSETS / "GeistMono-Regular.ttf"


@lru_cache(maxsize=64)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    path = {"regular": FONT_REGULAR_PATH, "bold": FONT_BOLD_PATH, "mono": FONT_MONO_PATH}[kind]
    return ImageFont.truetype(str(path), size=size)


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease(v: float) -> float:
    v = clamp(v)
    return v * v * (3.0 - 2.0 * v)


def draw_left(draw: ImageDraw.ImageDraw, x: float, y: float, text: str,
              fnt: ImageFont.FreeTypeFont, fill, anchor: str = "lt") -> None:
    draw.text((int(x), int(y)), text, font=fnt, fill=fill, anchor=anchor)


def draw_center(draw: ImageDraw.ImageDraw, y: float, text: str,
                fnt: ImageFont.FreeTypeFont, fill, xmid: float = W / 2) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    tw = box[2] - box[0]
    draw.text((int(xmid - tw / 2 - box[0]), int(y - box[1])), text, font=fnt, fill=fill)


def draw_wrapped(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, max_width: int,
                 fnt: ImageFont.FreeTypeFont, fill, line_height: int, align: str = "left") -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if current and draw.textlength(candidate, font=fnt) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        if align == "center":
            draw_center(draw, y + i * line_height, line, fnt, fill)
        else:
            draw_left(draw, x, y + i * line_height, line, fnt, fill)
    return len(lines) * line_height


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(tuple(map(int, box)), radius=radius, fill=fill, outline=outline, width=width)


def draw_card(draw: ImageDraw.ImageDraw, box, *, radius: int = 28,
              fill=(19, 22, 29, 248), outline=(50, 57, 68, 255), accent=None,
              shadow: bool = True) -> None:
    x1, y1, x2, y2 = map(int, box)
    if shadow:
        rounded(draw, (x1 + 2, y1 + 14, x2 + 2, y2 + 14), radius, (0, 0, 0, 80))
    rounded(draw, (x1, y1, x2, y2), radius, fill, outline, 2)
    if accent:
        rounded(draw, (x1 + 1, y1 + 24, x1 + 7, y2 - 24), 3, (*accent, 230))


def draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              *, accent: bool = False, fsize: int = 22, pad_x: int = 22, h: int = 52) -> int:
    fnt = font("mono", fsize)
    tw = draw.textlength(text, font=fnt)
    w = int(tw + pad_x * 2)
    fill = (30, 36, 42, 255) if not accent else (36, 47, 32, 255)
    border = (*BORDER, 255) if not accent else (*MINT, 170)
    rounded(draw, (x, y, x + w, y + h), h // 2, fill, border, 2)
    box = draw.textbbox((0, 0), text, font=fnt)
    yy = y + (h - (box[3] - box[1])) / 2 - box[1]
    draw.text((int(x + pad_x), int(yy)), text, font=fnt, fill=MINT if accent else WHITE)
    return w


def draw_wordmark(draw: ImageDraw.ImageDraw, scene_idx: int, scene_p: float = 0.0) -> None:
    # Typographic use of the published product name; no unofficial icon is fabricated.
    draw_left(draw, 70, 52, "MOTEUR", font("bold", 23), WHITE)
    draw_left(draw, 175, 55, "D’ACQUISITION 360°", font("mono", 17), MUTED)
    draw_left(draw, 940, 55, f"{scene_idx + 1:02d} / 08", font("mono", 17), MUTED)
    x0, y0, x1 = 70, 112, 1010
    draw.line((x0, y0, x1, y0), fill=(50, 57, 68, 190), width=2)
    full = x1 - x0
    current = sum(end - start for start, end, _ in SCENES[:scene_idx])
    current += (SCENES[scene_idx][1] - SCENES[scene_idx][0]) * clamp(scene_p)
    draw.line((x0, y0, x0 + int(full * current / DURATION), y0), fill=(*MINT, 225), width=3)


def make_background() -> Image.Image:
    base = Image.new("RGB", (W, H))
    px = base.load()
    top = (10, 11, 14)
    bottom = (16, 19, 25)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    bg = base.convert("RGBA")

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse((560, -330, 1330, 440), fill=(*MINT, 20))
    gd.ellipse((-360, 900, 390, 1670), fill=(*LILAC, 13))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    bg.alpha_composite(glow)

    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid, "RGBA")
    for x in range(30, W, 120):
        gd.line((x, 0, x, H), fill=(220, 226, 236, 7), width=1)
    for y in range(32, H, 120):
        gd.line((0, y, W, y), fill=(220, 226, 236, 7), width=1)
    bg.alpha_composite(grid)
    return bg


BACKGROUND = make_background()


def draw_kinetic_center(draw: ImageDraw.ImageDraw, y: float, text: str,
                        fnt: ImageFont.FreeTypeFont, fill, progress: float,
                        *, stagger: float = 0.13, duration: float = 0.43) -> None:
    """Reveal words in a quick, readable stagger with short directional travel."""
    words = text.split()
    if not words:
        return
    space = draw.textlength(" ", font=fnt)
    widths = [draw.textlength(word, font=fnt) for word in words]
    x = (W - (sum(widths) + space * (len(words) - 1))) / 2
    for i, word in enumerate(words):
        q = ease(clamp((progress - i * stagger) / duration))
        if q <= 0:
            x += widths[i] + space
            continue
        dx = (1 - q) * (32 if i % 2 else -32)
        dy = (1 - q) * 25
        alpha = int(255 * q)
        draw.text((int(x + dx), int(y + dy)), word, font=fnt, fill=(*fill, alpha))
        x += widths[i] + space


def scene_heading(draw: ImageDraw.ImageDraw, kicker: str, lines: list[str], subtitle: str,
                  p: float, *, title_y: int = 300, title_size: int = 86,
                  accent_indexes: tuple[int, ...] = (1,), subtitle_y: int | None = None) -> None:
    intro = ease(clamp(p / 0.30))
    shift = int((1 - intro) * 30)
    alpha = int(255 * intro)
    draw_center(draw, 205 + shift, kicker.upper(), font("mono", 22), (*MINT, alpha))
    y = title_y + shift
    line_h = int(title_size * 1.22)
    for i, line in enumerate(lines):
        fill = MINT if i in accent_indexes else WHITE
        progress = clamp((p - 0.025 - i * 0.055) / 0.22)
        draw_kinetic_center(draw, y + i * line_h, line, font("bold", title_size), fill, progress)
    if subtitle:
        sub_intro = ease(clamp((p - 0.18) / 0.24))
        sy = subtitle_y if subtitle_y is not None else y + len(lines) * line_h + 27
        draw_wrapped(draw, 82, sy + shift + int((1 - sub_intro) * 18), subtitle, 916,
                     font("regular", 31), (*MUTED, int(255 * sub_intro)), 43, align="center")


def entry(p: float, delay: float = 0.0, duration: float = 0.3) -> float:
    return ease(clamp((p - delay) / duration))


def draw_scene_1(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "Pour les freelances", ["Tes demandes", "arrivent partout."],
                  "Messages, recommandations, réseaux sociaux.", p, title_y=295, title_size=86,
                  accent_indexes=(1,), subtitle_y=558)
    cards = [
        (68, 760, 512, 930, "MESSAGE PRIVÉ", "Tu serais disponible pour un projet ?", -1),
        (565, 950, 1008, 1125, "RECOMMANDATION", "On m’a parlé de ton travail.", 1),
        (84, 1162, 590, 1344, "RÉSEAUX SOCIAUX", "Nouvelle demande à suivre.", -1),
        (507, 1384, 1005, 1552, "À TRAITER", "Une opportunité de plus.", 1),
    ]
    for i, (x1, y1, x2, y2, label, body, direction) in enumerate(cards):
        r = entry(p, 0.10 + i * 0.075, 0.34)
        float_phase = p * math.tau * 1.15 + i * 1.7
        x = x1 + int(direction * (1 - r) * 120) + int(math.sin(float_phase) * 13)
        dy = int(math.sin(float_phase + 0.8) * 16)
        draw_card(draw, (x, y1 + dy, x + (x2 - x1), y2 + dy), radius=26,
                  accent=MINT if i == 0 else None)
        draw_left(draw, x + 31, y1 + dy + 26, label, font("mono", 18), MINT if i == 0 else MUTED)
        draw_wrapped(draw, x + 31, y1 + dy + 72, body, (x2 - x1) - 62,
                     font("regular", 27), WHITE, 35)
    draw_center(draw, 1630, "Chaque opportunité mérite qu’on lui donne suite.", font("regular", 27), MUTED)


def draw_scene_2(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "Le quotidien du freelance", ["Tout repose sur toi.", "La machine ralentit."],
                  "Qualification, contenu et prospection prennent de la place.", p,
                  title_y=292, title_size=78, accent_indexes=(1,), subtitle_y=535)
    rows = [
        ("01", "QUALIFIER", "Reposer les mêmes questions."),
        ("02", "CRÉER", "Trouver le temps de publier."),
        ("03", "PROSPECTER", "Préparer chaque prise de contact."),
    ]
    for i, (num, label, detail) in enumerate(rows):
        r = entry(p, 0.10 + i * 0.09, 0.24)
        pulse = 0.48 + 0.52 * (0.5 + 0.5 * math.sin(p * math.tau * 2.2 + i * 1.8))
        y = 755 + i * 220 + int((1 - r) * 50) + int(math.sin(p * math.tau * 1.1 + i) * 7)
        draw_card(draw, (92, y, 988, y + 168), radius=26, accent=MINT if i == 0 else None)
        draw_left(draw, 126, y + 32, num, font("mono", 23), MINT)
        draw_left(draw, 208, y + 28, label, font("bold", 25), WHITE)
        draw_left(draw, 208, y + 79, detail, font("regular", 26), MUTED)
        # Moving signal bars visualize the workload, not task completion.
        rounded(draw, (858, y + 42, 938, y + 50), 4, (47, 55, 65, 255))
        rounded(draw, (858, y + 42, 858 + int(80 * pulse), y + 50), 4, (*MINT, 255))
    draw_center(draw, 1507, "Un espace pour structurer ce qui vient avant la mission.", font("regular", 25), MUTED)


def draw_scene_3(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "01 / Agent Qualification", ["Un lien public.", "Des réponses guidées."],
                  "L’IA t’aide à mieux comprendre chaque besoin.", p,
                  title_y=290, title_size=82, accent_indexes=(1,), subtitle_y=535)
    r = entry(p, 0.12, 0.32)
    link_y = 690 + int((1 - r) * 40)
    link_box = (85, link_y, 995, link_y + 84)
    draw_card(draw, link_box, radius=24, fill=(16, 20, 26, 255), outline=(*MINT, 120), shadow=False)
    draw_left(draw, 118, link_y + 28, "moteur-acquisition-360.onrender.com/?agent=ton-nom", font("mono", 21), WHITE)
    draw_pill(draw, 815, link_y + 16, "LIEN PUBLIC", accent=True, fsize=16, pad_x=16, h=50)

    cy = 824 + int((1 - r) * 55)
    draw_card(draw, (92, cy, 988, cy + 632), radius=30, fill=(18, 21, 28, 252))
    draw_left(draw, 132, cy + 34, "NOUVELLE DEMANDE", font("mono", 17), MUTED)
    draw_left(draw, 132, cy + 78, "Parle-nous de ton projet", font("bold", 31), WHITE)
    rounded(draw, (132, cy + 139, 948, cy + 141), 1, (*BORDER, 200))
    fields = [
        ("Quel est ton besoin ?", "Décris ton projet en quelques mots"),
        ("Un peu de contexte", "Ce qui est important pour toi"),
        ("Quelle est la prochaine étape ?", "Le résultat que tu recherches"),
    ]
    for i, (label, placeholder) in enumerate(fields):
        row_progress = ease(clamp((p - (0.16 + i * 0.10)) / 0.22))
        yy = cy + 169 + i * 117 + int((1 - row_progress) * 20)
        draw_left(draw, 137, yy, label, font("bold", 21), (*WHITE, int(255 * row_progress)))
        active = int(p * 5.0) % 3 == i and p > 0.24
        outline = (*MINT, 190) if active else (*BORDER, 210)
        rounded(draw, (132, yy + 39, 948, yy + 95), 15, (12, 14, 19, 255), outline, 2 if active else 1)
        type_progress = clamp((p - (0.19 + i * 0.11)) / 0.18)
        shown = placeholder[:int(len(placeholder) * ease(type_progress))]
        draw_left(draw, 154, yy + 54, shown, font("regular", 19), DIM)
        if active and type_progress < 1.0 and int(p * 12) % 2 == 0:
            caret_x = 154 + int(draw.textlength(shown, font=font("regular", 19))) + 3
            draw.line((caret_x, yy + 53, caret_x, yy + 77), fill=(*MINT, 220), width=2)
    # CTA shown as a form example only.
    rounded(draw, (132, cy + 540, 520, cy + 600), 16, (*MINT, 255))
    draw_left(draw, 164, cy + 558, "Envoyer ma demande", font("bold", 20), (12, 14, 17, 255))
    draw_left(draw, 700, cy + 562, "Questions guidées par l’IA", font("mono", 15), MUTED)


def draw_scene_4(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "Ton tableau de bord", ["Les demandes.", "Leur priorité."],
                  "Repère ce qui est nouveau ou urgent.", p,
                  title_y=292, title_size=84, accent_indexes=(1,), subtitle_y=535)
    r = entry(p, 0.11, 0.33)
    y = 745 + int((1 - r) * 55)
    draw_card(draw, (56, y, 1024, y + 720), radius=30, fill=(17, 20, 26, 255))
    draw_left(draw, 96, y + 31, "DEMANDES REÇUES", font("mono", 19), WHITE)
    draw_pill(draw, 773, y + 23, "ESPACE PRIVÉ", fsize=15, pad_x=15, h=43)
    rounded(draw, (96, y + 91, 984, y + 93), 1, (*BORDER, 200))
    draw_pill(draw, 96, y + 119, "Toutes", accent=True, fsize=17, pad_x=17, h=44)
    draw_pill(draw, 219, y + 119, "Urgentes", fsize=17, pad_x=17, h=44)
    rows = [
        ("URGENTE", "Aujourd’hui · 14:32", "Boutique en ligne", "Automatiser le traitement des commandes."),
        ("À COURT TERME", "Hier · 18:07", "PME", "Organiser les demandes et améliorer le suivi."),
    ]
    for i, (status, date, client, desc) in enumerate(rows):
        rr = entry(p, 0.16 + i * 0.12, 0.24)
        yy = y + 190 + i * 230 + int((1 - rr) * 42) + int(math.sin(p * math.tau * 1.2 + i) * 5)
        rounded(draw, (92, yy, 988, yy + 203), 23, (21, 25, 32, 255), (*BORDER, 180), 1)
        draw_pill(draw, 119, yy + 21, status, accent=(i == 0 and int(p * 5) % 2 == 0), fsize=15, pad_x=13, h=39)
        draw_left(draw, 782, yy + 30, date, font("mono", 14), MUTED)
        draw_left(draw, 122, yy + 77, client, font("bold", 24), WHITE)
        draw_wrapped(draw, 122, yy + 121, desc, 800, font("regular", 20), MUTED, 28)
        scan_x = 116 + int(((p * 1.7 + i * 0.32) % 1.0) * 710)
        draw.line((scan_x, yy + 193, scan_x + 92, yy + 193), fill=(*MINT, 95), width=2)
    draw_left(draw, 100, y + 670, "TRIER PAR PRIORITÉ OU PAR DATE", font("mono", 14), DIM)


def draw_scene_5(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "02 / Agent Contenu", ["Une idée brute.", "Un contenu à travailler."],
                  "LinkedIn · Facebook · prompt visuel", p,
                  title_y=290, title_size=78, accent_indexes=(1,), subtitle_y=535)
    r1 = entry(p, 0.10, 0.24)
    y1 = 710 + int((1 - r1) * 46) + int(math.sin(p * math.tau * 1.15) * 8)
    draw_card(draw, (84, y1, 996, y1 + 222), radius=28, fill=(18, 21, 28, 255), accent=LILAC)
    draw_left(draw, 124, y1 + 29, "TON IDÉE", font("mono", 17), LILAC)
    draw_wrapped(draw, 124, y1 + 77, "Partager 3 conseils pour mieux cadrer une mission freelance", 820,
                 font("bold", 29), WHITE, 38)
    # A moving signal travels from the raw idea toward its draft.
    r2 = entry(p, 0.25, 0.24)
    y2 = 1028 + int((1 - r2) * 54) + int(math.sin(p * math.tau * 1.15 + 0.8) * 8)
    start_y, end_y = y1 + 226, y2 - 18
    draw.line((W // 2, start_y, W // 2, end_y), fill=(*MINT, 100), width=3)
    dot_phase = (p * 1.7) % 1.0
    dot_y = int(start_y + (end_y - start_y) * dot_phase)
    draw.ellipse((W // 2 - 10, dot_y - 10, W // 2 + 10, dot_y + 10), fill=(*MINT, 255))
    draw_card(draw, (84, y2, 996, y2 + 454), radius=28, fill=(18, 21, 28, 255))
    draw_pill(draw, 122, y2 + 26, "PUBLICATION · LINKEDIN", accent=True, fsize=16, pad_x=15, h=44)
    draw_left(draw, 124, y2 + 96, "3 questions à poser avant de lancer un projet", font("bold", 28), WHITE)
    draw_wrapped(draw, 124, y2 + 151,
                 "Un bon brief commence par le besoin, le contexte et la prochaine étape. Voici comment les clarifier.",
                 812, font("regular", 21), MUTED, 31)
    rounded(draw, (124, y2 + 338, 949, y2 + 340), 1, (*BORDER, 190))
    draw_left(draw, 124, y2 + 363, "SORTIE", font("mono", 15), DIM)
    draw_left(draw, 124, y2 + 394, "Texte prêt à relire · prompt visuel disponible", font("regular", 18), MUTED)


def draw_scene_6(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "03 / Agent Prospection", ["Des messages", "plus personnalisés."],
                  "À partir des informations dont tu disposes.", p,
                  title_y=290, title_size=82, accent_indexes=(1,), subtitle_y=535)
    r = entry(p, 0.08, 0.24)
    pill_y = 718 + int((1 - r) * 42) + int(math.sin(p * math.tau * 1.2) * 5)
    labels = ["LINKEDIN", "EMAIL", "WHATSAPP"]
    active_idx = int(p * 3.4) % len(labels)
    x = 104
    for i, label in enumerate(labels):
        w = draw_pill(draw, x, pill_y, label, accent=(i == active_idx), fsize=18, pad_x=20, h=49)
        x += w + 20
    cy = 828 + int((1 - r) * 55) + int(math.sin(p * math.tau * 1.0 + 0.6) * 8)
    draw_card(draw, (84, cy, 996, cy + 610), radius=29, fill=(18, 21, 28, 255))
    draw_left(draw, 125, cy + 34, "BROUILLON PERSONNALISÉ", font("mono", 16), MINT)
    draw_left(draw, 125, cy + 87, "Objet · Une idée pour votre activité", font("bold", 24), WHITE)
    rounded(draw, (124, cy + 141, 954, cy + 143), 1, (*BORDER, 200))
    greeting_progress = ease(clamp((p - 0.14) / 0.18))
    draw_left(draw, 126, cy + 174, "Bonjour [Prénom],"[:int(len("Bonjour [Prénom],") * greeting_progress)], font("regular", 25), WHITE)
    message = "J’ai remarqué [élément de contexte]. Je vous écris au sujet de [besoin repéré] et d’une piste qui pourrait vous être utile."
    typing = ease(clamp((p - 0.22) / 0.37))
    typed = message[:int(len(message) * typing)]
    draw_wrapped(draw, 126, cy + 226, typed, 790, font("regular", 23), MUTED, 36)
    if typing < 1.0 and int(p * 12) % 2 == 0:
        cursor_x = 126 + int(draw.textlength(typed[-42:], font=font("regular", 23))) + 3
        draw.line((cursor_x, cy + 260, cursor_x, cy + 286), fill=(*MINT, 220), width=2)
    draw_left(draw, 126, cy + 400, "À adapter selon le prospect et le contexte.", font("regular", 18), DIM)
    rounded(draw, (124, cy + 470, 952, cy + 472), 1, (*BORDER, 180))
    draw_pill(draw, 125, cy + 505, "À RELIRE AVANT ENVOI", accent=False, fsize=15, pad_x=15, h=42)


def draw_scene_7(draw: ImageDraw.ImageDraw, p: float) -> None:
    intro = ease(clamp(p / 0.28))
    shift = int((1 - intro) * 30)
    draw_center(draw, 205 + shift, "MOTEUR D’ACQUISITION 360°", font("mono", 22), (*MINT, int(255 * intro)))
    lines = [("Attirer.", WHITE), ("Qualifier.", MINT), ("Développer.", WHITE)]
    for i, (txt, color) in enumerate(lines):
        draw_kinetic_center(draw, 278 + shift + i * 104, txt, font("bold", 78), color,
                            clamp((p - 0.02 - i * 0.045) / 0.24), stagger=0.08, duration=0.25)
    sub_alpha = int(255 * ease(clamp((p - 0.22) / 0.24)))
    draw_center(draw, 620 + shift, "Trois briques. Un seul système.", font("regular", 31), (*MUTED, sub_alpha))

    rows = [
        ("01", "ATTIRER", "Agent Contenu", LILAC),
        ("02", "QUALIFIER", "Agent Qualification", MINT),
        ("03", "DÉVELOPPER", "Agent Prospection", WHITE),
    ]
    # The moving connector makes the three-agent handoff legible without claiming automation.
    draw.line((540, 785, 540, 1318), fill=(77, 88, 101, 165), width=3)
    node_y = 785 + int(((p * 1.8) % 1.0) * 533)
    draw.ellipse((530, node_y - 10, 550, node_y + 10), fill=(*MINT, 245))
    for i, (num, title, detail, accent) in enumerate(rows):
        r = entry(p, 0.08 + i * 0.10, 0.22)
        y = 770 + i * 190 + int((1 - r) * 58) + int(math.sin(p * math.tau * 1.0 + i) * 5)
        draw_card(draw, (125, y, 955, y + 141), radius=26, accent=accent if accent in (MINT, LILAC) else None)
        draw_left(draw, 160, y + 25, num, font("mono", 18), accent)
        draw_left(draw, 233, y + 20, title, font("bold", 24), WHITE)
        draw_left(draw, 233, y + 66, detail, font("regular", 22), MUTED)
        cx, cy = 892, y + 68
        draw.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), outline=(*accent, 230), width=3)
        angle = p * math.tau * 2.0 + i * 2.1
        dot_x, dot_y = cx + math.cos(angle) * 11, cy + math.sin(angle) * 11
        draw.ellipse((int(dot_x - 5), int(dot_y - 5), int(dot_x + 5), int(dot_y + 5)), fill=(*accent, 255))
    draw_pill(draw, 295, 1402, "UN SEUL ESPACE DE TRAVAIL", accent=True, fsize=19, pad_x=24, h=56)


def draw_scene_8(draw: ImageDraw.ImageDraw, p: float) -> None:
    intro = ease(clamp(p / 0.30))
    shift = int((1 - intro) * 28)
    draw_center(draw, 236 + shift, "MOTEUR D’ACQUISITION", font("mono", 20), (*MUTED, int(255 * intro)))
    mark_size = int(122 + 7 * math.sin(p * math.tau * 2.0))
    draw_kinetic_center(draw, 285 + shift, "360°", font("bold", mark_size), MINT,
                        clamp((p - 0.015) / 0.22), stagger=0.05, duration=0.25)
    draw_kinetic_center(draw, 449 + shift, "Un système qui travaille", font("bold", 52), WHITE,
                        clamp((p - 0.08) / 0.24), stagger=0.075, duration=0.30)
    draw_kinetic_center(draw, 514 + shift, "avec toi.", font("bold", 52), WHITE,
                        clamp((p - 0.15) / 0.24), stagger=0.10, duration=0.28)
    draw_center(draw, 630 + shift, "POUR LES FREELANCES", font("mono", 19), (*MUTED, int(255 * intro)))

    r = entry(p, 0.08, 0.22)
    y = 748 + int((1 - r) * 42) + int(math.sin(p * math.tau * 0.9) * 5)
    draw_card(draw, (82, y, 998, y + 335), radius=30, fill=(18, 21, 28, 255), outline=(*MINT, 100))
    draw_left(draw, 126, y + 34, "OFFRE DE TEST", font("mono", 17), MINT)
    price_size = int(72 + 4 * math.sin(p * math.tau * 1.5))
    draw_left(draw, 126, y + 83, "0 F CFA", font("bold", price_size), WHITE)
    draw_left(draw, 126, y + 180, "Gratuit pendant la phase de test.", font("regular", 27), WHITE)
    draw_left(draw, 126, y + 236, "Sans carte bancaire. Sans engagement.", font("regular", 21), MUTED)

    button_y = 1174 + int((1 - r) * 40)
    pulse = 1.0 + 0.024 * math.sin(p * math.pi * 8)
    bw = int(882 * pulse)
    bx = (W - bw) // 2
    rounded(draw, (bx, button_y, bx + bw, button_y + 116), 25, (*MINT, 255))
    draw_center(draw, button_y + 33, "CRÉE TON ESPACE GRATUITEMENT", font("bold", 25), (12, 14, 17, 255))
    draw_center(draw, button_y + 69, "→", font("bold", 30), (12, 14, 17, 255))
    shine_x = bx + 22 + int(((p * 2.2) % 1.0) * (bw - 44))
    draw.line((shine_x, button_y + 18, shine_x, button_y + 97), fill=(255, 255, 255, 125), width=4)
    draw_center(draw, 1353, "moteur-acquisition-360.onrender.com", font("mono", 19), WHITE)
    draw_center(draw, 1502, "Attirer · Qualifier · Développer", font("regular", 24), MUTED)
    # A subtle, deterministic orbit suggests a connected system without inventing a logo.
    cx, cy = W // 2, 1682
    radius = 84
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(70, 81, 92, 170), width=2)
    angle = p * math.tau * 3.4
    for i, col in enumerate((MINT, LILAC, WHITE)):
        a = angle + i * (2 * math.pi / 3)
        x = cx + math.cos(a) * radius
        yy = cy + math.sin(a) * radius
        draw.ellipse((int(x - 7), int(yy - 7), int(x + 7), int(yy + 7)), fill=(*col, 255))


def apply_alpha(layer: Image.Image, opacity: float) -> Image.Image:
    if opacity >= 0.999:
        return layer
    lut = [int(i * opacity) for i in range(256)]
    layer.putalpha(layer.getchannel("A").point(lut))
    return layer


def draw_transition_fx(draw: ImageDraw.ImageDraw, elapsed: float, scene_idx: int) -> None:
    """Fast diagonal light-slice on each cut, with a short directional streak."""
    span = 0.34
    q = clamp(elapsed / span)
    if elapsed < 0 or elapsed > span:
        return
    strength = math.sin(math.pi * q)
    x = -430 + q * (W + 860)
    alpha = int(75 * strength)
    points = [(int(x - 130), 0), (int(x - 45), 0),
              (int(x + 335), H), (int(x + 250), H)]
    tint = MINT if scene_idx % 2 == 0 else LILAC
    draw.polygon(points, fill=(*tint, alpha))
    draw.line((int(x + 12), 0, int(x + 392), H), fill=(*WHITE, int(125 * strength)), width=4)
    draw.line((int(x - 42), 0, int(x + 338), H), fill=(*tint, int(80 * strength)), width=2)


def camera_move(frame: Image.Image, p: float, t: float, scene_idx: int, scene_start: float) -> Image.Image:
    """Deterministic punch-in/pull-out with a short whip-settle at every cut."""
    intro = 1.0 - ease(clamp((t - scene_start) / 0.28))
    zoom = 1.0 + 0.042 * math.sin(math.pi * p) ** 2 + 0.018 * intro
    sw, sh = int(W * zoom), int(H * zoom)
    scaled = frame.resize((sw, sh), Image.Resampling.LANCZOS)
    pan_x = int(math.sin(p * math.tau + scene_idx * 0.75) * 15 + (1 if scene_idx % 2 == 0 else -1) * intro * 28)
    pan_y = int(math.cos(p * math.tau * 0.78 + scene_idx) * 16 - intro * 22)
    left = max(0, min(sw - W, int((sw - W) / 2 + pan_x)))
    top = max(0, min(sh - H, int((sh - H) / 2 + pan_y)))
    return scaled.crop((left, top, left + W, top + H))


def render_frame(t: float) -> Image.Image:
    idx = next((i for i, (a, b, _) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)
    start, end, _ = SCENES[idx]
    p = clamp((t - start) / (end - start))
    # Only the video head and tail fade; scene-to-scene changes are whip cuts.
    opacity = ease(clamp(t / 0.08)) * min(1.0, max(0.0, (DURATION - t) / 0.10))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    draw_wordmark(d, idx, p)
    scene_fn = [draw_scene_1, draw_scene_2, draw_scene_3, draw_scene_4,
                draw_scene_5, draw_scene_6, draw_scene_7, draw_scene_8][idx]
    scene_fn(d, p)
    draw_transition_fx(d, t - start, idx)
    layer = apply_alpha(layer, opacity)
    frame = BACKGROUND.copy()
    frame.alpha_composite(layer)
    return camera_move(frame.convert("RGB"), p, t, idx, start)


def make_score(path: Path) -> dict:
    """Write an upbeat original electronic score. No external samples or copyrighted track."""
    path.parent.mkdir(parents=True, exist_ok=True)
    chord_sets = [
        (73.416, 110.000, 146.832, 174.614),  # Dm add9
        (58.270, 87.307, 110.000, 146.832),   # Bb add9
        (87.307, 130.813, 164.814, 220.000),  # Fmaj7
        (65.406, 98.000, 146.832, 164.814),   # C add9
    ]
    roots = [73.416, 58.270, 87.307, 65.406]
    samples = int(SR * DURATION)
    peak = 0.0
    square_sum = 0.0
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        buf = bytearray()
        for i in range(samples):
            t = i / SR
            chord_idx = int(t / 2.0) % 4
            chord_age = t % 2.0
            notes = chord_sets[chord_idx]
            attack = min(1.0, chord_age / 0.22)
            chord_release = min(1.0, max(0.0, 2.0 - chord_age) / 0.28)
            release = min(1.0, max(0.0, DURATION - t) / 1.5)
            env = attack * chord_release * release
            pad = 0.0
            for ni, freq in enumerate(notes):
                # Brighter, slightly detuned synth layers; chord changes every two seconds.
                phase = 2 * math.pi * freq * t
                pad += math.sin(phase + ni * 0.17) * 0.020
                pad += math.sin(phase * 2.001 + ni * 0.41) * 0.005
            pad *= env
            bass = math.sin(2 * math.pi * roots[chord_idx] * t) * env * 0.018

            # Four-on-the-floor pulse at 120 BPM with a snare-like synthetic backbeat.
            beat_phase = t % 0.5
            beat_env = math.exp(-beat_phase * 17.0) if beat_phase < 0.25 else 0.0
            kick_freq = 84.0 - 40.0 * min(1.0, beat_phase / 0.15)
            kick = math.sin(2 * math.pi * kick_freq * beat_phase) * beat_env * 0.095
            beat_number = int(t / 0.5)
            clap = 0.0
            if beat_number % 2 == 1 and beat_phase < 0.14:
                clap_env = math.exp(-beat_phase * 34.0)
                clap = (math.sin(2 * math.pi * 2100 * beat_phase)
                        + 0.6 * math.sin(2 * math.pi * 3700 * beat_phase)
                        + 0.35 * math.sin(2 * math.pi * 5400 * beat_phase)) * clap_env * 0.014
            eighth_phase = t % 0.25
            hat = (math.sin(2 * math.pi * 5900 * eighth_phase)
                   + 0.5 * math.sin(2 * math.pi * 8100 * eighth_phase)) * math.exp(-eighth_phase * 55.0) * 0.004

            # Brisk eighth-note arpeggio follows the current chord.
            step = int(t / 0.25)
            pluck_age = t - step * 0.25
            pluck_freq = notes[(step * 3) % len(notes)] * 2
            pluck_env = math.exp(-pluck_age * 8.0)
            pluck = math.sin(2 * math.pi * pluck_freq * pluck_age) * pluck_env * 0.026
            pluck += math.sin(2 * math.pi * pluck_freq * 1.5 * pluck_age) * pluck_env * 0.007

            # Light cue on each narrative beat; entirely synthesized.
            cue = 0.0
            for beat in (4.0, 7.7, 12.0, 16.2, 20.3, 24.4, 28.0):
                age = t - beat
                if 0 <= age < 0.20:
                    cue += math.sin(2 * math.pi * (880 - 380 * age) * age) * math.exp(-age * 22) * 0.014

            fade = min(1.0, t / 0.9) * min(1.0, max(0.0, DURATION - t) / 1.5)
            mono = (pad + bass + kick + clap + hat + pluck + cue) * fade
            # Gentle stereo spread, not a hard pan.
            left = mono * (0.91 + 0.05 * math.sin(2 * math.pi * 0.11 * t))
            right = mono * (0.91 + 0.05 * math.sin(2 * math.pi * 0.11 * t + 0.7))
            left = max(-0.9, min(0.9, left))
            right = max(-0.9, min(0.9, right))
            peak = max(peak, abs(left), abs(right))
            square_sum += left * left + right * right
            buf.extend(struct.pack("<hh", int(left * 32767), int(right * 32767)))
            if len(buf) >= 1024 * 1024:
                wf.writeframesraw(buf)
                buf.clear()
        if buf:
            wf.writeframesraw(buf)
    rms = math.sqrt(square_sum / (samples * 2))
    return {"sample_rate": SR, "duration_seconds": DURATION, "peak": peak, "rms": rms}


def main() -> int:
    for folder in (AUDIO, RENDERS, SNAPSHOTS):
        folder.mkdir(parents=True, exist_ok=True)
    output = RENDERS / "moteur-acquisition-360-vertical.mp4"
    score = AUDIO / "score.wav"
    score_stats = make_score(score)
    ffmpeg = get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{W}x{H}",
        "-framerate", str(FPS), "-i", "pipe:0",
        "-i", str(score),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level:v", "4.1",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-shortest", "-movflags", "+faststart",
        "-metadata", "title=Moteur d’Acquisition 360° — vidéo verticale",
        "-metadata", "comment=UI illustrative; textes fondés sur la page publique",
        str(output),
    ]
    print(f"Rendering {TOTAL_FRAMES} frames at {W}x{H} {FPS} fps -> {output}", flush=True)
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert process.stdin is not None
    started = time.time()
    snapshot_times = [1.2, 5.6, 9.8, 14.2, 18.3, 22.3, 26.1, 31.2]
    snapshot_index = 0
    try:
        for i in range(TOTAL_FRAMES):
            t = i / FPS
            frame = render_frame(t)
            if snapshot_index < len(snapshot_times) and t >= snapshot_times[snapshot_index]:
                frame.save(SNAPSHOTS / f"keyframe-{snapshot_index + 1:02d}.png", optimize=True)
                snapshot_index += 1
            process.stdin.write(frame.tobytes())
            if i and i % 150 == 0:
                print(f"  {i}/{TOTAL_FRAMES} frames ({100 * i / TOTAL_FRAMES:.0f}%)", flush=True)
        process.stdin.close()
    except Exception:
        process.stdin.close()
        process.terminate()
        raise
    stderr = process.stderr.read() if process.stderr else b""
    code = process.wait()
    if code:
        raise RuntimeError(f"FFmpeg exited {code}: {stderr.decode('utf-8', 'replace')}")
    elapsed = time.time() - started
    # The first frame doubles as a poster/thumbnail; the final scene is also captured for inspection.
    render_frame(0.55).save(SNAPSHOTS / "cover.png", optimize=True)
    render_frame(31.2).save(SNAPSHOTS / "end-card.png", optimize=True)
    print(f"Rendered {output.stat().st_size:,} bytes in {elapsed:.1f}s", flush=True)
    print(f"Score: {score_stats}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
