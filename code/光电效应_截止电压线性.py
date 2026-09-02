# -*- coding: utf-8 -*-
"""第 4 篇《光电效应与光子》配套脚本。

模型：Einstein 光电方程 eV0 = h*nu - W 的截止电压-频率直线（三种标准金属逸出功）。
数值验证：直线斜率 = h/e（普适）；各金属截止波长 lambda_0 = hc/W。

注意：本图绘制的是理论关系，基于标准逸出功文献值；并非 Millikan 1916 原始
测量数据点，避免编造实验数据。图注英文规避 matplotlib 缺中文字体；文件名中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# CODATA 2022 精确定义值
h_Js = C["h"]        # J*s
e_C = C["e"]        # C
c = C["c"]
# 以 eV 为单位时：h = 4.135667...e-15 eV*s；hc = 1239.84 eV*nm
h_eV_s = h_Js / e_C
hc_eV_nm = h_Js * c / e_C * 1e9

# 标准逸出功（金属，单位 eV；文献常见值）
WORK = {
    "Na": 2.28,
    "K": 2.30,
    "Cs": 2.10,
    "W": 4.50,
}


def main():
    print("[check] slope h/e = %.6e V*s (theory)" % (h_eV_s))
    assert abs(h_eV_s - 4.135667e-15) < 1e-20, "h/e mismatch"

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    nu = np.linspace(0.0, 1.6e15, 400)
    colors = {"Na": "#1f77b4", "K": "#2ca02c", "Cs": "#9467bd", "W": "#d62728"}
    for name, W in WORK.items():
        V0 = h_eV_s * nu - W          # Volt
        nu0 = W / h_eV_s              # cutoff frequency (Hz)
        lam0 = hc_eV_nm / W           # cutoff wavelength (nm)
        print("[metal %-2s] W=%.2f eV -> nu0=%.3e Hz, lambda0=%.1f nm"
              % (name, W, nu0, lam0))
        # 只画 V0>=0 部分（物理区）
        mask = V0 >= 0
        ax.plot(nu[mask] * 1e-15, V0[mask], "-", color=colors[name], lw=1.7,
                label="%s (W=%.2f eV, λ₀=%.0f nm)" % (name, W, lam0))
        ax.axvline(nu0 * 1e-15, color=colors[name], ls=":", lw=0.7)
    ax.set_xlabel("frequency ν (10¹⁵ Hz)")
    ax.set_ylabel("stopping voltage V₀ (volt)")
    ax.set_title("Photoelectric stopping voltage vs frequency (theoretical eV₀=hν−W)")
    ax.set_xlim(0, 1.6)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "光电效应_截止电压线性.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)


if __name__ == "__main__":
    main()
