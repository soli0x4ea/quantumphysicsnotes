# 量子霍尔_Landau能级与平台.py
# 对应笔记：第28篇《量子霍尔效应》
# 段1：朗道能级谱 E_n(B) = (n+1/2) hbar e B / m* 随磁场变化（式(2)(3)）
# 段2：霍尔电阻平台 rho_xy = h/(nu e^2) 与纵向电阻 rho_xx 在整数填充处的归零（式(5)）
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 量子霍尔_Landau能级与平台.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- constants (CODATA 2022) ----
hbar = 1.054571817e-34
m_e = 9.1093837015e-31
e = 1.602176634e-19
h = 6.62607015e-34
eV = 1.602176634e-19
RK = h / e**2          # von Klitzing constant

print(f"von Klitzing constant R_K = h/e^2 = {RK:.1f} ohm")

# =========================================================
# Section 1: Landau level spectrum vs magnetic field
# =========================================================
B = np.linspace(0.0, 15.0, 400)
n_max = 6
omega_c = e * B / m_e
En = np.array([(n + 0.5) * hbar * omega_c for n in range(n_max)])   # J
En_meV = En / eV * 1.0e3     # meV

hbar_omega_c_at10 = hbar * e * 10.0 / m_e / eV * 1.0e3
print(f"\n== Landau levels ==")
print(f"  hbar*omega_c at B=10 T = {hbar_omega_c_at10:.3f} meV (free electron)")
print(f"  degeneracy per area eB/h at B=10 T = {e*10.0/h:.3e} m^-2")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
for n in range(n_max):
    ax.plot(B, En_meV[n], lw=1.8, label=f"n={n}")
ax.set_xlabel("Magnetic field B (T)")
ax.set_ylabel(r"Landau level $E_n$ (meV)")
ax.set_title("Landau level spectrum vs magnetic field")
ax.legend(fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/量子霍尔_Landau能级.svg", dpi=140)
print("saved figures/量子霍尔_Landau能级.svg")

# =========================================================
# Section 2: Hall resistivity plateaus (IQHE toy model)
# =========================================================
ne = 2.4e15         # electron sheet density, m^-2 (nu=1 at ~B=10 T)
B2 = np.linspace(1.0, 10.0, 1200)
nu = ne * h / (e * B2)                      # filling factor
Nfilled = np.maximum(1.0, np.floor(nu))      # number of filled Landau levels
rho_xy = h / (Nfilled * e**2)               # plateau value, ohm
dist = np.abs(nu - np.round(nu))            # distance to nearest integer filling
rho_xx = 1.0e3 * np.clip(dist / 0.45, 0.0, 1.0)   # longitudinal dip (a.u. ohm)

print("\n== IQHE toy ==")
for Btest in [10.0, 5.0, 3.33, 2.0]:
    idx = np.argmin(np.abs(B2 - Btest))
    print(f"  B={Btest:.2f} T: nu={nu[idx]:.2f}, rho_xy={rho_xy[idx]:.1f} ohm (=R_K/{Nfilled[idx]:.0f})")

fig, ax1 = plt.subplots(figsize=(6.4, 4.4))
ax1.plot(B2, rho_xy / RK, color="#1f4e79", lw=2.0, label=r"$\rho_{xy}/R_K$")
ax1.set_xlabel("Magnetic field B (T)")
ax1.set_ylabel(r"$\rho_{xy}/R_K$ (plateau index $1/\nu$)", color="#1f4e79")
ax1.tick_params(axis="y", labelcolor="#1f4e79")
ax2 = ax1.twinx()
ax2.plot(B2, rho_xx, color="#c0392b", lw=1.6, label=r"$\rho_{xx}$ (dips)")
ax2.set_ylabel(r"$\rho_{xx}$ (a.u.)", color="#c0392b")
ax2.tick_params(axis="y", labelcolor="#c0392b")
ax1.set_title("Integer quantum Hall: rho_xy plateaus and rho_xx dips")
ax1.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/量子霍尔_霍尔平台.svg", dpi=140)
print("saved figures/量子霍尔_霍尔平台.svg")
