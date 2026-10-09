#!/usr/bin/env python3
"""Create a synchronized before/after showcase inspired by the two Our Work refs.

The left window shows the cut base without captions; the larger right window
shows the English-captioned motion edit. The template uses original project
branding and does not copy the reference studio logo or handle.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "edit" / "video-brut-1l-cut-base.mp4"
EDIT = ROOT / "renders" / "video-brut-1l-pinterest-en.mp4"
OUTPUT = ROOT / "renders" / "video-brut-1l-our-work-en.mp4"
ASSETS = ROOT / "assets"
MAIN_MASK = ASSETS / "our-work-main-mask.png"
SOURCE_MASK = ASSETS / "our-work-source-mask.png"
LAYOUT = ASSETS / "our-work-layout.png"
DURATION = 35.75
W, H, FPS = 720, 1280, 24
MAIN = (228, 224, 468, 832)
SOURCE = (18, 650, 180, 320)


def ffmpeg_path() -> str:
    candidate = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not candidate or not Path(candidate).is_file():
        raise SystemExit("Set FFMPEG or put ffmpeg on PATH")
    return candidate


def main() -> int:
    for path in (BASE, EDIT, MAIN_MASK, SOURCE_MASK, LAYOUT):
        if not path.is_file():
            raise SystemExit(f"Required input missing: {path}")
    ffmpeg = ffmpeg_path()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    mx, my, mw, mh = MAIN
    sx, sy, sw, sh = SOURCE
    graph = (
        f"[0:v]scale={sw}:{sh}:flags=lanczos,"
        "eq=saturation=0.82:brightness=-0.015,setsar=1,format=rgba[source_rgb];"
        "[3:v]format=gray[source_mask];"
        "[source_rgb][source_mask]alphamerge[source];"
        f"[1:v]scale={mw}:{mh}:flags=lanczos,setsar=1,format=rgba,"
        "fps=24[edit_rgb];"
        "[2:v]format=gray[edit_mask];"
        "[edit_rgb][edit_mask]alphamerge[edit];"
        f"color=c=0xF7F6F1:s={W}x{H}:r={FPS}:d={DURATION},format=rgba[paper];"
        f"[paper][source]overlay=x={sx}:y={sy}:eof_action=pass:format=auto[with_source];"
        f"[with_source][edit]overlay=x={mx}:y={my}:eof_action=pass:format=auto[with_edit];"
        "[4:v]format=rgba[frame];"
        "[with_edit][frame]overlay=x=0:y=0:eof_action=repeat:format=auto[showcase]"
    )
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "warning", "-y",
        "-i", str(BASE), "-i", str(EDIT),
        "-loop", "1", "-framerate", str(FPS), "-i", str(MAIN_MASK),
        "-loop", "1", "-framerate", str(FPS), "-i", str(SOURCE_MASK),
        "-loop", "1", "-framerate", str(FPS), "-i", str(LAYOUT),
        "-filter_complex", graph,
        "-map", "[showcase]", "-map", "1:a:0", "-map_metadata", "-1",
        "-metadata", "title=Our Work — Priorities / English social edit",
        "-metadata", "comment=Synchronised source cut and motion edit; English captions; original voice",
        "-t", str(DURATION), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(OUTPUT),
    ]
    subprocess.run(command, check=True)
    print(f"Rendered {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
