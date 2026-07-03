import math

import pandas as pd

from nba_textbook import metrics


def test_possessions_formula():
    assert metrics.possessions(fga=90, fta=20, oreb=10, tov=12) == 100.8


def test_per_minutes_formula():
    assert metrics.per_minutes(value=8, minutes=18, target_minutes=36) == 16


def test_per_possessions_formula():
    assert metrics.per_possessions(value=112, possessions_value=100) == 112


def test_shooting_efficiency_formulas():
    assert metrics.effective_fg_pct(fgm=8, fg3m=4, fga=16) == 0.625
    assert metrics.true_shooting_pct(points=24, fga=16, fta=4) == 24 / (2 * (16 + 0.44 * 4))


def test_turnover_and_rebound_formulas():
    assert metrics.turnover_pct(tov=12, fga=90, fta=20) == 12 / (90 + 0.44 * 20 + 12)
    assert metrics.offensive_rebound_pct(oreb=11, opponent_dreb=31) == 11 / 42
    assert metrics.defensive_rebound_pct(dreb=34, opponent_oreb=9) == 34 / 43


def test_usage_rate_formula():
    actual = metrics.usage_rate(
        player_fga=18,
        player_fta=8,
        player_tov=4,
        team_fga=90,
        team_fta=24,
        team_tov=13,
        player_minutes=36,
        team_minutes=240,
    )
    expected = 100 * ((18 + 0.44 * 8 + 4) * 240) / ((90 + 0.44 * 24 + 13) * 36)
    assert actual == expected


def test_zero_denominator_returns_nan():
    assert math.isnan(metrics.per_minutes(value=10, minutes=0))


def test_add_player_rate_columns_vectorized():
    df = pd.DataFrame(
        {
            "fg3a": [8],
            "fg3m": [3],
            "minutes": [36],
            "points": [24],
            "rebounds": [9],
            "assists": [6],
            "turnovers": [3],
            "fg2a": [12],
            "fg2m": [6],
            "fta": [4],
        }
    )
    out = metrics.add_player_rate_columns(df)
    assert out.loc[0, "fg3a_per36"] == 8
    assert out.loc[0, "points_per36"] == 24
    assert out.loc[0, "efg_pct_calc"] == (9 + 0.5 * 3) / 20
