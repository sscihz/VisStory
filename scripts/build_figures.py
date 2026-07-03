#!/usr/bin/env python
"""Build all textbook figures."""

from __future__ import annotations

from pathlib import Path

from nba_textbook.charts import build_all_figures
from nba_textbook.data import prepare_player_dataset, prepare_team_dataset


def main() -> None:
    output_dir = Path("docs/assets/figures")
    players = prepare_player_dataset(min_minutes=300)
    teams = prepare_team_dataset()
    paths = build_all_figures(players, teams, output_dir)
    for path in paths:
        print(f"generated: {path}")


if __name__ == "__main__":
    main()
