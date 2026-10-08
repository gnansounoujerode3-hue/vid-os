#!/usr/bin/env python3
"""Build a brisk, source-faithful vertical talking-head edit.

The only content-based edit is amplitude-only silence trimming at the measured
source intervals below. No speech recognition, transcript, captions, new voice,
or replacement soundtrack is used. FFmpeg and FFprobe must be on PATH.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "video-brut-1l-original.mp4"
OUTPUT = ROOT / "renders" / "video-brut-1l-dynamique.mp4"
TIMELINE = ROOT / "edit" / "timeline.json"
FILTERGRAPH = ROOT / "edit" / "ffmpeg-filtergraph.txt"

WIDTH, HEIGHT, FPS = 720, 1280, 24
SOURCE_END = 37.125  # video stream duration; 891 frames at 24 fps
KEEP_SILENCE = 0.12  # retain a short natural breath/room-tone gap around each splice

# Start/end times from FFmpeg silencedetect (noise=-34 dB, duration=0.24 s).
# This is signal-level timing only; dialogue is neither interpreted nor transcribed.
SILENCES = [
    (2.778186, 3.050113),
    (7.996077, 8.399955),
    (13.623401, 14.075374),
    (21.340045, 21.625011),
    (22.565374, 22.943197),
    (26.391542, 26.633469),
    (29.592562, 29.882018),
    (31.838730, 32.125238),
    (34.582041, 34.833175),
]

# Alternating, restrained punch-ins create a second-camera rhythm from the
# continuous source shot. Values are intentionally conservative to retain the
# microphone, ring light, and expressive hand gestures.
ZOOMS = [1.00, 1.055, 1.10, 1.045, 1.12, 1.07, 1.105, 1.05, 1.095, 1.025]
X_BIAS = [0, -4, 3, -2, 4, -3, 2, -4, 3, 0]
Y_BIAS = [0, 1, -2, 2, 1, -1, 2, -1, 1, 0]


def ffmpeg_binary(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        raise SystemExit(f"{name} is required and must be available on PATH")
    return binary


def ceil_frame(seconds: float) -> float:
    return math.ceil(seconds * FPS - 1e-9) / FPS


def floor_frame(seconds: float) -> float:
    return math.floor(seconds * FPS + 1e-9) / FPS


def make_segments() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    removed: list[tuple[float, float]] = []
    for start, end in SILENCES:
        half_gap = min(KEEP_SILENCE / 2, (end - start) / 2)
        cut_start = ceil_frame(start + half_gap)
        cut_end = floor_frame(end - half_gap)
        if cut_end > cut_start:
            removed.append((cut_start, cut_end))

    segments: list[tuple[float, float]] = []
    cursor = 0.0
    for start, end in removed:
        if start > cursor:
            segments.append((cursor, start))
        cursor = end
    if SOURCE_END > cursor:
        segments.append((cursor, SOURCE_END))
    return removed, segments


def crop_for(index: int) -> dict[str, float | int]:
    zoom = ZOOMS[index % len(ZOOMS)]
    crop_w = max(2, int((WIDTH / zoom) // 2) * 2)
    crop_h = max(2, int((HEIGHT / zoom) // 2) * 2)
    x = round((WIDTH - crop_w) / 2 + X_BIAS[index % len(X_BIAS)])
    y = round((HEIGHT - crop_h) * 0.30 + Y_BIAS[index % len(Y_BIAS)])
    x = max(0, min(WIDTH - crop_w, x))
    y = max(0, min(HEIGHT - crop_h, y))
    return {"zoom": zoom, "crop_width": crop_w, "crop_height": crop_h, "crop_x": x, "crop_y": y}


def build_graph(segments: list[tuple[float, float]]) -> tuple[str, list[dict[str, object]]]:
    chains: list[str] = []
    video_labels: list[str] = []
    audio_labels: list[str] = []
    timeline: list[dict[str, object]] = []
    output_cursor = 0.0

    for i, (start, end) in enumerate(segments):
        crop = crop_for(i)
        duration = end - start
        v_label, a_label = f"v{i}", f"a{i}"
        chains.append(
            f"[0:v]trim=start={start:.9f}:end={end:.9f},setpts=PTS-STARTPTS,"
            f"crop={crop['crop_width']}:{crop['crop_height']}:{crop['crop_x']}:{crop['crop_y']},"
            f"scale={WIDTH}:{HEIGHT}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p[{v_label}]"
        )
        chains.append(
            f"[0:a]atrim=start={start:.9f}:end={end:.9f},asetpts=PTS-STARTPTS,"
            f"aresample=44100,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[{a_label}]"
        )
        video_labels.append(f"[{v_label}]")
        audio_labels.append(f"[{a_label}]")
        timeline.append({
            "segment": i + 1,
            "source_start_seconds": round(start, 6),
            "source_end_seconds": round(end, 6),
            "output_start_seconds": round(output_cursor, 6),
            "output_end_seconds": round(output_cursor + duration, 6),
            "duration_seconds": round(duration, 6),
            **crop,
        })
        output_cursor += duration

    chains.append(f"{''.join(video_labels)}concat=n={len(segments)}:v=1:a=0[vcut]")
    chains.append(f"{''.join(audio_labels)}concat=n={len(segments)}:v=0:a=1[acut]")
    chains.append(
        "[vcut]eq=contrast=1.035:saturation=1.045,"
        "unsharp=5:5:0.10:5:5:0.0,format=yuv420p[vout]"
    )
    chains.append("[acut]anull[aout]")
    return ";\n".join(chains), timeline


def main() -> int:
    ffmpeg = ffmpeg_binary("ffmpeg")
    ffprobe = ffmpeg_binary("ffprobe")
    if not SOURCE.is_file():
        raise SystemExit(f"Source video is missing: {SOURCE}")

    removed, segments = make_segments()
    if len(segments) != len(ZOOMS):
        raise SystemExit(f"Expected {len(ZOOMS)} visual beats, got {len(segments)}")
    graph, timeline = build_graph(segments)
    duration = sum(end - start for start, end in segments)

    ROOT.joinpath("edit").mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    FILTERGRAPH.write_text(graph + "\n", encoding="utf-8")
    timeline_data = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_duration_seconds": SOURCE_END,
        "fps": FPS,
        "resolution": [WIDTH, HEIGHT],
        "silence_detection": {"filter": "silencedetect", "noise_db": -34, "minimum_duration_seconds": 0.24},
        "retained_gap_seconds": KEEP_SILENCE,
        "removed_source_intervals_seconds": [[round(a, 6), round(b, 6)] for a, b in removed],
        "output_duration_seconds": round(duration, 6),
        "segments": timeline,
        "sound": "Original source audio only; no music, speech recognition, transcript, or subtitles.",
    }
    TIMELINE.write_text(json.dumps(timeline_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    command = [
        ffmpeg, "-hide_banner", "-y", "-i", str(SOURCE),
        "-filter_complex", graph,
        "-map", "[vout]", "-map", "[aout]",
        "-map_metadata", "-1",
        "-metadata", "title=Vidéo brute 1L — montage dynamique",
        "-metadata", "comment=Image dynamisée; son d’origine conservé; sans sous-titres",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-t", f"{duration:.6f}", "-movflags", "+faststart", str(OUTPUT),
    ]
    subprocess.run(command, check=True)

    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(OUTPUT)],
        check=True, text=True, capture_output=True,
    )
    (ROOT / "renders" / "probe.json").write_text(
        json.dumps(json.loads(probe.stdout), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Rendered {OUTPUT} ({duration:.3f}s, {len(segments)} beats)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
