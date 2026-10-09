#!/usr/bin/env python3
"""Burn English ASR captions and a restrained editorial motion-graphics layer.

Captions are kept in the spoken language (English) and are not translated. They
are based on a local PocketSphinx first pass, with obvious grammar/context
normalization for readability. The first ~6 seconds contain a low-confidence
phrase and should be checked by a human before paid/public ad use.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "edit" / "video-brut-1l-cut-base.mp4"
OUTPUT = ROOT / "renders" / "video-brut-1l-pinterest-en.mp4"
ASS_PATH = ROOT / "subtitles" / "video-brut-1l-en.ass"
SRT_PATH = ROOT / "subtitles" / "video-brut-1l-en.srt"
CAPTION_JSON = ROOT / "subtitles" / "captions-en.json"
TIMELINE = ROOT / "edit" / "timeline.json"
FONTS = ROOT / "assets" / "fonts"
DURATION = 35.75
W, H = 720, 1280

# Source-time captions. Wording stays English; only punctuation and obvious
# ASR slips are normalized. The ASR draft is kept separately in this project.
CAPTIONS = [
    (0.05, 4.30, "Time doesn't need to be managed.\\NYour {gold}priorities{white} need to be managed."),
    (4.54, 8.05, "We have the {gold}cookie-cutter{white}\\Ninformation"),
    (8.36, 10.24, "about how to manage your {gold}calendars{white}"),
    (10.59, 13.36, "and how to spend {gold}X amount of time{white}\\Non certain things."),
    (13.37, 18.52, "Now we're moving from managing time\\Nto managing what's {gold}important{white}."),
    (18.68, 21.32, "And I wanna say something\\Nthat a lot of people won't say:"),
    (21.58, 26.40, "But at some point, you're gonna have to\\N{gold}choose{white} what your priorities are."),
    (26.62, 29.61, "I know we like to say we have\\Ncompeting {gold}priorities{white}."),
    (29.82, 31.85, "At some point,\\N{gold}something has to win{white}."),
    (32.09, 34.59, "You have to choose one thing\\Nover the other."),
    (34.81, 36.98, "If you wanna actually be {gold}effective{white}."),
]

CUTS = []  # populated from the reproducible edit timeline


def ffmpeg_path() -> str:
    candidate = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not candidate or not Path(candidate).is_file():
        raise SystemExit("Set FFMPEG or put ffmpeg on PATH")
    return candidate


def to_output_time(source_time: float, removed: list[list[float]]) -> float:
    elapsed = 0.0
    for start, end in removed:
        if source_time >= end:
            elapsed += end - start
        elif start < source_time < end:
            return max(0.0, start - elapsed)
    return max(0.0, source_time - elapsed)


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    hours, rest = divmod(centiseconds, 360000)
    minutes, rest = divmod(rest, 6000)
    whole_seconds, cs = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{cs:02d}"


def srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, rest = divmod(milliseconds, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    whole_seconds, ms = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{ms:03d}"


def caption_ass(text: str) -> str:
    return text.replace("{gold}", r"{\c&H0066D1FF&}").replace("{white}", r"{\c&H00F8F5F2&}")


def build_ass(removed: list[list[float]]) -> tuple[str, list[dict[str, object]]]:
    out: list[str] = [
        "[Script Info]",
        "Title: Video brut 1L — English kinetic captions",
        "ScriptType: v4.00+",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        f"PlayResX: {W}",
        f"PlayResY: {H}",
        "\n[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Caption,Instrument Sans,42,&H00F8F5F2,&H0066D1FF,&HCC090A12,&H80090A12,-1,0,0,0,100,100,0,0,1,3,1,2,52,52,78,1",
        "Style: Title,Instrument Sans,48,&H00F8F5F2,&H0066D1FF,&HAA090A12,&H00090A12,-1,0,0,0,100,100,0,0,1,1.5,0,7,48,48,40,1",
        "Style: Chapter,Geist Mono,17,&H00D8D1FF,&H0066D1FF,&H99090A12,&H00090A12,0,0,0,0,100,100,0,0,1,1,0,9,48,48,48,1",
        "Style: Kicker,Geist Mono,16,&H0066D1FF,&H00FFFFFF,&H99090A12,&H00090A12,0,0,0,0,100,100,0,0,1,1,0,7,48,48,48,1",
        "\n[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    rows: list[dict[str, object]] = []

    # Editorial chapter label + changing progress bar; deliberately minimal so
    # the speaker remains the hero of the frame.
    chapters = [
        (0.00, 13.00, "01 / THE SHIFT", 208),
        (13.00, 25.50, "02 / WHAT MATTERS", 416),
        (25.50, DURATION, "03 / THE CHOICE", 624),
    ]
    for start, end, label, width in chapters:
        out.append(
            f"Dialogue: 2,{ass_time(start)},{ass_time(end)},Chapter,,0,0,0,,"
            f"{{\\an9\\pos(672,50)\\fad(120,100)}}{label}"
        )
        out.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Kicker,,0,0,0,,"
            f"{{\\an7\\pos(48,42)\\p1\\bord0\\shad0\\c&H805C5260&}}m 0 0 l 624 0 624 4 0 4{{\\p0}}"
        )
        out.append(
            f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Kicker,,0,0,0,,"
            f"{{\\an7\\pos(48,42)\\p1\\bord0\\shad0\\c&H0066D1FF&\\fad(100,100)}}m 0 0 l {width} 0 {width} 4 0 4{{\\p0}}"
        )

    # Short kinetic headline and two editorial callouts. All on-screen copy is English.
    graphic_events = [
        (0.16, 2.76, "Kicker", r"{\an7\pos(50,69)\fad(100,120)}A QUICK RESET"),
        (0.16, 2.76, "Title", r"{\an7\pos(48,98)\fad(120,180)\fscx94\fscy94\t(0,180,\fscx100\fscy100)}TIME ≠ {\c&H0066D1FF&}PRIORITIES"),
        (13.10, 18.25, "Title", r"{\an7\pos(50,93)\fad(130,180)\fscx95\fscy95\t(0,160,\fscx100\fscy100)}MANAGE WHAT {\c&H0066D1FF&}MATTERS"),
        (21.95, 25.35, "Title", r"{\an7\pos(50,93)\fad(120,160)\fscx95\fscy95\t(0,160,\fscx100\fscy100)}MAKE THE {\c&H0066D1FF&}CHOICE"),
        (28.70, 31.55, "Title", r"{\an7\pos(50,93)\fad(120,160)\fscx95\fscy95\t(0,160,\fscx100\fscy100)}ONE THING {\c&H0066D1FF&}WINS"),
    ]
    for start, end, style, text in graphic_events:
        out.append(f"Dialogue: 3,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}")

    # A small warm accent stroke slides in under each title/callout.
    for start, end in [(0.16, 2.76), (13.10, 18.25), (21.95, 25.35), (28.70, 31.55)]:
        out.append(
            f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Kicker,,0,0,0,,"
            f"{{\\an7\\pos(50,157)\\p1\\bord0\\shad0\\fad(100,150)\\c&H0066D1FF&}}m 0 0 l 118 0 118 3 0 3{{\\p0}}"
        )

    for index, (source_start, source_end, raw_text) in enumerate(CAPTIONS, 1):
        start = to_output_time(source_start, removed)
        end = to_output_time(source_end, removed)
        # Small scale-up + fade makes each lower-third caption feel kinetic,
        # while preserving a generous reading window.
        text = r"{\an2\pos(360,1167)\fad(100,130)\fscx97\fscy97\t(0,135,\fscx100\fscy100)}" + caption_ass(raw_text)
        out.append(f"Dialogue: 5,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{text}")
        rows.append({
            "cue": index,
            "source_start_seconds": source_start,
            "source_end_seconds": source_end,
            "output_start_seconds": round(start, 3),
            "output_end_seconds": round(end, 3),
            "text": raw_text.replace("\\N", "\n").replace("{gold}", "").replace("{white}", ""),
            "language": "English",
            "translation": False,
        })

    return "\n".join(out) + "\n", rows


def main() -> int:
    ffmpeg = ffmpeg_path()
    if not BASE.is_file():
        raise SystemExit(f"Base edit missing: {BASE}")
    if not TIMELINE.is_file():
        raise SystemExit(f"Edit timeline missing: {TIMELINE}")
    removed = json.loads(TIMELINE.read_text(encoding="utf-8"))["removed_source_intervals_seconds"]
    ASS_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ass, cues = build_ass(removed)
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
        "review_note": "The opening 3–6 seconds contain low-confidence ASR wording; confirm before public/paid use.",
        "cues": cues,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subtitle_arg = f"subtitles='{ASS_PATH.as_posix()}':fontsdir='{FONTS.as_posix()}'"
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-i", str(BASE),
        "-vf", subtitle_arg,
        "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "-1",
        "-metadata", "title=Video brut 1L — Pinterest edit (English captions)",
        "-metadata", "comment=English captions burned in; original audio retained",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", str(OUTPUT),
    ]
    subprocess.run(command, check=True)
    print(f"Rendered {OUTPUT}")
    print(f"Captions: {ASS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
