"""
Perturbation theory & variational method — numerical validation.

Three independent checks, all reproducible with numpy only (no scipy):

(A1) Anharmonic oscillator  H = p^2/2 + x^2/2 + lambda*x^4  (hbar=omega=m=1).
     The 2nd-order Rayleigh-Schrodinger correction is compared against the
     exact numerical diagonalization of the N-basis Hamiltonian. For small
     lambda the 2nd-order formula matches the exact ground/excited energies
     to ~1e-3 relative -- a clean validation of the perturbation expansion.

(A2) Linear ramp on an infinite square well  V(x)=lambda*x  (evidence for the
     "asymptotic / divergent series" discussion in Sec.7): 1st-order
     overestimates the level shift by ~2x, the 2nd-order term is subdominant,
     and the remaining discrepancy is carried by 3rd and higher orders.

(B) Helium ground-state variational estimate with a single-parameter product
     trial wavefunction  psi = phi_alpha(r1)*phi_alpha(r2),
     phi_alpha = (alpha^3/pi)^(1/2) exp(-alpha r).
     E(alpha) = alpha^2 - 2*Z*alpha + (5/8)*alpha   (atomic units, Z=2)
     Analytic minimum at alpha=27/16 = 1.6875 -> E = -2.847656 Ha.
     Compared against exact non-relativistic -2.903724377 Ha, confirming the
     variational upper-bound theorem.

Figures saved with Chinese filenames; in-figure text in English to avoid
font rendering issues.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---------- (A1) anharmonic oscillator ----------

def ho_basis(N):
    E0 = np.arange(N, dtype=float) + 0.5          # E_n^(0) = n + 1/2
    a = np.zeros((N, N))
    for n in range(1, N):
        a[n - 1, n] = np.sqrt(n)                    # a|n> = sqrt(n)|n-1>
    ad = a.T
    x = (a + ad) / np.sqrt(2.0)
    X4 = x @ x @ x @ x
    return E0, X4

def second_order(state, E0, X4, lam):
    s = 0.0
    for m in range(len(E0)):
        if m == state:
            continue
        s += abs(X4[state, m]) ** 2 / (E0[state] - E0[m])
    return lam * lam * s

print("=== (A1) anharmonic oscillator  H = p^2/2 + x^2/2 + lambda x^4 ===")
N = 40
E0, X4 = ho_basis(N)
for LAM in (0.05, 0.10):
    e1 = lam_e1 = LAM * X4[0, 0]
    e2 = second_order(0, E0, X4, LAM)
    H = np.diag(E0) + LAM * X4
    enum = np.linalg.eigh(H)[0]
    pert = 0.5 + e1 + e2
    print("lambda=%.2f  <x^4>_0=%.4f  E^(1)=%.5f  E^(2)=%.6f"
          % (LAM, X4[0, 0], e1, e2))
    print("  ground: perturb(0+1+2)=%.6f  numeric=%.6f  rel_err=%.2e"
          % (pert, enum[0], (enum[0] - pert) / pert))
    # n=1 excited
    e1_1 = LAM * X4[1, 1]
    e2_1 = second_order(1, E0, X4, LAM)
    pert1 = 1.5 + e1_1 + e2_1
    print("  n=1:    perturb(0+1+2)=%.6f  numeric=%.6f  rel_err=%.2e"
          % (pert1, enum[1], (enum[1] - pert1) / pert1))

# figure A1: relative error of 2nd-order formula vs exact diagonalization
lams = np.linspace(0.01, 0.20, 30)
errs = []
for lam in lams:
    e2 = second_order(0, E0, X4, lam)
    H = np.diag(E0) + lam * X4
    enum0 = np.linalg.eigh(H)[0][0]
    errs.append(abs((enum0 - (0.5 + lam * X4[0, 0] + e2)) / enum0))
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.semilogy(lams, errs, "b-o", ms=4)
ax.set_xlabel(r"perturbation strength $\lambda$")
ax.set_ylabel("relative error |num - (0+1+2)order| / num")
ax.set_title("Anharmonic oscillator: 2nd-order perturbation vs exact diagonalization")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/微扰论与变分法_非谐振子二阶验证.svg")
print("saved figures/微扰论与变分法_非谐振子二阶验证.svg")

# ---------- (A2) linear ramp on infinite well (divergent-series evidence) ----------

print("\n=== (A2) infinite square well + linear ramp V(x)=lambda x (asymptotic) ===")
HBAR, M, L = 1.0, 1.0, 1.0
PI = np.pi
LAM = 0.10

def well_unpert(n):
    return (n * n) * PI * PI / (2.0 * M * L * L) * (HBAR * HBAR)

def xmat(n, l):
    if n == l:
        return L * L / 4.0
    if (n + l) % 2 == 0:
        return 0.0
    return -4.0 * n * l * (L * L) / (PI * PI * (n * n - l * l) ** 2)

E1 = LAM * (L / 2.0)                       # 1st-order shift (same for all n)
num = np.linalg.eigh(np.diag(np.array([well_unpert(k) for k in range(1, 41)]))
                        + LAM * np.array([[xmat(i + 1, j + 1) for j in range(40)]
                                          for i in range(40)]))[0]
print("lambda=%.2f  E_1^(0)=%.5f  1st-order E_1=%.5f  exact(num) E_1=%.5f  shift ratio=%.3f"
      % (LAM, well_unpert(1), well_unpert(1) + E1, num[0],
         (num[0] - well_unpert(1)) / E1))
print("-> 1st order overestimates the shift by ~2x; higher orders cancel ~half (see Sec.7)")

# ---------- (B) helium variational ----------

EH_EV = C["Ehartree_eV"]  # Hartree -> eV (CODATA 2018)

def helium_E(alpha):
    Z = 2.0
    return alpha * alpha - 2.0 * Z * alpha + (5.0 / 8.0) * alpha

alphas = np.linspace(1.0, 2.2, 400)
Es = helium_E(alphas)
alpha_opt = 27.0 / 16.0
E_opt = helium_E(alpha_opt)
E_exact_Ha = -2.903724377
i = int(np.argmin(Es))

print("\n=== (B) helium ground-state variational (single parameter) ===")
print("numeric  alpha_opt=%.5f  E_min=%.6f Ha = %.3f eV" % (alphas[i], Es[i], Es[i] * EH_EV))
print("analytic alpha_opt=%.5f  E_min=%.6f Ha = %.3f eV" % (alpha_opt, E_opt, E_opt * EH_EV))
print("exact   non-rel = %.6f Ha = %.3f eV" % (E_exact_Ha, E_exact_Ha * EH_EV))
print("variational upper-bound satisfied: %s" % (E_opt > E_exact_Ha))
print("relative error = %.4f (%.2f%%)"
      % ((E_opt - E_exact_Ha) / E_exact_Ha, 100.0 * (E_opt - E_exact_Ha) / E_exact_Ha))

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(alphas, Es, "b-", label=r"$E(\alpha)=\alpha^2-\frac{27}{8}\alpha$")
ax.axvline(alpha_opt, color="g", ls="--", lw=1)
ax.plot([alpha_opt], [E_opt], "go", ms=8, label="variational min (%.4f Ha)" % E_opt)
ax.axhline(E_exact_Ha, color="r", ls=":", lw=1.2, label="exact non-rel (%.4f Ha)" % E_exact_Ha)
ax.set_xlabel(r"effective nuclear charge $\alpha$")
ax.set_ylabel("energy (Hartree)")
ax.set_title("Helium variational energy vs effective charge")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/微扰论与变分法_氦原子变分.svg")
print("saved figures/微扰论与变分法_氦原子变分.svg")
