import pandas as pd
import pytest

from nba_textbook import data


def test_validate_player_columns_accepts_fallback_sample():
    sample = data._fallback_player_stats()
    data.validate_player_columns(sample)


def test_validate_team_columns_accepts_fallback_sample():
    sample = data._fallback_team_stats()
    data.validate_team_columns(sample)


def test_validate_player_columns_reports_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        data.validate_player_columns(pd.DataFrame({"name": ["A"]}))


def test_validate_team_columns_reports_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        data.validate_team_columns(pd.DataFrame({"name": ["A"]}))


def test_prepare_player_dataset_uses_fallback_when_patched(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(data, "load_player_stats", lambda use_cache=True: data._fallback_player_stats())

    players = data.prepare_player_dataset(min_minutes=300)

    assert {"fg3a_per36", "ts_pct_calc", "position_group", "player_label"}.issubset(players.columns)
    assert set(players["position_group"]) >= {"Guard", "Forward", "Center"}
    assert "Austin Reaves" in set(players["name"])
    assert (tmp_path / "data" / "processed" / "player_rates.csv").exists()


def test_prepare_team_dataset_uses_fallback_when_patched(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(data, "load_team_stats", lambda use_cache=True: data._fallback_team_stats())

    teams = data.prepare_team_dataset()

    expected = {"efg_pct_calc", "tov_pct_calc", "orb_pct", "ft_rate_calc", "off_rtg_calc", "possessions_per_game"}
    assert expected.issubset(teams.columns)
    assert "LAL" in set(teams["teamabbreviation"])
    assert (tmp_path / "data" / "processed" / "team_rates.csv").exists()
