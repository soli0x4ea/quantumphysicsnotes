# -*- coding: utf-8 -*-
"""
Path integral: free-particle (Euclidean) propagator time-slicing convergence,
and harmonic-oscillator ground state via Euclidean (imaginary-time) projection.

Natural units: m = hbar = omega = 1.
Deterministic (no Monte Carlo). numpy only (isolated venv, no scipy).
Figure captions in English to avoid CJK font issues in SVG; filenames Chinese.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

HBAR = 1.0
FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def free_euclidean_kernel_matrix(x, eps):
    """Euclidean short-time free-particle kernel K0(x',x; eps) on grid x, as a matrix."""
    dx = x[1] - x[0]
    m = 1.0
    diff2 = np.subtract.outer(x, x) ** 2
    K = np.sqrt(m / (2.0 * np.pi * HBAR * eps)) * np.exp(-m * diff2 / (2.0 * HBAR * eps))
    return K * dx  # include grid measure dx -> matrix multiplication approximates integral


def analytic_free_euclidean_modsq(x, T):
    m = 1.0
    K = np.sqrt(m / (2.0 * np.pi * HBAR * T)) * np.exp(-m * x**2 / (2.0 * HBAR * T))
    return np.abs(K) ** 2


def example1_free_propagator():
    L = 30.0
    Nx = 800
    x = np.linspace(-L / 2, L / 2, Nx)
    dx = x[1] - x[0]
    T = 4.0
    # initial narrow gaussian (normalized)
    sigma0 = 0.5
    psi0 = np.exp(-(x ** 2) / (4.0 * sigma0 ** 2))
    psi0 = psi0 / np.sqrt(np.sum(psi0 ** 2) * dx)
    # reference: single-step Euclidean convolution at total time T (P_T includes dx measure)
    PT = free_euclidean_kernel_matrix(x, T)
    psi_ana = PT @ psi0
    norm_a = np.sqrt(np.sum(np.abs(psi_ana) ** 2) * dx)
    rows = []
    for N in (4, 8, 16, 32, 64):
        eps = T / N
        P = free_euclidean_kernel_matrix(x, eps)
        PN = P
        for _ in range(1, N):
            PN = PN @ P
        psi_num = PN @ psi0
        rel = np.sqrt(np.sum(np.abs(psi_num - psi_ana) ** 2) * dx) / norm_a
        rows.append((N, rel))
        print(f"[free] N={N:3d}  relative error = {rel:.3e}")
    # plot: reference profile + numeric profile for N=64, and convergence curve
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    P = free_euclidean_kernel_matrix(x, T / 64)
    PN = P
    for _ in range(1, 64):
        PN = PN @ P
    psi64 = PN @ psi0
    ax1.plot(x, np.abs(psi_ana) ** 2 / norm_a, "-", color="#1f77b4", lw=1.6,
             label="single-step (analytic kernel)")
    ax1.plot(x, np.abs(psi64) ** 2 / np.sqrt(np.sum(np.abs(psi64) ** 2) * dx), "--",
             color="#d62728", lw=1.2, label="sliced N=64")
    ax1.set_xlabel("x")
    ax1.set_ylabel("normalized |psi(x,T)|^2")
    ax1.set_title("Euclidean free-particle wave-packet evolution (T=4)")
    ax1.legend(fontsize=8)
    ax1.set_xlim(-12, 12)

    Ns = [r[0] for r in rows]
    errs = [r[1] for r in rows]
    ax2.loglog(Ns, errs, "o-", color="#2ca02c", label="rel. error")
    ax2.loglog(Ns, [1.0 / n for n in Ns], "k:", lw=1.0, label="~1/N reference")
    ax2.set_xlabel("number of time slices N")
    ax2.set_ylabel("relative error vs reference")
    ax2.set_title("Time-slicing convergence of path integral")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "路径积分_自由粒子传播子收敛.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print(f"[free] saved {out}")


def osc_euclidean_kernel(x, eps):
    """Symmetric Trotter Euclidean short-time kernel for HO V=x^2/2."""
    dx = x[1] - x[0]
    m = 1.0
    V = 0.5 * x ** 2
    diff2 = np.subtract.outer(x, x) ** 2
    free = np.sqrt(m / (2.0 * np.pi * HBAR * eps)) * np.exp(-m * diff2 / (2.0 * HBAR * eps))
    K = np.outer(np.exp(-eps * V / (2 * HBAR)), np.exp(-eps * V / (2 * HBAR))) * free
    return K * dx


def example2_osc_ground_state():
    L = 18.0
    Nx = 800
    x = np.linspace(-L / 2, L / 2, Nx)
    dx = x[1] - x[0]
    eps = 0.02
    KE = osc_euclidean_kernel(x, eps)
    # initial narrow gaussian (normalized)
    w = np.exp(-(x ** 2) / (2 * 0.5 ** 2))
    w = w / np.sqrt(np.sum(w ** 2) * dx)
    rows = []
    M_total = 200
    every = 20
    prev_norm = np.sqrt(np.sum(w ** 2) * dx)  # = 1.0
    plot_wave = w
    for M in range(1, M_total + 1):
        w = KE @ w  # unnormalized: norm = prev_norm * exp(-eps*E0/hbar)
        cur_norm = np.sqrt(np.sum(w ** 2) * dx)
        E0 = -(HBAR / eps) * np.log(cur_norm / prev_norm)
        prev_norm = cur_norm
        if M % every == 0:
            rows.append((M, E0))
            print(f"[osc] M={M:3d}  projected E0 = {E0:.4f}  (analytic 0.5000)")
        # normalize only a copy for plotting (do not break the unnormalized energy chain)
        plot_wave = w / cur_norm
    # analytic ground state |psi0| propto exp(-x^2/2)
    psi0_ana = np.exp(-x ** 2 / 2)
    psi0_ana = psi0_ana / np.sqrt(np.sum(psi0_ana ** 2) * dx)
    vn = plot_wave / np.sqrt(np.sum(plot_wave ** 2) * dx)
    maxdev = np.max(np.abs(vn - psi0_ana))
    print(f"[osc] max pointwise deviation from gaussian = {maxdev:.3e}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.plot(x, vn ** 2, "-", color="#1f77b4", lw=1.6, label="path-integral projected")
    ax1.plot(x, psi0_ana ** 2, "--", color="#d62728", lw=1.2, label="analytic |psi0|^2=exp(-x^2)")
    ax1.set_xlabel("x")
    ax1.set_ylabel("|psi_0(x)|^2")
    ax1.set_title("Harmonic oscillator ground state (Euclidean projection)")
    ax1.legend(fontsize=8)
    ax1.set_xlim(-5, 5)

    Ms = [r[0] for r in rows]
    Es = [r[1] for r in rows]
    ax2.plot(Ms, Es, "o-", color="#2ca02c", label="projected E0")
    ax2.axhline(0.5, color="k", ls=":", lw=1.0, label="analytic hbar*omega/2 = 0.5")
    ax2.set_xlabel("iteration step M (tau = M*eps)")
    ax2.set_ylabel("E0")
    ax2.set_title("Ground-state energy convergence")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "路径积分_谐振子虚时间基态.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print(f"[osc] saved {out}")


if __name__ == "__main__":
    example1_free_propagator()
    example2_osc_ground_state()
    print("ALL DONE")
