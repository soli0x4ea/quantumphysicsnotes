# 篇名：量子引力与全息原理（Quantum Gravity and the Holographic Principle）
# 公式：S_BH = A c^3 / (4 G hbar) = k_B A / (4 l_P^2),  A = 4 pi R_s^2,  R_s = 2 G M / c^2
#       Planck-unit form: S_BH = 4 pi (M / m_P)^2   [对应正文第二节、第六节脚本2]
# 产出：figures/量子引力与全息原理_黑洞熵.svg  (SVG 内图注全英文)
# 依赖：numpy + matplotlib only (numpy 2.x: 不使用 numpy.trapz，不 import scipy)

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- SI constants (CODATA 2018) ----
hbar = C["hbar"]   # J*s
c    = C["c"]       # m/s
G    = C["G"]       # m^3 kg^-1 s^-2
kB   = C["kB"]      # J/K
Msun = 1.98847e30        # kg

# ---- Planck units ----
lP = np.sqrt(hbar * G / c**3)
mP = np.sqrt(hbar * c / G)

def R_s(M):
    """Schwarzschild radius (m) for mass M (kg)."""
    return 2.0 * G * M / c**2

def S_BH(M):
    """Bekenstein-Hawking entropy divided by k_B (dimensionless count)."""
    A = 4.0 * np.pi * R_s(M)**2
    return A / (4.0 * lP**2)   # = S_BH / k_B

# mass range: 1 M_sun -> 1e10 M_sun (covers stellar & supermassive like M87*)
M = np.logspace(np.log10(Msun), np.log10(1.0e10 * Msun), 400)
S = S_BH(M)

fig, ax = plt.subplots(figsize=(7.2, 5.0))
ax.loglog(M, S, 'r-', lw=2,
          label=r'$S_{BH}/k_B = A/(4 l_P^2) \propto M^2$')

ref_points = [
    (Msun,         '1 M_sun'),
    (6.5e9 * Msun, 'M87*'),
]
for Mref, label in ref_points:
    Sref = S_BH(Mref)
    ax.plot(Mref, Sref, 'ko')
    ax.annotate(f'{label}\nS/k_B = {Sref:.1e}',
                (Mref, Sref), textcoords='offset points',
                xytext=(8, 6), fontsize=8)

# Planck-unit consistency overlay: S_BH = 4 pi (M / m_P)^2 (should coincide exactly)
M_ov = np.logspace(np.log10(mP), np.log10(1.0e10 * Msun), 400)
S_ov = 4.0 * np.pi * (M_ov / mP)**2
ax.loglog(M_ov, S_ov, 'g--', lw=1.5,
          label=r'Planck units: $S_{BH} = 4\pi (M/m_P)^2$')

ax.set_xlabel('Black hole mass M (kg)')
ax.set_ylabel('Bekenstein-Hawking entropy S_BH / k_B')
ax.set_title('Black Hole Entropy vs Mass')
ax.grid(True, which='both', ls=':', alpha=0.5)
ax.legend(loc='lower right')
fig.text(0.5, 0.02,
         r'$S_{BH} = A c^3 / (4 G \hbar) = k_B A / (4 l_P^2)$',
         ha='center', fontsize=9, style='italic')
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子引力与全息原理_黑洞熵.svg',
            format='svg')

print('Planck length l_P (m)     =', lP)
print('Planck mass m_P (kg)      =', mP)
print('S_BH(1 M_sun)/k_B         =', S_BH(Msun))
print('S_BH(M87*, 6.5e9 M_sun)/k_B =', S_BH(6.5e9 * Msun))
