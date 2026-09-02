# 量子统计_BEC与费米气体.py
# 对应笔记：第26篇《量子统计》
# 段1：理想玻色气体 BEC 临界温度 T_c 与凝聚分数 N0/N（式(3)(4)）
# 段2：理想费米气体费米能 E_F 与零温简并压 P0（式(5)(6)）
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 量子统计_BEC与费米气体.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- constants (CODATA 2022) ----
hbar = C["hbar"]
kB = C["kB"]
me = C["m_e"]
eV = C["e"]
amu = C["u"]

# =========================================================
# Section 1: BEC critical temperature and condensate fraction
# =========================================================
# Rb-87 atom gas
m_rb = 86.909 * amu
n_rb = 1.0e19         # m^-3 (typical evaporative cooling density)
zeta_32 = 2.612       # Riemann zeta(3/2)

# k_B T_c = (2*pi*hbar^2 / m) * (n / zeta(3/2))^(2/3)
Tc = (2.0 * np.pi * hbar**2 / m_rb) * (n_rb / zeta_32) ** (2.0 / 3.0) / kB
print("== BEC (Rb-87, n=1e19 m^-3) ==")
print(f"  T_c = {Tc:.2e} K  (~{Tc*1e9:.0f} nK)")

Tr = np.linspace(0.0, 1.3, 400)
frac = np.where(Tr < 1.0, 1.0 - Tr**1.5, 0.0)

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.plot(Tr, frac, color="#1f4e79", lw=2.2)
ax.axvline(1.0, color="#c0392b", ls="--", lw=1.0, label=r"$T/T_c=1$")
ax.set_xlabel(r"$T/T_c$")
ax.set_ylabel(r"Condensate fraction $N_0/N$")
ax.set_title("BEC condensate fraction vs temperature")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/量子统计_BEC凝聚分数.svg", dpi=140)
print("saved figures/量子统计_BEC凝聚分数.svg")

# =========================================================
# Section 2: Fermi gas Fermi energy and degeneracy pressure
# =========================================================
n = np.logspace(27.0, 36.0, 400)     # electron density, m^-3
EF = hbar**2 / (2.0 * me) * (3.0 * np.pi**2 * n) ** (2.0 / 3.0)   # J
EF_eV = EF / eV
P0 = (2.0 / 5.0) * n * EF           # Pa (non-relativistic)

# reference points
# Cu metal
n_Cu = 8.49e28
EF_Cu = hbar**2 / (2.0 * me) * (3.0 * np.pi**2 * n_Cu) ** (2.0 / 3.0) / eV
P0_Cu = (2.0 / 5.0) * n_Cu * (EF_Cu * eV)
# white dwarf (non-rel approx, rho=1e9 kg/m^3, mu_e=2)
rho_wd = 1.0e9
mu_e = 2.0
n_wd = rho_wd / (mu_e * amu)
EF_wd = hbar**2 / (2.0 * me) * (3.0 * np.pi**2 * n_wd) ** (2.0 / 3.0) / eV
P0_wd = (2.0 / 5.0) * n_wd * (EF_wd * eV)

print("\n== Fermi gas ==")
print(f"  Cu (n=8.49e28 m^-3): E_F = {EF_Cu:.3f} eV, P0 = {P0_Cu:.3e} Pa")
print(f"  White dwarf (rho=1e9 kg/m^3, non-rel): E_F = {EF_wd:.2f} eV, P0 = {P0_wd:.3e} Pa")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.loglog(n, P0, color="#1f4e79", lw=2.0, label=r"$P_0\propto n^{5/3}$")
ax.axvline(n_Cu, color="#c0392b", ls="--", lw=1.0)
ax.axvline(n_wd, color="#27ae60", ls=":", lw=1.0, label="white dwarf (non-rel)")
ax.set_xlabel(r"Electron density $n$ (m$^{-3}$)")
ax.set_ylabel(r"Degeneracy pressure $P_0$ (Pa)")
ax.set_title("Zero-temperature degeneracy pressure vs density")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/量子统计_费米简并压.svg", dpi=140)
print("saved figures/量子统计_费米简并压.svg")
