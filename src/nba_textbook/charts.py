"""Figure builders for the Chinese NBA data-thinking textbook."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


def _position_order(df: pd.DataFrame) -> list[str]:
    return [pos for pos in ["Guard", "Forward", "Center"] if pos in set(df["position_group"])]


def _strip_axes(ax: plt.Axes) -> None:
    ax.spines["left"].set_color("#d6d0c8")
    ax.spines["bottom"].set_color("#d6d0c8")


def _label_extremes(ax: plt.Axes, df: pd.DataFrame, x_col: str, y_col: str, label_col: str, n: int = 3) -> None:
    label_df = pd.concat([df.nlargest(n, y_col), df.nsmallest(n, y_col)]).drop_duplicates()
    for _, row in label_df.iterrows():
        ax.text(row[x_col], row[y_col], f" {row[label_col]}", fontsize=8, color=INK, va="center")


def build_possessions_pace_chart(teams: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = teams.dropna(subset=["pace", "off_rtg", "points_per_game"]).copy()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    ax.hist(df["pace"], bins=9, color=ACCENT, alpha=0.86, edgecolor="white")
    ax.axvline(df["pace"].median(), color=INK, linestyle="--", linewidth=1.2)
    ax.set_title("真实球队节奏分布", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("PACE：每 48 分钟回合数")
    ax.set_ylabel("球队数量")
    _strip_axes(ax)

    ax = axes[1]
    scatter = ax.scatter(
        df["pace"],
        df["off_rtg"],
        c=df["points_per_game"],
        cmap="YlOrBr",
        s=92,
        alpha=0.86,
        edgecolor="white",
        linewidth=0.8,
    )
    ax.axvline(df["pace"].median(), color=MUTED, linestyle="--", linewidth=1)
    ax.axhline(df["off_rtg"].median(), color=MUTED, linestyle="--", linewidth=1)
    _label_extremes(ax, df, "pace", "off_rtg", "teamabbreviation", n=3)
    ax.set_title("节奏快不等于进攻好", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("PACE")
    ax.set_ylabel("进攻效率：每 100 回合得分")
    cbar = fig.colorbar(scatter, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("场均得分", color=MUTED)
    _strip_axes(ax)
    fig.suptitle("回合与节奏：先看球队用了多少机会，再看每次机会打得多好", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "数据：surennba_stats 球队常规赛统计；每个点为一支球队。")
    return save_figure(fig, _figure_path(output_dir, "01-possessions-pace.png"))


def build_per36_three_point_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["fg3a_per36", "fg3pct"]).copy()
    df = df[(df["minutes"] >= 500) & (df["fg3a"] >= 20)]
    order = _position_order(df)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    data = [df.loc[df["position_group"] == pos, "fg3a_per36"] for pos in order]
    parts = ax.violinplot(data, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS.get(order[idx], MUTED))
        body.set_alpha(0.58)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    ax.axhline(8, color=RED, linestyle="--", linewidth=1.2)
    ax.set_xticks(range(1, len(order) + 1), [{"Guard": "后卫", "Forward": "锋线", "Center": "中锋"}[pos] for pos in order])
    ax.set_title("按位置看三分出手频率分布", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("三分出手 / 36 分钟")
    _strip_axes(ax)

    ax = axes[1]
    top = df.sort_values("fg3a_per36", ascending=False).head(14).sort_values("fg3a_per36")
    colors = [POSITION_COLORS.get(pos, MUTED) for pos in top["position_group"]]
    ax.barh(top["player_label"], top["fg3a_per36"], color=colors)
    ax.axvline(8, color=RED, linestyle="--", linewidth=1.4)
    ax.text(8.1, len(top) - 0.8, "8 次/36 分钟", color=RED, fontsize=9)
    ax.set_title("真实球员里谁接近或超过 8 次线", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("三分出手 / 36 分钟")
    ax.set_ylabel("")
    _strip_axes(ax)
    fig.suptitle("每 36 分钟：把出场时间拿掉后，再理解产量", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "数据：surennba_stats 球员统计；过滤：500+ 分钟且 20+ 三分出手。")
    return save_figure(fig, _figure_path(output_dir, "02-per36-three-point-volume.png"))


def build_four_factors_chart(teams: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = teams.dropna(subset=["off_rtg", "efg_pct_calc", "tov_pct_calc", "oreb_pct_calc", "ft_rate_calc"]).copy()
    df = df.sort_values("off_rtg", ascending=False).head(12)
    metrics = ["efg_pct_calc", "tov_pct_calc", "oreb_pct_calc", "ft_rate_calc"]
    labels = ["eFG%", "TOV% 越低越好", "ORB%", "FT/FGA"]
    values = df[metrics].copy()
    values["tov_pct_calc"] = 1 - values["tov_pct_calc"]
    normalized = (values - values.min()) / (values.max() - values.min())

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="YlOrBr", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(labels)), labels=labels)
    ax.set_yticks(np.arange(len(df)), labels=df["teamabbreviation"] + "  " + df["off_rtg"].round(1).astype(str))
    ax.set_title("真实进攻效率前列球队的 Four Factors 画像", loc="left", fontsize=15, weight="bold")
    for row in range(len(df)):
        for col, metric in enumerate(metrics):
            value = df.iloc[row][metric]
            text = f"{value:.3f}"
            ax.text(col, row, text, ha="center", va="center", fontsize=10, color=INK)
    cbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("同列相对表现", color=MUTED)
    ax.set_ylabel("球队  进攻效率")
    add_source_note(fig, "数据：surennba_stats 球队统计；行内数字为真实指标值，颜色为同列相对表现。")
    return save_figure(fig, _figure_path(output_dir, "03-four-factors-heatmap.png"))


def build_usage_efficiency_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["usage", "ts_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    order = _position_order(df)
    data = [df.loc[df["position_group"] == pos, "usage"] for pos in order]
    parts = ax.violinplot(data, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS.get(order[idx], MUTED))
        body.set_alpha(0.58)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    ax.axhline(30, color=RED, linestyle="--", linewidth=1.2)
    ax.text(0.65, 30.6, "30% 高使用率参考线", color=RED, fontsize=9)
    ax.set_xticks(range(1, len(order) + 1), [{"Guard": "后卫", "Forward": "锋线", "Center": "中锋"}[pos] for pos in order])
    ax.set_title("使用率在不同位置的分布", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("Usage Rate")
    _strip_axes(ax)

    ax = axes[1]
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
    ax.set_title("同样高使用率，还要看效率能否撑住", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("Usage Rate / 使用率")
    ax.set_ylabel("TS% / 真实命中率")
    ax.legend(frameon=False, title="位置组")
    _strip_axes(ax)
    fig.suptitle("使用率：真实球员里谁在大量结束回合？", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "数据：surennba_stats；点大小约代表上场时间。")
    return save_figure(fig, _figure_path(output_dir, "04-usage-vs-efficiency.png"))


def build_turnover_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["tov_per36", "tov_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    order = _position_order(df)
    data = [df.loc[df["position_group"] == pos, "tov_pct_calc"] * 100 for pos in order]
    parts = ax.violinplot(data, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS.get(order[idx], MUTED))
        body.set_alpha(0.58)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    ax.set_xticks(range(1, len(order) + 1), [{"Guard": "后卫", "Forward": "锋线", "Center": "中锋"}[pos] for pos in order])
    ax.set_title("不同位置的 TOV% 分布", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("估算失误率 TOV%")
    _strip_axes(ax)

    ax = axes[1]
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
    label_df = pd.concat([df.nlargest(4, "tov_pct_calc"), df.nlargest(4, "tov_per36")]).drop_duplicates()
    for _, row in label_df.iterrows():
        ax.text(row["tov_per36"] + 0.03, row["tov_pct_calc"] * 100, row["name"], fontsize=8, color=INK)
    ax.set_title("失误数和失误率不是同一个问题", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("失误 / 36 分钟")
    ax.set_ylabel("估算失误率 TOV%")
    ax.legend(frameon=False, title="位置组")
    _strip_axes(ax)
    fig.suptitle("失误率：把失误放回使用机会里理解", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "TOV% = TOV / (FGA + 0.44 * FTA + TOV)。")
    return save_figure(fig, _figure_path(output_dir, "05-turnover-rate.png"))


def build_rebound_rate_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["rebounds_per36", "offrebounds", "defrebounds"]).copy()
    df = df[df["minutes"] >= 500]
    order = _position_order(df)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    data = [df.loc[df["position_group"] == pos, "rebounds_per36"] for pos in order]
    parts = ax.violinplot(data, showmeans=False, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS[order[idx]])
        body.set_alpha(0.55)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    for idx, values in enumerate(data, start=1):
        x = np.full(len(values), idx) + np.linspace(-0.05, 0.05, len(values))
        ax.scatter(x, values, color=INK, s=18, alpha=0.55)
    ax.set_xticks(range(1, len(order) + 1), [{"Guard": "后卫", "Forward": "锋线", "Center": "中锋"}[pos] for pos in order])
    ax.set_title("每 36 分钟篮板：先消除上场时间", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("篮板 / 36 分钟")
    _strip_axes(ax)

    ax = axes[1]
    if {"offfgreboundpct", "deffgreboundpct"}.issubset(df.columns):
        for position, group in df.groupby("position_group"):
            ax.scatter(
                group["offfgreboundpct"] * 100,
                group["deffgreboundpct"] * 100,
                s=np.clip(group["minutes"] / 12, 30, 180),
                alpha=0.74,
                color=POSITION_COLORS.get(position, MUTED),
                label=position,
                edgecolor="white",
                linewidth=0.7,
            )
        label_df = df.nlargest(5, "rebounds_per36")
        for _, row in label_df.iterrows():
            ax.text(row["offfgreboundpct"] * 100 + 0.1, row["deffgreboundpct"] * 100, row["name"], fontsize=8, color=INK)
        ax.set_xlabel("进攻篮板机会占比（%）")
        ax.set_ylabel("防守篮板机会占比（%）")
        ax.legend(frameon=False, title="位置组")
    ax.set_title("真实篮板率：同位置职责差异更清楚", loc="left", fontsize=13, weight="bold")
    _strip_axes(ax)
    fig.suptitle("篮板率：从抢到几个，转向抢到多少机会", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "数据：surennba_stats 球员统计；右图使用表内投篮篮板率字段。")
    return save_figure(fig, _figure_path(output_dir, "06-rebound-role-distribution.png"))


def build_shooting_efficiency_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["efg_pct_calc", "ts_pct_calc", "fg3pct"]).copy()
    df = df[(df["minutes"] >= 500) & (df["fg3a"] >= 50)]
    summary = (
        df.groupby("position_group")[["fg3pct", "efg_pct_calc", "ts_pct_calc"]]
        .median()
        .reindex(["Guard", "Forward", "Center"])
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    x = np.arange(len(summary))
    width = 0.24
    ax.bar(x - width, summary["fg3pct"] * 100, width, label="3P%", color=BLUE)
    ax.bar(x, summary["efg_pct_calc"] * 100, width, label="eFG%", color=ACCENT)
    ax.bar(x + width, summary["ts_pct_calc"] * 100, width, label="TS%", color=GREEN)
    ax.set_xticks(x, ["后卫", "锋线", "中锋"])
    ax.set_title("按位置看三种效率的中位数", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("命中率 / 效率（%）")
    ax.legend(frameon=False, ncol=3)
    _strip_axes(ax)

    ax = axes[1]
    order = _position_order(df)
    data = [df.loc[df["position_group"] == pos, "ts_pct_calc"] * 100 for pos in order]
    parts = ax.violinplot(data, showmedians=True)
    for idx, body in enumerate(parts["bodies"]):
        body.set_facecolor(POSITION_COLORS.get(order[idx], MUTED))
        body.set_alpha(0.58)
        body.set_edgecolor("white")
    parts["cmedians"].set_color(INK)
    ax.set_xticks(range(1, len(order) + 1), [{"Guard": "后卫", "Forward": "锋线", "Center": "中锋"}[pos] for pos in order])
    ax.set_title("TS% 分布：效率不是只看三分准度", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("TS%")
    _strip_axes(ax)
    fig.suptitle("投篮效率：FG%、eFG%、TS%各自修正了什么？", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "数据：surennba_stats；过滤：500+ 分钟且 50+ 三分出手。")
    return save_figure(fig, _figure_path(output_dir, "07-shooting-efficiency.png"))


def build_three_point_volume_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["fg3a_per36", "fg3pct"]).copy()
    df = df[(df["minutes"] >= 500) & (df["fg3a"] >= 50)]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    ax.hist(df["fg3a_per36"], bins=18, color=PURPLE, alpha=0.82, edgecolor="white")
    ax.axvline(8, color=RED, linestyle="--", linewidth=1.3)
    ax.axvline(df["fg3a_per36"].median(), color=INK, linestyle="--", linewidth=1.1)
    ax.set_title("真实球员三分产量分布", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("三分出手 / 36 分钟")
    ax.set_ylabel("球员数量")
    _strip_axes(ax)

    ax = axes[1]
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
    ax.set_title("产量和准度要一起读", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("三分出手 / 36 分钟")
    ax.set_ylabel("三分命中率（%）")
    ax.legend(frameon=False, title="位置组")
    _strip_axes(ax)
    fig.suptitle("三分出手量：高产才会真正改变防守选择", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "点大小约代表赛季三分总出手。")
    return save_figure(fig, _figure_path(output_dir, "08-three-point-volume-efficiency.png"))


def build_role_map_chart(players: pd.DataFrame, output_dir: Path) -> Path:
    configure_matplotlib()
    df = players.dropna(subset=["usage", "fg3a_per36", "ts_pct_calc"]).copy()
    df = df[df["minutes"] >= 500]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
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
    _strip_axes(ax)

    ax = axes[1]
    role_df = pd.DataFrame(
        {
            "高使用+高三分": [(df["usage"].ge(df["usage"].median()) & df["fg3a_per36"].ge(8)).sum()],
            "高使用+低三分": [(df["usage"].ge(df["usage"].median()) & df["fg3a_per36"].lt(8)).sum()],
            "低使用+高三分": [(df["usage"].lt(df["usage"].median()) & df["fg3a_per36"].ge(8)).sum()],
            "低使用+低三分": [(df["usage"].lt(df["usage"].median()) & df["fg3a_per36"].lt(8)).sum()],
        }
    ).T.reset_index()
    role_df.columns = ["角色区域", "球员数"]
    ax.barh(role_df["角色区域"], role_df["球员数"], color=[ACCENT, BLUE, PURPLE, GREEN])
    for idx, value in enumerate(role_df["球员数"]):
        ax.text(value + 0.3, idx, str(int(value)), va="center", color=INK)
    ax.set_title("把散点图切成四种角色区域", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("球员数量")
    ax.set_ylabel("")
    _strip_axes(ax)
    fig.suptitle("角色地图：使用率、空间产量和效率要一起读", x=0.01, ha="left", fontsize=16, weight="bold")
    add_source_note(fig, "横轴读回合终结，纵轴读空间参与，颜色读 TS%。")
    return save_figure(fig, _figure_path(output_dir, "09-player-role-map.png"))


def build_all_figures(players: pd.DataFrame, teams: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Build all static figures used by the textbook."""
    return [
        build_possessions_pace_chart(teams, output_dir),
        build_per36_three_point_chart(players, output_dir),
        build_four_factors_chart(teams, output_dir),
        build_usage_efficiency_chart(players, output_dir),
        build_turnover_chart(players, output_dir),
        build_rebound_rate_chart(players, output_dir),
        build_shooting_efficiency_chart(players, output_dir),
        build_three_point_volume_chart(players, output_dir),
        build_role_map_chart(players, output_dir),
    ]
