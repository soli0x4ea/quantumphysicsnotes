# -*- coding: utf-8 -*-
"""
量子测量与退相干_退相干动力学.py
================================

对应笔记: 量子测量与退相干_系统笔记.md  (第 31 篇, 第四部分 量子信息与量子光学, L3)

本脚本复现该篇 §6 的数值/解析式, 并输出两张 SVG 图 (图内文字全部用英文 ASCII, 避免 CJK 缺失与 mathtext 解析风险).

公式对应:
  (6.1)(6.2) 两能级系统振幅阻尼与退相位  -> 图2(a)
  (6.3)(6.4) 位置叠加退相干时间 (Caldeira-Leggett 高温布朗模型) -> 图1
  (6.5)      腔 QED 猫态 Wigner 负性衰减 -> 图2(c)
  §2.7/§6.4 指针基 (einselection) 形成演示 -> 图2(b)

依赖: numpy, scipy, matplotlib  (已装于 managed venv)
运行: ~/.workbuddy/binaries/python/envs/default/bin/python 量子测量与退相干_退相干动力学.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 无头环境
import matplotlib.pyplot as plt

# ---- 基本常数 (CODATA 2022) ----
HBAR = 1.054571817e-34      # J·s
KB   = 1.380649e-23         # J/K  (exact since 2019, CODATA 2022)
ETA  = 1.8e-5               # Pa·s  空气动力黏度 (量级)
TENV = 300.0                # K     环境温度


def fig_decoherence_timescale():
    """图1: 退相干时间 tau_D 随球体半径 a 的变化 (式 6.4, 布朗模型, 取 Δx = a)."""
    a = np.logspace(-9, -3, 400)          # 半径 1 nm .. 1 mm
    # tau_D = hbar^2 / (12 pi eta kB T a^3)
    tau = HBAR**2 / (12.0 * np.pi * ETA * KB * TENV * a**3)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.loglog(a, tau, color="#1f4e79", lw=2.2,
              label=r"tau_D(a) = hbar^2 / (12 pi eta kB T a^3)")

    # 标注几个尺度
    for aa, label in [(1e-9, "atomic ~1 nm"),
                      (1e-6, "dust ~1 um"),
                      (1e-3, "macro ~1 mm")]:
        tt = HBAR**2 / (12.0 * np.pi * ETA * KB * TENV * aa**3)
        ax.plot(aa, tt, "o", color="#c0392b")
        ax.annotate("%s\ntau_D ~ %.0e s" % (label, tt),
                    xy=(aa, tt), xytext=(aa * 1.6, tt * 4),
                    fontsize=8, color="#c0392b",
                    arrowprops=dict(arrowstyle="->", color="#c0392b"))

    # 可观测时间参考线
    for tt_obs, lab in [(1.0, "1 s (human)"), (1e-3, "1 ms"), (1e-12, "1 ps")]:
        ax.axhline(tt_obs, color="#7f8c8d", ls=":", lw=0.9)
        ax.text(1.05e-9, tt_obs, lab, fontsize=7, color="#7f8c8d", va="center")

    ax.set_xlabel("object radius  a  (m)")
    ax.set_ylabel("decoherence time  tau_D  (s)")
    ax.set_title("Decoherence timescale vs object size\n(Caldeira-Leggett Brownian model, air 300 K, dx=a)")
    ax.set_ylim(1e-45, 1e5)
    ax.grid(True, which="both", ls="--", lw=0.4, alpha=0.5)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig("figures/量子测量与退相干_退相干时间尺度.svg", format="svg")
    print("[OK] figures/量子测量与退相干_退相干时间尺度.svg")
    plt.close(fig)


def fig_twolevel_pointer_cat():
    """图2: (a) 两能级 T1/T2 衰减  (b) 指针基 einselection 演示  (c) 腔 QED 猫态 Wigner 负性."""
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.6))

    # ---- (a) 两能级振幅阻尼 + 退相位 ----
    ax = axes[0]
    gamma = 1.0                      # 1/T1
    t = np.linspace(0, 5, 400)
    rho_ee = np.exp(-gamma * t)                 # 式 6.1
    rho_eg = np.exp(-(gamma / 2.0) * t)         # 式 6.2 (取 |·|)
    ax.plot(t, rho_ee, color="#1f4e79", lw=2, label="rho_ee(t) = exp(-t/T1)")
    ax.plot(t, rho_eg, color="#c0392b", lw=2, label="|rho_eg(t)| = exp(-t/(2 T1))")
    ax.set_xlabel("time  t  (T1 = 1)")
    ax.set_ylabel("density-matrix element")
    ax.set_title("(a) Two-level decay:  T2 = 2 T1")
    ax.set_ylim(0, 1.05)
    ax.grid(True, ls="--", lw=0.4, alpha=0.5)
    ax.legend(fontsize=8)

    # ---- (b) 指针基 einselection 演示 ----
    # 环境耦合到位置 x -> 退相干核 exp(-(x-x')^2 t / tau0)
    # 初态 A: 位置叠加 (|x0>+|-x0>)/sqrt2  -> 其非对角 <x0|rho|-x0> 衰减
    # 初态 B: 位置对角混态 0.5|x0><x0|+0.5|-x0><-x0| -> 非对角恒为 0 (稳健)
    ax = axes[1]
    x0 = 1.0
    tau0 = 0.6
    tt = np.linspace(0, 4, 400)
    coh_superpos = np.exp(-(2 * x0) ** 2 * tt / (2 * tau0))   # 位置叠加相干
    coh_mixture = np.zeros_like(tt)                            # 对角混态, 无相干
    ax.plot(tt, coh_superpos, color="#c0392b", lw=2,
            label="position superposition (|x0>+|-x0>)/sqrt2")
    ax.plot(tt, coh_mixture, color="#27ae60", lw=2, ls="--",
            label="position-diagonal mixture (classical record)")
    ax.set_xlabel("time  t")
    ax.set_ylabel("off-diagonal coherence  |<x0|rho|-x0>|")
    ax.set_title("(b) Pointer basis (einselection)\nenv. couples to x -> position survives")
    ax.set_ylim(0, 1.05)
    ax.grid(True, ls="--", lw=0.4, alpha=0.5)
    ax.legend(fontsize=7)

    # ---- (c) 腔 QED 猫态 Wigner 负性衰减 (式 6.5) ----
    # 负性 N(t) = 0.5*int|W| - 1 ; 对损耗通道衰减率 Gamma_cat = 2 kappa |alpha|^2
    ax = axes[2]
    kappa = 1.0
    for alpha, c in [(1.0, "#1f4e79"), (2.0, "#c0392b"), (3.0, "#8e44ad")]:
        g = 2.0 * kappa * alpha**2
        N = np.exp(-g * t)   # 趋势: 单指数衰减, 速率 Gamma_cat = 2 kappa |alpha|^2
        ax.plot(t, N, color=c, lw=2, label="|alpha|=%g, Gamma_cat=%g" % (alpha, g))
    ax.set_xlabel("time  t  (1/kappa = 1)")
    ax.set_ylabel("Wigner negativity  N(t)")
    ax.set_title("(c) Cavity-QED cat decoherence\nGamma_cat = 2 kappa |alpha|^2 (Brune 1996)")
    ax.set_ylim(0, 1.05)
    ax.grid(True, ls="--", lw=0.4, alpha=0.5)
    ax.legend(fontsize=7)

    fig.tight_layout()
    fig.savefig("figures/量子测量与退相干_两能级与指针基.svg", format="svg")
    print("[OK] figures/量子测量与退相干_两能级与指针基.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig_decoherence_timescale()
    fig_twolevel_pointer_cat()
    print("[DONE] article-31 figures generated.")
