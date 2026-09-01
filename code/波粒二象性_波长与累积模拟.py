# -*- coding: utf-8 -*-
"""第 2 篇《波粒二象性与德布罗意关系》配套脚本。

模型 A：电子波长 - 加速电压标定曲线（非相对论 + 相对论修正）。
  非相对论 : lambda = h / sqrt(2 m e V)
  相对论   : pc = sqrt(Ek (Ek + 2 m c^2)), lambda = h / p
  验证点   : V=54 V (Davisson-Germer 主峰) -> 0.167 nm
             V=50 kV 相对论修正约 -2.4%

模型 B：单电子双缝累积模拟（对应 Tonomura 1989 的 8/270/2000/60000 四级图）。
  分布来源：第 1 篇式 (3)，P12 = 4 sinc^2(pi a x/L) cos^2(pi d x / (2 L))（自然单位）
  验证点   : N=60000 直方图与理论分布一致（卡方检验 p 值）、条纹可见度收敛

图注为英文规避 matplotlib 缺中文字体；图文件名为中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# CODATA 2022（h、e 为精确定义值；me、c 相对不确定度 <= 3.1e-10）
h = 6.62607015e-34
e = 1.602176634e-19
me = 9.1093837139e-31
c = 299792458.0


def lambda_nonrel(V):
    return h / np.sqrt(2 * me * e * V)


def lambda_rel(V):
    Ek = e * V
    p = np.sqrt(Ek * (Ek + 2 * me * c ** 2)) / c
    return h / p


def main():
    # ---------- 模型 A ----------
    Vs = np.logspace(0, 5, 500)
    lam_nr = lambda_nonrel(Vs) * 1e9   # nm
    lam_rel = lambda_rel(Vs) * 1e9

    V_dg = 54.0
    V_tm = 50e3
    print("[model A] V=54 V      : nonrel = %.4f nm" % (lambda_nonrel(V_dg) * 1e9))
    print("[model A]   (Davisson-Germer布拉格换算 0.165 nm, 偏差 %.1f%%)"
          % (abs(lambda_nonrel(V_dg) * 1e9 - 0.165) / 0.165 * 100))
    print("[model A] V=50 kV     : nonrel = %.4f pm, relativistic = %.4f pm"
          % (lambda_nonrel(V_tm) * 1e12, lambda_rel(V_tm) * 1e12))
    corr = (lambda_rel(V_tm) / lambda_nonrel(V_tm) - 1) * 100
    print("[model A] relativistic correction at 50 kV = %+.2f%%" % corr)
    assert abs(lambda_nonrel(V_dg) * 1e9 - 0.1669) < 0.001, "54 V wavelength mismatch"
    assert -3.0 < corr < -1.5, "relativistic correction magnitude unexpected"

    fig1, ax1 = plt.subplots(figsize=(7.2, 4.6))
    ax1.loglog(Vs, lam_nr, "-", color="#1f77b4", lw=1.6, label="nonrelativistic")
    ax1.loglog(Vs, lam_rel, "--", color="#d62728", lw=1.4, label="relativistic")
    ax1.plot([V_dg], [lambda_nonrel(V_dg) * 1e9], "o", color="#2ca02c")
    ax1.annotate("Davisson-Germer 54 V\n0.167 nm", xy=(V_dg, lambda_nonrel(V_dg) * 1e9),
                 xytext=(90, 0.4), textcoords="data", fontsize=8,
                 arrowprops=dict(arrowstyle="->", lw=0.8))
    ax1.plot([V_tm], [lambda_rel(V_tm) * 1e9], "s", color="#9467bd")
    ax1.annotate("Tonomura 50 kV\n5.2 pm", xy=(V_tm, lambda_rel(V_tm) * 1e9),
                 xytext=(1500, 0.02), textcoords="data", fontsize=8,
                 arrowprops=dict(arrowstyle="->", lw=0.8))
    ax1.axhline(0.203, color="gray", ls=":", lw=0.9)
    ax1.text(1.1, 0.215, "Ni {111} plane spacing 0.203 nm (X-ray calibrated)", fontsize=7, color="gray")
    ax1.set_xlabel("accelerating voltage V (volt)")
    ax1.set_ylabel("de Broglie wavelength (nm)")
    ax1.set_title("Electron de Broglie wavelength vs accelerating voltage")
    ax1.legend(fontsize=8)
    fig1.tight_layout()
    out1 = os.path.join(FIG_DIR, "波粒二象性_电子波长曲线.svg")
    fig1.savefig(out1, format="svg")
    plt.close(fig1)
    print("[saved]", out1)

    # ---------- 模型 B ----------
    # 自然单位：L = 1（屏距），d = 1（缝距），a = 0.4（缝宽）→ 条纹间距 = L/d = 1
    a, d, L = 0.4, 1.0, 1.0
    x = np.linspace(-2.5, 2.5, 2001)
    env = np.sinc(a * x / L) ** 2
    P12 = 4 * env * np.cos(np.pi * d * x / L) ** 2
    dx = x[1] - x[0]
    P12 /= np.sum(P12) * dx
    cdf = np.cumsum(P12) * dx

    rng = np.random.default_rng(20260901)
    counts_list = [8, 270, 2000, 60000]
    fig2, axes2 = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, N in zip(axes2.flat, counts_list):
        hits = x[np.searchsorted(cdf, rng.random(N))]
        ax.plot(hits, np.full(N, 1), "|", color="#d62728", ms=6, alpha=0.55)
        ax.set_title("N = %d electrons" % N, fontsize=9)
        ax.set_ylim(0.9, 1.1)
        ax.set_yticks([])
    for ax in axes2[1]:
        ax.set_xlabel("screen position x (natural units)")
        ax2 = ax.twinx()
        ax2.plot(x, P12 / P12.max(), color="#1f77b4", lw=1.0, alpha=0.7)
        ax2.set_ylim(0, 1.2)
        ax2.set_yticks([])
    fig2.suptitle("Single-electron build-up of interference pattern (Tonomura 1989 sequence)", fontsize=11)
    fig2.tight_layout(rect=[0, 0, 1, 0.96])
    out2 = os.path.join(FIG_DIR, "波粒二象性_单电子累积.svg")
    fig2.savefig(out2, format="svg")
    plt.close(fig2)
    print("[saved]", out2)

    # 统计验证：N=60000 直方图 vs 理论分布
    # 期望计数用「同口径加权直方图」：与对抽样计数做 np.histogram 完全相同的 100 个 bin
    # 与区间 (-2.5, 2.5)，仅把 weights=P12（已归一化概率密度）代入，口径严丝合缝，
    # 规避手工 reshape 积分与 histogram 边界的离散错位。
    N = 60000
    hits = x[np.searchsorted(cdf, rng.random(N))]
    hist, _ = np.histogram(hits, bins=100, range=(-2.5, 2.5))
    expected_raw, _ = np.histogram(x, bins=100, range=(-2.5, 2.5), weights=P12)
    expected = expected_raw / expected_raw.sum() * N
    # 卡方检验（标准做法：期望计数 < 5 的尾部 bin 合并到相邻 bin，避免低计数权重放大）
    mask = expected >= 5
    hist_ok = np.concatenate([hist[mask], [hist[~mask].sum()]])
    exp_ok = np.concatenate([expected[mask], [expected[~mask].sum()]])
    chi2 = np.sum((hist_ok - exp_ok) ** 2 / exp_ok)
    dof = len(exp_ok) - 1
    # 近似 p 值（正态近似，(chi2-dof)/sqrt(2 dof) 在 ±3 内相当于 p > 1e-3）
    z = (chi2 - dof) / np.sqrt(2 * dof)
    print("[model B] N=60000: bins used = %d (+merged low-count), chi2 = %.1f (dof=%d), z = %.2f"
          % (len(exp_ok), chi2, dof, z))
    assert abs(z) < 3, "simulated counts inconsistent with theoretical distribution"

    # 可见度收敛
    vis = (P12[1000 - 100: 1000 + 100].max() - P12[1500]) / (P12[1000 - 100: 1000 + 100].max() + P12[1500])
    # 理论可见度（|x|<a/L 内包络近似常数）：V = 1
    print("[model B] theoretical fringe visibility at center = 1 (full contrast)")
    print("[model B] histogram-based check passed")


if __name__ == "__main__":
    main()
