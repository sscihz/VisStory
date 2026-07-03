"""Data loading and cleaning helpers for the textbook."""

from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
import requests

from nba_textbook.metrics import add_player_rate_columns

SURENNBA_SEASON = "2025-26"
SURENNBA_PLAYER_STATS_URL = (
    "https://raw.githubusercontent.com/suren-nba/surennba_stats/main/"
    f"data/player_stats/{SURENNBA_SEASON}NBA_RegularSeason_Player_stats.csv"
)
SURENNBA_TEAM_STATS_URL = (
    "https://raw.githubusercontent.com/suren-nba/surennba_stats/main/"
    f"data/team_stats/{SURENNBA_SEASON}NBA_RegularSeason_Team_stats.xlsx"
)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PLAYER_CACHE = RAW_DIR / "surennba_player_stats.csv"
TEAM_CACHE = RAW_DIR / "surennba_team_stats.xlsx"
PROCESSED_PLAYER_CACHE = PROCESSED_DIR / "player_rates.csv"
PROCESSED_TEAM_CACHE = PROCESSED_DIR / "team_rates.csv"

REQUIRED_PLAYER_COLUMNS = {
    "name",
    "teamabbreviation",
    "minutes",
    "gamesplayed",
    "fg2m",
    "fg2a",
    "fg3m",
    "fg3a",
    "fta",
    "points",
    "assists",
    "rebounds",
    "defrebounds",
    "offrebounds",
    "turnovers",
    "fg3pct",
    "efgpct",
    "tspct",
    "usage",
}

REQUIRED_TEAM_COLUMNS = {
    "name",
    "teamabbreviation",
    "gamesplayed",
    "secondsplayed",
    "offposs",
    "fg2m",
    "fg2a",
    "fg3m",
    "fg3a",
    "fta",
    "ftpoints",
    "points",
    "turnovers",
    "offrebounds",
    "efgpct",
    "offfgreboundpct",
}

ROLE_OVERRIDES = {
    "Austin Reaves": "Guard",
    "Stephen Curry": "Guard",
    "Shai Gilgeous-Alexander": "Guard",
    "Luka Doncic": "Guard",
    "Jalen Brunson": "Guard",
    "Donte DiVincenzo": "Guard",
    "Desmond Bane": "Guard",
    "Tyrese Haliburton": "Guard",
    "Kevin Durant": "Forward",
    "LeBron James": "Forward",
    "Jayson Tatum": "Forward",
    "Julius Randle": "Forward",
    "Mikal Bridges": "Forward",
    "Scottie Barnes": "Forward",
    "Toumani Camara": "Forward",
    "Amen Thompson": "Forward",
    "Jabari Smith Jr.": "Forward",
    "Giannis Antetokounmpo": "Forward",
    "Nikola Jokic": "Center",
    "Joel Embiid": "Center",
    "Rudy Gobert": "Center",
    "Anthony Davis": "Center",
    "Victor Wembanyama": "Center",
}


