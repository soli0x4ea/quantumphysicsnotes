# 全同粒子_费米气体与HOM.py
# 对应笔记：第21篇《全同粒子与泡利不相容原理》
# 段1：自由电子费米气体 —— 式(5)态密度 D(E) propto E^{1/2}，复现铜的 E_F/k_F/T_F/v_F
# 段2：Hong-Ou-Mandel 双光子干涉 —— 式(3)符合率 R_c(tau)，全同 vs 非全同可见度
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 全同粒子_费米气体与HOM.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- constants (CODATA 2022, 精确值) ----
hbar = C["hbar"]      # J*s
me = C["m_e"]       # kg
kB = C["kB"]           # J/K
eV = C["e"]        # J

# =========================================================
# Section 1: free electron Fermi gas
# =========================================================
n = 8.49e28                 # electron density in Cu, m^-3
kF = (3.0 * np.pi**2 * n) ** (1.0 / 3.0)
EF = hbar**2 * kF**2 / (2.0 * me)      # J
TF = EF / kB
vF = hbar * kF / me

print("== Free electron Fermi gas (Cu, n=8.49e28 m^-3) ==")
print(f"k_F = {kF:.4e} m^-1")
print(f"E_F = {EF/eV:.4f} eV")
print(f"T_F = {TF:.4e} K")
print(f"v_F = {vF:.4e} m/s")

# density of states per unit volume, per unit energy: D(E) = (2me)^{3/2}/(2 pi^2 hbar^3) * E^{1/2}
pref = (2.0 * me) ** 1.5 / (2.0 * np.pi**2 * hbar**3)   # J^-1 m^-3
E = np.linspace(1e-3, 3.0 * EF, 600)
D = pref * np.sqrt(E)

fig, ax = plt.subplots(figsize=(6.0, 4.2))
ax.plot(E / eV, D * eV, color="#1f4e79", lw=2.0, label=r"$D(E)\propto E^{1/2}$")
ax.axvline(EF / eV, color="#c0392b", ls="--", lw=1.5,
           label=f"E_F = {EF/eV:.2f} eV")
ax.set_xlabel("Energy E (eV)")
ax.set_ylabel("DOS D(E) (states / J / m^3)")
ax.set_title("Free-electron DOS and Fermi energy (Cu)")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/全同粒子_费米气体.svg", dpi=140)
print("saved figures/全同粒子_费米气体.svg")

# =========================================================
# Section 2: Hong-Ou-Mandel two-photon interference
# =========================================================
# R_c(tau) = 0.5 * (1 - |g1(tau)|^2), g1(tau) = FT of spectral envelope S(omega)
# identical photons (same pol/freq): gaussian S(w) -> g1(tau)=exp(-sigma_w^2 tau^2 / 2)
# non-identical (orthogonal pol): interference term vanishes -> R_c = 0.5 constant

sigma_w = 1.0e12               # rad/s, spectral width
tau = np.linspace(-4e-12, 4e-12, 800)    # s

g1_ident = np.exp(-(sigma_w**2) * tau**2 / 2.0)
Rc_ident = 0.5 * (1.0 - np.abs(g1_ident) ** 2)
Rc_nonident = 0.5 * np.ones_like(tau)

V_ident = (Rc_ident.max() - Rc_ident.min()) / (Rc_ident.max() + Rc_ident.min())
V_non = (Rc_nonident.max() - Rc_nonident.min()) / (Rc_nonident.max() + Rc_nonident.min())

print("\n== Hong-Ou-Mandel interference ==")
print(f"identical   : R_c(0) = {Rc_ident[np.argmin(np.abs(tau))]:.6f}, visibility V = {V_ident:.6f}")
print(f"non-identical: R_c(0) = {Rc_nonident[0]:.6f}, visibility V = {V_non:.6f}")

fig, ax = plt.subplots(figsize=(6.0, 4.2))
ax.plot(tau * 1e12, Rc_ident, color="#1f4e79", lw=2.0,
        label=f"identical (V={V_ident:.3f})")
ax.plot(tau * 1e12, Rc_nonident, color="#7f8c8d", ls="--", lw=1.8,
        label=f"non-identical (V={V_non:.3f})")
ax.axvline(0.0, color="#c0392b", lw=0.8, alpha=0.6)
ax.set_xlabel("Time delay tau (ps)")
ax.set_ylabel("Coincidence rate R_c")
ax.set_title("Hong-Ou-Mandel dip: visibility 1 vs 0")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/全同粒子_HOM干涉.svg", dpi=140)
print("saved figures/全同粒子_HOM干涉.svg")
