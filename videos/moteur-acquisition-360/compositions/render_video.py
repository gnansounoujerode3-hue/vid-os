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


def draw_wordmark(draw: ImageDraw.ImageDraw, scene_idx: int) -> None:
    # Typographic use of the published product name; no unofficial icon is fabricated.
    draw_left(draw, 70, 52, "MOTEUR", font("bold", 23), WHITE)
    draw_left(draw, 175, 55, "D’ACQUISITION 360°", font("mono", 17), MUTED)
    draw_left(draw, 940, 55, f"{scene_idx + 1:02d} / 08", font("mono", 17), MUTED)
    x0, y0, x1 = 70, 112, 1010
    draw.line((x0, y0, x1, y0), fill=(50, 57, 68, 190), width=2)
    full = x1 - x0
    current = sum(end - start for start, end, _ in SCENES[:scene_idx])
    draw.line((x0, y0, x0 + int(full * current / DURATION), y0), fill=(*MINT, 210), width=3)


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


def scene_heading(draw: ImageDraw.ImageDraw, kicker: str, lines: list[str], subtitle: str,
                  p: float, *, title_y: int = 300, title_size: int = 86,
                  accent_indexes: tuple[int, ...] = (1,), subtitle_y: int | None = None) -> None:
    intro = ease(clamp(p / 0.32))
    shift = int((1 - intro) * 34)
    draw_center(draw, 205 + shift, kicker.upper(), font("mono", 22), MINT)
    y = title_y + shift
    line_h = int(title_size * 1.22)
    for i, line in enumerate(lines):
        fill = MINT if i in accent_indexes else WHITE
        draw_center(draw, y + i * line_h, line, font("bold", title_size), fill)
    if subtitle:
        sy = subtitle_y if subtitle_y is not None else y + len(lines) * line_h + 27
        draw_wrapped(draw, 82, sy + shift, subtitle, 916, font("regular", 31), MUTED, 43, align="center")


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
        x = x1 + int(direction * (1 - r) * 90)
        dy = int(math.sin(p * 7 + i) * 5)
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
        r = entry(p, 0.12 + i * 0.11, 0.30)
        y = 755 + i * 220 + int((1 - r) * 38)
        draw_card(draw, (92, y, 988, y + 168), radius=26, accent=MINT if i == 0 else None)
        draw_left(draw, 126, y + 32, num, font("mono", 23), MINT)
        draw_left(draw, 208, y + 28, label, font("bold", 25), WHITE)
        draw_left(draw, 208, y + 79, detail, font("regular", 26), MUTED)
        # A small, restrained progress track—not a claim of automated completion.
        rounded(draw, (858, y + 42, 938, y + 50), 4, (47, 55, 65, 255))
        rounded(draw, (858, y + 42, 858 + int(80 * r), y + 50), 4, (*MINT, 255))
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
        yy = cy + 169 + i * 117
        draw_left(draw, 137, yy, label, font("bold", 21), WHITE)
        rounded(draw, (132, yy + 39, 948, yy + 95), 15, (12, 14, 19, 255), (*BORDER, 210), 1)
        draw_left(draw, 154, yy + 54, placeholder, font("regular", 19), DIM)
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
        rr = entry(p, 0.24 + i * 0.15, 0.34)
        yy = y + 190 + i * 230 + int((1 - rr) * 34)
        rounded(draw, (92, yy, 988, yy + 203), 23, (21, 25, 32, 255), (*BORDER, 180), 1)
        draw_pill(draw, 119, yy + 21, status, accent=(i == 0), fsize=15, pad_x=13, h=39)
        draw_left(draw, 782, yy + 30, date, font("mono", 14), MUTED)
        draw_left(draw, 122, yy + 77, client, font("bold", 24), WHITE)
        draw_wrapped(draw, 122, yy + 121, desc, 800, font("regular", 20), MUTED, 28)
    draw_left(draw, 100, y + 670, "TRIER PAR PRIORITÉ OU PAR DATE", font("mono", 14), DIM)


