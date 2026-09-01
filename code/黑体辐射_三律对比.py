# -*- coding: utf-8 -*-
"""第 3 篇《黑体辐射与能量量子化》配套脚本。

模型：Planck 定律 (u_nu 与 u_lambda) 与经典极限 (Rayleigh-Jeans, Wien 近似)。
数值验证：
  1) 全频段积分 Planck 得 U(T) = a T^4，辐射出射度 j* = c/4 U = sigma T^4，
     与解析斯特藩-玻尔兹曼定律比对（相对误差量级）。
  2) 数值找 u_lambda 峰值 lambda_max，与维恩位移 b/T 比对。
  3) 太阳(5772 K)/人体(310 K)/CMB(2.725 K) 的峰值波长。
  4) 绘图：T=5772 K 下 Planck 谱 + Wien 近似 + Rayleigh-Jeans（展示紫外端发散）。

图注英文规避 matplotlib 缺中文字体；图文件名为中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# CODATA 2022 精确定义值
h = 6.62607015e-34
kB = 1.380649e-23
c = 299792458.0

# 解析常数（自洽核对用）
sigma = 2 * np.pi**5 * kB**4 / (15 * h**3 * c**2)   # W/m^2/K^4
b_wien = h * c / (4.965114231 * kB)                  # m*K


def u_nu(nu, T):
    """谱能量密度（频率表示），单位 J*s/m^3（= J/m^3/Hz）。"""
    return 8 * np.pi * h * nu**3 / c**3 / (np.exp(h * nu / (kB * T)) - 1.0)


def u_lambda(lam, T):
    """谱能量密度（波长表示），单位 J/m^4。"""
    lam = np.asarray(lam, dtype=float)
    out = np.zeros_like(lam)
    nz = lam > 0
    out[nz] = 8 * np.pi * h * c / lam[nz]**5 / (np.exp(h * c / (lam[nz] * kB * T)) - 1.0)
    return out


def trapz(y, x):
    return np.sum(y) * (x[1] - x[0])


def main():
    # ---------- 验证 1: 斯特藩-玻尔兹曼 ----------
    T = 5772.0
    nu = np.linspace(1e9, 60 * kB * T / h, 60000)  # 上限足够覆盖热峰
    U_num = trapz(u_nu(nu, T), nu)                  # J/m^3
    j_num = c / 4.0 * U_num                         # W/m^2
    j_analytic = sigma * T**4
    rel1 = abs(j_num - j_analytic) / j_analytic
    print("[check1] Stefan-Boltzmann: j*(num)=%.4e  j*(analytic sigma T^4)=%.4e  rel.err=%.2e"
          % (j_num, j_analytic, rel1))
    print("[check1] sigma (self-derived)=%.6e W/m^2/K^4 (CODATA 5.670374e-8)" % sigma)
    assert rel1 < 1e-3, "Stefan-Boltzmann numerical integration mismatch"

    # ---------- 验证 2: 维恩位移 ----------
    lam = np.linspace(1e-8, 8e-6, 200000)
    Ulam = u_lambda(lam, T)
    ilam_peak = np.argmax(Ulam)
    lam_peak = lam[ilam_peak]
    lam_analytic = b_wien / T
    rel2 = abs(lam_peak - lam_analytic) / lam_analytic
    print("[check2] Wien displacement: lambda_max(num)=%.4e m  lambda_max(b/T)=%.4e m  rel.err=%.2e"
          % (lam_peak, lam_analytic, rel2))
    assert rel2 < 1e-3, "Wien displacement peak mismatch"

    # ---------- 验证 3: 天体/人体/CMB 峰值 ----------
    for name, Tt in (("Sun (effective)", 5772.0), ("Human body", 310.0), ("CMB", 2.72548)):
        print("[check3] %-16s T=%.3f K -> lambda_max = %.4e m (%.1f um / %.2f mm)"
              % (name, Tt, b_wien / Tt, b_wien / Tt * 1e6, b_wien / Tt * 1e3))

    # ---------- 绘图: T=5772 K 谱（波长表示） ----------
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    lam_plot = np.linspace(5e-8, 3e-6, 4000)
    ax.plot(lam_plot * 1e9, u_lambda(lam_plot, T) * 1e9, "-", color="#1f77b4", lw=1.7,
            label="Planck (1901)")
    # Wien 近似（高频）
    u_wien = 8 * np.pi * h * c / lam_plot**5 * np.exp(-h * c / (lam_plot * kB * T))
    ax.plot(lam_plot * 1e9, u_wien * 1e9, "--", color="#9467bd", lw=1.2, label="Wien approx.")
    # Rayleigh-Jeans（低频，高频发散——截断显示）
    u_rj = 8 * np.pi * kB * T / lam_plot**4
    mask = u_rj * 1e9 < 4 * u_lambda(lam_plot, T).max() * 1e9
    ax.plot(lam_plot[mask] * 1e9, u_rj[mask] * 1e9, ":", color="#d62728", lw=1.3,
            label="Rayleigh-Jeans (diverges UV)")
    ax.axvline(lam_analytic * 1e9, color="gray", ls="-", lw=0.8)
    ax.text(lam_analytic * 1e9 + 8, u_lambda(lam_plot, T).max() * 1e9 * 0.5,
            "lambda_max = %.0f nm" % (lam_analytic * 1e9), fontsize=8, color="gray")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("spectral energy density (J / m^4 / nm)")
    ax.set_title("Blackbody spectrum at T = 5772 K (Sun effective temperature)")
    ax.set_ylim(0, u_lambda(lam_plot, T).max() * 1e9 * 1.15)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "黑体辐射_三律对比.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)


if __name__ == "__main__":
    main()
