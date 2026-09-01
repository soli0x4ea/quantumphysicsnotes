# 绘景变换与密度矩阵_两能级Rabi.py
# 对应笔记：第 18 篇《绘景变换与密度矩阵》 §2.4, §6.1
# 两能级系统在薛定谔绘景与相互作用绘景下积分，验证二者期望值完全等价
# 哈密顿量 H = H0 + V, H0 = (hbar*omega/2) sz, V = (hbar*Omega/2) sx
# 单位取 hbar = 1（无量纲时间）。依赖：numpy, matplotlib（隔离 venv）
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Pauli matrices
sx = np.array([[0,1],[1,0]], dtype=complex)
sy = np.array([[0,-1j],[1j,0]], dtype=complex)
sz = np.array([[1,0],[0,-1]], dtype=complex)

# parameters (hbar = 1)
omega = 1.0    # detuning / Larmor precession rate
Omega = 2.0    # drive (Rabi) rate
psi0 = np.array([1,0], dtype=complex)   # initial |up>

# ---- Schrodinger picture: closed-form expm for 2x2 Hermitian H ----
# H = (omega/2) sz + (Omega/2) sx ; eigenvalues +/- Omega_R/2, Omega_R = sqrt(omega^2+Omega^2)
Omega_R = np.sqrt(omega**2 + Omega**2)
cphi = Omega/Omega_R
sphi = omega/Omega_R
# expm(-i H t) = cos(Omega_R t/2) I - i sin(Omega_R t/2) (cphi sx + sphi sz)
def U_S(t):
    return np.cos(Omega_R*t/2)*np.eye(2) - 1j*np.sin(Omega_R*t/2)*(cphi*sx + sphi*sz)

# ---- Interaction picture: RK4 integrate d|psi_I>/dt = -i V_I(t) |psi_I> ----
# V_I(t) = (Omega/2)(cos(omega t) sx - sin(omega t) sy)
def dpsi_I(t, psi):
    VI = (Omega/2.0)*(np.cos(omega*t)*sx - np.sin(omega*t)*sy)
    return -1j*VI.dot(psi)

def rk4(t, psi, dt):
    k1 = dpsi_I(t, psi)
    k2 = dpsi_I(t+dt/2, psi+dt/2*k1)
    k3 = dpsi_I(t+dt/2, psi+dt/2*k2)
    k4 = dpsi_I(t+dt,   psi+dt*k3)
    return psi + dt/6.0*(k1+2*k2+2*k3+k4)

# ---- scan time ----
ts = np.linspace(0, 8*np.pi, 400)
N = len(ts)
exp_S = np.zeros(N)     # <sz> Schrodinger
exp_I = np.zeros(N)     # <sz> interaction (sz_I(t)=sz since commutes with H0)
psi_I = psi0.copy()
dt = ts[1]-ts[0]
exp_S[0] = np.real((U_S(ts[0]) @ psi0).conj().T @ sz @ (U_S(ts[0]) @ psi0))
exp_I[0] = np.real(psi_I.conj().T @ sz @ psi_I)
for n in range(1, N):
    # Schrodinger expectation
    psiS = U_S(ts[n]) @ psi0
    exp_S[n] = np.real(psiS.conj().T @ sz @ psiS)
    # interaction picture: advance from ts[n-1] to ts[n]
    psi_I = rk4(ts[n-1], psi_I, dt)
    exp_I[n] = np.real(psi_I.conj().T @ sz @ psi_I)

max_diff = np.max(np.abs(exp_S - exp_I))
print(f"max |<sz>_S - <sz>_I| = {max_diff:.3e}  (picture equivalence)")

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(ts, exp_S, color="#c0392b", lw=2.0, label="Schrödinger picture $\\langle\\sigma_z\\rangle_S$")
ax.plot(ts, exp_I, color="#2c3e88", lw=1.6, ls="--", label="Interaction picture $\\langle\\sigma_z\\rangle_I$")
ax.set_xlabel(r"time $t$ ($\hbar=1$)")
ax.set_ylabel(r"$\langle\sigma_z\rangle$")
ax.set_title("Picture equivalence: identical predictions (two-level Rabi)")
ax.legend(frameon=False)
ax.set_ylim(-1.1, 1.1)
fig.tight_layout()
fig.savefig("figures/绘景变换与密度矩阵_两能级Rabi.svg", bbox_inches="tight")
print("saved figures/绘景变换与密度矩阵_两能级Rabi.svg")
