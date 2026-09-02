# 半导体_载流子与pn结.py
# 对应笔记：第25篇《半导体与 pn 结》
# 段1：本征载流子浓度 n_i(T) 随温度变化（Si, 质量作用定律式(3)(8)）
# 段2：理想二极管 I-V 特性（Shockley 方程 (6)）
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 半导体_载流子与pn结.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- constants (CODATA 2022) ----
kB = C["kB"]           # J/K
e = C["e"]        # C
eV = C["e"]       # J

# =========================================================
# Section 1: intrinsic carrier concentration vs temperature (Si)
# =========================================================
Nc300 = 2.8e19      # cm^-3 effective DOS conduction band at 300 K
Nv300 = 1.04e19     # cm^-3 effective DOS valence band at 300 K
Eg = 1.12 * eV      # Si band gap (300 K), J

T = np.linspace(100.0, 600.0, 400)
Nc = Nc300 * (T / 300.0) ** 1.5
Nv = Nv300 * (T / 300.0) ** 1.5
ni = np.sqrt(Nc * Nv) * np.exp(-Eg / (2.0 * kB * T))     # cm^-3

ni_300 = float(ni[np.argmin(np.abs(T - 300.0))])
print("== Intrinsic carrier concentration (Si) ==")
print(f"  n_i(300 K) = {ni_300:.3e} cm^-3  (textbook ~1.0e10 cm^-3)")
print(f"  n_i(400 K) = {float(ni[np.argmin(np.abs(T-400.0))]):.3e} cm^-3")
print(f"  n_i(600 K) = {float(ni[np.argmin(np.abs(T-600.0))]):.3e} cm^-3")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.semilogy(T, ni, color="#1f4e79", lw=2.0)
ax.axvline(300.0, color="#c0392b", ls="--", lw=1.0, label="T = 300 K")
ax.set_xlabel("Temperature T (K)")
ax.set_ylabel(r"Intrinsic carrier density $n_i$ (cm$^{-3}$)")
ax.set_title("Intrinsic carrier concentration of Si vs T")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/半导体_载流子浓度随温度.svg", dpi=140)
print("saved figures/半导体_载流子浓度随温度.svg")

# =========================================================
# Section 2: ideal diode I-V (Shockley equation)
# =========================================================
Is = 1.0e-12       # A, reverse saturation current (Si, typical)
T_diode = 300.0
kT_q = kB * T_diode / e     # thermal voltage, ~0.02585 V
V = np.linspace(-1.0, 0.85, 900)
I = Is * (np.exp(V / kT_q) - 1.0)

print("\n== Ideal diode I-V (Si, Is=1e-12 A, T=300 K) ==")
print(f"  thermal voltage kT/e = {kT_q*1000:.2f} mV")
for vtest in [0.5, 0.6, 0.7, 0.8]:
    print(f"  V={vtest:.2f} V -> I = {float(Is*(np.exp(vtest/kT_q)-1)):.3e} A")
print(f"  reverse V=-1.0 V -> I = {float(Is*(np.exp(-1.0/kT_q)-1)):.3e} A (saturation)")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.semilogy(V, np.abs(I), color="#1f4e79", lw=2.0)
ax.axhline(Is, color="#7f8c8d", ls=":", lw=1.0, label=f"I_s = {Is:.0e} A")
ax.axvline(0.7, color="#c0392b", ls="--", lw=1.0, label="turn-on ~0.7 V")
ax.set_xlabel("Applied voltage V (V)")
ax.set_ylabel(r"|Diode current| I (A)")
ax.set_title("Ideal p-n junction I-V (Shockley equation)")
ax.set_ylim(1e-13, 1e-1)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/半导体_pn结IV.svg", dpi=140)
print("saved figures/半导体_pn结IV.svg")