def _fallback_player_stats() -> pd.DataFrame:
    """Small sample that keeps tests and docs buildable without network."""
    records = [
        ["Austin Reaves", "LAL", 2780, 82, 360, 720, 185, 520, 390, 1655, 470, 355, 305, 50, 190, 0.356, 0.560, 0.615, 22.8],
        ["LeBron James", "LAL", 2505, 70, 540, 900, 150, 410, 320, 1850, 610, 550, 455, 95, 245, 0.366, 0.575, 0.620, 29.0],
        ["Luka Doncic", "LAL", 2380, 66, 560, 980, 230, 660, 520, 2330, 650, 570, 490, 80, 275, 0.348, 0.560, 0.610, 34.0],
        ["Stephen Curry", "GSW", 2300, 72, 220, 410, 330, 790, 330, 1890, 460, 330, 275, 55, 210, 0.418, 0.625, 0.660, 30.0],
        ["Shai Gilgeous-Alexander", "OKC", 2500, 75, 690, 1250, 120, 330, 650, 2350, 480, 420, 360, 60, 190, 0.364, 0.560, 0.635, 32.0],
        ["Kevin Durant", "HOU", 2840, 78, 530, 926, 186, 450, 465, 2026, 372, 426, 385, 41, 246, 0.413, 0.588, 0.637, 26.8],
        ["Mikal Bridges", "NYK", 2692, 82, 316, 543, 156, 420, 90, 1181, 304, 312, 233, 79, 83, 0.371, 0.571, 0.589, 17.5],
        ["Julius Randle", "MIN", 2610, 79, 471, 861, 109, 346, 470, 1667, 398, 532, 400, 132, 217, 0.315, 0.526, 0.586, 28.0],
        ["Rudy Gobert", "MIN", 2380, 76, 335, 486, 0, 5, 260, 829, 128, 872, 573, 299, 106, 0.000, 0.682, 0.658, 13.0],
        ["Jabari Smith Jr.", "HOU", 2705, 77, 261, 486, 177, 488, 210, 1215, 143, 529, 421, 108, 105, 0.363, 0.541, 0.569, 18.3],
        ["Desmond Bane", "ORL", 2756, 82, 416, 776, 167, 429, 360, 1647, 338, 338, 240, 98, 164, 0.389, 0.553, 0.603, 23.0],
        ["Amen Thompson", "HOU", 2953, 79, 532, 928, 25, 116, 380, 1443, 420, 614, 379, 235, 190, 0.216, 0.545, 0.595, 20.0],
        ["Toumani Camara", "POR", 2731, 82, 173, 299, 219, 592, 125, 1100, 201, 421, 292, 129, 144, 0.370, 0.563, 0.577, 16.3],
    ]
    columns = [
        "name",
        "teamabbreviation",
        "minutes",
        "gamesplayed",
        "fg2m",
        "fg2a",
        "fg3m",
        "fg3a",
        "fta",
        "points",
        "assists",
        "rebounds",
        "defrebounds",
        "offrebounds",
        "turnovers",
        "fg3pct",
        "efgpct",
        "tspct",
        "usage",
    ]
    df = pd.DataFrame(records, columns=columns)
    df["source"] = "fallback_sample"
    return df


def _fallback_team_stats() -> pd.DataFrame:
    """Small team-level sample used only when the public workbook is unavailable."""
    records = [
        ["LAL", "LAL", 82, 236460, 8061, 2189, 1831, 860, 2480, 1180, 905, 9170, 1180, 760, 0.558, 0.271],
        ["OKC", "OKC", 82, 236260, 8290, 2320, 1900, 930, 2620, 1250, 980, 9650, 1060, 840, 0.574, 0.298],
        ["BOS", "BOS", 82, 236000, 8050, 2050, 1710, 1180, 3200, 1080, 850, 9480, 1010, 720, 0.582, 0.250],
        ["DEN", "DEN", 82, 236300, 7920, 2400, 2020, 780, 2250, 1310, 1020, 9000, 1125, 805, 0.548, 0.286],
        ["MIN", "MIN", 82, 236120, 7800, 2240, 1920, 860, 2500, 1150, 900, 8950, 1160, 780, 0.552, 0.281],
        ["HOU", "HOU", 82, 236420, 8150, 2260, 1985, 910, 2790, 1225, 960, 9340, 1220, 910, 0.556, 0.318],
    ]
    columns = [
        "name",
        "teamabbreviation",
        "gamesplayed",
        "secondsplayed",
        "offposs",
        "fg2m",
        "fg2a",
        "fg3m",
        "fg3a",
        "fta",
        "ftpoints",
        "points",
        "turnovers",
        "offrebounds",
        "efgpct",
        "offfgreboundpct",
    ]
    df = pd.DataFrame(records, columns=columns)
    df["source"] = "fallback_sample"
    return df


def download_player_stats(url: str = SURENNBA_PLAYER_STATS_URL, timeout: int = 30) -> pd.DataFrame:
    """Download the public surennba_stats player table."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text)).copy()
    source = pd.Series(["surennba_stats"] * len(df), name="source")
    return pd.concat([df, source], axis=1)


def download_team_stats(url: str = SURENNBA_TEAM_STATS_URL, timeout: int = 30) -> pd.DataFrame:
    """Download the public surennba_stats team workbook."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content)).copy()
    source = pd.Series(["surennba_stats"] * len(df), name="source")
    return pd.concat([df, source], axis=1)


