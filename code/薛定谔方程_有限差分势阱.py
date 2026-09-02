# -*- coding: utf-8 -*-
"""Schrodinger equation: finite-difference solution of the 1D infinite square well.

Discretizes the time-independent SE - (hbar^2/2m) psi'' = E psi on a grid with
hard-wall boundaries, diagonalizes the tridiagonal Hamiltonian, and verifies:
  (a) numerical eigenvalues E_n ~ n^2 pi^2 hbar^2 / (2 m L^2)
  (b) the n-th eigenfunction has exactly n-1 nodes (node theorem)
Outputs: figures/schrodinger_equation_finite_difference_well.svg
All labels in English to avoid CJK font issues.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

HBAR = C["hbar"]       # J.s
M_E  = C["m_e"]      # electron mass, kg
EV   = C["e"]       # J/eV
L    = 1.0e-9                # well width, 1 nm
N    = 800                   # interior grid points
dx   = L / (N + 1)

# Finite-difference Hamiltonian (tridiagonal): -hbar^2/(2m) * d^2/dx^2
diag = np.full(N, HBAR**2 / (M_E * dx**2))
off  = np.full(N - 1, -HBAR**2 / (2 * M_E * dx**2))
# Build dense small matrix (N=800 is fine); use numpy.linalg.eigh (no scipy needed)
H = np.diag(diag) + np.diag(off, 1) + np.diag(off, -1)

# Lowest 6 eigenvalues/eigenvectors (full eigh, then sort)
vals, vecs = np.linalg.eigh(H)
order = np.argsort(vals)
vals = vals[order]
vecs = vecs[:, order]
vals = vals[:6]
vecs = vecs[:, :6]
vals_ev = vals / EV

# Analytic eigenvalues
n_vec = np.arange(1, 7)
E_analytic = (n_vec**2 * np.pi**2 * HBAR**2) / (2 * M_E * L**2) / EV

print("n   E_num(eV)   E_analytic(eV)   rel_err     nodes")
for i, n in enumerate(n_vec):
    psi = vecs[:, i]
    # normalize on grid
    psi = psi / np.sqrt(np.sum(psi**2) * dx)
    # count sign changes (nodes) excluding endpoints
    nodes = int(np.sum(np.diff(np.sign(psi)) != 0))
    rel = abs(vals_ev[i] - E_analytic[i]) / E_analytic[i]
    print(f"{n}   {vals_ev[i]:.6f}    {E_analytic[i]:.6f}      {rel:.2e}    {nodes}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(dx, L - dx, N) * 1e9  # nm

ax = axes[0]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
for i in range(4):
    psi = vecs[:, i] / np.sqrt(np.sum(vecs[:, i]**2) * dx)
    ax.plot(x, psi + i * 1.2, color=colors[i], lw=1.6, label=f"n={i+1}")
ax.set_xlabel("position x (nm)")
ax.set_ylabel("psi(x) + offset (a.u.)")
ax.set_title("Numerical eigenfunctions (node count = n-1)")
ax.set_ylim(-0.6, 4.8)
ax.legend(frameon=False, ncol=4, loc="upper right")

ax = axes[1]
ax.plot(n_vec, E_analytic, "o--", color="#2ca02c", label="analytic n^2 pi^2 hbar^2/(2mL^2)")
ax.plot(n_vec, vals_ev, "s", color="#d62728", label="finite-difference numeric")
ax.set_xlabel("quantum number n")
ax.set_ylabel("energy E (eV)")
ax.set_title("Eigenvalues: numeric vs analytic")
ax.legend(frameon=False)
ax.set_xticks(n_vec)

fig.suptitle("1D infinite square well (L=1 nm): finite-difference verification of SE eigenvalues")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("figures/薛定谔方程_有限差分势阱.svg", format="svg")
print("saved figures/薛定谔方程_有限差分势阱.svg")
