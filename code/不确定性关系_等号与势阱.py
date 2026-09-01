# -*- coding: utf-8 -*-
"""第 8 篇《不确定性关系》配套脚本。

数值验证：
  (a) 高斯波包（最小不确定态）：Delta x * Delta p = hbar/2 精确（等号）；
  (b) 无限深方势阱基态：Delta x * Delta p = 0.568 hbar > hbar/2（严格超等号）。
两例均用自实现梯形积分（numpy 2.x 已移除 np.trapz）+ 有限差分二阶导算 <p^2>。
图注英文；文件名中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

hbar = 1.054571817e-34


def trapz(y, x):
    dx = x[1] - x[0]
    return dx * (np.sum(y) - 0.5 * (y[0] + y[-1]))


def gaussian_minimum_uncertainty():
    """高斯波包：psi = (2 pi sigma0^2)^(-1/4) exp(-x^2/(4 sigma0^2))，Delta x * Delta p = hbar/2。"""
    sigma0 = 1.0
    x = np.linspace(-12 * sigma0, 12 * sigma0, 4000)
    psi = (2 * np.pi * sigma0 ** 2) ** (-0.25) * np.exp(-x ** 2 / (4 * sigma0 ** 2))
    # 归一化检查
    norm = trapz(psi ** 2, x)
    # 位置方差
    x2 = trapz(x ** 2 * psi ** 2, x) / norm
    dx = np.sqrt(x2)
    # 动量：FFT（psi 已衰减到 0，零填充足够）
    N = len(x)
    dx_step = x[1] - x[0]
    psif = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(psi))) * dx_step
    k = np.fft.fftshift(np.fft.fftfreq(N, d=dx_step)) * 2 * np.pi
    p = hbar * k
    # 动量分布归一化
    pnorm = trapz(np.abs(psif) ** 2, p)
    p2 = trapz(p ** 2 * np.abs(psif) ** 2, p) / pnorm
    dp = np.sqrt(p2)
    prod = dx * dp
    print("[gaussian] <x^2>=%.6f, Delta x=%.6f (sigma0 units)" % (x2, dx))
    print("[gaussian] Delta p/hbar=%.6f, product/hbar=%.6f (expect 0.5000)" % (dp / hbar, prod / hbar))
    assert abs(prod / hbar - 0.5) < 1e-3, "gaussian must saturate lower bound"
    return x, psi, p / hbar, np.abs(psif) ** 2 / pnorm, dx, dp


def infinite_well_ground():
    """无限深方势阱 [0,L] 基态：psi = sqrt(2/L) sin(pi x/L)。
    Delta x = L sqrt((pi^2-6)/(12 pi^2)) = 0.1808 L;  Delta p = pi hbar / L;
    product = 0.568 hbar > hbar/2。"""
    L = 1.0
    N = 4000
    x = np.linspace(0.0, L, N)
    dx_step = x[1] - x[0]
    psi = np.sqrt(2.0 / L) * np.sin(np.pi * x / L)
    # 归一化
    norm = trapz(psi ** 2, x)
    # 位置方差
    xmean = trapz(x * psi ** 2, x) / norm
    x2 = trapz(x ** 2 * psi ** 2, x) / norm
    dx = np.sqrt(x2 - xmean ** 2)
    # 动量方差：有限差分二阶导，<p^2> = -hbar^2 int psi psi'' dx
    psi2nd = np.zeros_like(psi)
    psi2nd[1:-1] = (psi[2:] - 2 * psi[1:-1] + psi[:-2]) / dx_step ** 2
    # 边界 psi=0 处 psi'' 贡献为 0（psi_i=0）
    p2 = -hbar ** 2 * trapz(psi * psi2nd, x) / norm
    dp = np.sqrt(p2)
    prod = dx * dp
    # 解析参考
    dx_ana = L * np.sqrt((np.pi ** 2 - 6) / (12 * np.pi ** 2))
    dp_ana = np.pi * hbar / L
    prod_ana = dx_ana * dp_ana
    print("[well] Delta x = %.5f L (ana %.5f), Delta p = %.5f hbar/L (ana %.5f)"
          % (dx / L, dx_ana / L, dp / hbar * L, dp_ana / hbar * L))
    print("[well] product = %.5f hbar (ana %.5f, lower bound 0.5000)" % (prod / hbar, prod_ana / hbar))
    assert prod / hbar > 0.5 + 1e-3, "well ground state must exceed lower bound"
    assert abs(prod / hbar - prod_ana / hbar) < 1e-2, "well product mismatch with analytic"
    return x, psi, dx, dp


def main():
    x, psi, p, pf, dx, dp = gaussian_minimum_uncertainty()
    xw, psiw, dxw, dpw = infinite_well_ground()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    # 左：高斯位置 + 动量分布（均归一）
    ax1.plot(x, psi ** 2 / psi.max(), "-", lw=1.6, color="#1f77b4", label="|ψ(x)|²")
    # 动量分布采样绘制
    pk = np.argsort(np.abs(p))
    pm = p[pk]
    pfm = pf[pk]
    ax1.plot(pm / 3.0, pfm / pfm.max(), "--", lw=1.4, color="#d62728", label="|φ(p)|²")
    ax1.axvline(0.0, color="k", lw=0.6)
    ax1.set_xlabel("x (left) / p/3 (right, arb. unit)")
    ax1.set_ylabel("normalized density")
    ax1.set_title("Gaussian: Δx·Δp = ħ/2 (saturates bound)")
    ax1.legend(fontsize=8)

    # 右：势阱基态 + 不等式示意
    ax2.plot(xw, psiw ** 2 / psiw.max(), "-", lw=1.8, color="#2ca02c",
             label="|ψ₁(x)|² (infinite well)")
    ax2.axhline(0.0, color="k", lw=0.6)
    ax2.set_xlabel("x / L")
    ax2.set_ylabel("normalized |ψ₁|²")
    ax2.set_title("Infinite well ground state: Δx·Δp ≈ 0.568 ħ > ħ/2")
    ax2.legend(fontsize=8)

    fig.tight_layout()
    out = os.path.join(FIG_DIR, "不确定性关系_等号与势阱.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)


if __name__ == "__main__":
    main()
