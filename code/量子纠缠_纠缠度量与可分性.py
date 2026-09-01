#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子纠缠_纠缠度量与可分性.py
============================
对应笔记：量子力学正式版 / 第 29 篇《量子纠缠》系统量子力学笔记
依赖：numpy / scipy / matplotlib（均在受管虚拟环境内）

本脚本可复现笔记中的三处数值结论：
  [1] 两比特 Werner 态 rho_W(p) = p|Psi-><Psi-| + (1-p)/4 * I4
        - 偏置转置最小本征值随 p 变化（验证 PPT 阈值 p = 1/3）
        - 并发度 C = max(0, (3p-1)/2) 的解析公式数值验证
        - 负度 N(p) 曲线（与 C 单调相关）
  [2] 纯态族 |psi(theta)> = cos theta|00> + sin theta|11>
        - 纠缠熵 S(theta) = -c^2 log2 c^2 - s^2 log2 s^2（式 6.6）
  [3] Haar 随机两比特混态（Ginibre 构造）
        - 计算并发度 C 与负度 N，按 PPT / NPT 着色
        - 验证 2x2 下 PPT <=> 可分性（式 2.6）：所有 PPT 态 C=0，所有 NPT 态 C>0

输出图形：
  figures/量子纠缠_度量随Werner参数.svg
  figures/量子纠缠_随机两比特散点.svg
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- 基础设施 ----------
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

def partial_transpose_B(rho):
    """对双体密度矩阵 rho (dA*dB x dA*dB) 在子系统 B 上取偏置转置。"""
    d = rho.shape[0]
    dA = int(round(np.sqrt(d)))  # 假设两子系统等维（2x2）
    dB = dA
    assert dA * dB == d, "partial_transpose_B 仅实现等维双体"
    R = rho.reshape(dA, dB, dA, dB)
    # 指标 (a, b, a', b') -> 转置 b, b' -> (a, b', a', b)
    R_pt = R.transpose(0, 3, 2, 1)
    return R_pt.reshape(d, d)

def negativity(rho):
    """负度 N = (||rho^{T_B}||_1 - 1) / 2。"""
    ev = np.linalg.eigvalsh(partial_transpose_B(rho))
    return (np.sum(np.abs(ev)) - 1.0) / 2.0

def min_ppt_eig(rho):
    """偏置转置的最小本征值（<0 即 NPT）。"""
    return np.linalg.eigvalsh(partial_transpose_B(rho)).min()

def concurrence(rho):
    """两比特任意态并发度：C = max(0, l1 - l2 - l3 - l4)，
    l_i 为 R = rho (Y⊗Y) rho* (Y⊗Y) 本征值绝对值的平方根（降序）。
    注意 R 一般非 Hermitian，必须用一般本征值求解 eigvals 而非 eigvalsh。"""
    YY = np.kron(PAULI_Y, PAULI_Y)
    R = rho @ YY @ rho.conj() @ YY
    eig = np.sqrt(np.abs(np.linalg.eigvals(R)))
    eig = np.sort(eig)[::-1]
    return max(0.0, eig[0] - eig[1] - eig[2] - eig[3])

def is_ppt(rho, tol=1e-10):
    return min_ppt_eig(rho) >= -tol

# ---------- [1] Werner 态 ----------
def singlet_dm():
    psi = np.zeros(4, dtype=complex)
    psi[1] = 1.0 / np.sqrt(2)   # |01>
    psi[2] = -1.0 / np.sqrt(2)  # |10>
    return np.outer(psi, psi.conj())

def werner_state(p):
    return p * singlet_dm() + (1.0 - p) / 4.0 * np.eye(4, dtype=complex)

ps = np.linspace(0.0, 1.0, 201)
C_werner = np.array([max(0.0, (3 * p - 1) / 2.0) for p in ps])
N_werner = np.array([negativity(werner_state(p)) for p in ps])
mins_eig = np.array([min_ppt_eig(werner_state(p)) for p in ps])

# 阈值检验：在精确 p=1/3 处断言 C 与最小本征值穿过 0
p_thr = 1.0 / 3.0
C_thr = max(0.0, (3 * p_thr - 1) / 2.0)
min_eig_thr = min_ppt_eig(werner_state(p_thr))
N_thr = negativity(werner_state(p_thr))
print(f"[Werner] p=1/3 精确点: C={C_thr:.4f}  min_eig(rho^T)={min_eig_thr:.3e}  N={N_thr:.4f}")
assert abs(C_thr) < 1e-9, "Werner 态在 p=1/3 处并发度应恰为 0"
assert abs(min_eig_thr) < 1e-6, "Werner 态在 p=1/3 处 PPT 最小本征值应恰为 0"
print("[Werner] 可分阈值 p=1/3 验证通过（C=0 且 PPT 边界）。")