def draw_scene_5(draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_heading(draw, "02 / Agent Contenu", ["Une idée brute.", "Un contenu à travailler."],
                  "LinkedIn · Facebook · prompt visuel", p,
                  title_y=290, title_size=78, accent_indexes=(1,), subtitle_y=535)
    r1 = entry(p, 0.12, 0.28)
    y1 = 710 + int((1 - r1) * 42)
    draw_card(draw, (84, y1, 996, y1 + 222), radius=28, fill=(18, 21, 28, 255), accent=LILAC)
    draw_left(draw, 124, y1 + 29, "TON IDÉE", font("mono", 17), LILAC)
    draw_wrapped(draw, 124, y1 + 77, "Partager 3 conseils pour mieux cadrer une mission freelance", 820,
                 font("bold", 29), WHITE, 38)
    # Animated path from raw idea to a usable draft.
    mid = 976
    draw.line((W // 2, y1 + 226, W // 2, mid - 18), fill=(*MINT, 170), width=3)
    draw.ellipse((W // 2 - 8, mid - 8, W // 2 + 8, mid + 8), fill=(*MINT, 255))
    r2 = entry(p, 0.32, 0.30)
    y2 = 1028 + int((1 - r2) * 54)
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
    r = entry(p, 0.12, 0.30)
    pill_y = 718 + int((1 - r) * 35)
    x = 104
    for label in ["LINKEDIN", "EMAIL", "WHATSAPP"]:
        w = draw_pill(draw, x, pill_y, label, accent=(label == "LINKEDIN"), fsize=18, pad_x=20, h=49)
        x += w + 20
    cy = 828 + int((1 - r) * 48)
    draw_card(draw, (84, cy, 996, cy + 610), radius=29, fill=(18, 21, 28, 255))
    draw_left(draw, 125, cy + 34, "BROUILLON PERSONNALISÉ", font("mono", 16), MINT)
    draw_left(draw, 125, cy + 87, "Objet · Une idée pour votre activité", font("bold", 24), WHITE)
    rounded(draw, (124, cy + 141, 954, cy + 143), 1, (*BORDER, 200))
    draw_left(draw, 126, cy + 174, "Bonjour [Prénom],", font("regular", 25), WHITE)
    draw_wrapped(draw, 126, cy + 226,
                 "J’ai remarqué [élément de contexte]. Je vous écris au sujet de [besoin repéré] et d’une piste qui pourrait vous être utile.",
                 790, font("regular", 23), MUTED, 36)
    draw_left(draw, 126, cy + 400, "À adapter selon le prospect et le contexte.", font("regular", 18), DIM)
    rounded(draw, (124, cy + 470, 952, cy + 472), 1, (*BORDER, 180))
    draw_pill(draw, 125, cy + 505, "À RELIRE AVANT ENVOI", accent=False, fsize=15, pad_x=15, h=42)


def draw_scene_7(draw: ImageDraw.ImageDraw, p: float) -> None:
    intro = ease(clamp(p / 0.32))
    shift = int((1 - intro) * 34)
    draw_center(draw, 205 + shift, "MOTEUR D’ACQUISITION 360°", font("mono", 22), MINT)
    lines = [("Attirer.", WHITE), ("Qualifier.", MINT), ("Développer.", WHITE)]
    for i, (txt, color) in enumerate(lines):
        draw_center(draw, 278 + shift + i * 104, txt, font("bold", 78), color)
    draw_center(draw, 620 + shift, "Trois briques. Un seul système.", font("regular", 31), MUTED)

    rows = [
        ("01", "ATTIRER", "Agent Contenu", LILAC),
        ("02", "QUALIFIER", "Agent Qualification", MINT),
        ("03", "DÉVELOPPER", "Agent Prospection", WHITE),
    ]
    for i, (num, title, detail, accent) in enumerate(rows):
        r = entry(p, 0.12 + i * 0.13, 0.30)
        y = 770 + i * 190 + int((1 - r) * 45)
        draw_card(draw, (125, y, 955, y + 141), radius=26, accent=accent if accent in (MINT, LILAC) else None)
        draw_left(draw, 160, y + 25, num, font("mono", 18), accent)
        draw_left(draw, 233, y + 20, title, font("bold", 24), WHITE)
        draw_left(draw, 233, y + 66, detail, font("regular", 22), MUTED)
        draw.ellipse((875, y + 51, 909, y + 85), outline=(*accent, 255), width=3)
        draw.ellipse((887, y + 63, 897, y + 73), fill=(*accent, 255))
    draw_pill(draw, 295, 1402, "UN SEUL ESPACE DE TRAVAIL", accent=True, fsize=19, pad_x=24, h=56)


def draw_scene_8(draw: ImageDraw.ImageDraw, p: float) -> None:
    intro = ease(clamp(p / 0.30))
    shift = int((1 - intro) * 28)
    draw_center(draw, 236 + shift, "MOTEUR D’ACQUISITION", font("mono", 20), MUTED)
    draw_center(draw, 285 + shift, "360°", font("bold", 122), MINT)
    draw_center(draw, 449 + shift, "Un système qui travaille", font("bold", 52), WHITE)
    draw_center(draw, 514 + shift, "avec toi.", font("bold", 52), WHITE)
    draw_center(draw, 630 + shift, "POUR LES FREELANCES", font("mono", 19), MUTED)

    r = entry(p, 0.12, 0.30)
    y = 748 + int((1 - r) * 42)
    draw_card(draw, (82, y, 998, y + 335), radius=30, fill=(18, 21, 28, 255), outline=(*MINT, 100))
    draw_left(draw, 126, y + 34, "OFFRE DE TEST", font("mono", 17), MINT)
    draw_left(draw, 126, y + 83, "0 F CFA", font("bold", 72), WHITE)
    draw_left(draw, 126, y + 180, "Gratuit pendant la phase de test.", font("regular", 27), WHITE)
    draw_left(draw, 126, y + 236, "Sans carte bancaire. Sans engagement.", font("regular", 21), MUTED)

    button_y = 1174 + int((1 - r) * 40)
    pulse = 1.0 + 0.015 * math.sin(p * math.pi * 8)
    bw = int(882 * pulse)
    bx = (W - bw) // 2
    rounded(draw, (bx, button_y, bx + bw, button_y + 116), 25, (*MINT, 255))
    draw_center(draw, button_y + 33, "CRÉE TON ESPACE GRATUITEMENT", font("bold", 25), (12, 14, 17, 255))
    draw_center(draw, button_y + 69, "→", font("bold", 30), (12, 14, 17, 255))
    draw_center(draw, 1353, "moteur-acquisition-360.onrender.com", font("mono", 19), WHITE)
    draw_center(draw, 1502, "Attirer · Qualifier · Développer", font("regular", 24), MUTED)
    # A subtle, deterministic orbit suggests a connected system without inventing a logo.
    cx, cy = W // 2, 1682
    radius = 84
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(70, 81, 92, 170), width=2)
    angle = p * math.pi * 4
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


def render_frame(t: float) -> Image.Image:
    idx = next((i for i, (a, b, _) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)
    start, end, _ = SCENES[idx]
    p = clamp((t - start) / (end - start))
    # Brief, clean fades between cards; content remains seekable and deterministic.
    fade_in = ease(clamp((t - start) / 0.20))
    fade_out = ease(clamp((end - t) / 0.20))
    opacity = min(fade_in, fade_out)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    draw_wordmark(d, idx)
    scene_fn = [draw_scene_1, draw_scene_2, draw_scene_3, draw_scene_4,
                draw_scene_5, draw_scene_6, draw_scene_7, draw_scene_8][idx]
    scene_fn(d, p)
    layer = apply_alpha(layer, opacity)
    frame = BACKGROUND.copy()
    frame.alpha_composite(layer)
    return frame.convert("RGB")


def make_score(path: Path) -> dict:
    """Write a quiet original synth bed. No external samples or copyrighted track."""
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
            chord_idx = int(t / 4.0) % 4
            chord_age = t % 4.0
            notes = chord_sets[chord_idx]
            attack = min(1.0, chord_age / 0.62)
            release = min(1.0, max(0.0, DURATION - t) / 1.9)
            env = attack * release
            pad = 0.0
            for ni, freq in enumerate(notes):
                # Soft, slightly detuned sine partials for a calm modern-tech bed.
                phase = 2 * math.pi * freq * t
                pad += math.sin(phase + ni * 0.17) * 0.016
                pad += math.sin(phase * 2.001 + ni * 0.41) * 0.003
            pad *= env

            # Rounded low pulse every half second, gently ducked beneath text beats.
            beat_phase = t % 0.5
            beat_env = math.exp(-beat_phase * 18.0) if beat_phase < 0.25 else 0.0
            kick_freq = 68.0 - 23.0 * min(1.0, beat_phase / 0.16)
            kick = math.sin(2 * math.pi * kick_freq * beat_phase) * beat_env * 0.050

            # A soft arpeggio, with changing notes following the current chord.
            step = int(t / 0.5)
            pluck_age = t - step * 0.5
            pluck_freq = notes[(step * 3) % len(notes)] * 2
            pluck_env = math.exp(-pluck_age * 5.3)
            pluck = math.sin(2 * math.pi * pluck_freq * pluck_age) * pluck_env * 0.017
            pluck += math.sin(2 * math.pi * pluck_freq * 1.5 * pluck_age) * pluck_env * 0.004

            # Light cue on each narrative beat; entirely synthesized.
            cue = 0.0
            for beat in (4.0, 7.7, 12.0, 16.2, 20.3, 24.4, 28.0):
                age = t - beat
                if 0 <= age < 0.20:
                    cue += math.sin(2 * math.pi * (880 - 380 * age) * age) * math.exp(-age * 22) * 0.014

            fade = min(1.0, t / 0.9) * min(1.0, max(0.0, DURATION - t) / 1.5)
            mono = (pad + kick + pluck + cue) * fade
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
