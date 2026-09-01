# 篇名：量子引力与全息原理（Quantum Gravity and the Holographic Principle）
# 公式：T_H = hbar c^3 / (8 pi G M k_B)   [对应正文第二节、第六节脚本1]
# 产出：figures/量子引力与全息原理_霍金温度.svg  (SVG 内图注全英文)
# 依赖：numpy + matplotlib only (numpy 2.x: 不使用 numpy.trapz，不 import scipy)

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# ---- SI constants (CODATA 2018 exact/defined where applicable) ----
hbar = 1.054571817e-34   # J*s  (reduced Planck constant)
c    = 299792458.0       # m/s  (speed of light)
G    = 6.67430e-11       # m^3 kg^-1 s^-2  (gravitational constant)
kB   = 1.380649e-23      # J/K  (Boltzmann constant, defined)
Msun = 1.98847e30        # kg   (solar mass, nominal)

# ---- Planck units (for reference points) ----
lP = np.sqrt(hbar * G / c**3)
mP = np.sqrt(hbar * c / G)
tP = np.sqrt(hbar * G / c**5)
TP = mP * c**2 / kB

def T_Hawking(M):
    """Hawking temperature (K) for black-hole mass M (kg)."""
    return hbar * c**3 / (8.0 * np.pi * G * M * kB)

# mass range: Planck mass -> 1e10 solar masses (covers stellar & microscopic & M87*)
M = np.logspace(np.log10(mP), np.log10(1.0e10 * Msun), 400)
T = T_Hawking(M)

fig, ax = plt.subplots(figsize=(7.2, 5.0))
ax.loglog(M, T, 'b-', lw=2, label=r'$T_H \propto M^{-1}$')

ref_points = [
    (mP,          'Planck mass\n(2.18e-8 kg)'),
    (Msun,        '1 M_sun'),
    (10.0 * Msun, '10 M_sun'),
    (6.5e9 * Msun,'M87*'),
]
for Mref, label in ref_points:
    Tref = T_Hawking(Mref)
    ax.plot(Mref, Tref, 'ko')
    ax.annotate(f'{label}\nT = {Tref:.1e} K',
                (Mref, Tref), textcoords='offset points',
                xytext=(8, 6), fontsize=8)

ax.set_xlabel('Black hole mass M (kg)')
ax.set_ylabel('Hawking temperature T_H (K)')
ax.set_title('Hawking Temperature vs Black Hole Mass')
ax.grid(True, which='both', ls=':', alpha=0.5)
ax.legend(loc='lower left')
fig.text(0.5, 0.02,
         r'$T_H = \hbar c^3 / (8 \pi G M k_B)$',
         ha='center', fontsize=9, style='italic')
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子引力与全息原理_霍金温度.svg',
            format='svg')

print('Planck mass mP (kg)      =', mP)
print('Planck temp T_P (K)      =', TP)
print('T_H(1 M_sun)  (K)        =', T_Hawking(Msun))
print('T_H(10 M_sun) (K)        =', T_Hawking(10.0 * Msun))
print('T_H(m_P)     (K)         =', T_Hawking(mP))
