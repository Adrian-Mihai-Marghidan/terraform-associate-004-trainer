#!/usr/bin/env python3
"""Create missing private progress records without overwriting any existing file."""
import argparse
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

RECORDS = (
    "PROGRESS.json",
    "REVIEWS.json",
    "SESSION_HISTORY.json",
    "SESSION_HANDOFF.md",
    "KNOWLEDGE_GAPS.md",
)

def _read_progress(path):
    try:
        progress = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as error:
        raise ValueError(f"Progress record is not valid UTF-8: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid progress JSON in {path}: {error.msg}") from error
    if not isinstance(progress, dict):
        raise ValueError(f"Progress record must be a JSON object: {path}")
    return progress


def _validate_timezone(value, source):
    if not isinstance(value, str) or not value:
        raise ValueError(f"Invalid timezone in {source}: expected an IANA timezone name")
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ValueError(f"Invalid IANA timezone {value!r} in {source}") from error
    return value


def bootstrap(root=DEFAULT_ROOT, timezone=None):
    """Create missing records, retaining an existing learner's timezone and files."""
    root = Path(root).resolve()
    templates = root / "templates"
    for name in RECORDS:
        if not (templates / name).is_file():
            raise FileNotFoundError(f"Missing template: {templates / name}")
    destination = root / "private"
    template_progress = _read_progress(templates / "PROGRESS.json")
    template_timezone = _validate_timezone(
        template_progress.get("timezone"), "templates/PROGRESS.json"
    )
    selected_timezone = template_timezone
    requested_timezone = (
        _validate_timezone(timezone, "--timezone") if timezone is not None else None
    )
    existing_progress = destination / "PROGRESS.json"
    if existing_progress.exists():
        progress = _read_progress(existing_progress)
        if "timezone" in progress:
            selected_timezone = _validate_timezone(
                progress["timezone"], "private/PROGRESS.json"
            )
            if requested_timezone is not None and requested_timezone != selected_timezone:
                raise ValueError(
                    f"Existing learner timezone is {selected_timezone!r}; --timezone "
                    f"{requested_timezone!r} would change that preference. Bootstrap only "
                    "creates missing records. Change the learner's timezone separately "
                    "and keep their progress and handoff consistent."
                )
        elif requested_timezone is not None:
            selected_timezone = requested_timezone
    elif requested_timezone is not None:
        selected_timezone = requested_timezone

    # Prepare and validate all new content before creating any private files.
    payloads = {name: (templates / name).read_bytes() for name in RECORDS}
    if selected_timezone != template_timezone:
        template_progress["timezone"] = selected_timezone
        payloads["PROGRESS.json"] = (
            json.dumps(template_progress, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
    handoff = payloads["SESSION_HANDOFF.md"].decode("utf-8")
    timezone_line = f"Timezone: {template_timezone}."
    if handoff.splitlines().count(timezone_line) != 1:
        raise ValueError("Expected one matching timezone line in templates/SESSION_HANDOFF.md")
    payloads["SESSION_HANDOFF.md"] = handoff.replace(
        timezone_line, f"Timezone: {selected_timezone}.", 1
    ).encode("utf-8")

    destination.mkdir(exist_ok=True)
    for name in RECORDS:
        target = destination / name
        try:
            with target.open("xb") as output:
                output.write(payloads[name])
        except FileExistsError:
            print(f"Preserved private/{name}")
        else:
            print(f"Created private/{name}")
    (destination / "assessments").mkdir(exist_ok=True)
    (destination / "evidence").mkdir(exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--timezone", help="IANA timezone for a new learner (default: Europe/Bucharest)"
    )
    arguments = parser.parse_args()
    try:
        bootstrap(arguments.root, arguments.timezone)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))
