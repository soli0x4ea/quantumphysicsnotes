# -*- coding: utf-8 -*-
"""
光场量子化与相干态 —— 脚本2：二阶相干度 g^(2)(0) 三态对比 + 压缩态 Wigner 函数
对应笔记：第35篇《光场量子化与相干态》
公式编号：式(12) g^(2)(0) = <n(n-1)> / <n>^2
          相干态=1、热态=2、单模 Fock(n=1)=0
          压缩真空 Wigner W(x,p)=(1/pi) exp(-x^2 e^{2r} - p^2 e^{-2r})
运行：/Users/soli/.workbuddy/binaries/python/envs/default/bin/python 光场量子化_二阶相干度.py
依赖：numpy, matplotlib (Agg 后端保存 SVG)；禁止 scipy 及其他第三方库
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============ 1) g^(2)(0) 三态对比 ============
mu = 5.0
# 计算矩用量程：泊松与热态在 n>120 之外质量可忽略；
# nmax=120 远小于双精度阶乘上限(~170)，避免 overflow 警告
nmax = 120
n = np.arange(0, nmax + 1)

# 阶乘数组
fact = np.empty(nmax + 1)
fact[0] = 1.0
for i in range(1, nmax + 1):
    fact[i] = fact[i - 1] * i

# 相干态（泊松）
Pc = np.exp(-mu) * (mu ** n) / fact
mean_c = np.sum(n * Pc)
mom2_c = np.sum(n * (n - 1) * Pc)   # <n(n-1)>
g2_coh = mom2_c / (mean_c ** 2)

# 热态（玻色-爱因斯坦）
q = mu / (1.0 + mu)
Pt = (1.0 / (1.0 + mu)) * (q ** n)
mean_t = np.sum(n * Pt)
mom2_t = np.sum(n * (n - 1) * Pt)
g2_th = mom2_t / (mean_t ** 2)

# 单模 Fock 态 |1>：<n(n-1)> = 0
g2_fock = 0.0

print("g^(2)(0): coherent=%.6f  thermal=%.6f  Fock(n=1)=%.6f" % (g2_coh, g2_th, g2_fock))

# ============ 2) 压缩真空 Wigner 函数 (r=1) ============
r = 1.0
xs = np.linspace(-3.0, 3.0, 320)
ps = np.linspace(-3.0, 3.0, 320)
X, P = np.meshgrid(xs, ps)
# 真空 Wigner = (1/pi) exp(-x^2 - p^2); 压缩真空沿 x 压缩 => x 方差减小
W = (1.0 / np.pi) * np.exp(-(X ** 2) * np.exp(2 * r) - (P ** 2) * np.exp(-2 * r))

# 1-sigma 等值线（指数 = -1）：x^2 e^{2r} + p^2 e^{-2r} = 1
contour_val = (1.0 / np.pi) * np.exp(-1.0)

# ============ 绘图 ============
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))

# 左：三态 g^(2)(0) 柱状图
labels = ["Coherent", "Thermal", "Fock (n=1)"]
vals = [g2_coh, g2_th, g2_fock]
colors = ["#2c7fb8", "#d95f0e", "#31a354"]
bars = axes[0].bar(labels, vals, color=colors)
axes[0].axhline(1.0, ls="--", color="black", lw=1.0)
axes[0].set_ylim(0, 2.4)
axes[0].set_ylabel(r"$g^{(2)}(0)$")
axes[0].set_title("Second-order coherence at zero delay")
for b, v in zip(bars, vals):
    axes[0].text(b.get_x() + b.get_width() / 2.0, v + 0.05, "%.2f" % v,
                 ha="center", va="bottom", fontsize=10)

# 右：压缩真空 Wigner 函数
cf = axes[1].contourf(X, P, W, levels=30, cmap="viridis")
axes[1].contour(X, P, W, levels=[contour_val], colors="white", linestyles="--", linewidths=1.2)
axes[1].set_xlabel("x (squeezed quadrature)")
axes[1].set_ylabel("p (anti-squeezed quadrature)")
axes[1].set_title("Wigner function of squeezed vacuum (r=1)")
cb = fig.colorbar(cf, ax=axes[1])
cb.set_label("W(x,p)")

fig.tight_layout()

# 保存到 figures/
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(os.path.dirname(HERE), "figures")
os.makedirs(FIGDIR, exist_ok=True)
out = os.path.join(FIGDIR, "光场量子化_二阶相干度.svg")
fig.savefig(out)
print("Saved:", out)
