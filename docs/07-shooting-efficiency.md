# 07 投篮效率：FG%、eFG%、TS%

## 这个指标想解决什么问题

传统命中率 FG% 的问题是：它把两分和三分当成同一种命中。

一个球员 10 投 5 中：

- 如果 5 个全是两分，得到 10 分；
- 如果 5 个全是三分，得到 15 分。

FG% 都是 50%，但进攻价值完全不同。

![投篮效率指标](assets/figures/07-shooting-efficiency.svg)

![Austin Reaves TS% 分布](assets/figures/07-austin-ts-distribution.svg)

## FG%

$$
FG\% = \frac{FGM}{FGA}
$$

它回答“投篮进了多少比例”，但不区分两分和三分价值。

## eFG%

$$
eFG\% = \frac{FGM + 0.5 \times 3PM}{FGA}
$$

eFG% 把三分多出来的 1 分折算进命中率。命中一个三分相当于命中 1.5 个两分球的得分价值。

## TS%

$$
TS\% = \frac{PTS}{2 \times (FGA + 0.44 \times FTA)}
$$

TS% 进一步把罚球也纳入得分效率。它更适合评价整体终结效率，尤其是擅长造犯规的球员。

## 常见误读

**误读：FG% 低就是效率低。**

不一定。大量投三分的球员 FG% 往往不会特别高，但 eFG% 和 TS% 可能很好。反过来，一个只投近筐两分的球员 FG% 很高，也要看他有没有罚球、失误、空间价值和角色限制。

## Austin Reaves 案例：效率要和角色一起读

TS% 分布图回答的是“他把投篮和罚球机会转成得分的效率，在联盟里处在哪”。

1. **全联盟分布**：先看 Reaves 的 TS% 是高效、中位，还是低效。
2. **同位置分布**：后卫往往有更多持球投、急停和高难度出手，和同位置比较更公平。
3. **湖人队内语境**：队内点图能看出他相对队友是高效终结点，还是承担了更难的中等效率回合。

如果 TS% 靠右但使用率很低，可能是优秀终结点；如果 TS% 靠右且使用率也靠右，才更接近高价值主攻或二当家进攻角色。

## 代码入口

```python
from nba_textbook.metrics import effective_fg_pct, true_shooting_pct

efg = effective_fg_pct(fgm=8, fg3m=4, fga=16)
ts = true_shooting_pct(points=24, fga=16, fta=4)
```

## 读图结论

三分命中率只回答“远投准不准”。eFG% 回答“投篮出手的得分价值”。TS% 回答“所有投篮和罚球机会合起来的得分效率”。现代篮球评价得分手时，通常至少要同时看出手量和 TS%。
