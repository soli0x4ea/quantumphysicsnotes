# 分子结构_H2与苯.py
# 对应笔记：第23篇《分子结构与化学键》
# 段1：H2 Morse 势能曲线（实验参数 D_e=4.52 eV, a=1.94 A^-1, R_e=0.741 A）
# 段2：苯 Huckel pi 能级（beta=-2.5 eV），标注占据与 HOMO-LUMO 能隙
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 分子结构_H2与苯.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# Section 1: H2 Morse potential (experimental parameters)
# =========================================================
De = 4.52       # eV, dissociation energy (Herzberg)
a = 1.94        # 1/Angstrom, width parameter
Re = 0.741      # Angstrom, equilibrium bond length

R = np.linspace(0.4, 4.0, 400)   # Angstrom
E = De * ((1.0 - np.exp(-a * (R - Re))) ** 2 - 1.0)   # E(Re)=-De, E(inf)=0

print("== H2 Morse potential ==")
print(f"D_e = {De:.2f} eV, R_e = {Re:.3f} A, a = {a:.2f} A^-1")
print(f"E at R_e = {E[np.argmin(np.abs(R-Re))]:.3f} eV (expect -{De:.2f})")
print(f"E at large R = {E[-1]:.3f} eV (expect 0)")

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(R, E, color="#0b6e4f", lw=2.2, label="Morse V(R)")
ax.axhline(0.0, color="gray", lw=0.8, ls=":")
ax.scatter([Re], [-De], color="red", zorder=5, label=f"min: R_e={Re} A, -D_e={De} eV")
ax.set_xlabel("Internuclear distance R (Angstrom)")
ax.set_ylabel("Potential energy (eV)")
ax.set_title("H2 bond potential well (Morse, experimental)")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/分子结构_H2势能.svg", dpi=140)
print("saved figures/分子结构_H2势能.svg")

# =========================================================
# Section 2: benzene Huckel pi levels
# =========================================================
beta = -2.5     # eV, empirical resonance integral
alpha = 0.0     # set alpha=0 as energy reference
k = np.arange(6)
eps = alpha + 2.0 * beta * np.cos(2.0 * np.pi * k / 6.0)

# occupancy: 6 pi electrons fill lowest 3 levels
# k=0 (2e), k=1&5 degenerate (4e) -> HOMO=k=1/5, LUMO=k=2/4
occupied = [0, 1, 5]   # level indices with electrons
HOMO = alpha + beta
LUMO = alpha - beta
gap = abs(LUMO - HOMO)

print("\n== Benzene Huckel pi levels (beta=-2.5 eV) ==")
for ki, e in zip(k, eps):
    mark = "occ" if ki in occupied else "vir"
    print(f"k={ki}: eps = {e:+.2f} eV  ({mark})")
print(f"HOMO = {HOMO:+.2f} eV, LUMO = {LUMO:+.2f} eV, gap = {gap:.2f} eV")

fig, ax = plt.subplots(figsize=(5.6, 4.6))
for ki, e in zip(k, eps):
    color = "#1f4e79" if ki in occupied else "#c0392b"
    ax.hlines(e, ki - 0.25, ki + 0.25, color=color, lw=3.0)
    ax.plot(ki, e, "o", color=color)
    ax.text(ki, e + 0.25, f"{e:+.1f}", ha="center", fontsize=8)
ax.axhspan(HOMO - 0.15, LUMO + 0.15, color="orange", alpha=0.15,
           label=f"gap={gap:.1f} eV")
ax.set_xlabel("Level index k")
ax.set_ylabel("Energy (eV, alpha=0)")
ax.set_title("Benzene Huckel pi levels")
ax.set_xticks(range(6))
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/分子结构_苯Hückel.svg", dpi=140)
print("saved figures/分子结构_苯Hückel.svg")
