#!/usr/bin/env python3
import argparse
import collections
import datetime as dt
import subprocess
import sys
from typing import Dict, List

YELLOW = "\x1b[38;5;220m"   # bright yellow
RESET = "\x1b[0m"


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


def print_heatmap(start_date: dt.date, end_date: dt.date, counts: Dict[dt.date, int]) -> None:
    all_days = build_date_range(start_date, end_date)

    # Align start to Monday so columns are full weeks
    offset = start_date.weekday()  # Monday = 0
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

    labels = ["M", "T", "W", "T", "F", "S", "S"]

    print(
        f"Git commit map from {start_date.isoformat()} to {end_date.isoformat()}\n")

    # Highlight current day label (yellow)
    today_wd = dt.date.today().weekday()  # Monday = 0 … Sunday = 6

    for weekday in range(7):
        label = labels[weekday]

        # Colour the label if it's the current day
        if weekday == today_wd:
            label = f"{YELLOW}{label}{RESET}"

        # Build cells
        line_cells = []
        for week in range(num_weeks):
            line_cells.append(COLORS[grid[weekday][week]])

        print(f"{label} " + "".join(line_cells))

    print("")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show a compact git-cal-style commit map for the current repo."
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=52,
        help="Number of weeks to show (default: 52). Reduce if your terminal is narrow.",
    )
    args = parser.parse_args()

    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(weeks=args.weeks)

    counts = run_git_log(start_date, end_date)
    print_heatmap(start_date, end_date, counts)


if __name__ == "__main__":
    main()
