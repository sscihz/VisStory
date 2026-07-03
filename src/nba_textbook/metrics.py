"""Basketball metric formulas used throughout the textbook.

The formulas intentionally stay close to common public definitions from
Basketball-Reference, NBA Stats, and possession-based basketball analytics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

NumberLike = float | int | pd.Series | np.ndarray


def _safe_divide(numerator: NumberLike, denominator: NumberLike) -> Any:
    """Divide while returning NaN for zero denominators."""
    result = np.divide(
        numerator,
        denominator,
        out=np.full_like(np.asarray(numerator, dtype=float), np.nan, dtype=float),
        where=np.asarray(denominator, dtype=float) != 0,
    )
    if np.ndim(result) == 0:
        return float(result)
    if isinstance(numerator, pd.Series):
        return pd.Series(result, index=numerator.index)
    return result


def possessions(
    fga: NumberLike,
    fta: NumberLike,
    oreb: NumberLike,
    tov: NumberLike,
    free_throw_weight: float = 0.44,
) -> Any:
    """Estimate possessions as FGA + 0.44 * FTA - OREB + TOV."""
    return fga + free_throw_weight * fta - oreb + tov


def plays(
    fga: NumberLike,
    fta: NumberLike,
    tov: NumberLike,
    free_throw_weight: float = 0.44,
) -> Any:
    """Estimate possession-ending opportunities before offensive rebounds."""
    return fga + free_throw_weight * fta + tov


def pace(possessions_value: NumberLike, minutes: NumberLike, game_minutes: float = 48.0) -> Any:
    """Convert possessions and minutes to possessions per 48 minutes."""
    return _safe_divide(possessions_value * game_minutes, minutes)


def per_minutes(value: NumberLike, minutes: NumberLike, target_minutes: float = 36.0) -> Any:
    """Scale a counting stat to a target number of minutes."""
    return _safe_divide(value * target_minutes, minutes)


def per_possessions(value: NumberLike, possessions_value: NumberLike, target_possessions: float = 100.0) -> Any:
    """Scale a counting stat to a target number of possessions."""
    return _safe_divide(value * target_possessions, possessions_value)


def effective_fg_pct(fgm: NumberLike, fg3m: NumberLike, fga: NumberLike) -> Any:
    """Effective field-goal percentage: (FGM + 0.5 * 3PM) / FGA."""
    return _safe_divide(fgm + 0.5 * fg3m, fga)


def true_shooting_pct(points: NumberLike, fga: NumberLike, fta: NumberLike, free_throw_weight: float = 0.44) -> Any:
    """True shooting percentage: PTS / (2 * (FGA + 0.44 * FTA))."""
    return _safe_divide(points, 2 * (fga + free_throw_weight * fta))


def turnover_pct(tov: NumberLike, fga: NumberLike, fta: NumberLike, free_throw_weight: float = 0.44) -> Any:
    """Share of plays that end in a turnover."""
    return _safe_divide(tov, fga + free_throw_weight * fta + tov)


def offensive_rebound_pct(oreb: NumberLike, opponent_dreb: NumberLike) -> Any:
    """Share of available offensive rebounds collected."""
    return _safe_divide(oreb, oreb + opponent_dreb)


def defensive_rebound_pct(dreb: NumberLike, opponent_oreb: NumberLike) -> Any:
    """Share of available defensive rebounds collected."""
    return _safe_divide(dreb, dreb + opponent_oreb)


def free_throw_rate(ftm: NumberLike, fga: NumberLike) -> Any:
    """Free throws made per field-goal attempt."""
    return _safe_divide(ftm, fga)


def usage_rate(
    player_fga: NumberLike,
    player_fta: NumberLike,
    player_tov: NumberLike,
    team_fga: NumberLike,
    team_fta: NumberLike,
    team_tov: NumberLike,
    player_minutes: NumberLike,
    team_minutes: NumberLike,
    free_throw_weight: float = 0.44,
) -> Any:
    """Estimate the percentage of team plays used by a player while on court.

    team_minutes should be total team player-minutes, usually 5 * team game
    minutes for a team game or sum of player minutes for a season.
    """
    player_plays = player_fga + free_throw_weight * player_fta + player_tov
    team_plays = team_fga + free_throw_weight * team_fta + team_tov
    return 100 * _safe_divide(player_plays * team_minutes, team_plays * player_minutes)


def offensive_rating(points: NumberLike, possessions_value: NumberLike) -> Any:
    """Points scored per 100 possessions."""
    return per_possessions(points, possessions_value, 100.0)


def defensive_rating(opponent_points: NumberLike, opponent_possessions: NumberLike) -> Any:
    """Points allowed per 100 possessions."""
    return per_possessions(opponent_points, opponent_possessions, 100.0)


@dataclass(frozen=True)
class FourFactors:
    """Dean Oliver's four factors for one team or series of teams."""

    efg_pct: Any
    tov_pct: Any
    oreb_pct: Any
    ft_rate: Any


def four_factors(
    fgm: NumberLike,
    fg3m: NumberLike,
    fga: NumberLike,
    fta: NumberLike,
    ftm: NumberLike,
    oreb: NumberLike,
    opponent_dreb: NumberLike,
    tov: NumberLike,
) -> FourFactors:
    """Compute the offensive Four Factors."""
    return FourFactors(
        efg_pct=effective_fg_pct(fgm, fg3m, fga),
        tov_pct=turnover_pct(tov, fga, fta),
        oreb_pct=offensive_rebound_pct(oreb, opponent_dreb),
        ft_rate=free_throw_rate(ftm, fga),
    )


def add_player_rate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add textbook-friendly rate columns to a player-level dataframe."""
    out = df.copy()
    out["fg3a_per36"] = per_minutes(out["fg3a"], out["minutes"], 36)
    out["fg3m_per36"] = per_minutes(out["fg3m"], out["minutes"], 36)
    out["points_per36"] = per_minutes(out["points"], out["minutes"], 36)
    out["rebounds_per36"] = per_minutes(out["rebounds"], out["minutes"], 36)
    out["assists_per36"] = per_minutes(out["assists"], out["minutes"], 36)
    out["tov_per36"] = per_minutes(out["turnovers"], out["minutes"], 36)
    out["estimated_plays"] = plays(out["fg2a"] + out["fg3a"], out["fta"], out["turnovers"])
    out["points_per100_plays"] = per_possessions(out["points"], out["estimated_plays"], 100)
    out["fg3a_per100_plays"] = per_possessions(out["fg3a"], out["estimated_plays"], 100)
    out["tov_pct_calc"] = turnover_pct(out["turnovers"], out["fg2a"] + out["fg3a"], out["fta"])
    out["efg_pct_calc"] = effective_fg_pct(out["fg2m"] + out["fg3m"], out["fg3m"], out["fg2a"] + out["fg3a"])
    out["ts_pct_calc"] = true_shooting_pct(out["points"], out["fg2a"] + out["fg3a"], out["fta"])
    return out
