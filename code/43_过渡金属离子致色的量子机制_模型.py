# -*- coding: utf-8 -*-
"""
43_过渡金属离子致色的量子机制_模型.py

对应笔记：第 43 篇《过渡金属离子致色的量子机制》（第六部分·交叉应用）。
公式：由晶体场分裂能量 Δ 反算吸收波长 λ = 10^7 / Δ(cm^-1)  [nm]，
      以及八面体 d 轨道在 Oh 场中的分裂 E(eg)=+6Dq, E(t2g)=-4Dq, Δ_o=10Dq。

依赖：仅 numpy + matplotlib（禁用 scipy）。
运行环境：~/.workbuddy/binaries/python/envs/default/bin/python
生成：figures/43_过渡金属离子致色的量子机制_图1.svg
"""

import os
import matplotlib
matplotlib.use("Agg")  # 无显示后端，便于服务器/沙箱运行
import matplotlib.pyplot as plt
import numpy as np
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- 物理常数（CODATA 2018；2019 SI 重新定义后 h、c、k_B 为精确值）----
H = C["h"]        # J·s   普朗克常数（精确）
C = C["c"]           # m/s   光速（精确）
HC_EV_NM = 1239.841984    # eV·nm = h*c 换算（精确，派生量）
NM_PER_CM = 1.0e7         # 1 cm = 1e7 nm（波数 <-> 波长换算用）

# 代表矿物的晶体场分裂 Δ_o（来源：Burns 1993；Nassau 1983。见笔记正文第八节）
# Δ 单位 cm^-1；ruby/emerald 为 Cr3+ 在八面体场中的 10Dq；peridot 为 Fe2+ 近红外主带（约 1050 nm）。
MINERALS = [
    ("Ruby (Cr3+ in Al2O3)",   18000.0),   # 红宝石：2.23 eV 量级（Nassau 1983）
    ("Emerald (Cr3+ in Be3Al2Si6O18)", 16500.0),  # 祖母绿：2.05 eV 量级
    ("Peridot (Fe2+ in olivine)", 9524.0),  # 橄榄石 Fe2+ 近红外主带 ~1050 nm
]

# 由 Δ(cm^-1) 计算吸收波长 λ(nm)
def delta_to_lambda_nm(delta_cm):
    return NM_PER_CM / delta_cm

print("=== 由晶体场分裂 Δ 反算吸收波长 λ = 10^7 / Δ(cm^-1) ===")
print(f"{'矿物 / 离子':<38}{'Δ (cm^-1)':>12}{'λ (nm)':>12}{'E (eV)':>10}")
for name, d in MINERALS:
    lam = delta_to_lambda_nm(d)
    ev = HC_EV_NM / lam
    print(f"{name:<38}{d:>12.1f}{lam:>12.1f}{ev:>10.3f}")

# ---- 八面体 d 轨道分裂核验（点电荷/简单晶体场结果）----
Dq = 1830.0  # cm^-1，ruby 量级（Rama Moorthy 1982 拟合 B=732, Dq=1830）
E_eg = 6.0 * Dq
E_t2g = -4.0 * Dq
delta_o = E_eg - E_t2g
bary = 2.0 * E_eg + 3.0 * E_t2g  # 质心守恒检验，应为 0
print("\n=== 八面体 Oh 场 d 轨道分裂核验 ===")
print(f"Dq = {Dq:.0f} cm^-1")
print(f"E(eg)  = +6Dq = {E_eg:.0f} cm^-1")
print(f"E(t2g) = -4Dq = {E_t2g:.0f} cm^-1")
print(f"Δ_o = E(eg)-E(t2g) = 10Dq = {delta_o:.0f} cm^-1")
print(f"质心检验 2*E(eg)+3*E(t2g) = {bary:.0f}  (应=0)")
print(f"对应吸收波长 λ = 10^7/{delta_o:.0f} = {NM_PER_CM/delta_o:.1f} nm")

# ---- 作图：λ 随 Δ 的变化（反比关系）并标注代表点 ----
fig, ax = plt.subplots(figsize=(7.2, 4.6))
delta_grid = np.linspace(5000.0, 25000.0, 400)
lam_grid = NM_PER_CM / delta_grid
ax.plot(delta_grid, lam_grid, color="#1f4e79", lw=2.0, label=r"$\lambda = 10^7 / \Delta$  (nm)")

colors = ["#c0392b", "#1e7d34", "#8e6f00"]
for (name, d), col in zip(MINERALS, colors):
    lam = NM_PER_CM / d
    ax.scatter([d], [lam], s=70, color=col, zorder=5, edgecolor="black")
    short = name.split(" (")[0]
    ax.annotate(f"{short}\nΔ={d/1000:.1f}k cm⁻¹\nλ={lam:.0f} nm",
                (d, lam), textcoords="offset points", xytext=(8, -22),
                fontsize=9, color=col)

ax.axvspan(12820, 25000, color="#ffe0b2", alpha=0.35)  # 可见光 400-780 nm 对应 Δ≈12820-25000 cm^-1
ax.set_xlabel(r"Crystal-field splitting  $\Delta$  (cm$^{-1}$)")
ax.set_ylabel(r"Absorption wavelength  $\lambda$  (nm)")
ax.set_title("Absorption wavelength versus crystal-field splitting for gem chromophores")
ax.invert_yaxis()  # Δ 越大 -> λ 越短（越偏蓝/紫），符合视觉直觉
ax.grid(True, ls=":", alpha=0.6)
ax.legend(loc="upper right", fontsize=9)
ax.text(0.02, 0.04, "Visible band shaded (≈400–780 nm)", transform=ax.transAxes,
        fontsize=8, color="#a35a00")

# 输出到 figures/ （相对脚本位置）
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)
OUT = os.path.join(FIGDIR, "43_过渡金属离子致色的量子机制_图1.svg")
fig.savefig(OUT, format="svg", bbox_inches="tight")
print(f"\n图已写出：{OUT}")
