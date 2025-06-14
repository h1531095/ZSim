import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['HarmonyOS Sans SC', 'Microsoft YaHei']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def plot_skill_distribution(theta=90, T_A_base=273, c=0.8, Lp=1, ax=None):
    """
    基于对数正态分布的玩家水平模型
    参数:
        theta: 基础反应时间 (ms)
        T_A: 中位数反应时间 (ms)
        c: 波动系数
        Lp: 玩家水平 (1~5)
        ax: 绘图坐标系
    """
    delta = 32  # 每级水平中位数变化量(ms)
    T_A = T_A_base + delta * (2.5 - Lp)

    # 方差控制公式
    sigma = c / (Lp ** 0.38)  # 高水平玩家波动更小
    mu = np.log(T_A - theta) - (sigma ** 2) / 2  # 保持中位数=T_A

    # 生成对数正态分布
    scale = np.exp(mu)
    dist = lognorm(s=sigma, scale=scale)

    # 生成反应时间轴
    rt_min = theta + 1
    rt_max = theta + int(3 * (T_A - theta))  # 自适应显示范围
    x = np.linspace(rt_min, rt_max, 500)
    pdf_values = dist.pdf(x - theta)  # PDF值

    # 绘图处理
    ax = ax or plt.gca()
    line = ax.plot(x, pdf_values, label=f'Lv{Lp} (σ={sigma:.2f})，Lp={Lp}')

    # 标注关键指标
    median = theta + dist.median()
    p250 = dist.cdf(250 - theta)
    ax.text(250, np.max(pdf_values) * 0.8,
            f'P250={p250:.1%}',
            color=line[0].get_color(),
            ha='center')

    # 添加中位线
    ax.axvline(median, color=line[0].get_color(),
               linestyle=':', alpha=0.5)
    return ax


# 使用示例
fig, ax = plt.subplots(figsize=(10, 6))
for Lp in range(1, 6):
    plot_skill_distribution(T_A_base=273, c=0.5, Lp=Lp, ax=ax)
ax.set_title('玩家反应时间分布 (大数据中位数273ms)')
ax.legend()
plt.show()
