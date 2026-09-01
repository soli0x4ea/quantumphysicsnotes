# Quantum harmonic oscillator: finite-difference spectrum + coherent-state non-spreading.
# Isolated venv: numpy only (no scipy). Natural units hbar=m=omega=1.

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def trapz(y, x):
    # numpy 2.x removed np.trapz; uniform/nonuniform trapezoidal rule.
    return np.sum((y[1:] + y[:-1]) / 2.0 * (x[1:] - x[:-1]))


def finite_diff_oscillator(N=3000, L=18.0, nstates=6):
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    main = 1.0 / dx**2 + 0.5 * x**2          # T = -0.5 d2/dx2, V = 0.5 x^2
    off = -0.5 / dx**2
    H = (np.diag(main)
         + np.diag(np.full(N - 1, off), 1)
         + np.diag(np.full(N - 1, off), -1))
    vals, vecs = np.linalg.eigh(H)
    return x, dx, vals[:nstates], vecs[:, :nstates]


def count_nodes(vec):
    # suppress boundary numerical noise: only count sign flips where both
    # neighbours exceed a small fraction of the peak amplitude.
    mx = np.max(np.abs(vec))
    th = 1.0e-3 * mx
    mask = np.abs(vec) > th
    s = np.sign(vec[mask])
    return int(np.sum((s[1:] * s[:-1]) < 0))


def hermite(n, x):
    if n == 0:
        return np.ones_like(x)
    if n == 1:
        return 2.0 * x
    Hp = np.ones_like(x)
    H = 2.0 * x
    for k in range(2, n + 1):
        Hn = 2.0 * x * H - 2.0 * (k - 1) * Hp
        Hp, H = H, Hn
    return H


def psi_n(n, x):
    norm = 1.0 / math.sqrt(2**n * math.factorial(n)) * (1.0 / math.pi)**0.25
    return norm * hermite(n, x) * np.exp(-x**2 / 2.0)


def coherent_state(alpha, t, Nmax=44, xgrid=None):
    if xgrid is None:
        xgrid = np.linspace(-9, 9, 2400)
    psi = np.zeros_like(xgrid, dtype=complex)
    pre = math.exp(-abs(alpha)**2 / 2.0)
    for n in range(Nmax):
        coeff = (pre * alpha**n / math.sqrt(math.factorial(n))
                 * np.exp(-1j * 1.0 * t * (n + 0.5)))
        psi += coeff * psi_n(n, xgrid)
    return xgrid, psi


def variance_of(rho, xgrid):
    rho = rho / trapz(rho, xgrid)
    mean = trapz(xgrid * rho, xgrid)
    return trapz((xgrid - mean)**2 * rho, xgrid)


def main():
    # ---- part 1: spectrum & nodes ----
    x, dx, evals, evecs = finite_diff_oscillator()
    analytic = np.arange(6) + 0.5
    print("n   E_num        E_ana        rel_err      nodes")
    for n in range(6):
        nodes = count_nodes(evecs[:, n])
        rel = abs(evals[n] - analytic[n]) / analytic[n]
        print(f"{n}   {evals[n]:.10f}  {analytic[n]:.10f}  {rel:.2e}  {nodes}")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.2))
    # energy levels: numeric (bars) vs analytic (markers)
    for n in range(6):
        axL.barh(n, evals[n], height=0.5, color="#4C72B0", alpha=0.75)
        axL.plot(analytic[n], n, "r*", markersize=11)
    axL.set_xlabel("Energy E / (hbar omega)")
    axL.set_ylabel("Quantum number n")
    axL.set_title("Energy levels: numeric (bar) vs analytic (red star)")
    axL.set_xlim(0, 6)
    axL.set_yticks(range(6))
    axL.grid(True, alpha=0.3)

    # wavefunctions n=0,1,2 vs analytic Hermite
    xzoom = np.linspace(-5, 5, 800)
    colors = ["#4C72B0", "#DD8452", "#55A868"]
    for n in range(3):
        axR.plot(xzoom, psi_n(n, xzoom), "-", color=colors[n],
                 label=f"analytic n={n}")
        # interpolate numeric on zoom grid
        num = np.interp(xzoom, x, evecs[:, n])
        num = num / np.sqrt(trapz(num**2, xzoom))  # renormalize on zoom
        axR.plot(xzoom, num, "--", color=colors[n], alpha=0.6, linewidth=1)
    axR.set_xlabel("x / sqrt(hbar/(m omega))")
    axR.set_ylabel("psi(x)")
    axR.set_title("Wavefunctions (solid analytic, dashed numeric)")
    axR.legend(fontsize=8)
    axR.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("figures/量子谐振子_能级与波函数.svg", dpi=140)
    plt.close(fig)
    print("saved figures/量子谐振子_能级与波函数.svg")

    # ---- part 2: coherent state non-spreading ----
    alpha = 2.0
    xg = np.linspace(-9, 9, 2400)
    times = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]
    vars_t = []
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for t in times:
        _, psi = coherent_state(alpha, t, xgrid=xg)
        rho = np.abs(psi) ** 2
        rho = rho / trapz(rho, xg)
        v = variance_of(rho, xg)
        vars_t.append(v)
        center = 2.0 * math.cos(t)  # 2*Re(alpha e^{-i t})
        ax.plot(xg, rho, label=f"t={t/math.pi:.2f} pi, x_c={center:.2f}")
    print("coherent-state variance at 4 phases (analytic base = 0.5):")
    for t, v in zip(times, vars_t):
        print(f"  t={t/math.pi:.2f} pi  Var = {v:.6f}")
    ax.axvline(0, color="gray", lw=0.8, alpha=0.5)
    ax.set_xlabel("x / sqrt(hbar/(m omega))")
    ax.set_ylabel("|psi(x,t)|^2")
    ax.set_title("Coherent state |alpha=2>: centroid oscillates, width constant")
    ax.legend(fontsize=8)
    ax.set_xlim(-6, 6)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("figures/量子谐振子_相干态波包不扩散.svg", dpi=140)
    plt.close(fig)
    print("saved figures/量子谐振子_相干态波包不扩散.svg")


if __name__ == "__main__":
    main()
