# 中文 NBA 基础数据思维教材

这是一套面向 NBA 球迷和初级数据分析读者的中文教材。它想回答的问题不是“某个指标怎么算”，而是：

- 为什么现代篮球分析总是从“回合”开始？
- 为什么同样场均 20 分，可能代表完全不同的进攻价值？
- 为什么 36 分钟出手 8 次三分已经是很强的空间参与？
- 为什么使用率、失误率、篮板率比简单的出手数、失误数、篮板数更适合比较球员？

教材中的图表由 Python 代码生成，数据优先来自 [suren-nba/surennba_stats](https://github.com/suren-nba/surennba_stats) 的 `2025-26` 常规赛单赛季全量球员表和球队表。如果网络不可用，代码会使用内置小样例，保证教材仍然可以构建。

## 学习路线

1. **先理解回合**：把比赛从 48 分钟切成一段段进攻机会。
2. **再理解归一化**：每 36 分钟、每 100 回合解决“出场时间”和“节奏”问题。
3. **学习 Four Factors**：把赢球拆成投篮、失误、篮板、罚球。
4. **阅读球员角色**：用使用率、效率、失误率、篮板率和出手结构判断球员在球队里做什么。

## 统一读图方法

本教材现在用 Austin Reaves 作为贯穿案例。选择他不是因为他是联盟最极端的样本，而是因为他很适合练习“中高使用外线球员该怎么读”：他有持球、有投射、有造罚球，也会受到队内核心和球队空间的影响。

每个球员指标都先看全联盟分布，再看同位置分布，最后把湖人队内语境单独拆出来。这个顺序的目的不是给球员排座次，而是先回答三个基础问题：

1. 这个数字在 NBA 轮换球员里稀不稀缺？
2. 放到同位置职责里，它还稀不稀缺？
3. 回到球队内部，他承担的是第几层任务？

球队概念，如节奏和 Four Factors，则使用球队数据另行画图，不和个人指标混读。读完这套路线后，你应该能把一个球员的单项数据翻译成“角色、频率、效率、风险和球队语境”的组合判断。

## 运行代码

```bash
python -m pip install -e ".[dev]"
python scripts/build_figures.py
mkdocs serve
```

所有公式函数在 `src/nba_textbook/metrics.py`，所有图表函数在 `src/nba_textbook/charts.py`。

## 参考脉络

这套教材主要吸收以下资料的思想：

- Dean Oliver 的 `Basketball on Paper`：回合制思维和 Four Factors。
- Basketball-Reference 的 Four Factors 说明：公开、清晰的公式定义。
- `A Starting Point for Analyzing Basketball Statistics`：入门级 possession、pace、rating 框架。
- `basketballrelativity/basketball_data_science`：用 Python/Notebook 写篮球数据教材的组织方式。
- `hoopR`：指标函数体系与命名参考。
