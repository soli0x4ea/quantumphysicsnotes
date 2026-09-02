# -*- coding: utf-8 -*-
"""第 6 篇《原子光谱与玻尔模型》配套脚本。

模型 A：Bohr 模型巴尔末系 (n1=2) 前 4 条线波长，用氢原子约化质量口径里德伯常数
         R_H = R_inf * mu/m_e，与真空观测标称值比对。
模型 B：氢原子能级图 E_n = -13.598434 eV / n^2（约化质量口径），画代表性跃迁。

图注英文规避中文字体；文件名中文。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# CODATA 2022
me = C["m_e"]
mp = C["m_p"]
h = C["h"]
c = C["c"]
R_inf = C["R_inf"]          # m^-1 (infinite nuclear mass)
mu_over_me = mp / (me + mp)      # reduced-mass factor
R_H = R_inf * mu_over_me         # m^-1, hydrogen
E_ion_H = 13.598434              # eV, hydrogen ionization (reduced mass)


def main():
    print("[check] R_H = %.3f m^-1 (CODATA 10967758.340)" % R_H)
    assert abs(R_H - 10967758.340) / 10967758.340 < 1e-5, "R_H mismatch"

    # 巴尔末系 n2 = 3..6 -> n1 = 2（真空观测标称值，单位 nm）
    obs = {3: 656.469, 4: 486.273, 5: 434.173, 6: 410.293}
    print("%-10s %14s %14s %10s" % ("n2->2", "lambda(calc)", "lambda(obs)", "rel.err"))
    for n2 in (3, 4, 5, 6):
        lam = 1.0 / (R_H * (1.0 / 4 - 1.0 / n2**2)) * 1e9   # nm
        rel = abs(lam - obs[n2]) / obs[n2]
        print("  %d->2    %14.3f %14.3f %9.2e" % (n2, lam, obs[n2], rel))
        assert rel < 1e-3, "Balmer line mismatch n2=%d" % n2

    # ---------- 绘图 A: 巴尔末系 ----------
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ns = np.arange(3, 7)
    lams = np.array([1.0 / (R_H * (1.0 / 4 - 1.0 / n2**2)) * 1e9 for n2 in ns])
    labels = ["Hα (3→2)", "Hβ (4→2)", "Hγ (5→2)", "Hδ (6→2)"]
    ax.scatter(lams, np.ones_like(lams), c="#d62728", s=60, zorder=3)
    for ln, lm in zip(labels, lams):
        ax.annotate(ln, (lm, 1.0), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8)
    ax.set_yticks([])
    ax.set_ylim(0.9, 1.2)
    ax.set_xlabel("wavelength (nm, vacuum)")
    ax.set_title("Balmer series of hydrogen (Bohr model, R_H reduced-mass)")
    fig.tight_layout()
    out1 = os.path.join(FIG_DIR, "原子光谱与玻尔模型_巴尔末系.svg")
    fig.savefig(out1, format="svg")
    plt.close(fig)
    print("[saved]", out1)

    # ---------- 绘图 B: 能级图 ----------
    fig2, ax2 = plt.subplots(figsize=(7.5, 5.2))
    nmax = 6
    En = -E_ion_H / np.arange(1, nmax + 1)**2
    for n, E in enumerate(En, start=1):
        ax2.hlines(E, 0, 1, color="#1f77b4", lw=1.4)
        ax2.text(1.02, E, "n=%d  %.3f eV" % (n, E), va="center", fontsize=8)
    # 跃迁箭头
    def arrow(n1, n2, x0):
        ax2.annotate("", xy=(x0, En[n2 - 1]), xytext=(x0, En[n1 - 1]),
                     arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.2))
        ax2.text(x0 - 0.05, (En[n1 - 1] + En[n2 - 1]) / 2, "%d→%d" % (n1, n2),
                 color="#d62728", fontsize=8, ha="right", va="center")
    arrow(2, 1, 0.35)
    arrow(3, 2, 0.55)
    arrow(4, 2, 0.75)
    ax2.set_xlim(0, 2.2)
    ax2.set_ylabel("energy E_n (eV, n=1..6)")
    ax2.set_title("Hydrogen energy levels E_n = −13.598 eV / n²")
    fig2.tight_layout()
    out2 = os.path.join(FIG_DIR, "原子光谱与玻尔模型_能级图.svg")
    fig2.savefig(out2, format="svg")
    plt.close(fig2)
    print("[saved]", out2)


if __name__ == "__main__":
    main()
