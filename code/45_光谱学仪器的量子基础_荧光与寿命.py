# -*- coding: utf-8 -*-
"""
45_光谱学仪器的量子基础_荧光与寿命.py
配套脚本（第45篇《光谱学仪器的量子基础》系统量子力学笔记）。
仅依赖 numpy + matplotlib（Agg 后端），不引入 scipy。
对应正文：第二节 2.4 爱因斯坦 A 系数公式，第六节 6.2，图2/图3/图4。

- 图2：固定 1 D 跃迁偶极矩下，自发辐射速率 A（与寿命 tau）随发射波长变化；
       并以氢原子 2p->1s（Lyman-alpha）作标定（理论 A~6.25e8 s^-1, tau~1.60 ns）。
- 图3：荧光（ns 级，允许跃迁）与磷光（ms 级，自旋禁戒如 Cr3+ 红宝石）指数衰减对比。
- 图4：Jablonski 图示意（S0 / S1 / T1，吸收 / 内转换 / 振动弛豫 / 荧光 / 系间窜越 / 磷光）。
"""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

h = 6.62607015e-34
hbar = 1.054571817e-34
c = 299792458.0
eps0 = 8.8541878128e-12
e = 1.602176634e-19
a0 = 5.29177210903e-11
D = 3.33564095e-30   # 1 Debye in C·m


def einstein_A(wavelength_m, d_Cm):
    """SI 单位制下的爱因斯坦 A 系数（自发辐射速率）。

    A = omega^3 * |d|^2 / (3 pi eps0 hbar c^3)
    """
    omega = 2 * np.pi * c / wavelength_m
    return omega ** 3 * d_Cm ** 2 / (3 * np.pi * eps0 * hbar * c ** 3)


# --- 标定：氢原子 2p -> 1s（Lyman-alpha，lambda = 121.567 nm）---
d_H = 0.7449 * e * a0      # 约 1.89 D（电偶极跃迁矩阵元幅值）
lam_H = 121.567e-9
A_H = einstein_A(lam_H, d_H)
tau_H = 1.0 / A_H
print("=== calibration: H 2p->1s (Lyman-alpha) ===")
print("d = %.3f D" % (d_H / D))
print("A = %.3e s^-1" % A_H)
print("tau = %.3f ns" % (tau_H * 1e9))

# --- 固定 1 D 偶极：A(lambda) 曲线 ---
wl = np.linspace(300e-9, 800e-9, 300)
A1 = einstein_A(wl, 1.0 * D)
tau1 = 1.0 / A1

fig2, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(wl * 1e9, A1, color="#1f4e79", lw=2)
ax.set_xlabel("emission wavelength / nm")
ax.set_ylabel("spontaneous rate A / s$^{-1}$")
ax.set_title("Einstein A coefficient vs emission wavelength (fixed 1 D dipole)")
ax2 = ax.twinx()
ax2.plot(wl * 1e9, tau1 * 1e9, color="#b22222", lw=1.2, ls="--")
ax2.set_ylabel("lifetime tau / ns", color="#b22222")
ax2.tick_params(axis="y", labelcolor="#b22222")
ax.plot(lam_H * 1e9, A_H, "o", color="black")
ax.annotate("H 2p->1s\nA=%.2e s$^{-1}$\ntau=%.2f ns" % (A_H, tau_H * 1e9),
            xy=(lam_H * 1e9, A_H), xytext=(lam_H * 1e9 + 45, A_H * 1.2),
            fontsize=8, arrowprops=dict(arrowstyle="->"))
fig2.tight_layout()
out2 = "figures/45_光谱学仪器的量子基础_图2_自发辐射速率.svg"
fig2.savefig(out2, format="svg", dpi=150)
print("Saved:", out2)