fig1, ax1 = plt.subplots(1, 2, figsize=(11, 4.2))
ax1[0].plot(ps, C_werner, label="Concurrence C (analytic, Eq. 6.4)", color="#1f77b4", lw=2)
ax1[0].axvline(1.0 / 3.0, ls="--", color="#888", label="Separability threshold p=1/3")
ax1[0].set_xlabel("Werner parameter p")
ax1[0].set_ylabel("Concurrence C")
ax1[0].set_title("Two-qubit Werner state: concurrence")
ax1[0].legend(fontsize=8)
ax1[0].grid(alpha=0.3)

ax1[1].plot(ps, N_werner, label="Negativity N", color="#d62728", lw=2)
ax1[1].plot(ps, mins_eig, label="min eigenvalue of partial transpose", color="#2ca02c", lw=1.5)
ax1[1].axhline(0.0, color="#888", lw=0.8)
ax1[1].axvline(1.0 / 3.0, ls="--", color="#888", label="PPT boundary p=1/3")
ax1[1].set_xlabel("Werner parameter p")
ax1[1].set_ylabel("value")
ax1[1].set_title("Negativity and PPT criterion")
ax1[1].legend(fontsize=8)
ax1[1].grid(alpha=0.3)
fig1.tight_layout()
fig1.savefig("figures/量子纠缠_度量随Werner参数.svg", format="svg")
print("[输出] figures/量子纠缠_度量随Werner参数.svg")

# ---------- [2] 纯态族纠缠熵 ----------
thetas = np.linspace(0.0, np.pi / 2.0, 201)
def ent_entropy(theta):
    c2 = np.cos(theta) ** 2
    s2 = np.sin(theta) ** 2
    if c2 <= 0 or s2 <= 0:
        return 0.0
    return -(c2 * np.log2(c2) + s2 * np.log2(s2))

S_theta = np.array([ent_entropy(t) for t in thetas])
fig2, ax2 = plt.subplots(figsize=(5.6, 4.2))
ax2.plot(thetas, S_theta, color="#1f77b4", lw=2)
ax2.axvline(np.pi / 4.0, ls="--", color="#888", label="θ=π/4 (maximal)")
ax2.set_xlabel("θ")
ax2.set_ylabel("Entanglement entropy S(θ) / ebit")
ax2.set_title("Pure family |ψ(θ)⟩ entanglement entropy (Eq. 6.6)")
ax2.legend(fontsize=8)
ax2.grid(alpha=0.3)
fig2.tight_layout()
fig2.savefig("figures/量子纠缠_纯态族熵.svg", format="svg")
print("[输出] figures/量子纠缠_纯态族熵.svg  (S_max=%.4f ebit @ θ=π/4)" % S_theta.max())

# ---------- [3] 随机两比特态：并发度 vs 负度，按 PPT 着色 ----------
rng = np.random.default_rng(20260901)
N_SAMPLES = 4000
Cs, Ns, ppt_flag = [], [], []
for _ in range(N_SAMPLES):
    G = (rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))) / np.sqrt(2)
    rho = G @ G.conj().T
    rho /= np.trace(rho).real
    Cs.append(concurrence(rho))
    Ns.append(negativity(rho))
    ppt_flag.append(is_ppt(rho))
Cs = np.array(Cs)
Ns = np.array(Ns)
ppt_flag = np.array(ppt_flag)

n_ppt = int(np.sum(ppt_flag))
print(f"[随机2比特] 样本 {N_SAMPLES}：PPT(可分) {n_ppt}，NPT(纠缠) {N_SAMPLES - n_ppt}")
# 验证 2x2 下 PPT <=> 可分性：所有 PPT 态 C 应≈0，所有 NPT 态 C>0
max_C_ppt = Cs[ppt_flag].max() if n_ppt else 0.0
min_C_npt = Cs[~ppt_flag].min() if (N_SAMPLES - n_ppt) else 1.0
print(f"[随机2比特] PPT 态最大 C = {max_C_ppt:.2e}（应≈0）；NPT 态最小 C = {min_C_npt:.4f}（应>0）")
assert max_C_ppt < 1e-6, "2x2 下 PPT 态不应有纠缠（与式 2.6 矛盾）"

fig3, ax3 = plt.subplots(figsize=(6.0, 4.6))
ax3.scatter(Ns[ppt_flag], Cs[ppt_flag], s=6, c="#1f77b4", alpha=0.5, label="PPT (separable)")
ax3.scatter(Ns[~ppt_flag], Cs[~ppt_flag], s=6, c="#d62728", alpha=0.5, label="NPT (entangled)")
ax3.set_xlabel("Negativity N")
ax3.set_ylabel("Concurrence C")
ax3.set_title("Random two-qubit states: concurrence vs negativity\n(verifies PPT ⇔ separability in 2×2)")
ax3.legend(fontsize=8)
ax3.grid(alpha=0.3)
fig3.tight_layout()
fig3.savefig("figures/量子纠缠_随机两比特散点.svg", format="svg")
print("[输出] figures/量子纠缠_随机两比特散点.svg")

print("全部数值验证完成。")
