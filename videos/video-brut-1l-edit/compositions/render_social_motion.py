#!/usr/bin/env python3
"""Render a full-screen social edit with graphic cutaways inspired by the refs.

Unlike an 'Our Work' showcase frame, this stays a conventional 9:16 video.
The original A-roll and English captions remain continuous; four short,
voice-led motion-graphic inserts add visual variety without adding narration.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from render_pinterest import (
    BASE, DURATION, FONTS, ROOT, TIMELINE, W, H,
    build_ass, ffmpeg_path, srt_time,
)

OUTPUT = ROOT / "renders" / "video-brut-1l-motion-v2-en.mp4"
ASS_PATH = ROOT / "subtitles" / "video-brut-1l-motion-v2-en.ass"
SRT_PATH = ROOT / "subtitles" / "video-brut-1l-motion-v2-en.srt"
CAPTION_JSON = ROOT / "subtitles" / "captions-motion-v2-en.json"

# ASS colours use AABBGGRR ordering.
PAPER = "&H00F1F6F7&"   # warm paper
INK = "&H001B1916&"
PURPLE = "&H00EB2E83&"  # reference-inspired violet
GREEN = "&H0094E7A3&"   # lively priority green
WHITE = "&H00FFFFFF&"
MUTED = "&H007A7975&"
DARK = "&H0017120F&"


def at(seconds: float) -> str:
    from render_pinterest import ass_time
    return ass_time(seconds)


def rect(layer: int, start: float, end: float, x: int, y: int, width: int, height: int,
         fill: str, *, fade: int = 90) -> str:
    drawing = f"m 0 0 l {width} 0 {width} {height} 0 {height}"
    tag = f"{{\\an7\\pos({x},{y})\\p1\\bord0\\shad0\\c{fill}\\fad({fade},{fade})}}"
    return f"Dialogue: {layer},{at(start)},{at(end)},Kicker,,0,0,0,,{tag}{drawing}{{\\p0}}"


def outline_rect(layer: int, start: float, end: float, x: int, y: int, width: int, height: int,
                 color: str, *, stroke: int = 4, fade: int = 90) -> str:
    drawing = f"m 0 0 l {width} 0 {width} {height} 0 {height}"
    tag = (f"{{\\an7\\pos({x},{y})\\p1\\bord{stroke}\\3c{color}\\1a&HFF&"
           f"\\shad0\\fad({fade},{fade})}}")
    return f"Dialogue: 6,{at(start)},{at(end)},Title,,0,0,0,,{tag}{drawing}{{\\p0}}"


def text(layer: int, start: float, end: float, x: int, y: int, value: str, color: str,
         size: int, *, fade: int = 90, move: tuple[int, int, int, int, int, int] | None = None,
         spacing: int = 0) -> str:
    if move:
        x1, y1, x2, y2, begin, finish = move
        placement = f"\\move({x1},{y1},{x2},{y2},{begin},{finish})"
    else:
        placement = f"\\pos({x},{y})"
    tag = (f"{{\\an7{placement}\\fs{size}\\fscx93\\fscy93"
           f"\\t(0,150,\\fscx100\\fscy100)\\c{color}\\bord0\\shad0\\fad({fade},{fade})")
    if spacing:
        tag += f"\\fsp{spacing}"
    tag += "}"
    return f"Dialogue: {layer},{at(start)},{at(end)},Title,,0,0,0,,{tag}{value}"


def line(layer: int, start: float, end: float, x: int, y: int, width: int, height: int,
         color: str, *, fade: int = 80) -> str:
    return rect(layer, start, end, x, y, width, height, color, fade=fade)


def card_events() -> list[str]:
    """Timed full-frame cutaways; captions stay on top in the ASS layer stack."""
    events: list[str] = []

    # 1) Calendar cutaway — the speaker is describing cookie-cutter calendars.
    start, end = 8.12, 9.48
    events.append(rect(4, start, end, 0, 0, W, H, PAPER, fade=70))
    events.append(text(6, start + .03, end - .02, 62, 238, "CALENDARS", PURPLE, 86, fade=70,
                       move=(760, 238, 62, 238, 0, 150)))
    events.append(rect(6, start + .08, end - .03, 79, 406, 562, 374, WHITE, fade=80))
    events.append(outline_rect(start=start + .08, end=end - .03, layer=7, x=79, y=406,
                               width=562, height=374, color=INK, stroke=4, fade=80))
    events.append(rect(7, start + .12, end - .03, 82, 409, 556, 74, PURPLE, fade=70))
    # A calendar grid with one lively highlighted block; no extra spoken copy.
    for gx in (194, 306, 418, 530):
        events.append(line(7, start + .15, end - .03, gx, 490, 3, 270, MUTED, fade=70))
    for gy in (578, 666):
        events.append(line(7, start + .15, end - .03, 82, gy, 556, 3, MUTED, fade=70))
    blocks = [
        (104, 515, 61, 43, MUTED), (218, 515, 61, 43, PURPLE), (330, 515, 61, 43, MUTED),
        (442, 515, 61, 43, GREEN), (554, 515, 61, 43, MUTED),
        (104, 603, 61, 43, PURPLE), (218, 603, 61, 43, MUTED), (330, 603, 61, 43, MUTED),
        (442, 691, 61, 43, GREEN), (554, 691, 61, 43, MUTED),
    ]
    for bx, by, bw, bh, color in blocks:
        events.append(rect(8, start + .18, end - .03, bx, by, bw, bh, color, fade=60))

    # 2) A visual transformation from clock-time to what matters.
    start, end = 14.68, 16.20
    events.append(rect(4, start, end, 0, 0, W, H, DARK, fade=65))
    events.append(text(6, start + .04, end - .02, 68, 247, "TIME", WHITE, 116, fade=60,
                       move=(-560, 247, 68, 247, 0, 170)))
    events.append(text(6, start + .12, end - .02, 68, 574, "WHAT MATTERS", GREEN, 76, fade=60,
                       move=(760, 574, 68, 574, 0, 190)))
    # Long violet arrow from first idea to the second.
    arrow = "m 0 28 l 285 28 285 0 352 52 285 104 285 76 0 76"
    events.append(f"Dialogue: 7,{at(start + .1)},{at(end - .02)},Kicker,,0,0,0,,"
                  f"{{\\an7\\pos(72,426)\\p1\\bord0\\shad0\\c{PURPLE}\\fad(60,70)}}{arrow}{{\\p0}}")
    events.append(line(7, start + .18, end - .03, 72, 726, 548, 7, GREEN, fade=70))

    # 3) Two abstract options, one chosen; timed to the word "choose".
    start, end = 22.20, 23.72
    events.append(rect(4, start, end, 0, 0, W, H, PAPER, fade=70))
    events.append(text(6, start + .02, end - .02, 64, 218, "CHOOSE", PURPLE, 102, fade=60,
                       move=(760, 218, 64, 218, 0, 160)))
    events.append(rect(6, start + .08, end - .02, 67, 461, 255, 310, WHITE, fade=75))
    events.append(outline_rect(start=start + .08, end=end - .02, layer=7, x=67, y=461,
                               width=255, height=310, color=MUTED, stroke=4, fade=75))
    events.append(rect(6, start + .13, end - .02, 398, 461, 255, 310, WHITE, fade=70))
    events.append(outline_rect(start=start + .13, end=end - .02, layer=7, x=398, y=461,
                               width=255, height=310, color=PURPLE, stroke=7, fade=65))
    # Abstract bars avoid inventing named priorities; the bright outline marks a deliberate choice.
    for rx, ry, rw, color in [
        (101, 520, 174, MUTED), (101, 580, 137, MUTED), (101, 640, 184, MUTED),
        (432, 520, 174, PURPLE), (432, 580, 137, GREEN), (432, 640, 184, PURPLE),
    ]:
        events.append(rect(8, start + .18, end - .02, rx, ry, rw, 15, color, fade=60))

    # 4) A stack of competing priorities resolves into one winner.
    start, end = 29.05, 30.28
    events.append(rect(4, start, end, 0, 0, W, H, DARK, fade=60))
    events.append(text(6, start + .03, end - .02, 52, 236, "ONE THING WINS", WHITE, 83, fade=60,
                       move=(760, 236, 52, 236, 0, 150)))
    events.append(line(7, start + .16, end - .02, 54, 358, 155, 8, PURPLE, fade=60))
    # Layered bars rise into the frame; the selected priority lands highest and green.
    events.append(rect(7, start + .08, end - .02, 118, 486, 482, 91, PURPLE, fade=55))
    events.append(rect(7, start + .12, end - .02, 144, 616, 430, 91, MUTED, fade=65))
    events.append(rect(7, start + .16, end - .02, 170, 746, 378, 91, MUTED, fade=75))
    events.append(rect(8, start + .26, end - .02, 118, 486, 482, 91, GREEN, fade=50))
    events.append(text(9, start + .32, end - .02, 145, 497, "01", DARK, 50, fade=45))

    return events


def main() -> int:
    ffmpeg = ffmpeg_path()
    if not BASE.is_file():
        raise SystemExit(f"Base edit missing: {BASE}")
    removed = json.loads(TIMELINE.read_text(encoding="utf-8"))["removed_source_intervals_seconds"]
    base_ass, cues = build_ass(removed)
    # Match the references' purple/green accents while retaining the original composition.
    base_ass = base_ass.replace("&H0066D1FF&", PURPLE)
    base_ass = base_ass.replace("Video brut 1L — English kinetic captions", "Video brut 1L — English motion edit v2")
    ass = base_ass.rstrip() + "\n" + "\n".join(card_events()) + "\n"

    ASS_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ASS_PATH.write_text(ass, encoding="utf-8")
    srt_entries: list[str] = []
    for cue in cues:
        srt_entries.extend([
            str(cue["cue"]),
            f"{srt_time(float(cue['output_start_seconds']))} --> {srt_time(float(cue['output_end_seconds']))}",
            str(cue["text"]),
            "",
        ])
    SRT_PATH.write_text("\n".join(srt_entries), encoding="utf-8")
    CAPTION_JSON.write_text(json.dumps({
        "language": "en",
        "translated": False,
        "method": "offline PocketSphinx first pass; punctuation and obvious context slips normalized",
        "review_note": "First-pass local ASR, not certified. Review source 3–6 s, 18.7–21.3 s, and the phrase X amount of time before public/paid use.",
        "visual_cutaways": [
            {"output_start_seconds": 8.12, "output_end_seconds": 9.48, "graphic": "calendar grid"},
            {"output_start_seconds": 14.68, "output_end_seconds": 16.20, "graphic": "time to what matters"},
            {"output_start_seconds": 22.20, "output_end_seconds": 23.72, "graphic": "abstract choice cards"},
            {"output_start_seconds": 29.05, "output_end_seconds": 30.28, "graphic": "priority stack resolves to one"},
        ],
        "cues": cues,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subtitle_arg = f"subtitles='{ASS_PATH.as_posix()}':fontsdir='{FONTS.as_posix()}'"
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-i", str(BASE),
        "-vf", subtitle_arg,
        "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "-1",
        "-metadata", "title=Video brut 1L — full-screen social motion edit (English)",
        "-metadata", "comment=Original voice; English captions; graphic cutaways; no added narration or music",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", str(OUTPUT),
    ]
    subprocess.run(command, check=True)
    print(f"Rendered {OUTPUT}")
    print(f"English captions and graphic cutaways: {ASS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
