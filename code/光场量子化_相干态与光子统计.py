# -*- coding: utf-8 -*-
"""
光场量子化与相干态 —— 脚本1：相干态与热态光子数分布
对应笔记：第35篇《光场量子化与相干态》
公式编号：式(8) 相干态光子数分布 P(n)=e^{-|alpha|^2}|alpha|^{2n}/n!  (Poisson)
         式(9) 同均值热态(玻色-爱因斯坦)分布 P(n)=(1+mu)^-1 (mu/(1+mu))^n
运行：/Users/soli/.workbuddy/binaries/python/envs/default/bin/python 光场量子化_相干态与光子统计.py
依赖：numpy, matplotlib (Agg 后端保存 SVG)；禁止 scipy 及其他第三方库
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 参数 ----
mu = 5.0          # 平均光子数 |alpha|^2 = 5
# 计算统计用量程需足够大（热态长尾，方差=mu(1+mu)=30，故取到 120 以保证归一化与矩收敛）
nmax = 120
n = np.arange(0, nmax + 1)

# 阶乘数组（不使用 scipy.special.factorial；nmax=120 远小于双精度上限 ~170，不会溢出）
fact = np.empty(nmax + 1)
fact[0] = 1.0
for i in range(1, nmax + 1):
    fact[i] = fact[i - 1] * i

# 相干态：泊松分布  P_coh(n) = e^{-mu} mu^n / n!
P_coh = np.exp(-mu) * (mu ** n) / fact

# 热态（玻色-爱因斯坦）同均值 mu：P_th(n) = (1+mu)^-1 (mu/(1+mu))^n
q = mu / (1.0 + mu)
P_th = (1.0 / (1.0 + mu)) * (q ** n)

# 归一化检查
print("sum coherent = %.10f  sum thermal = %.10f" % (P_coh.sum(), P_th.sum()))

# 均值与方差
mean_coh = np.sum(n * P_coh)
var_coh = np.sum(n * n * P_coh) - mean_coh ** 2
mean_th = np.sum(n * P_th)
var_th = np.sum(n * n * P_th) - mean_th ** 2
print("Coherent (mu=5): mean=%.6f  var=%.6f  (Poisson => mean=var=5)" % (mean_coh, var_coh))
print("Thermal  (mu=5): mean=%.6f  var=%.6f" % (mean_th, var_th))

# ---- 绘图（SVG 内文字全部英文）----
# 显示窗口：两种分布在 n<=25 之外已可忽略，聚焦绘制以避免横轴过长
n_show = np.arange(0, 26)
P_coh_show = P_coh[:26]
P_th_show = P_th[:26]

fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))

axes[0].bar(n_show, P_coh_show, color="#2c7fb8", width=0.82)
axes[0].set_title("Coherent state |alpha|^2 = 5 (Poisson)")
axes[0].set_xlabel("Photon number n")
axes[0].set_ylabel("Probability P(n)")

axes[1].bar(n_show, P_th_show, color="#d95f0e", width=0.82)
axes[1].set_title("Thermal state (mean 5, Bose-Einstein)")
axes[1].set_xlabel("Photon number n")
axes[1].set_ylabel("Probability P(n)")

fig.tight_layout()

# 保存到 figures/ 目录（相对脚本位置 ../figures）
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(os.path.dirname(HERE), "figures")
os.makedirs(FIGDIR, exist_ok=True)
out = os.path.join(FIGDIR, "光场量子化_相干态光子数.svg")
fig.savefig(out)
print("Saved:", out)
