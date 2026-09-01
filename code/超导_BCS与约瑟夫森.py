# 超导_BCS与约瑟夫森.py
# 对应笔记：第27篇《超导电性与宏观量子现象》
# 段1：BCS 能隙随温度（标准插值公式 (5)）
# 段2：约瑟夫森结临界电流随磁通的夫琅禾费调制 (6)
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 超导_BCS与约瑟夫森.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# Section 1: BCS gap vs temperature
# =========================================================
Tr = np.linspace(0.02, 1.4, 600)
arg = np.where(Tr < 1.0, 1.0 / Tr - 1.0, 0.0)
ratio = np.where(Tr < 1.0, np.tanh(1.76 * np.sqrt(arg)), 0.0)

Delta0_over_kTc = 1.76
print("== BCS gap (interpolation) ==")
print(f"  Delta(0)/k_B T_c = {Delta0_over_kTc} (BCS value)")
print(f"  Delta(T_c)/Delta(0) = {ratio[np.argmin(np.abs(Tr-1.0))-1]:.4f} (-> 0 at T_c)")
print(f"  Delta(0.5 T_c)/Delta(0) = {float(ratio[np.argmin(np.abs(Tr-0.5))]):.4f}")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.plot(Tr, ratio, color="#1f4e79", lw=2.2)
ax.axvline(1.0, color="#c0392b", ls="--", lw=1.0, label=r"$T/T_c=1$")
ax.set_xlabel(r"$T/T_c$")
ax.set_ylabel(r"$\Delta(T)/\Delta(0)$")
ax.set_title("BCS order parameter vs temperature")
ax.set_ylim(-0.05, 1.1)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/超导_BCS能隙.svg", dpi=140)
print("saved figures/超导_BCS能隙.svg")

# =========================================================
# Section 2: Josephson junction Fraunhofer pattern
# =========================================================
Phi_ratio = np.linspace(-3.0, 3.0, 900)
with np.errstate(divide="ignore", invalid="ignore"):
    Ic = np.abs(np.sin(np.pi * Phi_ratio) / (np.pi * Phi_ratio))
Ic[Phi_ratio == 0.0] = 1.0

print("\n== Josephson Fraunhofer ==")
print(f"  I_c(0)/I_c0 = {float(Ic[np.argmin(np.abs(Phi_ratio))]):.4f}")
print(f"  first zero at Phi/Phi0 = {1.0:.1f} (flux quantum)")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.plot(Phi_ratio, Ic, color="#1f4e79", lw=2.2)
ax.axvline(1.0, color="#c0392b", ls=":", lw=1.0)
ax.axvline(-1.0, color="#c0392b", ls=":", lw=1.0)
ax.set_xlabel(r"Applied flux $\Phi/\Phi_0$")
ax.set_ylabel(r"$I_c(\Phi)/I_{c0}$")
ax.set_title("Josephson junction critical current (Fraunhofer)")
ax.set_ylim(-0.05, 1.15)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/超导_约瑟夫森Fraunhofer.svg", dpi=140)
print("saved figures/超导_约瑟夫森Fraunhofer.svg")
