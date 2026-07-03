"""Figure builders for the Chinese NBA data-thinking textbook."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nba_textbook.data import illustrative_team_four_factors
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
    return save_figure(fig, _figure_path(output_dir, "01-possessions-pace.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "02-per36-three-point-volume.svg"))


def build_four_factors_chart(output_dir: Path) -> Path:
    configure_matplotlib()
    df = illustrative_team_four_factors()
    metrics = ["efg_pct", "tov_pct", "oreb_pct", "ft_rate"]
    labels = ["eFG%", "TOV% 越低越好", "ORB%", "FT/FGA"]
    values = df[metrics].copy()
    values["tov_pct"] = 1 - values["tov_pct"]
    normalized = (values - values.min()) / (values.max() - values.min())

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="YlOrBr", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(labels)), labels=labels)
    ax.set_yticks(np.arange(len(df)), labels=df["team"])
    ax.set_title("Four Factors：球队可以用不同方式打出好进攻", loc="left", fontsize=15, weight="bold")
    for row in range(len(df)):
        for col, metric in enumerate(metrics):
            value = df.iloc[row][metric]
            text = f"{value:.3f}"
            ax.text(col, row, text, ha="center", va="center", fontsize=10, color=INK)
    cbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("同列相对表现", color=MUTED)
    add_source_note(fig, "示意数据；指标定义参考 Basketball-Reference Four Factors。")
    return save_figure(fig, _figure_path(output_dir, "03-four-factors-heatmap.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "04-usage-vs-efficiency.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "05-turnover-rate.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "06-rebound-role-distribution.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "07-shooting-efficiency.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "08-three-point-volume-efficiency.svg"))


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
    return save_figure(fig, _figure_path(output_dir, "09-player-role-map.svg"))


def build_all_figures(players: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Build all static figures used by the textbook."""
    return [
        build_possessions_pace_chart(output_dir),
        build_per36_three_point_chart(players, output_dir),
        build_four_factors_chart(output_dir),
        build_usage_efficiency_chart(players, output_dir),
        build_turnover_chart(players, output_dir),
        build_rebound_rate_chart(players, output_dir),
        build_shooting_efficiency_chart(players, output_dir),
        build_three_point_volume_chart(players, output_dir),
        build_role_map_chart(players, output_dir),
    ]
