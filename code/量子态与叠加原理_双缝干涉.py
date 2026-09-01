# -*- coding: utf-8 -*-
"""
量子态与叠加原理_双缝干涉.py
对应笔记：量子态与叠加原理_系统笔记.md, 式 (6.1)
计算并绘制双缝干涉强度分布 I(x) = 4 I0 cos^2(pi d x / (lambda L))
验证条纹间距 dx = lambda L / d 与 de Broglie 波长、缝距、屏距的关系。

运行（隔离 venv）：
  ~/.workbuddy/binaries/python/envs/default/bin/python code/量子态与叠加原理_双缝干涉.py

依赖：numpy, matplotlib（已装于隔离 venv）
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 无显示环境
import matplotlib.pyplot as plt

# ---- 物理常数 (CODATA 2018/2022) ----
H = 6.62607015e-34        # J·s 普朗克常数（精确值）
M_E = 9.1093837015e-31    # kg 电子质量

# ---- 实验参数（示例：100 eV 电子双缝） ----
E_eV = 100.0              # 电子动能 (eV)
E_J = E_eV * 1.602176634e-19  # 转焦耳
p = np.sqrt(2.0 * M_E * E_J)  # 非相对论动量
lam = H / p               # de Broglie 波长 (m)
d = 1.0e-7               # 缝距 (m) = 100 nm
L = 1.0                  # 屏距 (m) = 1 m
I0 = 1.0

# ---- 计算 ----
x = np.linspace(-0.02, 0.02, 4000)   # 屏上位置 -2cm .. 2cm
phase = np.pi * d * x / (lam * L)
I = 4.0 * I0 * np.cos(phase) ** 2
dx_fringe = lam * L / d               # 条纹间距 (m)

print(f"de Broglie wavelength (100 eV e-) = {lam*1e10:.3f} Angstrom")
print(f"fringe spacing dx = lambda L / d = {dx_fringe*1e3:.3f} mm")
print(f"max intensity = {I.max():.3f}, min intensity = {I.min():.3f}")

# ---- 绘图（英文标签，规避中文渲染乱码） ----
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.plot(x * 1e3, I, color="#1f4e79", linewidth=1.4)
ax.set_xlabel("Screen position x (mm)")
ax.set_ylabel("Relative intensity I(x) / I0")
ax.set_title("Two-slit interference: I(x)=4 I0 cos^2(pi d x / (lambda L))")
ax.set_ylim(-0.05 * I0, 4.2 * I0)
ax.grid(True, alpha=0.3)
ax.annotate(f"fringe spacing dx = {dx_fringe*1e3:.2f} mm",
            xy=(0.04, 3.6), xycoords="axes fraction",
            fontsize=9, color="#444444")
fig.tight_layout()
out = "figures/量子态与叠加原理_双缝干涉.svg"
fig.savefig(out, format="svg", dpi=120)
print(f"Saved figure: {out}")
