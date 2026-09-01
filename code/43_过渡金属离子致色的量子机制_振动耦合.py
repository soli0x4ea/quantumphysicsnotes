# -*- coding: utf-8 -*-
"""
43_过渡金属离子致色的量子机制_振动耦合.py

对应笔记：第 43 篇《过渡金属离子致色的量子机制》第六节。
主题：Laporte 宇称禁戒的 d-d 跃迁，靠奇宇称振动（vibronic coupling）弛豫获得微弱强度。
      以无量纲振动耦合强度 ξ 为自变量，给出相对强度 I(ξ) 的示意模型，
      并演示用 numpy 2.x 的 np.trapezoid 对强度曲线积分（获得累积极化耦合强度）。

依赖：仅 numpy + matplotlib（禁用 scipy）。
运行环境：~/.workbuddy/binaries/python/envs/default/bin/python
生成：figures/43_过渡金属离子致色的量子机制_图2.svg
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---- 模型 ----
# 宇称禁戒的 d-d 跃迁本征偶极矩 ~ 0；奇宇称振动（eg / T1u 模式）瞬时打破反演对称，
# 混入少量 u 成分，使有效跃迁矩 ~ ξ（ξ = 奇宇称振动耦合幅度的无量纲度量）。
# 于是相对强度 I ∝ |μ_eff|^2 ∝ ξ^2（小 ξ）；大 ξ 时趋于饱和（受限于态密度/寿命）。
# 这里采用归一化饱和形式：I(ξ) = ξ^2 / (ξ^2 + ξ0^2)，ξ0 为半强度耦合常数。
XI0 = 0.5  # 半强度常数（无量纲，示意值）

def relative_intensity(xi):
    return xi**2 / (xi**2 + XI0**2)

xi = np.linspace(0.0, 3.0, 600)
I = relative_intensity(xi)

# numpy 2.x 用 np.trapezoid（旧 np.trapz 已弃用）对强度曲线积分
area = np.trapezoid(I, xi)
print("=== d-d 跃迁相对强度随振动耦合参数 ξ 的变化（示意模型）===")
print(f"半强度耦合常数 ξ0 = {XI0}")
print(f"ξ=0.1 -> I={relative_intensity(0.1):.4f}")
print(f"ξ=0.5 -> I={relative_intensity(0.5):.4f}  (半强度)")
print(f"ξ=1.0 -> I={relative_intensity(1.0):.4f}")
print(f"ξ=3.0 -> I={relative_intensity(3.0):.4f}  (近饱和)")
print(f"∫ I(ξ) dξ (ξ∈[0,3]) = {area:.3f}   [np.trapezoid 积分]")

# ---- 作图 ----
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(xi, I, color="#1f4e79", lw=2.2, label=r"$I(\xi)=\xi^2/(\xi^2+\xi_0^2)$")
ax.axhline(0.5, color="gray", ls="--", lw=1.0)
ax.annotate(r"$I=0.5$ at $\xi=\xi_0$", (XI0, 0.5), textcoords="offset points",
            xytext=(6, 6), fontsize=9, color="gray")
ax.fill_between(xi, 0, I, color="#a9c7e8", alpha=0.5)
# 标注典型 d-d 与电荷转移强度区间（示意）
ax.axhspan(0.0, 0.02, color="#f9c6c6", alpha=0.25)
ax.text(2.4, 0.01, "d-d (weak,\nε~1–100)", fontsize=8, color="#b03a2e", ha="center")
ax.axhspan(0.6, 1.0, color="#c6e0c6", alpha=0.25)
ax.text(2.4, 0.85, "charge-transfer\nregime (strong,\nε~10^3–10^4)",
        fontsize=8, color="#1e7d34", ha="center")

ax.set_xlabel(r"Odd-parity vibronic coupling strength  $\xi$  (dimensionless, illustrative)")
ax.set_ylabel(r"Relative d-d transition intensity  $I(\xi)$")
ax.set_title("Schematic d-d intensity versus vibronic coupling strength")
ax.set_ylim(-0.03, 1.05)
ax.grid(True, ls=":", alpha=0.6)
ax.legend(loc="lower right", fontsize=9)

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)
OUT = os.path.join(FIGDIR, "43_过渡金属离子致色的量子机制_图2.svg")
fig.savefig(OUT, format="svg", bbox_inches="tight")
print(f"\n图已写出：{OUT}")
