#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPR 佯谬与贝尔不等式 —— CHSH 数值验证脚本
对应笔记：《EPR佯谬与贝尔不等式（EPR Paradox and Bell Inequalities）系统量子力学笔记》
对应公式：笔记 (2.9) CHSH 组合量、(2.12) 自旋单态关联函数、(2.14) Tsirelson 界

验证五件事：
  1. 定域隐变量模型下 |S| <= 2（枚举全部 16 种取值组合）
  2. 自旋单态 |Psi-> 的 CHSH 值随角度变化，最大值 = 2*sqrt(2)
  3. 光子偏振纠缠态 |Phi+> 的 CHSH 值，Bell 角配置下达 2*sqrt(2)
  4. Tsirelson 界：随机采样测量方向，CHSH 值不超过 2*sqrt(2)
  5. 历代实验实测值与 2 / 2*sqrt(2) 两条界线的对比

依赖：numpy, matplotlib
运行：~/.workbuddy/binaries/python/envs/default/bin/python EPR与Bell不等式_CHSH.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from itertools import product
import os

# ---------- 全局绘图风格（浅色主题，与笔记 HTML 展示一致） ----------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": "#ffffff",
    "figure.facecolor": "#ffffff",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#1a1a1a",
    "text.color": "#1a1a1a",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "axes.grid": True,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
})

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

TSIRELSON = 2.0 * np.sqrt(2.0)


def chsh_from_correlators(E_ab, E_abp, E_apb, E_apbp):
    """CHSH 组合量 S = E(a,b) - E(a,b') + E(a',b) + E(a',b')（笔记式 2.9）"""
    return E_ab - E_abp + E_apb + E_apbp


# =====================================================================
# 1. 定域隐变量模型：枚举证明 |S| <= 2
# =====================================================================
def lhv_enumerate():
    """枚举 A(a), A(a'), B(b), B(b') 全部 16 种 ±1 取值，验证 |S| <= 2"""
    max_absS = 0.0
    for Aa, Aap, Bb, Bbp in product([-1, 1], repeat=4):
        S = Aa * Bb - Aa * Bbp + Aap * Bb + Aap * Bbp
        max_absS = max(max_absS, abs(S))
    return max_absS


# =====================================================================
# 2. 自旋单态：E(a,b) = -a·b，扫描共面角度
# =====================================================================
def E_singlet(theta_a, theta_b):
    """自旋单态关联函数，测量方向共面（笔记式 2.12）"""
    return -np.cos(theta_a - theta_b)


def singlet_scan():
    """
    固定 a = 0，取 a' 与 b 对称张开的经典最优族：
    a = 0, b = +phi, a' = 2*phi, b' = 3*phi
    S(phi) = -cos(phi) + cos(3phi) - cos(phi) - cos(phi)
    在 phi = pi/4 处取极值 -2*sqrt(2)
    """
    phi = np.linspace(0, np.pi / 2, 1000)
    S = (-np.cos(phi) + np.cos(3 * phi) - np.cos(phi) - np.cos(phi))
    idx = np.argmax(np.abs(S))
    return phi, S, phi[idx], S[idx]


# =====================================================================
# 3. 光子偏振纠缠态 |Phi+> = (|HH> + |VV>)/sqrt(2)
#    E(theta_a, theta_b) = cos(2*(theta_a - theta_b))
# =====================================================================
def E_phipol(theta_a, theta_b):
    """偏振纠缠关联函数（笔记式 2.13）；theta 为偏振片物理转角"""
    return np.cos(2.0 * (theta_a - theta_b))


def photon_scan():
    """
    取 a = 0, a' = 2*phi, b = phi, b' = 3*phi（相邻间隔均为 phi）。
    代入 E = cos 2(θa - θb)：
        S(phi) = E(a,b) - E(a,b') + E(a',b) + E(a',b')
               = cos(2phi) - cos(6phi) + cos(2phi) + cos(-2phi)
               = 3*cos(2phi) - cos(6phi)
    极值条件 dS/dphi = -6 sin(2phi) + 6 sin(6phi) = 0
        => sin(6phi) = sin(2phi) => 8*phi = pi => phi = 22.5 deg
    此时 S = 3*cos(45°) - cos(135°) = 3*(√2/2) + √2/2 = 2√2，
    对应的正是标准 Bell 角配置 (0°, 45° | 22.5°, 67.5°)。
    """
    phi = np.linspace(0, np.pi / 4, 2000)
    a, ap = 0.0, 2 * phi
    b, bp = phi, 3 * phi
    S = (E_phipol(a, b) - E_phipol(a, bp)
         + E_phipol(ap, b) + E_phipol(ap, bp))
    idx = np.argmax(np.abs(S))
    return phi, S, phi[idx], S[idx]


