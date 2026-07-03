"""Figure builders for the Chinese NBA data-thinking textbook."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nba_textbook.data import SURENNBA_SEASON, illustrative_team_four_factors
from nba_textbook.theme import (
    ACCENT,
    BLUE,
    GREEN,
    INK,
    MUTED,
    POSITION_COLORS,
    PURPLE,
    RED,
    YELLOW,
    add_source_note,
    configure_matplotlib,
    save_figure,
)


def _figure_path(output_dir: Path, filename: str) -> Path:
    return output_dir / filename


TARGET_PLAYER = "Austin Reaves"
TARGET_TEAM = "LAL"


def _density_curve(values: pd.Series, points: int = 220) -> tuple[np.ndarray, np.ndarray]:
    """Return a simple Gaussian KDE without adding a plotting dependency."""
    arr = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if len(arr) == 0:
        return np.array([]), np.array([])
    if len(arr) == 1 or np.nanstd(arr) == 0:
        center = arr[0]
        pad = max(abs(center) * 0.08, 1.0)
        x = np.linspace(center - pad, center + pad, points)
        y = np.exp(-0.5 * ((x - center) / (pad / 4)) ** 2)
        return x, y / np.trapezoid(y, x)

    std = np.std(arr, ddof=1)
    bandwidth = max(1.06 * std * len(arr) ** (-1 / 5), std * 0.18, 1e-6)
    pad = bandwidth * 3
    x = np.linspace(arr.min() - pad, arr.max() + pad, points)
    scaled = (x[:, None] - arr[None, :]) / bandwidth
    y = np.exp(-0.5 * scaled**2).sum(axis=1) / (len(arr) * bandwidth * np.sqrt(2 * np.pi))
    return x, y


def _metric_values(df: pd.DataFrame, metric: str, scale: float) -> pd.Series:
    return pd.to_numeric(df[metric], errors="coerce") * scale


def _find_target_player(players: pd.DataFrame, target_name: str = TARGET_PLAYER) -> pd.Series:
    match = players["name"].str.casefold() == target_name.casefold()
    if not match.any():
        raise ValueError(f"target player not found in player table: {target_name}")
    return players.loc[match].iloc[0]


def _draw_density_panel(
    ax: plt.Axes,
    values: pd.Series,
    target_value: float,
    *,
    color: str,
    title: str,
    annotation: str,
) -> None:
    x, y = _density_curve(values)
    if len(x) == 0:
        ax.text(0.5, 0.5, "没有可用数据", transform=ax.transAxes, ha="center", va="center", color=MUTED)
        return
    ax.fill_between(x, y, color=color, alpha=0.22)
    ax.plot(x, y, color=color, linewidth=2)
    ax.axvline(target_value, color=RED, linestyle="--", linewidth=1.8)
    ax.text(
        target_value,
        y.max() * 0.92,
        annotation,
        color=RED,
        fontsize=9,
        ha="left",
        va="top",
    )
    ax.set_title(title, loc="left", fontsize=11, weight="bold")
    ax.set_yticks([])
    ax.grid(axis="y", visible=False)


def _percentile_text(values: pd.Series, target_value: float, higher_is_better: bool) -> str:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) == 0:
        return "样本不足"
    share_below = (clean <= target_value).mean() * 100
    if higher_is_better:
        return f"约高于 {share_below:.0f}% 样本"
    return f"约低于 {100 - share_below:.0f}% 样本"


def build_team_pace_distribution_chart(teams: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = teams.dropna(subset=["possessions_per_game", "off_rtg_calc"]).copy()
    target = df.loc[df["teamabbreviation"] == TARGET_TEAM].iloc[0] if (df["teamabbreviation"] == TARGET_TEAM).any() else df.iloc[0]
    target_pace = float(target["possessions_per_game"])
    target_rtg = float(target["off_rtg_calc"])

    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.0), sharex=False)
    _draw_density_panel(
        axes[0],
        df["possessions_per_game"],
        target_pace,
        color=BLUE,
        title="全联盟球队节奏分布：先判断一队是快还是慢",
        annotation=f"{target['teamabbreviation']} {target_pace:.1f} 回合/场",
    )
    _draw_density_panel(
        axes[1],
        df["off_rtg_calc"],
        target_rtg,
        color=ACCENT,
        title="全联盟进攻效率分布：再判断每次机会值多少钱",
        annotation=f"{target['teamabbreviation']} {target_rtg:.1f} 分/100回合",
    )
    axes[0].set_xlabel("进攻回合 / 场")
    axes[1].set_xlabel("进攻效率：每 100 回合得分")
    fig.suptitle("球队数据要单独读：节奏和效率不是同一件事", x=0.01, ha="left", fontsize=15, weight="bold")
    add_source_note(fig, f"数据：surennba_stats {SURENNBA_SEASON} 常规赛球队统计。")
    return save_figure(fig, _figure_path(output_dir, "01-team-pace-efficiency-distribution.png"))


def build_possessions_pace_chart(output_dir: Path) -> Path:
    configure_matplotlib()
    df = pd.DataFrame(
        {
            "球队": ["慢节奏队", "联盟中速队", "快节奏队"],
            "每场回合": [92, 100, 108],
            "每场得分": [110, 110, 110],
        }
    )
    df["每100回合得分"] = df["每场得分"] / df["每场回合"] * 100

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bars = ax.bar(df["球队"], df["每100回合得分"], color=[BLUE, ACCENT, GREEN], width=0.58)
    ax.axhline(110, color=MUTED, linewidth=1.2, linestyle="--", label="110 分/100 回合参考线")
    ax.set_title("同样每场 110 分，节奏不同，进攻效率完全不同", loc="left", fontsize=15, weight="bold")
    ax.set_ylabel("每 100 回合得分")
    ax.set_ylim(95, 125)
    for bar, poss in zip(bars, df["每场回合"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{bar.get_height():.1f}\n{poss} 回合",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=10,
        )
    ax.legend(frameon=False, loc="upper right")
    add_source_note(fig, "示意图：用同样 110 分说明 possession-based thinking。")
    return save_figure(fig, _figure_path(output_dir, "01-possessions-pace.png"))


def build_per36_three_point_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["fg3a_per36"]).sort_values("fg3a_per36", ascending=False).head(14)
    df = df.sort_values("fg3a_per36")

    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    colors = [POSITION_COLORS.get(pos, MUTED) for pos in df["position_group"]]
    ax.barh(df["player_label"], df["fg3a_per36"], color=colors)
    ax.axvline(8, color=RED, linestyle="--", linewidth=1.5)
    ax.text(8.1, len(df) - 0.8, "每 36 分钟 8 次三分", color=RED, fontsize=10)
    ax.set_title("36 分钟出手 8 次三分：它在球员群体里是什么强度？", loc="left", fontsize=15, weight="bold")
    ax.set_xlabel("三分出手 / 36 分钟")
    ax.set_ylabel("")
    add_source_note(fig, "数据：surennba_stats 球员统计；若网络不可用则使用内置样例。")
    return save_figure(fig, _figure_path(output_dir, "02-per36-three-point-volume.png"))


def build_four_factors_chart(teams: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    if teams.empty:
        df = illustrative_team_four_factors()
    else:
        df = teams.copy()
    metrics = ["efg_pct", "tov_pct", "oreb_pct", "ft_rate"]
    labels = ["eFG%", "TOV% 越低越好", "ORB%", "FT/FGA"]

    if "efg_pct" not in df.columns:
        df["efg_pct"] = df["efg_pct_calc"]
    if "tov_pct" not in df.columns:
        df["tov_pct"] = df["tov_pct_calc"]
    if "oreb_pct" not in df.columns:
        df["oreb_pct"] = df["orb_pct"]
    if "ft_rate" not in df.columns:
        df["ft_rate"] = df["ft_rate_calc"]
    if "off_rtg" not in df.columns:
        df["off_rtg"] = df["off_rtg_calc"]
    if "team" not in df.columns:
        df["team"] = df["teamabbreviation"]

    target_rows = df[df["team"].eq(TARGET_TEAM)]
    leaders = df.sort_values("off_rtg", ascending=False).head(8)
    trailers = df.sort_values("off_rtg", ascending=True).head(4)
    df = pd.concat([target_rows, leaders, trailers]).drop_duplicates(subset=["team"]).head(14)
    df = df.sort_values("off_rtg", ascending=False)

    values = df[metrics].copy()
    values["tov_pct"] = 1 - values["tov_pct"]
    normalized = (values - values.min()) / (values.max() - values.min())

    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="YlOrBr", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(labels)), labels=labels)
    ax.set_yticks(np.arange(len(df)), labels=df["team"])
    ax.set_title("Four Factors：真实球队可以用不同方式打出好进攻", loc="left", fontsize=15, weight="bold")
    for row in range(len(df)):
        for col, metric in enumerate(metrics):
            value = df.iloc[row][metric]
            text = f"{value:.3f}"
            ax.text(col, row, text, ha="center", va="center", fontsize=10, color=INK)
    cbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("同列相对表现", color=MUTED)
    add_source_note(fig, f"数据：surennba_stats {SURENNBA_SEASON} 常规赛球队统计；热力颜色只比较本图球队。")
    return save_figure(fig, _figure_path(output_dir, "03-four-factors-heatmap.png"))


def build_team_four_factors_distribution_chart(teams: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = teams.dropna(subset=["efg_pct_calc", "tov_pct_calc", "orb_pct", "ft_rate_calc"]).copy()
    target = df.loc[df["teamabbreviation"] == TARGET_TEAM].iloc[0] if (df["teamabbreviation"] == TARGET_TEAM).any() else df.iloc[0]
    factor_specs = [
        ("efg_pct_calc", "eFG%：投篮价值", BLUE, True),
        ("tov_pct_calc", "TOV%：越低越好", RED, False),
        ("orb_pct", "ORB%：抢回投丢", GREEN, True),
        ("ft_rate_calc", "FT/FGA：罚球收益", ACCENT, True),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 6.4))
    for ax, (metric, title, color, higher_is_better) in zip(axes.ravel(), factor_specs):
        values = df[metric] * 100
        target_value = float(target[metric] * 100)
        annotation = f"{target['teamabbreviation']} {target_value:.1f}%\n{_percentile_text(values, target_value, higher_is_better)}"
        _draw_density_panel(
            ax,
            values,
            target_value,
            color=color,
            title=title,
            annotation=annotation,
        )
        ax.set_xlabel("球队赛季值（%）")
    fig.suptitle("Four Factors 要放回球队分布里读", x=0.01, ha="left", fontsize=15, weight="bold")
    add_source_note(fig, f"数据：surennba_stats {SURENNBA_SEASON} 常规赛球队统计；LAL 用作读图案例。")
    return save_figure(fig, _figure_path(output_dir, "03-four-factors-distribution.png"))


def build_usage_efficiency_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["usage", "ts_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    for position, group in df.groupby("position_group"):
        ax.scatter(
            group["usage"],
            group["ts_pct_calc"] * 100,
            s=np.clip(group["minutes"] / 10, 30, 260),
            alpha=0.72,
            label=position,
            color=POSITION_COLORS.get(position, MUTED),
            edgecolor="white",
            linewidth=0.7,
        )
    ax.axvline(df["usage"].median(), color=MUTED, linestyle="--", linewidth=1)
    ax.axhline((df["ts_pct_calc"] * 100).median(), color=MUTED, linestyle="--", linewidth=1)
    label_df = df.sort_values(["usage", "ts_pct_calc"], ascending=False).head(5)
    for _, row in label_df.iterrows():
        ax.text(row["usage"] + 0.2, row["ts_pct_calc"] * 100 + 0.2, row["name"], fontsize=8, color=INK)
    ax.set_title("使用率不是持球时间：它描述谁结束了进攻回合", loc="left", fontsize=15, weight="bold")
    ax.set_xlabel("Usage Rate / 使用率")
    ax.set_ylabel("TS% / 真实命中率")
    ax.legend(frameon=False, title="位置组")
    add_source_note(fig, "数据：surennba_stats；点大小约代表上场时间。")
    return save_figure(fig, _figure_path(output_dir, "04-usage-vs-efficiency.png"))


def build_player_distribution_context_chart(
    players: pd.DataFrame,
    output_dir: Path,
    *,
    metric: str,
    filename: str,
    title: str,
    xlabel: str,
    scale: float = 1.0,
    higher_is_better: bool = True,
    min_minutes: int = 500,
    target_name: str = TARGET_PLAYER,
) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=[metric, "position_group", "teamabbreviation"]).copy()
    df = df[df["minutes"] >= min_minutes]
    target = _find_target_player(players, target_name)
    target_value = float(target[metric] * scale)
    target_position = target["position_group"]
    target_team = target["teamabbreviation"]
    position_df = df[df["position_group"] == target_position]
    team_df = df[df["teamabbreviation"] == target_team].sort_values(metric)

    fig, axes = plt.subplots(3, 1, figsize=(8.5, 7.4), gridspec_kw={"height_ratios": [1, 1, 0.85]})
    league_values = _metric_values(df, metric, scale)
    position_values = _metric_values(position_df, metric, scale)

    _draw_density_panel(
        axes[0],
        league_values,
        target_value,
        color=BLUE,
        title="第一步：放回全联盟轮换球员分布",
        annotation=f"{target_name} {target_value:.1f}\n{_percentile_text(league_values, target_value, higher_is_better)}",
    )
    _draw_density_panel(
        axes[1],
        position_values,
        target_value,
        color=POSITION_COLORS.get(target_position, ACCENT),
        title=f"第二步：只和同位置组比较（{target_position}）",
        annotation=f"{target_value:.1f}\n{_percentile_text(position_values, target_value, higher_is_better)}",
    )

    team_values = _metric_values(team_df, metric, scale)
    y = np.linspace(0.1, 0.9, len(team_df)) if len(team_df) else np.array([])
    axes[2].scatter(team_values, y, color=MUTED, s=46, alpha=0.72)
    axes[2].scatter([target_value], [0.5], color=RED, s=92, zorder=3)
    axes[2].axvline(target_value, color=RED, linestyle="--", linewidth=1.3)
    axes[2].text(target_value, 0.96, f"{target_team} 队内位置", color=RED, fontsize=9, ha="left", va="top")
    for _, row in team_df.tail(4).iterrows():
        value = float(row[metric] * scale)
        axes[2].text(value, 0.06, row["name"], fontsize=7.5, color=INK, rotation=25, ha="right", va="bottom")
    axes[2].set_title("第三步：球队语境单独看（队内样本小，用点图）", loc="left", fontsize=11, weight="bold")
    axes[2].set_yticks([])
    axes[2].set_ylim(0, 1)
    axes[2].set_xlabel(xlabel)

    axes[0].set_xlabel(xlabel)
    axes[1].set_xlabel(xlabel)
    fig.suptitle(title, x=0.01, ha="left", fontsize=15, weight="bold")
    add_source_note(
        fig,
        f"数据：surennba_stats {SURENNBA_SEASON} 常规赛球员统计；位置组为本教材基于角色信号的粗分组。",
    )
    return save_figure(fig, _figure_path(output_dir, filename))


def build_turnover_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["tov_per36", "tov_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    for position, group in df.groupby("position_group"):
        ax.scatter(
            group["tov_per36"],
            group["tov_pct_calc"] * 100,
            s=75,
            alpha=0.76,
            label=position,
            color=POSITION_COLORS.get(position, MUTED),
            edgecolor="white",
            linewidth=0.7,
        )
    ax.set_title("同样是失误，失误率会告诉你它占用了多少机会", loc="left", fontsize=15, weight="bold")
    ax.set_xlabel("失误 / 36 分钟")
    ax.set_ylabel("估算失误率 TOV%")
    ax.legend(frameon=False, title="位置组")
    add_source_note(fig, "TOV% = TOV / (FGA + 0.44 * FTA + TOV)。")
    return save_figure(fig, _figure_path(output_dir, "05-turnover-rate.png"))


def build_rebound_rate_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["rebounds_per36", "offrebounds", "defrebounds"]).copy()
    df = df[df["minutes"] >= 500]
    order = ["Guard", "Forward", "Center"]
    data = [df.loc[df["position_group"] == pos, "rebounds_per36"] for pos in order]

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    parts = ax.violinplot(data, showmeans=False, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS[order[idx]])
        body.set_alpha(0.55)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    for idx, values in enumerate(data, start=1):
        x = np.full(len(values), idx) + np.linspace(-0.05, 0.05, len(values))
        ax.scatter(x, values, color=INK, s=18, alpha=0.55)
    ax.set_xticks(range(1, len(order) + 1), ["后卫", "锋线", "中锋"])
    ax.set_title("篮板要看机会：先从每 36 分钟篮板理解位置职责", loc="left", fontsize=15, weight="bold")
    ax.set_ylabel("篮板 / 36 分钟")
    add_source_note(fig, "真实 ORB%/DRB% 需要对手篮板机会；本图先用 per36 展示角色差异。")
    return save_figure(fig, _figure_path(output_dir, "06-rebound-role-distribution.png"))


def build_shooting_efficiency_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["efg_pct_calc", "ts_pct_calc", "fg3pct"]).copy()
    df = df[df["fg3a"] >= 100]
    summary = (
        df.groupby("position_group")[["fg3pct", "efg_pct_calc", "ts_pct_calc"]]
        .median()
        .reindex(["Guard", "Forward", "Center"])
    )

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    x = np.arange(len(summary))
    width = 0.24
    ax.bar(x - width, summary["fg3pct"] * 100, width, label="3P%", color=BLUE)
    ax.bar(x, summary["efg_pct_calc"] * 100, width, label="eFG%", color=ACCENT)
    ax.bar(x + width, summary["ts_pct_calc"] * 100, width, label="TS%", color=GREEN)
    ax.set_xticks(x, ["后卫", "锋线", "中锋"])
    ax.set_title("FG%、eFG%、TS%：效率指标在修正不同问题", loc="left", fontsize=15, weight="bold")
    ax.set_ylabel("命中率 / 效率（%）")
    ax.legend(frameon=False, ncol=3)
    add_source_note(fig, "3P% 只看三分；eFG% 修正三分价值；TS% 加入罚球。")
    return save_figure(fig, _figure_path(output_dir, "07-shooting-efficiency.png"))


def build_three_point_volume_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["fg3a_per36", "fg3pct"]).copy()
    df = df[(df["minutes"] >= 500) & (df["fg3a"] >= 50)]

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    for position, group in df.groupby("position_group"):
        ax.scatter(
            group["fg3a_per36"],
            group["fg3pct"] * 100,
            s=np.clip(group["fg3a"] / 2, 25, 260),
            alpha=0.74,
            label=position,
            color=POSITION_COLORS.get(position, MUTED),
            edgecolor="white",
            linewidth=0.7,
        )
    ax.axvline(8, color=RED, linestyle="--", linewidth=1.3)
    ax.axhline(36, color=MUTED, linestyle="--", linewidth=1)
    ax.text(8.15, ax.get_ylim()[1] - 1.0, "高三分产量线", color=RED, fontsize=9)
    ax.set_title("三分不是只看准度：产量和命中率要一起读", loc="left", fontsize=15, weight="bold")
    ax.set_xlabel("三分出手 / 36 分钟")
    ax.set_ylabel("三分命中率（%）")
    ax.legend(frameon=False, title="位置组")
    add_source_note(fig, "点大小约代表赛季三分总出手。")
    return save_figure(fig, _figure_path(output_dir, "08-three-point-volume-efficiency.png"))


def build_role_map_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["usage", "fg3a_per36", "ts_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    scatter = ax.scatter(
        df["usage"],
        df["fg3a_per36"],
        c=df["ts_pct_calc"] * 100,
        cmap="viridis",
        s=np.clip(df["minutes"] / 10, 35, 240),
        alpha=0.78,
        edgecolor="white",
        linewidth=0.7,
    )
    ax.axvline(df["usage"].median(), color=MUTED, linestyle="--", linewidth=1)
    ax.axhline(8, color=RED, linestyle="--", linewidth=1.3)
    for _, row in df.sort_values("fg3a_per36", ascending=False).head(4).iterrows():
        ax.text(row["usage"] + 0.15, row["fg3a_per36"] + 0.1, row["name"], fontsize=8, color=INK)
    cbar = fig.colorbar(scatter, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("TS%", color=MUTED)
    ax.set_title("读球员角色：谁负责消化回合，谁负责拉开空间？", loc="left", fontsize=15, weight="bold")
    ax.set_xlabel("Usage Rate / 使用率")
    ax.set_ylabel("三分出手 / 36 分钟")
    add_source_note(fig, "横轴读球权终结，纵轴读空间参与，颜色读效率。")
    return save_figure(fig, _figure_path(output_dir, "09-player-role-map.png"))


def build_role_density_dashboard(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players[players["minutes"] >= 500].copy()
    target = _find_target_player(players)
    target_position = target["position_group"]
    specs = [
        ("usage", "使用率", "%", 1.0, True, BLUE),
        ("ts_pct_calc", "TS%", "%", 100.0, True, GREEN),
        ("tov_pct_calc", "TOV%", "%", 100.0, False, RED),
        ("fg3a_per36", "三分出手/36", "次", 1.0, True, ACCENT),
        ("rebounds_per36", "篮板/36", "个", 1.0, True, PURPLE),
    ]

    fig, axes = plt.subplots(len(specs), 1, figsize=(8.5, 8.2), sharex=False)
    for ax, (metric, label, unit, scale, higher_is_better, color) in zip(axes, specs):
        values = _metric_values(df, metric, scale)
        position_values = _metric_values(df[df["position_group"] == target_position], metric, scale)
        target_value = float(target[metric] * scale)
        annotation = (
            f"{target_value:.1f}{unit}\n"
            f"联盟：{_percentile_text(values, target_value, higher_is_better)}；"
            f"同位置：{_percentile_text(position_values, target_value, higher_is_better)}"
        )
        _draw_density_panel(
            ax,
            values,
            target_value,
            color=color,
            title=label,
            annotation=annotation,
        )
        ax.set_xlabel(label)
    fig.suptitle("Austin Reaves 角色拆解：每个指标先看分布位置", x=0.01, ha="left", fontsize=15, weight="bold")
    add_source_note(
        fig,
        f"数据：surennba_stats {SURENNBA_SEASON} 常规赛球员统计；同位置比较使用 {target_position} 组。",
    )
    return save_figure(fig, _figure_path(output_dir, "09-austin-role-density-dashboard.png"))


def build_all_figures(players: pd.DataFrame, teams: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Build all static figures used by the textbook."""
    return [
        build_team_pace_distribution_chart(teams, output_dir),
        build_possessions_pace_chart(output_dir),
        build_per36_three_point_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="points_per36",
            filename="02-austin-points-per36-distribution.png",
            title="Austin Reaves 的得分要先按频率读",
            xlabel="得分 / 36 分钟",
        ),
        build_four_factors_chart(teams, output_dir),
        build_team_four_factors_distribution_chart(teams, output_dir),
        build_usage_efficiency_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="usage",
            filename="04-austin-usage-distribution.png",
            title="Austin Reaves 的使用率：先定位，再解释角色",
            xlabel="Usage Rate / 使用率",
        ),
        build_turnover_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="tov_pct_calc",
            filename="05-austin-turnover-distribution.png",
            title="Austin Reaves 的失误率：失误数要放回机会分布",
            xlabel="估算 TOV%",
            scale=100.0,
            higher_is_better=False,
        ),
        build_rebound_rate_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="rebounds_per36",
            filename="06-austin-rebound-distribution.png",
            title="Austin Reaves 的篮板：先和位置职责比较",
            xlabel="篮板 / 36 分钟",
        ),
        build_shooting_efficiency_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="ts_pct_calc",
            filename="07-austin-ts-distribution.png",
            title="Austin Reaves 的 TS%：效率一定要看分布",
            xlabel="TS%",
            scale=100.0,
        ),
        build_three_point_volume_chart(players, output_dir),
        build_player_distribution_context_chart(
            players,
            output_dir,
            metric="fg3a_per36",
            filename="08-austin-three-point-volume-distribution.png",
            title="Austin Reaves 的三分产量：准度之前先看频率",
            xlabel="三分出手 / 36 分钟",
        ),
        build_role_map_chart(players, output_dir),
        build_role_density_dashboard(players, output_dir),
    ]
