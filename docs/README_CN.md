# ZZZ_Calculator

[English](README.md) | 中文

## 简介

`ZZZ_Calculator` 是一个基于网页的《绝区零》伤害计算器。它提供了一个用户友好的界面来计算队伍组合的总伤害输出，考虑了每个角色的武器和装备特性。然后，它会根据预设的APL (Action Priority List)，自动模拟队伍中角色的出招顺序，自动触发Buff，并自动记录与分析结果，生成可视化的图表。

## 功能

- 基于队伍组合计算总伤害
- 根据APL模拟计算伤害输出
- 绘制可视化图表
- 提供每个角色的详细伤害信息

## 使用方法

将仓库克隆到本地目录。

```bash
git clone https://github.com/Steinwaysj/ZZZ_Calculator.git
```

安装依赖项。项目兼容Python 3.12或更高版本。

```bash
pip install -r requirements.txt
```

然后运行网页界面。

```bash
run
```

命令行版本也可用(至少目前)。

```bash
python main.py
```

*实验性功能:*

*如果你想编译C/C++扩展模块，可以使用以下命令。
确保已安装C编译器。*

```bash
python setup.py build_ext --inplace
```

## 待办事项

查看issues获取更多详情。
