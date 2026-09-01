# 晶体中的电子_能带与KronigPenney.py
# 对应笔记：第24篇《晶体中的电子与能带》
# 段1：一维 Kronig-Penney delta 势梳模型，复现允许带/禁带交替的能带结构
# 段2：由 Kronig-Penney 能带数值计算一维态密度 g(E)，展示带边范霍夫奇点与禁带内 g=0
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 晶体中的电子_能带与KronigPenney.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- constants (CODATA 2022) ----
hbar = 1.054571817e-34      # J*s
me = 9.1093837015e-31       # kg
# effective: hbar^2 / (2m) in eV * Angstrom^2  (for 1D energy E = (hbar^2/2m)*alpha^2)
# hbar^2/(2m) = 6.104e-39 J*m^2 = 3.81 eV*A^2
hbar2_2m_eV_A2 = 3.81

a = 1.0        # lattice constant, Angstrom
P = 1.0        # dimensionless Kronig-Penney delta strength

# =========================================================
# Section 1: Kronig-Penney band structure (reduced zone)
# =========================================================
N = 20000
Emax = 160.0
E = np.linspace(1e-4, Emax, N)
alpha = np.sqrt(E / hbar2_2m_eV_A2)      # Angstrom^-1
xa = alpha * a
f = np.cos(xa) + (P / (xa + 1e-30)) * np.sin(xa)
allowed = np.abs(f) <= 1.0

# reduced-zone k = arccos(f)/a  in [0, pi/a]
k_red = np.arccos(np.clip(f, -1.0, 1.0)) / a     # Angstrom^-1

kp = k_red[allowed]
km = -k_red[allowed]
Ep = E[allowed]

print("== Kronig-Penney band edges (P=%.1f) ==" % P)
# segment detection
segs = []
i = 0
while i < N:
    if allowed[i]:
        j = i
        while j < N and allowed[j]:
            j += 1
        segs.append((E[i], E[j-1]))
        i = j
    else:
        i += 1
for idx, (lo, hi) in enumerate(segs[:6]):
    print(f"  band {idx+1}: E in [{lo:.3f}, {hi:.3f}] eV, width = {hi-lo:.3f} eV")

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.scatter(km, Ep, s=1.0, color="#1f4e79", linewidths=0)
ax.scatter(kp, Ep, s=1.0, color="#1f4e79", linewidths=0)
ax.axvline(0.0, color="#888888", lw=0.6)
ax.axvline(np.pi / a, color="#c0392b", ls="--", lw=1.0, label=r"$k=\pi/a$ (BZ edge)")
ax.axvline(-np.pi / a, color="#c0392b", ls="--", lw=1.0)
ax.set_xlabel(r"Reduced-zone wave vector $k$ ($\AA^{-1}$)")
ax.set_ylabel("Energy E (eV)")
ax.set_title("Kronig-Penney band structure (delta comb, P=3)")
ax.set_xlim(-np.pi / a - 0.1, np.pi / a + 0.1)
ax.set_ylim(0, Emax)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig("../figures/晶体中的电子_KronigPenney能带.svg", dpi=140)
print("saved figures/晶体中的电子_KronigPenney能带.svg")

# =========================================================
# Section 2: 1D density of states from the bands
# =========================================================
g_list = []
E_list = []
for idx in range(len(segs)):
    lo, hi = segs[idx]
    mask = (E >= lo - 1e-9) & (E <= hi + 1e-9)
    Es = E[mask]
    ks = k_red[mask]            # in [0, pi/a], monotonic with E
    if len(Es) < 4:
        continue
    dE = np.gradient(Es)
    dk = np.gradient(ks)
    with np.errstate(divide="ignore", invalid="ignore"):
        dkde = dk / dE          # dk/dE
    g = (2.0 / np.pi) / np.abs(dkde)   # per unit length, full zone + spin factor 4 -> 2/pi
    g_list.append(g)
    E_list.append(Es)

# assemble
Eg = np.concatenate(E_list)
Gg = np.concatenate(g_list)
# sort by energy for plotting
order = np.argsort(Eg)
Eg = Eg[order]
Gg = Gg[order]

# mask out non-finite / clip divergence at band edges for visibility
finite = np.isfinite(Gg)
Eg_f = Eg[finite]
Gg_f = Gg[finite]
cap = np.nanpercentile(Gg_f, 98.0)
Gg_clip = np.where(Gg_f > cap, cap, Gg_f)

print("\n== 1D DOS sanity ==")
print(f"  number of band-edge divergences clipped: {np.sum(~finite)}")
print(f"  98th percentile of g = {cap:.4f}")

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(Eg_f, Gg_clip, color="#1f4e79", lw=1.6, label=r"$g(E)\propto|dE/dk|^{-1}$")
# mark band edges
for idx, (lo, hi) in enumerate(segs[:6]):
    ax.axvline(lo, color="#c0392b", ls=":", lw=0.7, alpha=0.6)
    ax.axvline(hi, color="#c0392b", ls=":", lw=0.7, alpha=0.6)
ax.set_xlabel("Energy E (eV)")
ax.set_ylabel("1D DOS g(E) (a.u.)")
ax.set_title("1D density of states: van Hove peaks at band edges")
ax.set_ylim(0, cap * 1.05)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig("../figures/晶体中的电子_一维态密度.svg", dpi=140)
print("saved figures/晶体中的电子_一维态密度.svg")
