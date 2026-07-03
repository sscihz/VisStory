# 中文 NBA 基础数据思维教材

这是一套面向 NBA 球迷和初级数据分析读者的中文教材。它想回答的问题不是“某个指标怎么算”，而是：

- 为什么现代篮球分析总是从“回合”开始？
- 为什么同样场均 20 分，可能代表完全不同的进攻价值？
- 为什么 36 分钟出手 8 次三分已经是很强的空间参与？
- 为什么使用率、失误率、篮板率比简单的出手数、失误数、篮板数更适合比较球员？

教材中的图表由 Python 代码生成，数据优先来自 [suren-nba/surennba_stats](https://github.com/suren-nba/surennba_stats)。如果网络不可用，代码会使用内置小样例，保证教材仍然可以构建。

## 学习路线

1. **先理解回合**：把比赛从 48 分钟切成一段段进攻机会。
2. **再理解归一化**：每 36 分钟、每 100 回合解决“出场时间”和“节奏”问题。
3. **学习 Four Factors**：把赢球拆成投篮、失误、篮板、罚球。
4. **阅读球员角色**：用使用率、效率、失误率、篮板率和出手结构判断球员在球队里做什么。

## 运行代码

```bash
python -m pip install -e ".[dev]"
python scripts/build_figures.py
mkdocs serve
```

所有公式函数在 [`src/nba_textbook/metrics.py`](../src/nba_textbook/metrics.py)，所有图表函数在 [`src/nba_textbook/charts.py`](../src/nba_textbook/charts.py)。

## 参考脉络

这套教材主要吸收以下资料的思想：

- Dean Oliver 的 `Basketball on Paper`：回合制思维和 Four Factors。
- Basketball-Reference 的 Four Factors 说明：公开、清晰的公式定义。
- `A Starting Point for Analyzing Basketball Statistics`：入门级 possession、pace、rating 框架。
- `basketballrelativity/basketball_data_science`：用 Python/Notebook 写篮球数据教材的组织方式。
- `hoopR`：指标函数体系与命名参考。
