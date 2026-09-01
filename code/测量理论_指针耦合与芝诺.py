# -*- coding: utf-8 -*-
"""第 10 篇《测量理论与波函数坍缩》配套脚本。

(a) von Neumann 指针耦合：两能级系统 (|0>,|1>) 与高斯指针耦合，
    演化后系统-指针纠缠 |psi>|phi_0> -> alpha|0>|phi_0(x-lam)> + beta|1>|phi_0(x+lam)>；
    约化系统密度矩阵非对角元幅度 ~ exp(-lam^2/(2 sigma^2))，随指针位移 lam 衰减（测量完成/退相干）。
(b) 量子芝诺效应：两能级在 Rabi 驱动下，每 tau=t/N 投影到初态 |0>，
    存活概率 P(N)=|cos(Omega tau/2)|^{2N} 随 N->inf 趋向 1（演化冻结）。
图注英文；文件名中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def trapz(y, x):
    dx = x[1] - x[0]
    return dx * (np.sum(y) - 0.5 * (y[0] + y[-1]))


def von_neumann_pointer():
    """验证约化密度矩阵非对角元 ~ exp(-lam^2/(2 sigma^2))。"""
    sig = 1.0
    x = np.linspace(-10 * sig, 10 * sig, 4000)
    phi0 = np.exp(-x ** 2 / (2 * sig ** 2)) / np.sqrt(np.sqrt(np.pi) * sig)
    # 归一化检查
    nrm = trapz(phi0 ** 2, x)
    assert abs(nrm - 1.0) < 1e-6, "pointer initial not normalized"
    alpha = np.sqrt(0.6)
    beta = np.sqrt(0.4)
    lambdas = np.array([0.0, 1.0, 2.0, 4.0])
    overlaps = []
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for lam in lambdas:
        # 平移：phi0(x-lam), phi0(x+lam)
        phi_plus = np.interp(x, x - lam, phi0)   # phi0(x-lam)
        phi_minus = np.interp(x, x + lam, phi0)  # phi0(x+lam)
        # 约化系统非对角元幅度 ~ |alpha*beta| * |int phi_minus(x) phi_plus(x) dx|
        ov = trapz(phi_minus * phi_plus, x)
        overlaps.append(ov)
        # 联合概率（忽略相干交叉项，展示两指针分支分离）
        prob = alpha ** 2 * phi_plus ** 2 + beta ** 2 * phi_minus ** 2
        ax.plot(x, prob / prob.max(), "-", lw=1.6,
                label="λ=%.1f σ, overlap=%.4f" % (lam, ov))
    ana = np.exp(-lambdas ** 2 / sig ** 2)
    print("[von Neumann] overlaps num =", ["%.4f" % o for o in overlaps])
    print("[von Neumann] overlaps ana =", ["%.4f" % a for a in ana])
    assert np.max(np.abs(np.array(overlaps) - ana)) < 2e-2, "off-diagonal decay mismatch"
    ax.set_xlabel("pointer coordinate x (σ units)")
    ax.set_ylabel("joint probability |Ψ|² (normalized)")
    ax.set_title("von Neumann coupling: system-pointer entanglement, coherence decays with λ")
    ax.legend(fontsize=8)
    ax.set_xlim(-6, 6)
    fig.tight_layout()
    out1 = os.path.join(FIG_DIR, "测量理论_vonNeumann指针耦合.svg")
    fig.savefig(out1, format="svg")
    plt.close(fig)
    print("[saved]", out1)
    return overlaps, ana


def quantum_zeno():
    """频繁投影到初态 |0>，存活概率随测量次数 N 趋向 1。"""
    Omega = 1.0
    t_total = np.pi  # 半 Rabi 周期
    Ns = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512])
    Ps = []
    for N in Ns:
        tau = t_total / N
        c = np.cos(Omega * tau / 2.0)
        P = abs(c) ** (2 * N)  # |<0|U(tau)|0>|^{2N}
        Ps.append(P)
    Ps = np.array(Ps)
    print("[zeno] N=1 P=%.6f (expect 0.0), N=512 P=%.6f (->1)" % (Ps[0], Ps[-1]))
    assert abs(Ps[0]) < 1e-9, "single half-period measurement must give P=0"
    assert Ps[-1] > 0.99, "frequent measurement must freeze evolution (P->1)"
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.semilogx(Ns, Ps, "o-", lw=1.6, color="#d62728")
    ax.axhline(1.0, color="k", lw=0.6, ls="--")
    ax.set_xlabel("number of measurements N")
    ax.set_ylabel("survival probability P(N)")
    ax.set_title("Quantum Zeno effect: frequent measurement freezes evolution")
    ax.set_ylim(-0.05, 1.1)
    fig.tight_layout()
    out2 = os.path.join(FIG_DIR, "测量理论_量子芝诺效应.svg")
    fig.savefig(out2, format="svg")
    plt.close(fig)
    print("[saved]", out2)
    return Ns, Ps


def main():
    von_neumann_pointer()
    quantum_zeno()


if __name__ == "__main__":
    main()
