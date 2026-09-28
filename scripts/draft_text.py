"""Open a Messages draft of today's lesson text, addressed to the learner. It never sends anything.

The recipient and greeting live outside this public repo, in ~/.config/teach-linalg/text.json:
    {"recipient": "+15551234567", "greeting": "Hey!"}

Run with --day N to draft a specific day's text instead of today's.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path.home() / ".config" / "teach-linalg" / "text.json"
COURSE_ZONE = ZoneInfo("America/Los_Angeles")


def lesson_meta() -> list[tuple[Path, dict]]:
    return [(meta.parent, json.loads(meta.read_text())) for meta in sorted(ROOT.glob("lessons/day-*/meta.json"))]


def find_lesson(day: int | None) -> Path | None:
    today = datetime.now(COURSE_ZONE).date().isoformat()
    for folder, meta in lesson_meta():
        if meta["day"] == day or (day is None and meta.get("published_on") == today):
            return folder
    return None


def open_draft(recipient: str, message: str) -> None:
    body = urllib.parse.quote(message)
    subprocess.run(["open", f"sms:{recipient}&body={body}"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int)
    args = parser.parse_args()

    folder = find_lesson(args.day)
    if folder is None:
        print("No lesson unlocks today.")
        return
    text_file = folder / "text.txt"
    if not text_file.exists():
        sys.exit(f"{text_file} is missing.")
    config = json.loads(CONFIG.read_text())
    message = f"{config.get('greeting', '')} {text_file.read_text().strip()}".strip()
    open_draft(config["recipient"], message)
    print(f"Opened a Messages draft for {folder.name}.")


if __name__ == "__main__":
    main()