# =====================================================================
# 4. Tsirelson 界：随机采样测量方向
# =====================================================================
def tsirelson_sampling(n=200000, seed=42):
    """
    对自旋单态随机采样 a, a', b, b' 四个三维单位矢量，
    计算 S = -a·b + a·b' - a'·b - a'·b'，验证不超过 2*sqrt(2)
    """
    rng = np.random.default_rng(seed)
    def rand_unit():
        v = rng.normal(size=(n, 3))
        return v / np.linalg.norm(v, axis=1, keepdims=True)
    a, ap, b, bp = rand_unit(), rand_unit(), rand_unit(), rand_unit()
    dot = lambda u, v: np.sum(u * v, axis=1)
    S = -dot(a, b) + dot(a, bp) - dot(ap, b) - dot(ap, bp)
    return S


# =====================================================================
# 4b. Bell 1964 原始不等式的违反样例（笔记式 2.10）
#     |P(a,b) - P(a,c)| <= 1 + P(b,c)，依赖完美反关联假设
# =====================================================================
def bell1964_violation():
    """a 垂直于 b，c 位于 a、b 平面内且与两者各成 45 度"""
    # P(a,b) = -a·b（自旋单态）
    Pab = 0.0                                   # a 垂直于 b
    Pac = -np.cos(np.radians(45.0))             # a 与 c 夹角 45 度
    Pbc = -np.cos(np.radians(45.0))             # b 与 c 夹角 45 度
    lhs = abs(Pab - Pac)
    rhs = 1.0 + Pbc
    return lhs, rhs


# =====================================================================
# 4c. 退极化（Werner）信道的 CHSH：rho = p|Psi-><Psi-| + (1-p) I/4
#     E(a,b) = -p a·b  =>  |S| = p * 2*sqrt(2)，违反需 p > 1/sqrt(2)
# =====================================================================
def werner_threshold():
    p = np.linspace(0, 1, 10001)
    S = p * TSIRELSON
    idx = np.argmax(S > 2.0)
    return p, S, p[idx]


# =====================================================================
# 5. 实验实测值
# =====================================================================
EXPERIMENTS = [
    # (标签, S 实测值, 不确定度, 年份, 体系, 文献)
    ("Freedman & Clauser 1972", None, None, 1972, "Ca cascade",
     "PRL 28, 938"),
    ("Aspect et al. 1982 (2ch)", 2.697, 0.015, 1982, "Ca cascade",
     "PRL 49, 91"),
    ("Rowe et al. 2001", 2.25, 0.03, 2001, "Be+ ions",
     "Nature 409, 791"),
    ("Hensen et al. 2015", 2.42, 0.20, 2015, "NV centres",
     "Nature 526, 682"),
]


