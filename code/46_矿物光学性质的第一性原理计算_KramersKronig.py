# -*- coding: utf-8 -*-
"""
46_矿物光学性质的第一性原理计算_KramersKronig.py

对应《矿物光学性质的第一性原理计算》（第 46 篇）第六节 "典型系统与可解模型"
中的模型 (b)：用 numpy 由 ε₂(ω) 经 Kramers–Kronig 数值（Hilbert 变换）反演 ε₁(ω)，
再得到折射率 n(ω)。

为保证"反演"可信，先做解析校验：采用满足因果性的 Lorentz 振子模型
    ε(ω) = 1 + ω_p² / (ω_0² - ω² - iγω)
其 ε₁、ε₂ 有闭式表达式，且严格满足 Kramers–Kronig 关系。把 ε₂ 喂给我的数值
KK 程序反推 ε₁，与解析 ε₁ 比对；二者重合即证明反演可信。随后用反演得到的 ε₁
与原始 ε₂ 计算 n(ω)，与解析 n(ω) 比对。

依赖：numpy + matplotlib 仅此二者（禁用 scipy）。
运行：~/.workbuddy/binaries/python/envs/default/bin/python 46_矿物光学性质的第一性原理计算_KramersKronig.py
输出：figures/46_矿物光学性质的第一性原理计算_图2.svg
"""

import matplotlib
matplotlib.use("Agg")  # 无显示后端，必须置于 pyplot 导入之前
import numpy as np
import matplotlib.pyplot as plt
import os


# ---------------------------------------------------------------------------
# Kramers–Kronig 数值反演（与模型 a 同一实现）
#   ε₁(ω) = 1 + (2/π) P ∫₀^∞ [ω' ε₂(ω')] / (ω'² - ω²) dω'
# 均匀网格上的 np.trapezoid；极点处主值置零（精细网格误差小）。
# ---------------------------------------------------------------------------
def kramers_kronig_epsilon1(w, eps2):
    eps1 = np.empty_like(w)
    for i, wi in enumerate(w):
        j0 = np.argmin(np.abs(w - wi))
        with np.errstate(divide="ignore", invalid="ignore"):
            integrand = w * eps2 / (w**2 - wi**2)
        integrand[j0] = 0.0
        eps1[i] = 1.0 + (2.0 / np.pi) * np.trapezoid(integrand, w)
    return eps1


# ---------------------------------------------------------------------------
# Lorentz 振子（解析闭式，严格满足 KK）
#   ε₂(ω) = ω_p² γ ω / [(ω_0² - ω²)² + (γ ω)²]
#   ε₁(ω) = 1 + ω_p² (ω_0² - ω²) / [(ω_0² - ω²)² + (γ ω)²]
# ---------------------------------------------------------------------------
WP = 8.0    # 等离子频率 ω_p (eV)
W0 = 5.0    # 共振频率 ω_0 (eV)
GAM = 0.6   # 阻尼 γ (eV)


def lorentz_eps2(w):
    denom = (W0**2 - w**2)**2 + (GAM * w)**2
    return WP**2 * GAM * w / denom


def lorentz_eps1(w):
    denom = (W0**2 - w**2)**2 + (GAM * w)**2
    return 1.0 + WP**2 * (W0**2 - w**2) / denom


def refractive_index(eps1, eps2):
    mod = np.sqrt(eps1**2 + eps2**2)
    n = np.sqrt((mod + eps1) / 2.0)
    kappa = np.sqrt((mod - eps1) / 2.0)
    return n, kappa


# ---------------------------------------------------------------------------
# 在均匀细化网格上做 KK 反演并校验（精细网格以解析分辨 Lorentz 共振）
# ---------------------------------------------------------------------------
w_kk = np.linspace(0.005, 40.0, 12000)
eps2_kk = lorentz_eps2(w_kk)
eps1_exact = lorentz_eps1(w_kk)
eps1_num = kramers_kronig_epsilon1(w_kk, eps2_kk)

abs_err = np.abs(eps1_num - eps1_exact)
rel_err = abs_err / (np.abs(eps1_exact) + 1e-9)
n_exact_kk, _ = refractive_index(eps1_exact, eps2_kk)
n_num_kk, _ = refractive_index(eps1_num, eps2_kk)
rel_err_n = np.abs(n_num_kk - n_exact_kk) / (np.abs(n_exact_kk) + 1e-9)
idx = np.abs(w_kk - 5.0).argmin()
print("[模型 b] Lorentz 校验: ω_0=%.1f eV, ω_p=%.1f eV, γ=%.2f eV" % (W0, WP, GAM))
print("[模型 b] ε₁ 最大绝对误差 = %.4e ; n(ω) 最大相对误差 = %.4e"
      % (abs_err.max(), rel_err_n.max()))
print("[模型 b] ω=5.0 eV: ε₁_exact=%.4f, ε₁_num=%.4f, ε₂=%.4f"
      % (eps1_exact[idx], eps1_num[idx], eps2_kk[idx]))

# ---------------------------------------------------------------------------
# 绘图网格：KK 反演在细化网格 w_kk 上完成后插值到绘图网格，保证曲线重合
# ---------------------------------------------------------------------------
w = np.linspace(0.05, 12.0, 1200)
eps2 = lorentz_eps2(w)
eps1_a = lorentz_eps1(w)
eps1_n = np.interp(w, w_kk, eps1_num)
n_a, kappa_a = refractive_index(eps1_a, eps2)
n_n, kappa_n = refractive_index(eps1_n, eps2)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 8.0))

ax1.plot(w, eps2, color="#1f4e79", lw=2.0, label=r"$\varepsilon_2(\omega)$ (input)")
ax1.plot(w, eps1_a, color="#c00000", lw=1.8, label=r"$\varepsilon_1(\omega)$ analytic")
ax1.plot(w, eps1_n, color="#2e7d32", lw=1.2, ls="--",
         label=r"$\varepsilon_1(\omega)$ from KK inversion")
ax1.axvline(W0, color="#888888", ls=":", lw=1.0)
ax1.set_xlabel(r"Photon energy $\hbar\omega$ (eV)")
ax1.set_ylabel(r"$\varepsilon_1,\ \varepsilon_2$")
ax1.set_title("Fig 2a. Kramers–Kronig inversion validated on a Lorentz oscillator")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(True, alpha=0.3)

ax2.plot(w, n_a, color="#c00000", lw=1.8, label=r"$n(\omega)$ analytic")
ax2.plot(w, n_n, color="#2e7d32", lw=1.2, ls="--",
         label=r"$n(\omega)$ from KK + $\varepsilon_2$")
ax2.plot(w, kappa_a, color="#7030a0", lw=1.4, label=r"$\kappa(\omega)$")
ax2.set_xlabel(r"Photon energy $\hbar\omega$ (eV)")
ax2.set_ylabel(r"$n$, $\kappa$")
ax2.set_title(r"Fig 2b. Refractive index recovered from $\varepsilon_2$ via KK")
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(True, alpha=0.3)

fig.tight_layout()

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "46_矿物光学性质的第一性原理计算_图2.svg")
fig.savefig(out_path, format="svg", dpi=150)
print("[模型 b] 已保存:", os.path.abspath(out_path))
