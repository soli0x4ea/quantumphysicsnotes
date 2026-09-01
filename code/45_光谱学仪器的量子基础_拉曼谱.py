# -*- coding: utf-8 -*-
"""
45_光谱学仪器的量子基础_拉曼谱.py
配套脚本（第45篇《光谱学仪器的量子基础》系统量子力学笔记）。
仅依赖 numpy + matplotlib（Agg 后端），不引入 scipy。
对应正文：第二节 Kramers-Heisenberg / Placzek 极化率选择定则，第六节 6.1，图1。

模型：以 785 nm 激光激发的拉曼谱，给出若干振动模式的洛伦兹线型，
分别画出斯托克斯带（散射光子损失 hbar*omega_v）与反斯托克斯带（获得 hbar*omega_v）。
反斯托克斯强度含玻尔兹曼布居因子 n_v，体现热布居上振动能级对反斯托克斯线的贡献。
"""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

# ---- CODATA 2018 常数 (SI) ----
h = 6.62607015e-34
hbar = 1.054571817e-34
c = 299792458.0          # m/s
kB = 1.380649e-23        # J/K
c_cm = c * 100.0         # cm/s，用于波数换算
T = 300.0                # K

# ---- 入射激光（宝石学便携拉曼常用 785 nm）----
lambda0 = 785e-9
nu0 = 1.0 / lambda0 * 1e-2   # 波数，单位 cm^-1（1/m * 1e-2 = 1/cm）

# ---- 模型振动模式（cm^-1）与洛伦兹线宽 FWHM（cm^-1）----
# 说明：1332 cm^-1 为金刚石一阶拉曼位移（宝石学鉴别钻石与仿制品的公认实验值）；
#       其余为示意模式，覆盖典型宝石/分子的拉曼区间 200-3500 cm^-1。
modes = [
    ("mode A (illustrative)",   520.0, 10.0),
    ("diamond Raman (1332)",  1332.0,  6.0),
    ("mode C (illustrative)",  2900.0, 14.0),
]


def lorentz(x, x0, gamma, amp):
    g2 = (gamma / 2.0) ** 2
    return amp * g2 / ((x - x0) ** 2 + g2)


# ---- 构建谱（横轴：散射光波数 cm^-1）----
shift_max = 3000.0
xs = np.linspace(nu0 - shift_max, nu0 + shift_max, 60001)   # 0.1 cm^-1 步长
spectrum = np.zeros_like(xs)

print("incident laser lambda = %.1f nm, wavenumber nu0 = %.1f cm^-1" % (lambda0 * 1e9, nu0))
print("T = %.1f K, k_B T = %.2f cm^-1" % (T, kB * T / (h * c_cm)))
print("%-24s %10s %10s %12s %14s" % ("mode", "nu_v/cm-1", "n_v", "I_S/I_Ray", "I_AS/I_S"))
for name, nu_v, gamma in modes:
    omega_v = 2 * np.pi * c_cm * nu_v
    n_v = 1.0 / (np.exp(hbar * omega_v / (kB * T)) - 1.0)
    nu_s_stokes = nu0 - nu_v          # 斯托克斯：散射波数更低
    nu_s_antistokes = nu0 + nu_v      # 反斯托克斯：散射波数更高
    # 强度标度因子 (omega_s)^4 * 布居（Rayleigh 取 nu0^4 * 1）
    A_stokes = (nu_s_stokes) ** 4 * (n_v + 1.0)
    A_antistokes = (nu_s_antistokes) ** 4 * n_v
    A_rayleigh = (nu0) ** 4 * 1.0
    spectrum += lorentz(xs, nu_s_stokes, gamma, A_stokes)
    spectrum += lorentz(xs, nu_s_antistokes, gamma, A_antistokes)
    print("%-24s %10.1f %10.4f %12.2e %14.2e" %
          (name, nu_v, n_v, A_stokes / A_rayleigh, A_antistokes / A_stokes))

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(xs, spectrum, color="#1f4e79", lw=1.3,
        label="Raman (Stokes + anti-Stokes)")
ax.axvline(nu0, color="#888888", ls="--", lw=1.0)
ax.text(nu0, ax.get_ylim()[1] * 0.92, "Rayleigh\n(elastic)",
        ha="center", va="top", fontsize=8, color="#555555")
ax.set_xlabel("scattered wavenumber / cm$^{-1}$")
ax.set_ylabel("relative intensity (a.u.)")
ax.set_title("Raman spectrum: Stokes and anti-Stokes bands (785 nm excitation)")
ax.set_xlim(nu0 - shift_max, nu0 + shift_max)
ax.legend(loc="upper left", fontsize=8)
i_st = np.argmin(np.abs(xs - (nu0 - 1332)))
i_as = np.argmin(np.abs(xs - (nu0 + 1332)))
ax.annotate("Stokes (loss $\\hbar\\omega_v$)", xy=(nu0 - 1332, spectrum[i_st]),
            xytext=(nu0 - 2200, spectrum.max() * 0.6), fontsize=8, color="#1f4e79",
            arrowprops=dict(arrowstyle="->", color="#1f4e79"))
ax.annotate("anti-Stokes (gain $\\hbar\\omega_v$)", xy=(nu0 + 1332, spectrum[i_as]),
            xytext=(nu0 + 1700, spectrum.max() * 0.3), fontsize=8, color="#b22222",
            arrowprops=dict(arrowstyle="->", color="#b22222"))
fig.tight_layout()
out = "figures/45_光谱学仪器的量子基础_图1_拉曼谱.svg"
fig.savefig(out, format="svg", dpi=150)
print("Saved figure:", out)
