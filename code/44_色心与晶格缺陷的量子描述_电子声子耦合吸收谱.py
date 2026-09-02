# -*- coding: utf-8 -*-
# 44_色心与晶格缺陷的量子描述_电子声子耦合吸收谱.py
# 配套：第 44 篇《色心与晶格缺陷的量子描述》第六节省型模型 (a)
# 模型：强电子-声子耦合下色心的吸收/发射谱（零声子线 ZPL + 泊松权重的声子边带）
# 对应公式：第二节 H_ep 黄昆因子 S 与 Franck-Condon 因子 P_m = e^{-S} S^m / m!
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 本文件
# 依赖：numpy, matplotlib（禁用 scipy）；matplotlib 后端 Agg
import matplotlib
matplotlib.use("Agg")
import math
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- CODATA 2018 相关常数（SI，能量在内部换算为 eV）----
hbar_eVs = C["hbar_eVs"]        # 约化普朗克常数 [eV·s]
kB_eV = C["kB_eVK"]           # 玻尔兹曼常数 [eV/K]
c_nm_ps = 299792458e-3 * 1e3     # 光速 [nm/ps] 仅用于波长换算直观展示

# ---- 模型参数（NV 中心近邻数量级；S、ħω、ZPL 见正文表与文献 [24jo][24jp][24js]）----
E_ZPL = 1.945      # 零声子线能量 [eV]（NV^- 中心 1.945 eV，对应 637 nm，Davies & Hamer 1976）
S = 3.0            # 黄昆因子 Huang-Rhys factor（NV 中心典型值 S ~ 3；强耦合）
hw = 0.065         # 单声子能量（代表性光学支）[eV] ~ 65 meV
gamma = 0.012      # 单条洛伦兹线宽 [eV]（量级参考，取窄线以分辨 ZPL 与边带）
T_K = 0.0          # 计算温度 [K]（此处展示 T=0 的干净泊松边带；正文讨论有限 T 的 coth 包络）

# 能量扫描范围：覆盖 ZPL 两侧若干声子能量
n_side = 9
E = np.linspace(E_ZPL - (n_side + 1) * hw, E_ZPL + (n_side + 1) * hw, 4000)


def lorentzian(x, x0, g):
    """归一化的洛伦兹型（峰面积 = 1）：L(x) = (g/pi) / [(x-x0)^2 + g^2]"""
    return (g / np.pi) / ((x - x0) ** 2 + g ** 2)


def fc_factors(S, n_max):
    """T=0 Franck-Condon 因子：P_m = e^{-S} S^m / m!（泊松分布）"""
    ms = np.arange(n_max + 1)
    logP = -S + ms * np.log(S) - np.array([math.lgamma(m + 1) for m in ms])
    return ms, np.exp(logP)


def build_spectrum(E, E_ZPL, S, hw, gamma, sign=+1, n_max=20):
    """吸收(sign=+1)：边带在 E_ZPL + m*hw；发射(sign=-1)：边带在 E_ZPL - m*hw。
    每条振动态用洛伦兹型叠加，权重为 Franck-Condon 因子 P_m。"""
    ms, Pm = fc_factors(S, n_max)
    I = np.zeros_like(E)
    for m, w in zip(ms, Pm):
        I = I + w * lorentzian(E, E_ZPL + sign * m * hw, gamma)
    return I


n_max = 20
abs_spec = build_spectrum(E, E_ZPL, S, hw, gamma, sign=+1, n_max=n_max)
emi_spec = build_spectrum(E, E_ZPL, S, hw, gamma, sign=-1, n_max=n_max)

# Debye-Waller 因子：零温 W = e^{-S}（即 ZPL 强度占总强度的比例）
W_T0 = np.exp(-S)
# 用 np.trapezoid 数值积分验证：ZPL 区域面积 / 总面积 应 ≈ e^{-S}
zmask = np.abs(E - E_ZPL) < gamma * 2.5
area_total_abs = np.trapezoid(abs_spec, E)
area_zpl_abs = np.trapezoid(abs_spec[zmask], E[zmask])
# 有限温度 Debye-Waller 因子：W(T)=exp[-S(2 n_bar + 1)]，n_bar=1/(exp(hw/kT)-1)
if T_K > 1e-6:
    nbar = 1.0 / (np.exp(hw / (kB_eV * T_K)) - 1.0)
else:
    nbar = 0.0
W_T = np.exp(-S * (2 * nbar + 1))

print("黄昆因子 S =", S)
print("零温 Debye-Waller 因子 e^{-S} =", round(W_T0, 4))
print("数值积分 ZPL 面积占比 =", round(area_zpl_abs / area_total_abs, 4),
      "（应与 e^{-S} 一致）")
print("有限 T Debye-Waller 因子 W(T) =", round(W_T, 4), "  T =", T_K, "K")
print("ZPL 波长 = %.1f nm" % (1239.841984 / E_ZPL))

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(8.4, 5.0))
ax.plot(E, abs_spec, color="#1f4e79", lw=1.8, label="Absorption (T=0)")
ax.plot(E, emi_spec, color="#b00020", lw=1.8, label="Emission (T=0)")
ax.axvline(E_ZPL, color="black", ls="--", lw=1.0)
ax.annotate("ZPL = %.3f eV (%.0f nm)" % (E_ZPL, 1239.841984 / E_ZPL),
            xy=(E_ZPL, max(abs_spec.max(), emi_spec.max()) * 0.55),
            xytext=(E_ZPL + 1.2 * hw, max(abs_spec.max(), emi_spec.max()) * 0.9),
            fontsize=10)
ax.set_xlabel("Photon energy (eV)")
ax.set_ylabel("Absorption / emission line shape (a.u.)")
ax.set_title("Electron-phonon absorption spectrum: ZPL + Poisson-weighted phonon sidebands\n"
             "Huang-Rhys factor S = %.1f, single-phonon energy $\\hbar\\omega$ = %.0f meV" % (S, hw * 1000))
ax.legend(loc="upper right")
ax.text(0.02, 0.96, "Debye-Waller factor $e^{-S}$ = %.3f" % W_T0,
        transform=ax.transAxes, va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="#f2f2f2", ec="#999999"))
ax.set_xlim(E.min(), E.max())
fig.tight_layout()
out = "figures/44_色心与晶格缺陷的量子描述_吸收谱.svg"
fig.savefig(out, format="svg", dpi=150)
print("已写出:", out)
