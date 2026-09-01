# -*- coding: utf-8 -*-
"""第 5 篇《康普顿散射》配套脚本。

模型：康普顿位移 Delta_lambda = lambda_C (1 - cos theta)，及反冲电子动能 K_e(theta)。
数值验证：lambda_C = h/(m_e c) 与 CODATA 2.4263e-12 m 比对；
          theta=0 时 K_e=0、theta=pi 时最大。
图注英文规避中文字体；文件名中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

h = 6.62607015e-34
me = 9.1093837015e-31
c = 299792458.0
lam_C = h / (me * c)            # m


def main():
    print("[check] Compton wavelength lambda_C = %.6e m (CODATA 2.426310e-12)" % lam_C)
    assert abs(lam_C - 2.426310e-12) / 2.426310e-12 < 1e-4, "lambda_C mismatch"

    theta = np.linspace(0, np.pi, 400)
    dlam = lam_C * (1 - np.cos(theta))

    # 反冲电子动能（取入射 X 射线 lambda = 71 pm, Mo K-alpha）
    lam0 = 71e-12
    hc = h * c
    Ke = hc / lam0 - hc / (lam0 + dlam)

    print("[check] theta=0   : Delta_lambda=%.3e m, K_e=%.3e J" % (dlam[0], Ke[0]))
    print("[check] theta=pi  : Delta_lambda=%.3e m (=2 lambda_C), K_e=%.3e eV"
          % (dlam[-1], Ke[-1] / 1.602176634e-19))
    assert dlam[0] == 0 and abs(Ke[0]) < 1e-30, "theta=0 must give zero shift/energy"
    assert abs(dlam[-1] - 2 * lam_C) / (2 * lam_C) < 1e-12, "theta=pi must give 2 lambda_C"

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    axes[0].plot(theta * 180 / np.pi, dlam * 1e12, "-", color="#1f77b4", lw=1.7)
    axes[0].axhline(2 * lam_C * 1e12, color="gray", ls=":", lw=0.9)
    axes[0].text(10, 2 * lam_C * 1e12 * 1.02, "2 λ_C = 4.85 pm", fontsize=8, color="gray")
    axes[0].set_xlabel("scattering angle θ (deg)")
    axes[0].set_ylabel("Δλ (pm)")
    axes[0].set_title("Compton shift Δλ = λ_C(1−cos θ)")
    axes[0].set_xlim(0, 180)

    axes[1].plot(theta * 180 / np.pi, Ke / 1.602176634e-19, "-", color="#d62728", lw=1.7)
    axes[1].set_xlabel("scattering angle θ (deg)")
    axes[1].set_ylabel("recoil electron kinetic energy (eV)")
    axes[1].set_title("Recoil electron energy K_e(θ), λ=71 pm")
    axes[1].set_xlim(0, 180)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "康普顿散射_位移与反冲.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)


if __name__ == "__main__":
    main()