# --- 图3：荧光 vs 磷光衰减 ---
tau_fluor = tau_H                # ns 量级（允许电偶极跃迁）
tau_phos = 3.0e-3               # s 量级（如 Cr3+ 红宝石自旋禁戒，~3 ms）
t = np.logspace(-11, -2, 400)    # 10 ps - 10 ms
If = np.exp(-t / tau_fluor)
Ip = np.exp(-t / tau_phos)
fig3, ax = plt.subplots(figsize=(7, 4.5))
ax.semilogx(t, If, color="#1f4e79", lw=2,
            label="fluorescence (tau~1.6 ns, allowed E1)")
ax.semilogx(t, Ip, color="#b22222", lw=2,
            label="phosphorescence (tau~3 ms, spin-forbidden e.g. ruby Cr$^{3+}$)")
ax.set_xlabel("time / s")
ax.set_ylabel("normalized intensity")
ax.set_title("Fluorescence vs phosphorescence: exponential decays")
ax.legend(fontsize=8)
ax.grid(True, which="both", alpha=0.3)
fig3.tight_layout()
out3 = "figures/45_光谱学仪器的量子基础_图3_荧光磷光衰减.svg"
fig3.savefig(out3, format="svg", dpi=150)
print("Saved:", out3)
print("fluorescence tau=%.3e s, phosphorescence tau=%.3e s, ratio=%.2e"
      % (tau_fluor, tau_phos, tau_phos / tau_fluor))

# --- 图4：Jablonski 图（全英文图注）---
fig4, ax = plt.subplots(figsize=(6.5, 6.0))
ax.axis("off")
levels = {"S0": 0.0, "S1": 3.0, "T1": 1.6}


def bar(y, x0, x1, color, label):
    ax.plot([x0, x1], [y, y], color=color, lw=6)
    ax.text(x0 - 0.5, y, label, ha="right", va="center", fontsize=10)


bar(levels["S0"], 1.0, 4.0, "#1f4e79", "S0")
bar(levels["S1"], 1.0, 4.0, "#1f4e79", "S1")
bar(levels["T1"], 1.0, 4.0, "#b22222", "T1")


def arrow(x0, y0, x1, y1, color, style="-|>", ls="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.6, ls=ls))


# absorption S0 -> S1
arrow(2.5, levels["S0"], 2.5, levels["S1"], "#2ca02c")
ax.text(2.62, (levels["S0"] + levels["S1"]) / 2, "absorption\nS0->S1",
        fontsize=8, color="#2ca02c")
# internal conversion / vibrational relaxation at S1
arrow(3.2, levels["S1"], 3.6, levels["S1"] - 0.25, "#888888")
ax.text(3.7, levels["S1"] - 0.1, "IC / VR", fontsize=7, color="#555555")
# fluorescence S1 -> S0
arrow(2.0, levels["S1"] - 0.25, 2.0, levels["S0"] + 0.05, "#1f4e79")
ax.text(1.5, (levels["S0"] + levels["S1"]) / 2 - 0.1,
        "fluorescence\nS1->S0 (ns)", fontsize=8, color="#1f4e79")
# intersystem crossing S1 -> T1
arrow(3.0, levels["S1"] - 0.25, 3.0, levels["T1"] + 0.05, "#b22222", ls="--")
ax.text(3.12, (levels["T1"] + levels["S1"] - 0.25) / 2, "ISC\nS1->T1",
        fontsize=8, color="#b22222")
# phosphorescence T1 -> S0
arrow(1.8, levels["T1"], 1.8, levels["S0"] + 0.05, "#b22222", ls=":")
ax.text(1.15, levels["T1"] / 2, "phosphorescence\nT1->S0 (ms)",
        fontsize=8, color="#b22222")
ax.set_title("Jablonski diagram")
ax.set_ylim(-0.3, 3.6)
fig4.tight_layout()
out4 = "figures/45_光谱学仪器的量子基础_图4_Jablonski图.svg"
fig4.savefig(out4, format="svg", dpi=150)
print("Saved:", out4)
