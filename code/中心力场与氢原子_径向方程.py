# -*- coding: utf-8 -*-
"""
Central potential and hydrogen atom: finite-difference radial equation.

Verifies the analytic results in note 17 (L3):
  - Bound-state energies E_n ~ -13.6 eV / n^2 (with reduced mass)
  - Radial probability densities u(r)^2 / r for lowest states
  - n^2 degeneracy structure

Environment: isolated venv (numpy only; no scipy). Uses numpy.linalg.eigh.
Figures saved as Chinese-named SVGs (consistent with note references).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

HBAR = C["hbar"]
ME = C["m_e"]
MP = C["m_p"]
EV = C["e"]
EPS0 = C["epsilon_0"]
E_CHARGE = C["e"]

MU = ME * MP / (ME + MP)          # reduced mass
A0 = 4 * np.pi * EPS0 * HBAR**2 / (MU * E_CHARGE**2)   # Bohr radius (m)
RY = MU * E_CHARGE**4 / (2 * (4 * np.pi * EPS0)**2 * HBAR**2)  # Rydberg (J)

FIG_DIR = "/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures"


def radial_eigen(l, n_states=5, r_max=3.0e-9, N=3000):
    """Lowest eigenvalues (J) and eigenvectors of the radial equation for given l."""
    h = r_max / N
    M = N - 1                      # interior points
    r = h * np.arange(1, N)        # r_i = i*h, i=1..N-1
    kin_diag = HBAR**2 / (MU * h**2)
    cent = l * (l + 1) * HBAR**2 / (2 * MU * r**2)
    coul = -E_CHARGE**2 / (4 * np.pi * EPS0 * r)
    d = kin_diag + cent + coul
    off = np.full(M - 1, -HBAR**2 / (2 * MU * h**2))
    A = np.diag(d) + np.diag(off, 1) + np.diag(off, -1)
    w, vec = np.linalg.eigh(A)     # ascending
    return r, w[:n_states], vec[:, :n_states]


def main_energy_check():
    print(f"Bohr radius a0   = {A0*1e10:.6f} Angstrom (CODATA 0.529177)")
    print(f"Rydberg energy   = {RY/EV:.4f} eV (CODATA 13.6057 with reduced mass)")
    print("Radial finite-difference energies (l=0,1,2):")
    results = {}
    for l in (0, 1, 2):
        r, evals, _ = radial_eigen(l, n_states=5)
        for j, E in enumerate(evals):
            n = j + 1 + l          # n = n_r + l + 1
            rel = (E - (-RY / n**2)) / (-RY / n**2)
            deg = n * n
            print(f"  l={l} state {j+1}: E={E/EV:10.5f} eV  "
                  f"(expect -{RY/n**2/EV:.5f})  rel.err={rel:+.2e}  n={n} deg={deg}")
            results[(l, j)] = (r, evals[j], None)
    return results


def main_figures():
    # radial probability densities for n=1,2,3 lowest-l states
    states = []   # (l, r, u)
    for l in (0, 1, 2):
        r, evals, vecs = radial_eigen(l, n_states=4)
        for j in range(min(3, len(evals))):
            u = vecs[:, j]
            # normalize: integral |u|^2 dr = 1  (u = r R)
            dr = r[1] - r[0]
            norm = np.sqrt(np.sum(u**2) * dr)
            u = u / norm
            states.append((l, j + 1 + l, r, u))

    fig, (axr, axe) = plt.subplots(1, 2, figsize=(11, 4.6))
    for l, n, r, u in states:
        # radial probability density |R|^2 r^2 = |u|^2 / r  (clip r>0)
        P = (u**2) / r
        P = np.where(r > 1e-12, P, 0.0)
        nodes = int(np.sum(np.diff(np.sign(u)) != 0))
        axr.plot(r / A0, P, lw=1.6, label=f"n={n}, l={l} (nodes={nodes})")
    axr.set_xlabel("r / a0")
    axr.set_ylabel("radial probability density |R(r)|^2 r^2")
    axr.set_title("Hydrogen radial probability densities (lowest states)")
    axr.legend(fontsize=8)
    axr.grid(True, alpha=0.3)
    axr.set_xlim(0, 25)

    # energy level diagram with degeneracy
    for n in (1, 2, 3):
        E = -RY / n**2 / EV
        axe.plot([0, 1], [E, E], "b-", lw=2)
        axe.text(1.03, E, f"n={n}, g={n*n}", fontsize=9)
    axe.axhline(0.0, color="k", lw=1.0, label="ionization limit (E=0)")
    axe.set_xlim(0, 1.4)
    axe.set_ylabel("Energy (eV)")
    axe.set_title("Hydrogen bound-state energies and degeneracy n^2")
    axe.legend(fontsize=8)
    axe.grid(True, alpha=0.3)

    fig.tight_layout()
    out = f"{FIG_DIR}/中心力场与氢原子_能级图.svg"
    fig.savefig(out, format="svg")
    print("saved", out)

    # separate radial-density figure (clearer)
    fig2, ax = plt.subplots(figsize=(6.4, 4.4))
    for l, n, r, u in states:
        P = np.where(r > 1e-12, u**2 / r, 0.0)
        ax.plot(r / A0, P, lw=1.6, label=f"n={n}, l={l}")
    ax.set_xlabel("r / a0")
    ax.set_ylabel("radial probability density |R(r)|^2 r^2")
    ax.set_title("Hydrogen radial probability densities")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 25)
    fig2.tight_layout()
    out2 = f"{FIG_DIR}/中心力场与氢原子_径向波函数.svg"
    fig2.savefig(out2, format="svg")
    print("saved", out2)


if __name__ == "__main__":
    main_energy_check()
    main_figures()