def main():
    print("=" * 68)
    print("EPR 与 Bell 不等式 —— CHSH 数值验证")
    print("=" * 68)

    # --- 1 ---
    maxS = lhv_enumerate()
    print("\n[1] 定域隐变量模型（枚举 16 种 ±1 取值组合）")
    print(f"    max |S| = {maxS:.6f}   -> 定域实在论上界 = 2")
    assert abs(maxS - 2.0) < 1e-12, "LHV 界应当恰为 2"

    # --- 2 ---
    phi, S_sing, phi_best, S_best = singlet_scan()
    print("\n[2] 自旋单态 |Psi-> 共面角度扫描")
    print(f"    最优 phi = {np.degrees(phi_best):.3f} deg")
    print(f"    S(phi*) = {S_best:.6f}   (|S| = {abs(S_best):.6f})")
    print(f"    Tsirelson 界 2*sqrt(2) = {TSIRELSON:.6f}")
    assert abs(abs(S_best) - TSIRELSON) < 1e-3

    # --- 3 ---
    theta, S_ph, th_best, Sph_best = photon_scan()
    print("\n[3] 光子偏振纠缠 |Phi+> 角度扫描（a=0, a'=45deg, b=-theta, b'=+theta）")
    print(f"    最优 theta = {np.degrees(th_best):.3f} deg")
    print(f"    S(theta*) = {Sph_best:.6f}")
    assert abs(Sph_best - TSIRELSON) < 1e-3

    # 标准 Bell 角配置
    a, ap = 0.0, np.radians(45.0)
    b, bp = np.radians(22.5), np.radians(67.5)
    S_bell_angles = chsh_from_correlators(
        E_phipol(a, b), E_phipol(a, bp), E_phipol(ap, b), E_phipol(ap, bp))
    print(f"    Bell 角配置 (0, 45 | 22.5, 67.5) deg -> S = {S_bell_angles:.6f}")

    # --- 4 ---
    S_rand = tsirelson_sampling()
    print("\n[4] Tsirelson 界随机采样检验（n = 200000）")
    print(f"    max  S = {S_rand.max():.6f}")
    print(f"    min  S = {S_rand.min():.6f}")
    print(f"    超出 2*sqrt(2) 的样本数 = {np.sum(np.abs(S_rand) > TSIRELSON + 1e-9)}")
    assert S_rand.max() <= TSIRELSON + 1e-9

    # --- 4b ---
    lhs, rhs = bell1964_violation()
    print("\n[4b] Bell (1964) 原始不等式违反样例（a 垂直 b，c 与两者各 45 度）")
    print(f"    |P(a,b) - P(a,c)| = {lhs:.6f}")
    print(f"    1 + P(b,c)        = {rhs:.6f}")
    print(f"    违反：{lhs > rhs}（超出量 {lhs - rhs:.6f}）")
    assert lhs > rhs

    # --- 4c ---
    p_grid, S_werner, p_thr = werner_threshold()
    print("\n[4c] 退极化（Werner）信道  rho = p|Psi-><Psi-| + (1-p)I/4")
    print(f"    |S|(p) = p * 2*sqrt(2)")
    print(f"    违反 CHSH 的临界白噪声比例 p* = {p_thr:.4f}")
    print(f"    解析值 1/sqrt(2) = {1/np.sqrt(2):.6f}")
    assert abs(p_thr - 1 / np.sqrt(2)) < 1e-3

    # --- 5 ---
    print("\n[5] 历代实验实测值对比")
    print(f"    {'实验':<28}{'S':>10}{'±':>8}{'偏离 LHV 界':>14}")
    for label, S, err, *_ in EXPERIMENTS:
        if S is not None:
            print(f"    {label:<28}{S:>10.3f}{err:>8.3f}{(S - 2.0):>14.3f}")
        else:
            print(f"    {label:<28}{'(见注)':>10}")
    print("    注：Freedman & Clauser 1972 检验的是 CHSH 的前身形式，")
    print("        其原始论文给出的是关联函数比值而非标准 CHSH 的 S，")
    print("        故此处不代入 S 数值，避免误读。")

    # ================= 绘图 =================
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3))

    # 左：自旋单态
    ax = axes[0]
    ax.plot(np.degrees(phi), S_sing, color="#c0392b", lw=2.0,
            label=r"spin singlet  $|S(\phi)|$")
    ax.plot(np.degrees(phi), np.abs(S_sing), color="#c0392b", lw=1.2, ls=":")
    ax.axhline(2.0, color="#2c3e50", lw=1.4, ls="--", label=r"LHV bound  $|S|=2$")
    ax.axhline(-2.0, color="#2c3e50", lw=1.4, ls="--")
    ax.axhline(TSIRELSON, color="#27ae60", lw=1.4, ls="-.",
               label=r"Tsirelson bound  $2\sqrt{2}$")
    ax.axhline(-TSIRELSON, color="#27ae60", lw=1.4, ls="-.")
    ax.axvline(np.degrees(phi_best), color="#8e44ad", lw=1.0, ls=":",
               label=rf"$\phi^*={np.degrees(phi_best):.1f}^\circ$")
    ax.set_xlabel(r"coplanar angle offset  $\phi$  (deg)")
    ax.set_ylabel(r"CHSH combination  $S$")
    ax.set_title(r"Spin singlet: $E(\mathbf{a},\mathbf{b})=-\mathbf{a}\cdot\mathbf{b}$",
                 fontsize=10.5)
    ax.set_ylim(-3.1, 3.1)
    ax.legend(fontsize=8.2, loc="lower right")

    # 右：光子偏振 + 实验点
    ax = axes[1]
    ax.plot(np.degrees(theta), S_ph, color="#2980b9", lw=2.0,
            label=r"$|\Phi^+\rangle$ polarisation entanglement")
    ax.axhline(2.0, color="#2c3e50", lw=1.4, ls="--", label=r"LHV bound  $S=2$")
    ax.axhline(TSIRELSON, color="#27ae60", lw=1.4, ls="-.",
               label=r"Tsirelson bound  $2\sqrt{2}$")
    ax.axvline(np.degrees(th_best), color="#8e44ad", lw=1.0, ls=":",
               label=rf"$\theta^*={np.degrees(th_best):.2f}^\circ$")
    for label, S, err, year, *_ in EXPERIMENTS:
        if S is None:
            continue
        ax.errorbar(0, 0, fmt="none")  # 占位，避免图例重复
    ax.set_xlabel(r"analyser offset  $\theta$  (deg)")
    ax.set_ylabel(r"CHSH combination  $S$")
    ax.set_title(r"Photon pair: $E(\theta_a,\theta_b)=\cos 2(\theta_a-\theta_b)$",
                 fontsize=10.5)
    ax.set_ylim(1.6, 3.1)
    ax.legend(fontsize=8.2, loc="lower right")

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "EPR与Bell不等式_CHSH.svg")
    fig.savefig(out, format="svg", bbox_inches="tight")
    print(f"\n[图] 已输出：{out}")

    # ================= 第二张图：实验里程碑时间线 =================
    fig2, ax2 = plt.subplots(figsize=(9.0, 4.0))
    labels, vals, errs, colors = [], [], [], []
    cmap = {"Ca cascade": "#c0392b", "Be+ ions": "#8e44ad", "NV centres": "#16a085"}
    for label, S, err, year, sysname, ref in EXPERIMENTS:
        if S is None:
            continue
        labels.append(f"{label}\n{sysname}")
        vals.append(S)
        errs.append(err)
        colors.append(cmap.get(sysname, "#34495e"))
    ypos = np.arange(len(labels))
    ax2.errorbar(vals, ypos, xerr=errs, fmt="o", color="#2c3e50",
                 ecolor="#7f8c8d", elinewidth=1.6, capsize=4, markersize=7,
                 markerfacecolor="#ecf0f1", zorder=3)
    for i, c in enumerate(colors):
        ax2.scatter(vals[i], ypos[i], s=55, color=c, zorder=4)
    ax2.axvline(2.0, color="#2c3e50", lw=1.6, ls="--", label=r"LHV bound  $S=2$")
    ax2.axvline(TSIRELSON, color="#27ae60", lw=1.6, ls="-.",
                label=r"Tsirelson bound  $2\sqrt{2}$")
    ax2.set_yticks(ypos)
    ax2.set_yticklabels(labels, fontsize=8.6)
    ax2.set_xlabel(r"measured CHSH value  $S$")
    ax2.set_title("Reported CHSH / Bell-parameter values (selected experiments)",
                  fontsize=10.5)
    ax2.set_xlim(1.9, 3.0)
    ax2.legend(fontsize=8.6, loc="lower right")
    fig2.tight_layout()
    out2 = os.path.join(OUT_DIR, "EPR与Bell不等式_实验时间线.svg")
    fig2.savefig(out2, format="svg", bbox_inches="tight")
    print(f"[图] 已输出：{out2}")

    print("\n" + "=" * 68)
    print("全部断言通过：LHV 界 = 2，量子最大值 = 2*sqrt(2) = "
          f"{TSIRELSON:.6f}")
    print("=" * 68)


if __name__ == "__main__":
    main()