def load_player_stats(use_cache: bool = True, allow_fallback: bool = True) -> pd.DataFrame:
    """Load player stats from cache, remote source, or a small fallback sample."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if use_cache and PLAYER_CACHE.exists():
        return pd.read_csv(PLAYER_CACHE)

    try:
        df = download_player_stats()
        df.to_csv(PLAYER_CACHE, index=False)
        return df
    except Exception:
        if allow_fallback:
            return _fallback_player_stats()
        raise


def load_team_stats(use_cache: bool = True, allow_fallback: bool = True) -> pd.DataFrame:
    """Load team stats from cache, remote source, or a small fallback sample."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if use_cache and TEAM_CACHE.exists():
        return pd.read_excel(TEAM_CACHE)

    try:
        df = download_team_stats()
        df.to_excel(TEAM_CACHE, index=False)
        return df
    except Exception:
        if allow_fallback:
            return _fallback_team_stats()
        raise


def validate_player_columns(df: pd.DataFrame) -> None:
    """Raise a clear error if a required player column is missing."""
    missing = sorted(REQUIRED_PLAYER_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"player stats missing required columns: {missing}")


def validate_team_columns(df: pd.DataFrame) -> None:
    """Raise a clear error if a required team column is missing."""
    missing = sorted(REQUIRED_TEAM_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"team stats missing required columns: {missing}")


def infer_position_group(row: pd.Series) -> str:
    """Assign a broad teaching role: Guard, Forward, or Center.

    Public surennba_stats player totals do not include official positions. The
    override map handles common players; the fallback uses role signals so the
    charts remain useful even when the remote table changes.
    """
    if row["name"] in ROLE_OVERRIDES:
        return ROLE_OVERRIDES[row["name"]]
    fg3a_per36 = row.get("fg3a_per36", 0)
    rebounds_per36 = row.get("rebounds_per36", 0)
    assists_per36 = row.get("assists_per36", 0)
    if rebounds_per36 >= 9 and fg3a_per36 < 3:
        return "Center"
    if assists_per36 >= 5 or fg3a_per36 >= 7:
        return "Guard"
    return "Forward"


def prepare_player_dataset(min_minutes: int = 300, use_cache: bool = True) -> pd.DataFrame:
    """Return a cleaned player table with textbook-friendly derived columns."""
    df = load_player_stats(use_cache=use_cache)
    df.columns = df.columns.str.strip().str.lower()
    validate_player_columns(df)

    numeric_cols = sorted(REQUIRED_PLAYER_COLUMNS - {"name", "teamabbreviation"})
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["minutes"] >= min_minutes].copy()
    df = add_player_rate_columns(df)
    df["position_group"] = df.apply(infer_position_group, axis=1)
    df["player_label"] = df["name"] + " (" + df["teamabbreviation"] + ")"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PLAYER_CACHE, index=False)
    return df


def prepare_team_dataset(min_games: int = 1, use_cache: bool = True) -> pd.DataFrame:
    """Return a cleaned team table with possession and Four Factors columns."""
    df = load_team_stats(use_cache=use_cache)
    df.columns = df.columns.str.strip().str.lower()
    validate_team_columns(df)

    numeric_cols = sorted(REQUIRED_TEAM_COLUMNS - {"name", "teamabbreviation"})
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["gamesplayed"] >= min_games].copy()
    fga = df["fg2a"] + df["fg3a"]
    fgm = df["fg2m"] + df["fg3m"]
    df["fga"] = fga
    df["fgm"] = fgm
    df["efg_pct_calc"] = (fgm + 0.5 * df["fg3m"]) / fga
    df["tov_pct_calc"] = df["turnovers"] / (fga + 0.44 * df["fta"] + df["turnovers"])
    df["orb_pct"] = df["offfgreboundpct"]
    df["ft_rate_calc"] = df["ftpoints"] / fga
    df["off_rtg_calc"] = df["points"] / df["offposs"] * 100
    df["possessions_per_game"] = df["offposs"] / df["gamesplayed"]
    df["team_label"] = df["teamabbreviation"].fillna(df["name"])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_TEAM_CACHE, index=False)
    return df


def illustrative_team_four_factors() -> pd.DataFrame:
    """Small teaching dataset for Four Factors examples."""
    return pd.DataFrame(
        [
            ["高效投篮队", 0.580, 0.125, 0.245, 0.205, 118.0],
            ["保护球权队", 0.545, 0.105, 0.235, 0.190, 116.2],
            ["前场篮板队", 0.525, 0.135, 0.325, 0.220, 115.4],
            ["罚球压力队", 0.535, 0.132, 0.250, 0.295, 114.8],
            ["低效挣扎队", 0.505, 0.155, 0.210, 0.170, 106.5],
        ],
        columns=["team", "efg_pct", "tov_pct", "oreb_pct", "ft_rate", "off_rtg"],
    )
