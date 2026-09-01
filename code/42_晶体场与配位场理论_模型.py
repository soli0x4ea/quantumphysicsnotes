# -*- coding: utf-8 -*-
# 对应篇名：第42篇《晶体场与配位场理论》（Crystal Field and Ligand Field Theory）
# 模型：d5 离子在 O_h 八面体晶体场中 高自旋(HS) vs 低自旋(LS) 的总能量随 Δ_o 变化
# 公式（见笔记第六节 6.1）：
#   高自旋 t2g^3 eg^2 : CFSE = 3*(-4Dq) + 2*(+6Dq) = 0 ;  成对数 0  -> E_HS = 0
#   低自旋 t2g^5      : CFSE = 5*(-4Dq) = -20 Dq = -2 Δ_o ; 成对数 2 -> E_LS = -20 Dq + 2P = 2(P - Δ_o)
#   交叉点（E_LS = E_HS）恰为 Δ_o = P
# 仅依赖 numpy + matplotlib（Agg 后端）。运行：隔离 venv python 本文件。
import os
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures", "42_晶体场与配位场理论_图1.svg")

# 成对能 P（典型 3d 量级，~15000-30000 cm^-1；Sugano 专著 [24iy]）
P = 20000.0  # cm^-1
Delta = np.linspace(0.0, 40000.0, 400)  # Δ_o in cm^-1

E_HS = np.zeros_like(Delta)          # 高自旋总能量（以 barycenter 为零）
E_LS = 2.0 * (P - Delta)            # 低自旋总能量

# 自旋交叉判据：Δ_o < P 高自旋；Δ_o > P 低自旋
cross = P

fig, ax = plt.subplots(figsize=(7.0, 5.0))
ax.plot(Delta, E_HS, "-", color="#1f77b4", label="High-spin  t2g^3 eg^2")
ax.plot(Delta, E_LS, "-", color="#d62728", label="Low-spin  t2g^5")
ax.axvline(cross, color="k", ls="--", lw=1.2, label="crossover  Delta_o = P")
ax.fill_between(Delta, np.minimum(E_HS, E_LS), np.maximum(E_HS, E_LS),
                color="gray", alpha=0.15)
ax.set_xlabel("Octahedral splitting  Delta_o  (cm^-1)")
ax.set_ylabel("Relative energy  (cm^-1)")
ax.set_title("d5 high-spin vs low-spin energy in Oh crystal field")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
fig.savefig(FIG, format="svg")
print("Saved figure:", FIG)
print("crossover at Delta_o = P =", cross, "cm^-1  (=", cross/8065.54, "eV approx)")
print("E_LS - E_HS at Delta_o=0 :", E_LS[0], "cm^-1  (should be +2P)")
print("Sign check: Delta_o<P -> HS lower; Delta_o>P -> LS lower")
