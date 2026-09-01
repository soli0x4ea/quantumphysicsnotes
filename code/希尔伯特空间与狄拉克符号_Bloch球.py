# -*- coding: utf-8 -*-
"""
希尔伯特空间与狄拉克符号_Bloch球.py
对应笔记：希尔伯特空间与狄拉克符号_系统笔记.md, 式 (6.1)
绘制两能级系统（2 维复 Hilbert 空间）的归一化态
  |psi> = cos(theta/2)|0> + exp(i phi) sin(theta/2)|1>
在 Bloch 球上的态矢量，并显示 |alpha|^2, |beta|^2 与相对相位。

运行（隔离 venv）：
  ~/.workbuddy/binaries/python/envs/default/bin/python code/希尔伯特空间与狄拉克符号_Bloch球.py

依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ---- 参数（示例叠加态） ----
theta = np.pi / 3.0   # 极角
phi = np.pi / 4.0     # 相对相位

alpha = np.cos(theta / 2.0)
beta = np.exp(1j * phi) * np.sin(theta / 2.0)
p0 = np.abs(alpha) ** 2
p1 = np.abs(beta) ** 2
print(f"|alpha|^2 = {p0:.4f}  |beta|^2 = {p1:.4f}  (sum = {p0+p1:.4f})")
print(f"relative phase phi = {phi:.4f} rad")

# Bloch 矢量
bx = np.sin(theta) * np.cos(phi)
by = np.sin(theta) * np.sin(phi)
bz = np.cos(theta)
print(f"Bloch vector = ({bx:.4f}, {by:.4f}, {bz:.4f})  |b| = {np.sqrt(bx**2+by**2+bz**2):.4f}")

# ---- 绘图 ----
fig = plt.figure(figsize=(6.0, 6.0))
ax = fig.add_subplot(111, projection="3d")

# 单位球
u = np.linspace(0, 2 * np.pi, 60)
v = np.linspace(0, np.pi, 40)
X = np.outer(np.cos(u), np.sin(v))
Y = np.outer(np.sin(u), np.sin(v))
Z = np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_wireframe(X, Y, Z, color="#cccccc", alpha=0.35, rstride=4, cstride=4)

# 坐标轴
ax.plot([-1.2, 1.2], [0, 0], [0, 0], color="#888888", lw=0.8)
ax.plot([0, 0], [-1.2, 1.2], [0, 0], color="#888888", lw=0.8)
ax.plot([0, 0], [0, 0], [-1.2, 1.2], color="#888888", lw=0.8)
ax.text(1.3, 0, 0, "x", color="#444444")
ax.text(0, 1.3, 0, "y", color="#444444")
ax.text(0, 0, 1.3, "z", color="#444444")

# 基矢 |0>, |1>
ax.scatter([0], [0], [1], color="#1f4e79", s=40, label="|0> (z=+1)")
ax.scatter([0], [0], [-1], color="#c0392b", s=40, label="|1> (z=-1)")

# 态矢量
ax.quiver(0, 0, 0, bx, by, bz, color="#2e7d32", arrow_length_ratio=0.12, lw=2.5)
ax.scatter([bx], [by], [bz], color="#2e7d32", s=50)

ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.set_zlim(-1.2, 1.2)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title("Bloch sphere: 2-dim Hilbert space state")
ax.legend(loc="upper left", fontsize=8)

fig.tight_layout()
out = "figures/希尔伯特空间与狄拉克符号_Bloch球.svg"
fig.savefig(out, format="svg", dpi=120)
print(f"Saved figure: {out}")
