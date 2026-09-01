# -*- coding: utf-8 -*-
"""
46_矿物光学性质的第一性定理计算_模型.py

对应《矿物光学性质的第一性原理计算》（第 46 篇系统笔记）第六节 "典型系统与可解模型"
中的模型 (a)：两带（直接带隙）有效质量模型，由联合态密度（joint density of states,
JDOS）计算虚介电函数 ε₂(ω)，展示吸收边在带隙 E_g 处开启；并由 Kramers–Kronig 关系
数值反演得到 ε₁(ω)、折射率 n(ω)。

依赖：numpy + matplotlib 仅此二者（禁用 scipy）。
运行：~/.workbuddy/binaries/python/envs/default/bin/python 46_矿物光学性质的第一性原理计算_模型.py
输出：figures/46_矿物光学性质的第一性原理计算_图1.svg

说明：本脚本只做"物理结构"演示，不跑真实 DFT。带隙 E_g 与有效质量均为模型参数，
不代表任何具体矿物的实测值（矿物实测光学常数见第 46 篇第三节与第八节文献 [24km]）。
"""

import matplotlib
matplotlib.use("Agg")  # 无显示后端，必须置于 pyplot 导入之前
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------------
# Kramers–Kronig 数值反演（因果性约束：ε₁ 与 ε₂ 互为 Hilbert 变换）
#   ε₁(ω) = 1 + (2/π) P ∫₀^∞ [ω' ε₂(ω')] / (ω'² - ω²) dω'
# 采用均匀网格上的梯形公式；极点处（ω' = ω）贡献按主值 (Cauchy principal value)
# 置零，精细网格下误差很小。numpy 2.x 用 np.trapezoid（替代旧 np.trapz）。
# ---------------------------------------------------------------------------
def kramers_kronig_epsilon1(w, eps2):
    """由 ε₂(ω) 数值反演 ε₁(ω)。w, eps2 为同长数组，w 单调递增、均匀。"""
    eps1 = np.empty_like(w)
    for i, wi in enumerate(w):
        # 主值：将最靠近 wi 的网格点（极点 ω'=ω）处函数值置零
        # （奇函数 1/(ω'-ω) 在对称网格上的主值为 0）。先抑制极点处的除零告警。
        j0 = np.argmin(np.abs(w - wi))
        with np.errstate(divide="ignore", invalid="ignore"):
            integrand = w * eps2 / (w**2 - wi**2)
        integrand[j0] = 0.0
        eps1[i] = 1.0 + (2.0 / np.pi) * np.trapezoid(integrand, w)
    return eps1


# ---------------------------------------------------------------------------
# 模型 (a)：三维各向同性两带直接带隙（垂直跃迁）
#   价带  E_v(k) = -E_g/2 - ħ²k²/(2m_v*)
#   导带  E_c(k) = +E_g/2 + ħ²k²/(2m_c*)
#   跃迁能量  ħω(k) = E_c - E_v = E_g + ħ²k²/(2μ),  1/μ = 1/m_c* + 1/m_v*
#   取 m_c* = m_v* = m* ⇒ μ = m*/2，故 ħω(k) - E_g = (ħ²/(m*)) k²
#   联合态密度 J(ħω) ∝ √(ħω - E_g)  (三维抛物线带的平方根开启行为)
# ε₂(ω) = C · J(ħω) · |M|²，取偶极矩阵元 |M|² 与常数 C 合并为 1（任意单位，a.u.）
# ---------------------------------------------------------------------------
EG = 4.0          # 模型带隙 (eV)，仅作演示参数
TK = 1.0          # t = ħ²/(2μ) (eV·Å²)，决定能带展宽
KMAX = 3.5        # 最大波矢 (Å⁻¹)
N_K = 200001      # k 采样点数（径向，带 k² 权重 = 3D 态密度因子）
N_E = 600         # 能量直方图 bin 数

ks = np.linspace(0.0, KMAX, N_K)
E_of_k = EG + TK * ks**2                 # 跃迁能量 ħω(k) ∈ [EG, EG+TK*KMAX²]
w_max_data = E_of_k[-1]                  # 联合态密度的能量上界
weights = ks**2                         # dN ∝ k² dk（各向同性 3D 球壳权重）

# 用直方图估计联合态密度 J(ħω)
E_bins = np.linspace(EG, w_max_data, N_E)
JDOS, _ = np.histogram(E_of_k, bins=E_bins, weights=weights)
dE = E_bins[1] - E_bins[0]
E_centers = 0.5 * (E_bins[:-1] + E_bins[1:])
JDOS = JDOS / JDOS.max()                # 归一到峰值 ~1（仅整体量级由 SCALE 决定）

