# 角动量与自旋_斯特恩-盖拉赫分裂.py
# 对应笔记：第 16 篇《角动量与自旋》 §6.2
# 计算银原子束在非均匀磁场中的空间量子化偏转，验证"分立两束"量级自洽
# 依赖：numpy, matplotlib（隔离 venv）
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 常数 (CODATA 2022) ----
u = 1.66053906660e-27          # atomic mass unit, kg
m_Ag = 107.8682 * u            # silver-107/109 average, kg
kB = 1.380649e-23              # Boltzmann constant, J/K
muB = 9.2740100783e-24         # Bohr magneton, J/T
hbar = 1.054571817e-34         # J*s (exact)

# ---- 实验参数 (Gerlach-Stern 类磁极, 量级估算) ----
T = 1000.0                     # oven temperature, K
v = np.sqrt(2.0 * kB * T / m_Ag)   # representative thermal speed, m/s
gradB = 1.0e3                  # dB/dz, T/m (~10 T/cm)
L_m = 0.10                     # magnet length, m
D = 1.0                        # drift to detector, m

# ---- 偏转计算 (two spin orientations m_s = +/- 1/2) ----
# Force F = mu_z * dB/dz ;  mu_z = +/- muB  (Ag valence electron, L=0)
a = muB * gradB / m_Ag         # transverse acceleration magnitude, m/s^2
t1 = L_m / v                   # time in magnet, s
v_z = a * t1                   # transverse velocity at exit, m/s
d1 = 0.5 * a * t1**2           # deflection inside magnet, m
t2 = D / v                     # drift time, s
d2 = v_z * t2                  # deflection in drift, m
dz = d1 + d2                   # total deflection per beam, m

print(f"v        = {v:.1f} m/s")
print(f"a        = {a:.3e} m/s^2")
print(f"defl in magnet = {d1*1e3:.3f} mm")
print(f"defl in drift  = {d2*1e3:.3f} mm")
print(f"total dz per beam = {dz*1e3:.3f} mm")
print(f"separation 2*dz  = {2*dz*1e3:.3f} mm")

# ---- 探测屏上的两束强度分布 ----
z = np.linspace(-3*dz, 3*dz, 600)        # detector position, m
sigma = 0.25 * dz                         # beam width (representative)
I_up = np.exp(-((z - dz)/(np.sqrt(2)*sigma))**2)
I_dn = np.exp(-((z + dz)/(np.sqrt(2)*sigma))**2)
I_tot = I_up + I_dn

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(z*1e3, I_up, color="#c0392b", lw=2, label=r"$m_s=+1/2$")
ax.plot(z*1e3, I_dn, color="#2c3e88", lw=2, label=r"$m_s=-1/2$")
ax.fill_between(z*1e3, I_tot, color="#888888", alpha=0.18, label="total")
ax.set_xlabel("Detector position $z$ (mm)")
ax.set_ylabel("Relative beam intensity")
ax.set_title("Stern-Gerlach split: two discrete beams (not continuous)")
ax.legend(frameon=False)
ax.set_xlim(-3*dz*1e3, 3*dz*1e3)
ax.text(0.0, 0.92, f"separation 2$\\Delta z$ = {2*dz*1e3:.2f} mm\n"
               f"(Ag, T={T:.0f} K, dB/dz={gradB:.0f} T/m)",
        transform=ax.transAxes, ha="center", va="top", fontsize=9)
fig.tight_layout()
fig.savefig("figures/角动量与自旋_斯特恩-盖拉赫分裂.svg", bbox_inches="tight")
print("saved figures/角动量与自旋_斯特恩-盖拉赫分裂.svg")
