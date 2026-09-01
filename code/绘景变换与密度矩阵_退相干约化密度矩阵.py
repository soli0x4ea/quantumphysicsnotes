# 绘景变换与密度矩阵_退相干约化密度矩阵.py
# 对应笔记：第 18 篇《绘景变换与密度矩阵》 §2.6, §6.2  (链接第 31 篇《退相干》)
# 纠缠 Bell 单态经退相位噪声后，约化密度矩阵非对角元按 e^{-Gamma t} 衰减，熵升至 ln2
# 依赖：numpy, matplotlib（隔离 venv）
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# reduced density matrix of subsystem (Bell singlet attacked by dephasing)
# rho_A(t) = 1/2 [[1, e^{-Gamma t}], [e^{-Gamma t}, 1]]
Gamma = 1.0
t = np.linspace(0, 4.0, 300)
offdiag = np.exp(-Gamma*t)                 # coherence amplitude
purity = 0.5*(1.0 + offdiag**2)            # Tr(rho^2) = (1+e^{-2Gamma t})/2

# von Neumann entropy S = -Tr(rho ln rho)
# eigenvalues of rho_A = 1/2 (1 +/- e^{-Gamma t})
def vn_entropy(t):
    ev1 = 0.5*(1.0 + np.exp(-Gamma*t))
    ev2 = 0.5*(1.0 - np.exp(-Gamma*t))
    ev1 = np.clip(ev1, 1e-15, 1)
    ev2 = np.clip(ev2, 1e-15, 1)
    return -(ev1*np.log(ev1) + ev2*np.log(ev2))
S = vn_entropy(t)

print(f"t=0 : coherence={offdiag[0]:.3f}, purity={purity[0]:.3f}, S={S[0]/np.log(2):.3f} ebit")
print(f"t->inf: purity->{purity[-1]:.3f}, S->{S[-1]/np.log(2):.3f} ebit (max mixed)")

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
# left: coherence and purity vs t
axes[0].plot(t, offdiag, color="#c0392b", lw=2, label=r"off-diagonal $\rho_{12}(t)$")
axes[0].plot(t, purity, color="#2c3e88", lw=2, label=r"purity $\mathrm{Tr}\,\rho^2$")
axes[0].set_xlabel(r"$t$")
axes[0].set_ylabel("amplitude")
axes[0].set_title("Decoherence: off-diagonal decays, purity drops")
axes[0].legend(frameon=False)
axes[0].set_ylim(-0.05, 1.1)

# right: von Neumann entropy vs t (ebits)
axes[1].plot(t, S/np.log(2), color="#1e7d3a", lw=2, label=r"$S(\rho_A)/\ln2$")
axes[1].axhline(1.0, color="k", lw=0.6, ls=":")
axes[1].set_xlabel(r"$t$")
axes[1].set_ylabel(r"entanglement entropy (ebit)")
axes[1].set_title("Entropy rises from 0 to 1 ebit")
axes[1].legend(frameon=False)
axes[1].set_ylim(-0.05, 1.15)

fig.suptitle(r"Reduced density matrix under dephasing: off-diagonal decays as $\exp(-\Gamma t)$")
fig.tight_layout()
fig.savefig("figures/绘景变换与密度矩阵_退相干约化密度矩阵.svg", bbox_inches="tight")
print("saved figures/绘景变换与密度矩阵_退相干约化密度矩阵.svg")
