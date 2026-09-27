"""Render one lesson folder: the video, every Fig* still, and a poster frame.

Usage: python scripts/render_lesson.py lessons/day-01-vectors [--draft]
A scene class named Poster, if present, becomes poster.jpg; otherwise a video frame is used.
Outputs inside the lesson folder: lesson.mp4, poster.jpg, figures/<name>.png, meta.json (duration filled in).
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scene_names(scene_file: Path) -> list[str]:
    tree = ast.parse(scene_file.read_text())
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def render_still(lesson: Path, name: str) -> Path:
    manim(lesson, "-qh", "-s", "scene.py", name)
    return next((lesson / ".media" / "images" / "scene").glob(f"{name}_*.png"))


def manim(lesson: Path, *args: str) -> None:
    command = [sys.executable, "-m", "manim", "--config_file", str(ROOT / "manim.cfg"), *args]
    subprocess.run(command, cwd=lesson, check=True)


def render_video(lesson: Path, draft: bool) -> Path:
    quality = "-ql" if draft else "-qh"
    manim(lesson, quality, "--frame_rate", "30", "--disable_caching", "scene.py", "Lesson")
    folder = "480p30" if draft else "1080p30"
    rendered = lesson / ".media" / "videos" / "scene" / folder / "Lesson.mp4"
    target = lesson / "lesson.mp4"
    encode_with_bed(rendered, target)
    return target


def has_audio(video: Path) -> bool:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(video)],
        check=True, capture_output=True, text=True,
    )
    return bool(probe.stdout.strip())


def encode_with_bed(rendered: Path, target: Path) -> None:
    """Lay the ambient bed under the scene's effects, fade it at both ends, and level the mix."""
    duration = video_duration(rendered)
    bed = ROOT / "engine" / "sounds" / "ambient.mp3"
    pad = f"[1:a]atrim=0:{duration},afade=t=in:d=2.5,afade=t=out:st={max(0, duration - 3.5)}:d=3.5,volume=0.07[bed]"
    if has_audio(rendered):
        mix = f"{pad};[0:a]apad=whole_dur={duration},volume=1.8[fx];[fx][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[mix]"
    else:
        mix = f"{pad};[bed]anull[mix]"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(rendered), "-i", str(bed), "-filter_complex", mix,
         "-map", "0:v", "-map", "[mix]", "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", str(target)],
        check=True,
    )


def render_figures(lesson: Path) -> list[str]:
    names = [name for name in scene_names(lesson / "scene.py") if name.startswith("Fig")]
    figures = lesson / "figures"
    figures.mkdir(exist_ok=True)
    for name in names:
        still = render_still(lesson, name)
        slug = re.sub(r"(?<!^)(?=[A-Z])", "-", name.removeprefix("Fig")).lower()
        shutil.copy(still, figures / f"{slug}.png")
    return names


def video_duration(video: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        check=True, capture_output=True, text=True,
    )
    return round(float(probe.stdout.strip()), 1)


def write_poster(lesson: Path, video: Path, seconds: float) -> None:
    """Prefer a clean Poster scene; fall back to a frame of the video."""
    if "Poster" in scene_names(lesson / "scene.py"):
        still = render_still(lesson, "Poster")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(still), "-q:v", "3", str(lesson / "poster.jpg")], check=True)
        return
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-ss", str(seconds), "-i", str(video), "-frames:v", "1",
         "-q:v", "3", str(video.with_name("poster.jpg"))],
        check=True,
    )


def main() -> None:
    lesson = (ROOT / sys.argv[1]).resolve()
    draft = "--draft" in sys.argv
    meta_path = lesson / "meta.json"
    meta = json.loads(meta_path.read_text())
    video = render_video(lesson, draft)
    render_figures(lesson)
    meta["duration_seconds"] = video_duration(video)
    write_poster(lesson, video, meta.get("poster_seconds", meta["duration_seconds"] * 0.7))
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Rendered {lesson.name}: {meta['duration_seconds']}s, {video.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
