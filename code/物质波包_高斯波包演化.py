# -*- coding: utf-8 -*-
"""第 7 篇《物质波包与波粒统一》配套脚本。

模型：自由电子高斯波包的解析演化
      |psi(x,t)|^2 = 高斯，中心 x_c = v_g t，宽度 sigma(t) = sigma0 sqrt(1 + (hbar t/(2 m sigma0^2))^2)。
数值验证：
      (a) 实验室系：波包峰值位置 = v_g t（群速度 = 粒子速度 v）；
      (b) 共动系 x' = x - v_g t：波包宽度 = sigma(t) 按色散展宽（相速度 v/2 仅相位、不载信息）。
图注英文规避中文字体；文件名中文。

注：电子 v=0.01c 时 v_g 很大，实验室系内波包在 ps 量级即移出 µm 窗口，
故平移验证用 ps 尺度、展宽验证用共动系（扣除平移后窗口可聚焦 µm 级展宽）。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

hbar = 1.054571817e-34
me = 9.1093837015e-31
c = 299792458.0


def main():
    v = 0.01 * c                     # 粒子速度
    k0 = me * v / hbar              # 中心波数
    lam = 2 * np.pi / k0            # 德布罗意波长
    vg = hbar * k0 / me             # 群速度 = v
    vp = hbar * k0 / (2 * me)       # 相速度 = v/2
    print("[check] de Broglie lambda(0.01c) = %.3f pm" % (lam * 1e12))
    print("[check] v_g = %.4e m/s (= v), v_p = %.4e m/s (= v/2)" % (vg, vp))
    assert abs(vg - v) / v < 1e-12, "group velocity must equal particle velocity"
    assert abs(vp - v / 2) / (v / 2) < 1e-12, "phase velocity must be v/2"

    sigma0 = 0.2e-6                 # 初波包宽度 0.2 um

    # ---- 左：实验室系，验证峰值以 v_g 平移（ps 尺度，窗口 [-1,9] um）----
    Ts_lab = [0.0, 0.5e-12, 1.0e-12, 2.0e-12]
    xlab = np.linspace(-1e-6, 9e-6, 2000)
    dxlab = xlab[1] - xlab[0]

    # ---- 右：共动系 x'，验证宽度按 sigma(t) 展宽（ns 尺度，窗口 [-1,1.5] um）----
    Ts_com = [0.0, 0.1e-9, 0.3e-9, 0.5e-9]
    xp = np.linspace(-1e-6, 1.5e-6, 2000)
    dxp = xp[1] - xp[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    for t in Ts_lab:
        xc = vg * t
        sigma_t = sigma0 * np.sqrt(1.0 + (hbar * t / (2 * me * sigma0 ** 2)) ** 2)
        psi2 = np.exp(-(xlab - xc) ** 2 / (2 * sigma_t ** 2)) / np.sqrt(2 * np.pi * sigma_t ** 2)
        ipeak = int(np.argmax(psi2))
        xpeak_num = xlab[ipeak]
        abs_pos = abs(xpeak_num - xc)
        # 数值宽度（应恒等于 sigma_t，因为只平移不改变形状）
        sig_num = np.sqrt(np.sum(psi2 * (xlab - xpeak_num) ** 2) * dxlab / np.sum(psi2 * dxlab))
        assert abs_pos < 1e-8, "lab peak position mismatch (abs %.3e m)" % abs_pos
        assert abs(sig_num - sigma_t) / sigma_t < 1e-3, "lab width mismatch"
        ax1.plot(xlab * 1e6, psi2 / psi2.max(), "-", lw=1.6,
                 label="t=%.1f ps (x_c=%.2f μm)" % (t * 1e12, xc * 1e6))
    ax1.set_xlabel("position x (μm)")
    ax1.set_ylabel("|ψ(x,t)|² (normalized)")
    ax1.set_title("Lab frame: peak center moves at v_g = v")
    ax1.legend(fontsize=7)
    ax1.set_xlim(-1, 9)

    for t in Ts_com:
        sigma_t = sigma0 * np.sqrt(1.0 + (hbar * t / (2 * me * sigma0 ** 2)) ** 2)
        psi2 = np.exp(-xp ** 2 / (2 * sigma_t ** 2)) / np.sqrt(2 * np.pi * sigma_t ** 2)
        sig_num = np.sqrt(np.sum(psi2 * xp ** 2) * dxp / np.sum(psi2 * dxp))
        rel_sig = abs(sig_num - sigma_t) / sigma_t
        assert rel_sig < 1e-3, "comoving width mismatch (num %.4f vs ana %.4f)" % (sig_num, sigma_t)
        print("[comoving t=%.1e s] sigma num=%.4f um, sigma(t) ana=%.4f um (rel %.2e)"
              % (t, sig_num * 1e6, sigma_t * 1e6, rel_sig))
        ax2.plot(xp * 1e6, psi2 / psi2.max(), "-", lw=1.6,
                 label="t=%.1f ns (σ=%.3f μm)" % (t * 1e9, sigma_t * 1e6))
    ax2.set_xlabel("comoving coordinate x' = x − v_g t (μm)")
    ax2.set_ylabel("|ψ(x',t)|² (normalized)")
    ax2.set_title("Comoving frame: width spreads as σ(t)")
    ax2.legend(fontsize=7)
    ax2.set_xlim(-1, 1.5)

    fig.tight_layout()
    out = os.path.join(FIG_DIR, "物质波包_高斯波包演化.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)


if __name__ == "__main__":
    main()
