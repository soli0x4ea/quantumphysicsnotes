# 角动量与自旋_两自旋单态三重态.py
# 对应笔记：第 16 篇《角动量与自旋》 §2.6, §6.1
# 构造两自旋 1/2 的 Bell 态，计算单态约化密度矩阵与纠缠熵，绘制自旋关联
# 依赖：numpy, matplotlib（隔离 venv）
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Pauli matrices
sx = np.array([[0,1],[1,0]], dtype=complex)
sy = np.array([[0,-1j],[1j,0]], dtype=complex)
sz = np.array([[1,0],[0,-1]], dtype=complex)

# basis |up>, |down>
up = np.array([1,0], dtype=complex)
dn = np.array([0,1], dtype=complex)

# Bell states
# |S>  singlet  (|ud>-|du>)/sqrt2
# |T+> (|uu>)
# |T0> (|ud>+|du>)/sqrt2
# |T-> (|dd>)
S  = (np.kron(up,dn) - np.kron(dn,up))/np.sqrt(2)
Tp = np.kron(up,up)
T0 = (np.kron(up,dn) + np.kron(dn,up))/np.sqrt(2)
Tm = np.kron(dn,dn)

def reduced(rho):
    # partial trace over subsystem B (last qubit) for 2x2 system
    rhoA = np.zeros((2,2), dtype=complex)
    for a in range(2):
        for a2 in range(2):
            rhoA[a,a2] = (rho[2*a+0, 2*a2+0] + rho[2*a+1, 2*a2+1])
    return rhoA

def vn_entropy(rho):
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 1e-12]
    return float(-np.sum(ev*np.log(ev)))

# reduced density matrix of singlet
rhoS = np.outer(S, S.conj())
rhoA_S = reduced(rhoS)
print("Singlet reduced rho_A =\n", np.real_if_close(rhoA_S))
print("Singlet entropy S =", vn_entropy(rhoA_S), "nat =", vn_entropy(rhoA_S)/np.log(2), "ebit")

# spin correlation <sigma_a . n1><sigma_b . n2> for a singlet/triplet |1,0>
# singlet: - n1 . n2 ; triplet T0: + n1 . n2  (anti-parallel vs parallel)
theta = np.linspace(0, np.pi, 200)
corr_singlet = -np.cos(theta)
corr_T0 = +np.cos(theta)

# ---- panel 1: reduced density matrix heatmap ----
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
im = axes[0].imshow(np.real(rhoA_S), cmap="Blues", vmin=0, vmax=0.5)
axes[0].set_xticks([0,1]); axes[0].set_yticks([0,1])
axes[0].set_xticklabels([r"$|\uparrow\rangle$", r"$|\downarrow\rangle$"])
axes[0].set_yticklabels([r"$|\uparrow\rangle$", r"$|\downarrow\rangle$"])
axes[0].set_title(r"Singlet reduced $\rho_A = \mathbb{1}/2$")
for i in range(2):
    for j in range(2):
        axes[0].text(j, i, f"{np.real(rhoA_S[i,j]):.2f}", ha="center", va="center")
fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

# ---- panel 2: spin correlation ----
axes[1].plot(theta, corr_singlet, color="#c0392b", lw=2, label="singlet $|S\\rangle$")
axes[1].plot(theta, corr_T0, color="#2c3e88", lw=2, label=r"triplet $|1,0\rangle$")
axes[1].axhline(0, color="k", lw=0.6)
axes[1].set_xlabel(r"angle $\theta$ between measurement axes")
axes[1].set_ylabel(r"$\langle\boldsymbol{\sigma}_1\!\cdot\!\hat a\,\boldsymbol{\sigma}_2\!\cdot\!\hat b\rangle$")
axes[1].set_title("Spin correlations: anti-parallel vs parallel")
axes[1].legend(frameon=False)

fig.suptitle("Two spin-1/2: singlet (maximally entangled) vs triplet")
fig.tight_layout()
fig.savefig("figures/角动量与自旋_两自旋单态三重态.svg", bbox_inches="tight")
print("saved figures/角动量与自旋_两自旋单态三重态.svg")