# 构造 ω 网格（含带隙以下区间，用于 KK 与绘图）
w_plot = np.linspace(0.05, 18.0, 1200)
eps2_raw = np.zeros_like(w_plot)
mask = (w_plot >= EG) & (w_plot <= w_max_data)
eps2_raw[mask] = np.interp(w_plot[mask], E_centers, JDOS)   # 带隙以下 ε₂ = 0

# 物理包络：真实 ε₂(ω) 在远紫外必须趋于 0（满足 f 求和规则），且带内跃迁有有限宽度。
# 这里在联合态密度的平方根开启行为上乘一个指数衰减包络 exp[-(ħω-E_g)/Δ]，
# 使 ε₂ 先随 √(ħω-E_g) 上升、在高能侧回落，KK 积分因而良好收敛。
DECAY = 8.0  # 衰减宽度 (eV)，模型参数
envelope = np.where(w_plot >= EG, np.exp(-(w_plot - EG) / DECAY), 0.0)
eps2_raw = eps2_raw * envelope

# 缩放因子：将模型量纲调到"典型透明矿物"的折射率量级（仅示意，不代表任何具体矿物实测谱）。
# 因 KK 对 ε₂ 线性，缩放 ε₂ 即整体缩放 ε₁、n。SCALE 经试取使静态 n(0)≈1.73。
SCALE = 7.0
eps2 = SCALE * eps2_raw

# Kramers–Kronig 反演得到 ε₁
eps1 = kramers_kronig_epsilon1(w_plot, eps2)

# 折射率 n(ω) 与消光系数 κ(ω)：ñ = n + iκ,  ñ² = ε₁ + iε₂
#   n² - κ² = ε₁,   2nκ = ε₂
#   n = √[ (√(ε₁²+ε₂²) + ε₁)/2 ],   κ = √[ (√(ε₁²+ε₂²) - ε₁)/2 ]
mod_eps = np.sqrt(eps1**2 + eps2**2)
n_omega = np.sqrt((mod_eps + eps1) / 2.0)
kappa_omega = np.sqrt((mod_eps - eps1) / 2.0)

# 一致性检查：带隙以下 ε₂≈0 ⇒ n ≈ √ε₁，ε₁ 应趋于常数（这里有限支撑下接近 1+小量）
low = w_plot < (EG - 0.3)
print("[模型 a] 带隙 E_g = %.2f eV, 数据能量上界 = %.2f eV" % (EG, w_max_data))
print("[模型 a] 带隙以下平均 n = %.4f, 平均 ε₁ = %.4f" % (np.mean(n_omega[low]),
                                                         np.mean(eps1[low])))
print("[模型 a] ω≈%.1f eV 处 n = %.4f, κ = %.4f, ε₁ = %.4f, ε₂ = %.4f"
      % (w_plot[np.argmin(np.abs(w_plot - 6.0))],
         n_omega[np.argmin(np.abs(w_plot - 6.0))],
         kappa_omega[np.argmin(np.abs(w_plot - 6.0))],
         eps1[np.argmin(np.abs(w_plot - 6.0))],
         eps2[np.argmin(np.abs(w_plot - 6.0))]))

# ---------------------------------------------------------------------------
# 绘图（英文图注；中文文件名，英文 caption）
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 8.0))

ax1.plot(w_plot, eps2, color="#1f4e79", lw=2.0, label=r"$\varepsilon_2(\omega)$ (model)")
ax1.axvline(EG, color="#c00000", ls="--", lw=1.2)
ax1.text(EG + 0.08, 0.5 * np.max(eps2), r"absorption edge at $E_g$",
         color="#c00000", fontsize=10)
ax1.set_xlabel(r"Photon energy $\hbar\omega$ (eV)")
ax1.set_ylabel(r"$\varepsilon_2$ (a.u.)")
ax1.set_title("Fig 1a. Imaginary dielectric function of a two-band direct-gap model")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(True, alpha=0.3)

ax2.plot(w_plot, n_omega, color="#1f4e79", lw=2.0, label=r"$n(\omega)$")
ax2.plot(w_plot, kappa_omega, color="#7030a0", lw=1.6, ls="-",
         label=r"$\kappa(\omega)$")
ax2.axvline(EG, color="#c00000", ls="--", lw=1.2)
ax2.set_xlabel(r"Photon energy $\hbar\omega$ (eV)")
ax2.set_ylabel(r"$n$, $\kappa$")
ax2.set_title(r"Fig 1b. Refractive index $n(\omega)$ from Kramers–Kronig consistency")
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(True, alpha=0.3)

fig.tight_layout()

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "46_矿物光学性质的第一性原理计算_图1.svg")
fig.savefig(out_path, format="svg", dpi=150)
print("[模型 a] 已保存:", os.path.abspath(out_path))
