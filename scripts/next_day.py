"""Print the next unpublished curriculum day as JSON, or {"done": true} when the course is finished.

A day counts as published once lessons/day-NN-<slug>/lesson.mp4 exists.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def folder_for(day: dict) -> str:
    return f"day-{day['day']:02d}-{day['slug']}"


def main() -> None:
    days = json.loads((ROOT / "curriculum.json").read_text())["days"]
    for day in days:
        folder = folder_for(day)
        if not (ROOT / "lessons" / folder / "lesson.mp4").exists():
            previous = folder_for(days[day["day"] - 2]) if day["day"] > 1 else None
            print(json.dumps({**day, "folder": f"lessons/{folder}", "previous_folder": previous and f"lessons/{previous}"}, indent=2))
            return
    print(json.dumps({"done": True}))


if __name__ == "__main__":
    main()
