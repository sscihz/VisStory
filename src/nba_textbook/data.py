"""Data loading and cleaning helpers for the textbook."""

from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
import requests

from nba_textbook.metrics import add_player_rate_columns

SURENNBA_PLAYER_STATS_URL = (
    "https://raw.githubusercontent.com/suren-nba/surennba_stats/main/"
    "data/player_stats/2025-26NBA_RegularSeason_Player_stats.csv"
)
SURENNBA_TEAM_STATS_URL = (
    "https://raw.githubusercontent.com/suren-nba/surennba_stats/main/"
    "data/team_stats/2025-26NBA_RegularSeason_Team_stats.xlsx"
)
SURENNBA_OPPONENT_STATS_URL = (
    "https://raw.githubusercontent.com/suren-nba/surennba_stats/main/"
    "data/team_stats/2025-26NBA_RegularSeason_Opponent_stats.xlsx"
)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PLAYER_CACHE = RAW_DIR / "surennba_player_stats.csv"
TEAM_CACHE = RAW_DIR / "surennba_team_stats.xlsx"
OPPONENT_CACHE = RAW_DIR / "surennba_opponent_stats.xlsx"
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

OPTIONAL_PLAYER_NUMERIC_COLUMNS = {
    "offfgreboundpct",
    "deffgreboundpct",
    "offrebounds",
    "defrebounds",
    "fg3apct",
    "corner3frequency",
    "arc3frequency",
    "corner3accuracy",
    "arc3accuracy",
    "shotqualityavg",
}

REQUIRED_TEAM_COLUMNS = {
    "name",
    "teamabbreviation",
    "gamesplayed",
    "offposs",
    "defposs",
    "points",
    "opponentpoints",
    "fg2m",
    "fg2a",
    "fg3m",
    "fg3a",
    "ftpoints",
    "fta",
    "turnovers",
    "offrebounds",
    "defrebounds",
    "pace",
    "efgpct",
    "tspct",
    "fg3pct",
    "fg3apct",
}

ROLE_OVERRIDES = {
    "Stephen Curry": "Guard",
    "Shai Gilgeous-Alexander": "Guard",
    "Luka Doncic": "Guard",
    "Jalen Brunson": "Guard",
    "Donte DiVincenzo": "Guard",
    "Desmond Bane": "Guard",
    "Tyrese Haliburton": "Guard",
    "Austin Reaves": "Guard",
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
        ["Austin Reaves", "LAL", 1762, 73, 220, 390, 118, 328, 310, 1160, 340, 240, 190, 50, 150, 0.360, 0.567, 0.641, 26.3],
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


def download_player_stats(url: str = SURENNBA_PLAYER_STATS_URL, timeout: int = 30) -> pd.DataFrame:
    """Download the public surennba_stats player table."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text)).copy()
    source = pd.Series(["surennba_stats"] * len(df), name="source")
    return pd.concat([df, source], axis=1)


def download_excel_table(url: str, timeout: int = 30) -> pd.DataFrame:
    """Download a public Excel table from surennba_stats."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content)).copy()


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

    numeric_cols = sorted((REQUIRED_PLAYER_COLUMNS | OPTIONAL_PLAYER_NUMERIC_COLUMNS) & set(df.columns) - {"name", "teamabbreviation"})
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["minutes"] >= min_minutes].copy()
    df = add_player_rate_columns(df)
    df["position_group"] = df.apply(infer_position_group, axis=1)
    df["player_label"] = df["name"] + " (" + df["teamabbreviation"] + ")"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PLAYER_CACHE, index=False)
    return df


