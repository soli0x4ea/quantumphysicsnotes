# -*- coding: utf-8 -*-
"""
One-dimensional potentials: rectangular barrier transmission and finite square well.

Verifies the analytic results in note 14 (L3):
  - Exact transmission T(E) for a rectangular barrier, thick-barrier limit T ~ exp(-2 kappa a)
  - Finite square well bound-state energies from even/odd parity transcendental equations,
    with wavefunctions and node count (node theorem).

Environment: isolated venv (numpy only; no scipy). Use numpy.linalg-free root finding.
Figures saved as Chinese-named SVGs (consistent with note references).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HBAR = 1.054571817e-34      # J*s (CODATA 2018/2022)
ME = 9.1093837015e-31       # kg (electron)
EV = 1.602176634e-19        # J

FIG_DIR = "/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures"


# ---------- rectangular barrier transmission ----------
def transmission(E_J, V0_J, a_m, m=ME):
    """Exact transmission probability for a rectangular barrier (E < V0)."""
    if E_J <= 0 or E_J >= V0_J:
        return np.nan
    k = np.sqrt(2.0 * m * E_J) / HBAR
    kap = np.sqrt(2.0 * m * (V0_J - E_J)) / HBAR
    arg = kap * a_m
    sinh2 = np.sinh(arg) ** 2
    T = 1.0 / (1.0 + V0_J**2 * sinh2 / (4.0 * E_J * (V0_J - E_J)))
    return T


def thick_limit(E_J, V0_J, a_m, m=ME):
    k = np.sqrt(2.0 * m * E_J) / HBAR
    kap = np.sqrt(2.0 * m * (V0_J - E_J)) / HBAR
    return 16.0 * E_J * (V0_J - E_J) / V0_J**2 * np.exp(-2.0 * kap * a_m)


def main_barrier():
    V0 = 1.0 * EV
    a = 1.0e-9
    Es = np.linspace(0.02 * EV, 0.98 * EV, 400)
    Ts = np.array([transmission(E, V0, a) for e in Es for E in [e]])  # keep shape
    # simpler vectorized
    Ts = np.array([transmission(E, V0, a) for E in Es])
    # T vs width at fixed E = 0.3 eV
    Efix = 0.3 * EV
    as_ = np.linspace(0.1e-9, 3.0e-9, 400)
    Ts_a = np.array([transmission(Efix, V0, aw) for aw in as_])
    Tl_a = np.array([thick_limit(Efix, V0, aw) for aw in as_])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.plot(Es / EV, Ts, "b-", lw=2, label="exact T(E)")
    ax1.set_xlabel("E / V0 (dimensionless, V0 = 1 eV)")
    ax1.set_ylabel("Transmission T")
    ax1.set_title("Rectangular barrier: T vs incident energy (a = 1 nm)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(as_ / 1e-9, Ts_a, "b-", lw=2, label="exact T(a)")
    ax2.plot(as_ / 1e-9, Tl_a, "r--", lw=1.5, label="thick-barrier exp(-2 kappa a)")
    ax2.set_xlabel("barrier width a (nm)")
    ax2.set_ylabel("Transmission T")
    ax2.set_title("T vs barrier width (E = 0.3 eV), thin-barrier deviates")
    ax2.set_yscale("log")
    ax2.grid(True, alpha=0.3, which="both")
    ax2.legend()

    fig.tight_layout()
    out = f"{FIG_DIR}/一维势场_方势垒透射系数.svg"
    fig.savefig(out, format="svg")
    print("saved", out)
    # numeric checks
    T_at_03 = transmission(0.3 * EV, V0, a)
    print(f"T(E=0.3eV, a=1nm) = {T_at_03:.4e}  (thick limit {thick_limit(0.3*EV,V0,a):.4e})")


# ---------- finite square well bound states ----------
def well_energies(V0_J, L_m, m=ME, nmax=12):
    """Return bound-state energies (J, negative) by solving even/odd equations."""
    kmax = np.sqrt(2.0 * m * V0_J) / HBAR
    ks = np.linspace(1e-6, kmax * (1 - 1e-6), 200000)
    # even: f = k*tan(kL/2) - sqrt(kmax^2 - k^2)
    fe = ks * np.tan(ks * L_m / 2.0) - np.sqrt(kmax**2 - ks**2)
    # odd:  f = -k*cot(kL/2) - sqrt(kmax^2 - k^2)
    fo = -ks / np.tan(ks * L_m / 2.0) - np.sqrt(kmax**2 - ks**2)
    energies = []
    for f in (fe, fo):
        s = np.sign(f)
        for i in range(len(ks) - 1):
            if s[i] == 0 or s[i] != s[i + 1]:
                # bisect in this bracket
                lo, hi = ks[i], ks[i + 1]
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    fm = mid * np.tan(mid * L_m / 2.0) - np.sqrt(kmax**2 - mid**2)
                    if (fe is f):
                        pass
                    fmid = mid * np.tan(mid * L_m / 2.0) - np.sqrt(kmax**2 - mid**2)
                    fmid = fmid if (f is fe) else (-mid / np.tan(mid * L_m / 2.0) - np.sqrt(kmax**2 - mid**2))
                    if np.sign(fmid) == np.sign(f[i]) or fmid == 0:
                        lo = mid
                    else:
                        hi = mid
                kroot = 0.5 * (lo + hi)
                E = HBAR**2 * kroot**2 / (2.0 * m) - V0_J
                energies.append(E)
    return sorted(energies)[:nmax]


def well_wavefunction(kroot, V0_J, L_m, m=ME, x=None, parity=None):
    if x is None:
        x = np.linspace(-3 * L_m, 3 * L_m, 2000)
    k = kroot
    kap = np.sqrt(2.0 * m * V0_J / HBAR**2 - k**2)
    psi = np.where(np.abs(x) <= L_m / 2.0,
                   np.cos(k * x),                       # even
                   np.cos(k * L_m / 2.0) * np.exp(-kap * (np.abs(x) - L_m / 2.0)))
    if parity == "odd":
        psi = np.where(np.abs(x) <= L_m / 2.0,
                       np.sin(k * x),
                       np.sin(k * L_m / 2.0) * np.exp(-kap * (np.abs(x) - L_m / 2.0)))
    # normalize
    dx = x[1] - x[0]
    norm = np.sqrt(np.sum(psi**2) * dx)
    return x, psi / norm


def main_well():
    V0 = 0.5 * EV
    L = 2.0e-9
    ens = well_energies(V0, L)
    print(f"finite well: {len(ens)} bound states found")
    for i, E in enumerate(ens):
        print(f"  E_{i+1} = {E/EV:.4f} eV  (n^2 infinite-well ref {(i+1)**2*np.pi**2*HBAR**2/(2*ME*L**2)/EV:.4f} eV)")

    # reconstruct wavefunctions for plotting (parity: state 1 even, 2 odd, ...)
    kmax = np.sqrt(2 * ME * V0) / HBAR
    ks = np.linspace(1e-6, kmax * (1 - 1e-6), 200000)
    fe = ks * np.tan(ks * L / 2.0) - np.sqrt(kmax**2 - ks**2)
    fo = -ks / np.tan(ks * L / 2.0) - np.sqrt(kmax**2 - ks**2)
    roots = []
    for f in (fe, fo):
        s = np.sign(f)
        for i in range(len(ks) - 1):
            if s[i] == 0 or s[i] != s[i + 1]:
                lo, hi = ks[i], ks[i + 1]
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    fmid = (mid * np.tan(mid * L / 2.0) - np.sqrt(kmax**2 - mid**2)) if (f is fe) \
                           else (-mid / np.tan(mid * L / 2.0) - np.sqrt(kmax**2 - mid**2))
                    if np.sign(fmid) == np.sign(f[i]) or fmid == 0:
                        lo = mid
                    else:
                        hi = mid
                roots.append(0.5 * (lo + hi))
    roots = sorted(roots)

    fig, (axw, axe) = plt.subplots(1, 2, figsize=(11, 4.6))
    x = np.linspace(-3 * L, 3 * L, 2000)
    nshow = min(5, len(roots))
    for idx in range(nshow):
        parity = "even" if idx % 2 == 0 else "odd"
        _, psi = well_wavefunction(roots[idx], V0, L, parity=parity, x=x)
        nodes = int(np.sum(np.diff(np.sign(psi)) != 0))
        axw.plot(x / 1e-9, psi + idx * 0.6, label=f"n={idx+1} (nodes={nodes})")
    axw.axvspan(-L / 2 / 1e-9, L / 2 / 1e-9, color="orange", alpha=0.15, label="well region")
    axw.set_xlabel("x (nm)")
    axw.set_ylabel("psi (offset for clarity)")
    axw.set_title("Finite square well: lowest bound-state wavefunctions")
    axw.legend(fontsize=8)
    axw.grid(True, alpha=0.3)

    # energy level diagram
    for idx, E in enumerate(ens):
        axw.axhline(idx * 0.6, color="gray", lw=0.5)
    en_ev = np.array([E / EV for E in ens])
    for i, e in enumerate(en_ev):
        axe.plot([0, 1], [e, e], "b-", lw=2)
        axe.text(1.02, e, f"n={i+1}", fontsize=8)
    axe.axhline(0.0, color="k", lw=1.0, label="V=0 (asymptote)")
    axe.axhline(V0 / EV, color="r", ls="--", lw=1.0, label=f"well bottom = -{V0/EV:.1f} eV")
    axe.set_xlim(0, 1.3)
    axe.set_ylabel("Energy (eV)")
    axe.set_title(f"Bound-state energies ({len(ens)} states)")
    axe.legend(fontsize=8)
    axe.grid(True, alpha=0.3)

    fig.tight_layout()
    out = f"{FIG_DIR}/一维势场_有限深势阱.svg"
    fig.savefig(out, format="svg")
    print("saved", out)


if __name__ == "__main__":
    main_barrier()
    main_well()
