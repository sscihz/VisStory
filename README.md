# 中文 NBA 基础数据思维教材

这个仓库是一套中文、可复现的 NBA 基础数据思维教材。它面向普通 NBA 球迷和初级数据分析读者，目标不是堆公式，而是解释现代篮球数据到底在回答什么篮球问题。

教材会从回合、节奏、每 36 分钟、每 100 回合、Four Factors、使用率、失误率、篮板率、eFG%、TS%、三分出手结构等基本概念开始。每章都配套 Python 源代码和图表，并用 Austin Reaves 作为贯穿案例，先看全联盟分布，再看同位置分布，最后单独看球队语境，帮助读者把“36 分钟出手 8 次三分”“使用率 30%”“失误率 12%”这类数字转化成可理解的篮球语言。

## 数据与参考

- 数据抓取参考：[suren-nba/surennba_stats](https://github.com/suren-nba/surennba_stats)，默认使用 `2025-26` 常规赛单赛季全量球员统计和球队统计
- 基础概念参考：Dean Oliver 的 `Basketball on Paper`、Basketball-Reference 的 Four Factors 解释、`A Starting Point for Analyzing Basketball Statistics`
- 代码型教材参考：[basketballrelativity/basketball_data_science](https://github.com/basketballrelativity/basketball_data_science)
- 指标函数参考：[hoopR Basketball Analytics Utilities](https://hoopr.sportsdataverse.org/reference/index.html)

## 本地运行

如果需要生成中文图表，建议系统安装 Noto CJK 字体：

```bash
sudo apt-get install fonts-noto-cjk
```

```bash
python -m pip install -e ".[dev]"
python scripts/build_figures.py
mkdocs serve
```

运行测试：

```bash
pytest
```

## 教材目录

教材正文位于 [`docs/`](docs/)：

1. 回合与节奏
2. 总量、每 36 分钟、每 100 回合
3. Four Factors
4. 使用率/回合占有率
5. 失误率
6. 篮板率
7. 投篮效率
8. 三分出手量
9. 用指标阅读球员角色

图表生成代码位于 [`src/nba_textbook/`](src/nba_textbook/) 和 [`scripts/build_figures.py`](scripts/build_figures.py)。
