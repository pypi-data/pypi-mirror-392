#!/usr/bin/env python3
import argparse
import calendar
import collections
import datetime as dt
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

YELLOW = "\x1b[38;5;220m"   # bright yellow
RESET = "\x1b[0m"

USAGE_YEAR = "Usage: git-year --year [YEAR]"
USAGE_WEEK_START = "Usage: git-year --week-start [Sunday|Monday]"

DEFAULT_WEEK_START = "monday"  # keep it all lowercase
MONDAY_ALIASES = {"m", "mo", "mon", "monday"}
SUNDAY_ALIASES = {"s", "su", "sun", "sunday"}


def run_git_log(start_date: dt.date, end_date: dt.date) -> Dict[dt.date, int]:
    """Return a dict mapping date -> commit count between start_date and end_date."""

    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(
            f"{YELLOW}git-year: This directory is not a git repository.{RESET}\n"
            "Try: cd into a project folder that uses git."
        )
        sys.exit(1)

    since = start_date.isoformat()
    until = end_date.isoformat()
    result = subprocess.run(
        ["git", "log", f"--since={since}", f"--until={until}",
         "--date=short", "--pretty=%ad"],
        check=True,
        capture_output=True,
        text=True,
    )

    counter: Dict[dt.date, int] = collections.Counter()
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        y, m, d = map(int, line.split("-"))
        counter[dt.date(y, m, d)] += 1
    return counter


def build_date_range(start: dt.date, end: dt.date) -> List[dt.date]:
    days: List[dt.date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += dt.timedelta(days=1)
    return days


def choose_level(count: int, thresholds=(0, 1, 3, 6, 10)) -> int:
    """
    Map commit count to intensity level 0–4.
    """
    if count == 0:
        return 0
    if count < thresholds[2]:
        return 1
    if count < thresholds[3]:
        return 2
    if count < thresholds[4]:
        return 3
    return 4


def print_heatmap(start_date: dt.date, end_date: dt.date, counts: Dict[dt.date, int],
                  week_start: str) -> None:
    all_days = build_date_range(start_date, end_date)

    # Align start to requested week start so columns are full weeks
    if week_start == "monday":
        offset = start_date.weekday()  # Monday = 0
    else:  # sunday
        offset = (start_date.weekday() + 1) % 7
    grid_start = start_date - dt.timedelta(days=offset)

    total_days = (end_date - grid_start).days + 1
    num_weeks = (total_days + 6) // 7  # ceil division

    # grid[weekday][week]
    grid: List[List[int]] = [[0 for _ in range(num_weeks)] for _ in range(7)]
    for day in all_days:
        idx = (day - grid_start).days
        week = idx // 7
        weekday = day.weekday()  # 0–6
        count = counts.get(day, 0)
        grid[weekday][week] = choose_level(count)

    # --- Appearance (git-cal-ish palette) ---
    block = "|"
    CELL_0 = f"\x1b[38;5;234m{block}\x1b[0m"   # dark grey (no commits)
    CELL_1 = f"\x1b[38;5;22m{block}\x1b[0m"    # darker green (light activity)
    CELL_2 = f"\x1b[38;5;28m{block}\x1b[0m"    # dark green
    CELL_3 = f"\x1b[38;5;34m{block}\x1b[0m"    # medium green
    CELL_4 = f"\x1b[38;5;40m{block}\x1b[0m"    # bright green (high activity)

    COLORS = [CELL_0, CELL_1, CELL_2, CELL_3, CELL_4]

    base_labels = ["M", "T", "W", "T", "F", "S", "S"]
    if week_start == "sunday":
        order = [6, 0, 1, 2, 3, 4, 5]
        labels = ["S", "M", "T", "W", "T", "F", "S"]
    else:
        order = list(range(7))
        labels = base_labels

    print(
        f"Git commit map from {start_date.isoformat()} to {end_date.isoformat()}\n")

    # Highlight current day label (yellow)
    today_wd = dt.date.today().weekday()  # Monday = 0 … Sunday = 6

    for idx, weekday in enumerate(order):
        label = labels[idx]

        # Colour the label if it's the current day
        if weekday == today_wd:
            label = f"{YELLOW}{label}{RESET}"

        # Build cells
        line_cells = []
        for week in range(num_weeks):
            line_cells.append(COLORS[grid[weekday][week]])

        print(f"{label} " + "".join(line_cells))

    print("")


def config_file_path() -> Path:
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA")
        if base:
            base_path = Path(base)
        else:
            base_path = Path.home() / "AppData" / "Roaming"
    else:
        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            base_path = Path(xdg)
        else:
            base_path = Path.home() / ".config"
    return base_path / "git-year" / "config.toml"


def load_week_start_preference() -> Optional[str]:
    path = config_file_path()
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("week_start"):
            _, _, value = stripped.partition("=")
            value = value.strip().strip('"').strip("'").lower()
            if value in ("monday", "sunday"):
                return value
    return None


def save_week_start_preference(value: str) -> None:
    path = config_file_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'week_start = "{value}"\n', encoding="utf-8")
    except OSError:
        pass


def normalize_week_start(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in MONDAY_ALIASES:
        return "monday"
    if normalized in SUNDAY_ALIASES:
        return "sunday"
    print(USAGE_WEEK_START)
    sys.exit(2)


def one_year_ago(date: dt.date) -> dt.date:
    """Return the same month/day in the previous year (clamped for leap years)."""
    target_year = date.year - 1
    last_day = calendar.monthrange(target_year, date.month)[1]
    day = min(date.day, last_day)
    return dt.date(target_year, date.month, day)


class FriendlyArgumentParser(argparse.ArgumentParser):
    """Custom parser that prints concise usage hints on errors."""

    def error(self, message):  # type: ignore[override]
        print(USAGE_YEAR)
        print(USAGE_WEEK_START)
        sys.exit(2)


def main() -> None:
    parser = FriendlyArgumentParser(
        description="Display a year of commits in a compact GitHub-style heatmap in your terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              git-year
              git-year --year 2022
              git-year --week-start Monday
            """
        ),
    )
    parser.add_argument(
        "--year",
        type=str,
        help="Show activity for the specified calendar year (e.g. --year 2024).",
    )
    parser.add_argument(
        "--week-start",
        type=str,
        help="Set the first day of the week (Sunday or Monday).",
    )
    args = parser.parse_args()

    end_date = dt.date.today()
    if args.year is not None:
        try:
            year = int(args.year)
        except ValueError:
            print("Please enter a valid year :)")
            return
        if year <= 0:
            print("Please enter a valid year :)")
            return
        if year > end_date.year:
            print("Trying to look into the future? ;)")
            return
        start_date = dt.date(year, 1, 1)
        if year == end_date.year:
            # show year-to-date when requesting the current year
            end_date = dt.date.today()
        else:
            end_date = dt.date(year, 12, 31)
    else:
        start_date = one_year_ago(end_date)

    saved_week_start = load_week_start_preference() or DEFAULT_WEEK_START
    if args.week_start is not None:
        week_start = normalize_week_start(args.week_start)
        save_week_start_preference(week_start)
    else:
        week_start = saved_week_start

    counts = run_git_log(start_date, end_date)
    print_heatmap(start_date, end_date, counts, week_start)


if __name__ == "__main__":
    main()
