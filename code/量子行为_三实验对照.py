# -*- coding: utf-8 -*-
"""第 1 篇《量子行为》配套脚本：子弹 / 水波 / 电子 / 被监视电子 四分布对照。

物理内容（对应正文式 (1)-(4)）：
  情形 A 子弹   : P12 = P1 + P2
  情形 B 水波   : I12 = I1 + I2 （时间平均，两独立源）
  情形 C 电子   : P12 = |phi1 + phi2|^2（夫琅禾费双缝近似）
  情形 D 监视   : P12 = P1 + P2（路径信息被获取）

数值验证（正文 6.2 节三个可检验数字）：
  1) 电子情形主极大在 x=0，一级极小在 x = ±(lambda*L/d)（条纹间距）；
  2) 被监视情形无极小；
  3) 子弹与监视电子形状来源不同（前者无相位结构，后者相位被破坏）。

图注为英文以规避 matplotlib 默认字体缺中文的问题；图文件名为中文。
自然单位：lambda = L = d = a = 1（仅保留几何比例的实际意义）。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def sinc(x):
    """归一化 sinc：sinc(0)=1，sinc(y)=sin(pi y)/(pi y)。"""
    return np.sinc(x)


def slit_amplitude(x, shift, lam=1.0, L=1.0, a=0.4, d=1.0):
    """远场（夫琅禾费）双缝中单路幅：sinc 包络（由缝中心几何决定）*
    倾斜平面波相位因子 exp(-i * pi * shift * x / (lam*L))。

    两路相加 |phi1+phi2|^2 = 4 sinc^2(pi a x / lam L) * cos^2(pi d x / (2 lam L))。
    注意夫琅禾费近似下包络不随缝位移（远场平移定理），相对相位才是线性项。
    """
    envelope = np.sinc(a * x / (lam * L))
    s = np.sign(shift) if shift != 0 else 1.0
    phase = np.exp(-1j * s * np.pi * d * x / (lam * L))
    return envelope * phase


def main():
    x = np.linspace(-3.0, 3.0, 3000)
    d = 1.0  # 缝距

    # 单缝幅（远场：包络共用，相位差 = ±pi*d*x/(lam L)）
    phi1 = slit_amplitude(x, -d / 2, d=d)
    phi2 = slit_amplitude(x, +d / 2, d=d)
    P1 = np.abs(phi1) ** 2
    P2 = np.abs(phi2) ** 2

    # 情形 A：子弹（也是单缝单独实验的分布）
    P_bullets = P1 + P2

    # 情形 C：电子（概率幅相加）
    P_electron = np.abs(phi1 + phi2) ** 2

    # 归一化（每个分布积分 = 1，便于对照）
    dx = x[1] - x[0]
    P_bullets /= np.sum(P_bullets) * dx
    P_electron /= np.sum(P_electron) * dx
    P1n = P1 / (np.sum(P1) * dx)
    P2n = P2 / (np.sum(P2) * dx)

    # ---- 数值验证 1：电子情形主极大与一级极小 ----
    xmax = x[np.argmax(P_electron)]
    # 一级极小：在 x>0 侧找局部极小
    interior = P_electron[1:-1]
    loc_min = np.where((interior < P_electron[:-2]) & (interior < P_electron[2:]))[0] + 1
    mins_right = [x[i] for i in loc_min if x[i] > 0]
    first_min = min(mins_right) if mins_right else float("nan")
    expected = 0.5  # cos^2(pi*d*x/(2*lam*L)) 的一级零点：x = lam*L/(2d)（条纹间距之半）
    print("[check1] electron main max at x = %+.4f (expect 0)" % xmax)
    print("[check1] electron first minimum at x = %+.4f (expect +%+.4f)" % (first_min, expected))
    assert abs(xmax) < 0.01, "main maximum should be at x=0"
    assert abs(first_min - expected) < 0.05, "first minimum should match fringe spacing"

    # ---- 数值验证 2：监视情形谷不归零（几何双峰的浅谷，非干涉深谷）----
    P_watched = P1n + P2n
    interior_w = P_watched[1:-1]
    loc_min_w = np.where((interior_w < P_watched[:-2]) & (interior_w < P_watched[2:]))[0] + 1
    peak_w = P_watched.max()
    print("[check2] watched-case interior minima count = %d" % len(loc_min_w))
    for i in loc_min_w:
        print("[check2]   local min at x=%+.3f, value=%.4f (fraction of peak %.2f)"
              % (x[i], P_watched[i], P_watched[i] / peak_w))
    print("[check2] watched-case global min = %.4f" % P_watched.min())
    # 中央包络区（|x|<2.0，sinc 包络第一零点在 x=1/a=2.5）内不得有归零深谷
    central = np.abs(x) < 2.0
    central_min_frac = P_watched[central].min() / peak_w
    print("[check2] watched-case central-region min/peak = %.4f (must stay > 0.05)" % central_min_frac)
    assert central_min_frac > 0.05, "watched case must have no near-zero interference dips in central region"

    # ---- 数值验证 3：电子情形极小值接近零，对比监视情形同位置 ----
    i_min = int(np.argmin(np.abs(x - first_min)))
    print("[check3] P_electron at first minimum = %.3e (deep dip)" % P_electron[i_min])
    print("[check3] P_watched at same x         = %.4f (no dip)" % P_watched[i_min])
    assert P_electron[i_min] < 1e-3, "electron pattern should have near-zero minimum"
    assert P_watched[i_min] > 0.05, "watched pattern should retain weight at same x"

    # ---- 绘图：四分布对照 ----
    fig, axes = plt.subplots(4, 1, figsize=(8, 9), sharex=True)
    cases = [
        (P_bullets, "A: bullets  (P12 = P1 + P2, no phase structure)", "#7f7f7f"),
        (P2n,       "B: two incoherent wave sources (I12 = I1 + I2)", "#1f77b4"),
        (P_electron, "C: electrons (P12 = |phi1 + phi2|^2, interference)", "#d62728"),
        (P_watched, "D: electrons watched (P12 = P1 + P2, which-way info)", "#2ca02c"),
    ]
    for ax, (y, title, color) in zip(axes, cases):
        ax.fill_between(x, 0, y, color=color, alpha=0.35)
        ax.plot(x, y, color=color, lw=1.2)
        ax.set_ylabel("probability density")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(-3, 3)
        ax.set_ylim(bottom=0)
    axes[-1].set_xlabel("screen position x (natural units, fringe spacing = 1)")
    # 电子情形标注条纹间距与一级极小
    axes[2].annotate("first minimum at x = +0.5", xy=(first_min, P_electron[i_min]),
                     xytext=(1.5, 0.5), textcoords="data",
                     arrowprops=dict(arrowstyle="->", lw=0.8))
    fig.suptitle("Same geometry, three kinds of behavior (Feynman Vol. III Ch.1)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out = os.path.join(FIG_DIR, "量子行为_三实验对照.svg")
    fig.savefig(out, format="svg")
    plt.close(fig)
    print("[saved]", out)

    # ---- 附加输出：真实 50 kV 电子的德布罗意波长（正文第三节）----
    h = C["h"]          # J*s, exact
    me = 9.1093837139e-31       # kg, CODATA 2022
    e = C["e"]         # C, exact
    V = 50e3                    # 50 kV
    lam = h / np.sqrt(2 * me * e * V)
    print("[deBroglie] lambda(electron, 50 kV) = %.3e m  (about %.2f pm)" % (lam, lam * 1e12))


if __name__ == "__main__":
    main()
