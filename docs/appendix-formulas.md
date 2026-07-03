# 公式附录

本页集中整理教材中出现的基础公式。所有实现都位于 [`src/nba_textbook/metrics.py`](../src/nba_textbook/metrics.py)。

## 回合

$$
POSS = FGA + 0.44 \times FTA - OREB + TOV
$$

读法：估算球队拥有了多少次进攻机会。进攻篮板会延长回合，所以要减去。

## 节奏

$$
PACE = \frac{POSS \times 48}{MIN}
$$

读法：每 48 分钟大约有多少回合。

## 每 36 分钟

$$
STAT\_{per36} = \frac{STAT}{MIN} \times 36
$$

读法：消除出场时间差异后的生产频率。不能单独当作主力预测。

## 每 100 回合

$$
STAT\_{per100} = \frac{STAT}{POSS} \times 100
$$

读法：消除球队节奏差异后的回合产出。

## eFG%

$$
eFG\% = \frac{FGM + 0.5 \times 3PM}{FGA}
$$

读法：修正三分额外价值后的投篮效率。

## TS%

$$
TS\% = \frac{PTS}{2 \times (FGA + 0.44 \times FTA)}
$$

读法：把投篮和罚球都纳入的整体得分效率。

## TOV%

$$
TOV\% = \frac{TOV}{FGA + 0.44 \times FTA + TOV}
$$

读法：进攻机会中有多少比例以失误结束。

## ORB%

$$
ORB\% = \frac{ORB}{ORB + OppDRB}
$$

读法：本队投丢后的可抢篮板里，抢回了多少。

## DRB%

$$
DRB\% = \frac{DRB}{DRB + OppORB}
$$

读法：对手投丢后的可抢篮板里，保护了多少。

## FT/FGA

$$
FT/FGA = \frac{FTM}{FGA}
$$

读法：每次投篮出手对应多少罚球命中，粗略代表罚球收益。

## Usage Rate

$$
USG\% =
100 \times
\frac{(FGA + 0.44 \times FTA + TOV) \times TeamMinutes}
{(TeamFGA + 0.44 \times TeamFTA + TeamTOV) \times PlayerMinutes}
$$

读法：球员在场时，球队有多少回合由他用投篮、罚球或失误结束。

## 常见误读速查

| 指标 | 容易误读 | 更好的读法 |
| --- | --- | --- |
| 场均得分 | 得分高就是进攻好 | 先看回合和效率 |
| per36 | 替补 per36 高就能当主力 | 只说明当前角色下的频率 |
| 使用率 | 等于持球时间 | 表示回合终结比例 |
| 失误数 | 失误多就是不稳 | 要结合使用机会和传球任务 |
| 篮板数 | 篮板多就是篮板能力强 | 要看可抢篮板机会和位置职责 |
| FG% | 命中率高就是效率高 | 三分和罚球要看 eFG%、TS% |
| 三分命中率 | 准就有空间价值 | 还要看产量、出手速度和防守尊重 |