def _fallback_team_stats() -> pd.DataFrame:
    """Small team sample that keeps docs buildable without network."""
    records = [
        ["SAS", "SAS", 82, 8197, 8249, 9826, 9145, 2446, 4263, 1116, 3147, 1586, 2016, 1103, 1176, 3121, 100.0, 0.574, 0.591, 0.355, 0.425],
        ["LAL", "LAL", 82, 8061, 8125, 9540, 9396, 2478, 4162, 970, 2751, 1674, 2194, 1188, 1002, 2773, 98.6, 0.569, 0.605, 0.353, 0.398],
        ["MEM", "MEM", 82, 8271, 8337, 9896, 9403, 2464, 4296, 1151, 3199, 1515, 1954, 1272, 1305, 2984, 101.0, 0.559, 0.593, 0.360, 0.427],
        ["IND", "IND", 82, 8287, 8356, 9874, 9219, 2637, 4630, 993, 2831, 1621, 2096, 1106, 1164, 3101, 101.1, 0.553, 0.589, 0.351, 0.379],
        ["NYK", "NYK", 82, 7890, 7900, 9300, 9000, 2300, 4000, 1050, 2900, 1500, 1900, 980, 1200, 3000, 96.2, 0.560, 0.590, 0.362, 0.420],
    ]
    return pd.DataFrame(
        records,
        columns=[
            "name",
            "teamabbreviation",
            "gamesplayed",
            "offposs",
            "defposs",
            "points",
            "opponentpoints",
            "fg2m",
            "fg2a",
            "fg3m",
            "fg3a",
            "ftpoints",
            "fta",
            "turnovers",
            "offrebounds",
            "defrebounds",
            "pace",
            "efgpct",
            "tspct",
            "fg3pct",
            "fg3apct",
        ],
    )


def load_team_stats(use_cache: bool = True, allow_fallback: bool = True) -> pd.DataFrame:
    """Load team and opponent stats from cache, remote source, or fallback."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if use_cache and TEAM_CACHE.exists() and OPPONENT_CACHE.exists():
        team_df = pd.read_excel(TEAM_CACHE)
        opponent_df = pd.read_excel(OPPONENT_CACHE)
    else:
        try:
            team_df = download_excel_table(SURENNBA_TEAM_STATS_URL)
            opponent_df = download_excel_table(SURENNBA_OPPONENT_STATS_URL)
            team_df.to_excel(TEAM_CACHE, index=False)
            opponent_df.to_excel(OPPONENT_CACHE, index=False)
        except Exception:
            if allow_fallback:
                team_df = _fallback_team_stats()
                opponent_df = team_df.rename(
                    columns={
                        "points": "opponentpoints",
                        "opponentpoints": "points",
                        "offposs": "defposs",
                        "defposs": "offposs",
                        "offrebounds": "defrebounds",
                        "defrebounds": "offrebounds",
                    }
                )
            else:
                raise

    team_df.columns = team_df.columns.str.strip().str.lower()
    opponent_df.columns = opponent_df.columns.str.strip().str.lower()
    team_df = pd.concat([team_df.copy(), pd.Series(["surennba_stats"] * len(team_df), name="source")], axis=1)
    opponent_subset = opponent_df[["teamabbreviation", "defrebounds", "offrebounds"]].rename(
        columns={
            "defrebounds": "opponent_defrebounds",
            "offrebounds": "opponent_offrebounds",
        }
    )
    return team_df.merge(opponent_subset, on="teamabbreviation", how="left")


def prepare_team_dataset(use_cache: bool = True) -> pd.DataFrame:
    """Return a cleaned team table with real Four Factors and ratings."""
    df = load_team_stats(use_cache=use_cache)
    validate_team_columns(df)
    numeric_cols = sorted(set(df.columns) - {"name", "shortname", "teamabbreviation", "source"})
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "opponent_defrebounds" not in df.columns:
        df["opponent_defrebounds"] = df["defrebounds"]
    if "opponent_offrebounds" not in df.columns:
        df["opponent_offrebounds"] = df["offrebounds"]

    fga = df["fg2a"] + df["fg3a"]
    fgm = df["fg2m"] + df["fg3m"]
    derived = pd.DataFrame(
        {
            "fga": fga,
            "fgm": fgm,
            "off_rtg": df["points"] / df["offposs"] * 100,
            "def_rtg": df["opponentpoints"] / df["defposs"] * 100,
            "tov_pct_calc": df["turnovers"] / (fga + 0.44 * df["fta"] + df["turnovers"]),
            "oreb_pct_calc": df["offrebounds"] / (df["offrebounds"] + df["opponent_defrebounds"]),
            "ft_rate_calc": df["ftpoints"] / fga,
            "efg_pct_calc": (fgm + 0.5 * df["fg3m"]) / fga,
            "points_per_game": df["points"] / df["gamesplayed"],
            "poss_per_game": df["offposs"] / df["gamesplayed"],
        }
    )
    derived["net_rtg"] = derived["off_rtg"] - df["opponentpoints"] / df["defposs"] * 100
    df = pd.concat([df, derived], axis=1)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_TEAM_CACHE, index=False)
    return df


def illustrative_team_four_factors() -> pd.DataFrame:
    """Backward-compatible alias for older notebooks/tests."""
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
