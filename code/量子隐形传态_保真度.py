# -*- coding: utf-8 -*-
"""
量子隐形传态_保真度.py
对应篇目: 第33篇《量子隐形传态与密集编码》系统量子力学笔记
对应公式: 第二节式(7) 平均传态保真度 F(p) = (p + 1)/2
           （p 为共享信道的 Bell 权重 / Werner 态极化参数，见下）

物理模型
--------
Alice 与 Bob 预先共享一个两量子比特资源态
    rho(p) = p |Phi+><Phi+| + (1 - p) * I/4 ,   p in [0, 1]
其中 |Phi+> = (|00> + |11>)/sqrt(2) 是理想贝尔资源态，I/4 为最大混合态。
该态与理想贝尔态的重叠(单态分数)为  f = <Phi+|rho|Phi+> = (3p + 1)/4。

标准隐形传态协议下，对任意纯输入态的平均保真度为（见 Horodecki et al.
关于可分判据 / 单态分数与传态保真度关系的结论，PRL 1999；Bennett et al. 1996
纠缠纯化）：
    F(f) = (2 f + 1) / 3

代入 f = (3p + 1)/4 得
    F(p) = (2*(3p+1)/4 + 1)/3 = ( (3p+1)/2 + 1 )/3 = (3p+3)/6 = (p + 1)/2

关键点:
- p = 1   (纯贝尔态)        -> F = 1        （完美传态）
- p = 1/3 (f = 1/2, 可分边界) -> F = 2/3      （经典极限，任何可分/经典信道上限）
- p = 0   (最大混合 I/4)     -> F = 1/2

脚本绘制 F(p) 随 Bell 权重 p 的变化，并标出经典极限水平线 F = 2/3。
所有文字使用英文，避免 SVG 中文渲染乱码；文件名使用中文。
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 参数 ----
p = np.linspace(0.0, 1.0, 401)          # Bell 权重 / Werner 极化参数
f = (3.0 * p + 1.0) / 4.0               # 单态(贝尔)分数
F = (2.0 * f + 1.0) / 3.0               # 平均传态保真度 = (p + 1)/2

# 关键数值（回写正文）
F_perfect = F[p >= 1.0 - 1e-9][-1] if np.any(p >= 1.0 - 1e-9) else 1.0
p_classical = 1.0 / 3.0
F_classical = (2.0 * 0.5 + 1.0) / 3.0   # = 2/3
F_mixed = (0.0 + 1.0) / 2.0             # p=0 -> 1/2

print("Quantum teleportation fidelity F(p)=(p+1)/2")
print("  p=1   (pure Bell)      F = %.6f" % F_perfect)
print("  p=1/3 (separable bound, f=1/2)  F = %.6f  (=2/3)" % F_classical)
print("  p=0   (maximally mixed I/4)     F = %.6f" % F_mixed)
print("  check F at p=1/3 = %.6f" % ((p_classical + 1.0) / 2.0))

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=120)
ax.plot(p, F, color="#1f5fa8", linewidth=2.4, label=r"$F(p) = (p+1)/2$")

# 经典极限水平线
ax.axhline(F_classical, color="#c0392b", linestyle="--", linewidth=1.6,
           label=r"classical limit $F = 2/3$")

# 完美极限水平线
ax.axhline(1.0, color="#2e7d32", linestyle=":", linewidth=1.4,
           label=r"perfect $F = 1$")

# 标注关键点
ax.plot(1.0, 1.0, "o", color="#2e7d32", markersize=7)
ax.plot(p_classical, F_classical, "o", color="#c0392b", markersize=7)
ax.annotate(r"$p=1,\ F=1$",
            xy=(1.0, 1.0), xytext=(0.62, 0.95),
            arrowprops=dict(arrowstyle="->", color="#2e7d32"), fontsize=11)
ax.annotate(r"$p=1/3,\ F=2/3$",
            xy=(p_classical, F_classical), xytext=(0.10, 0.74),
            arrowprops=dict(arrowstyle="->", color="#c0392b"), fontsize=11)

ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.45, 1.05)
ax.set_xlabel(r"Bell weight $p$ of shared channel $\rho(p)=p|\Phi^+\rangle\langle\Phi^+|+(1-p)I/4$", fontsize=11)
ax.set_ylabel(r"average teleportation fidelity $F$", fontsize=11)
ax.set_title("Quantum teleportation fidelity vs channel Bell weight", fontsize=12)
ax.legend(loc="lower right", fontsize=10)
ax.grid(True, alpha=0.3)

fig.tight_layout()
out = "/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子隐形传态_保真度.svg"
fig.savefig(out, format="svg")
print("Saved:", out)
