# 篇名：狄拉克方程（Dirac Equation）系统量子力学笔记 第 38 篇
# 公式编号：对应正文 (16)(17) 氢原子狄拉克精确谱 vs 薛定谔能级
# 依赖：numpy, matplotlib（numpy 2.x；不使用 scipy / numpy.trapz）
# 产物：figures/狄拉克方程_氢原子精细结构.svg

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# ---- 常数（CODATA 2018，见参考文献 24hk）----
ALPHA = 1.0 / 137.035999084          # 精细结构常数
MEV = 0.51099895000                  # m_e c^2 (MeV)
M_EV = MEV * 1.0e6                   # m_e c^2 (eV)
EV_TO_HZ = 2.417989242e14            # 1 eV = 2.417989242e14 Hz
Z = 1.0                              # 氢原子

def E_Dirac_total(n, kappa):
    """氢原子狄拉克精确总能量 (eV)。kappa = j + 1/2。"""
    Zac = Z * ALPHA
    denom = n - kappa + np.sqrt(kappa**2 - Zac**2)
    return M_EV * (1.0 + (Zac**2) / (denom**2)) ** (-0.5)

def E_Schrodinger(n):
    """非相对论（薛定谔）束缚能级相对连续谱的偏移 (eV，负值)。"""
    return -M_EV * (Z * ALPHA) ** 2 / (2.0 * n ** 2)

# ---- 计算各能级（相对连续谱 E=0 的绑定能偏移）----
E1_1S = E_Dirac_total(1, 1) - M_EV            # 1S_{1/2} (n=1, j=1/2, kappa=1)
E2_S  = E_Dirac_total(2, 1) - M_EV            # 2S_{1/2} (n=2, j=1/2, kappa=1)
E2_P1 = E2_S                                  # 2P_{1/2} 与 2S_{1/2} 在狄拉克点核模型下简并
E2_P3 = E_Dirac_total(2, 2) - M_EV            # 2P_{3/2} (n=2, j=3/2, kappa=2)
E2_Schr = E_Schrodinger(2)                    # 薛定谔 n=2（l,j 全部简并）

print("E_rel (eV): 1S1/2 =", np.round(E1_1S, 6))
print("E_rel (eV): 2S1/2 / 2P1/2 (Dirac) =", np.round(E2_S, 6))
print("E_rel (eV): 2P3/2 (Dirac)        =", np.round(E2_P3, 6))
print("E_rel (eV): n=2 Schrodinger      =", np.round(E2_Schr, 6))
fs_split_eV = E2_P3 - E2_S                  # 2P3/2 比 2S1/2 高（结合更松）
fs_split_GHz = fs_split_eV * EV_TO_HZ / 1.0e9
print("Fine-structure split 2P3/2 - 2S1/2 =", fs_split_eV, "eV =", fs_split_GHz, "GHz")
lamb_MHz = 1058.0                            # 现代 Lamb 位移 ~1058 MHz（见 24hi, 24hm）
lamb_eV = lamb_MHz * 1.0e6 / EV_TO_HZ
print("Lamb shift (QED) ~", lamb_MHz, "MHz =", lamb_eV, "eV")

# ---- 绘图 ----
fig = plt.figure(figsize=(7.6, 6.2))

# 主面板：整体能级（n=1 与 n=2 群）
ax1 = fig.add_axes([0.14, 0.56, 0.74, 0.36])
ax1.axhline(0.0, color='grey', lw=0.8, ls='--')
ax1.plot([0.6, 1.4], [E1_1S, E1_1S], 'r-', lw=2.2, label=r'$1S_{1/2}$ (Dirac)')
ax1.plot([0.6, 1.4], [E2_S, E2_S], 'r-', lw=2.2, label=r'$2S_{1/2},2P_{1/2}$ (Dirac)')
ax1.plot([0.6, 1.4], [E2_P3, E2_P3], 'r-', lw=2.2)
ax1.plot([1.6, 2.4], [E2_Schr, E2_Schr], 'b--', lw=1.6, label=r'$n=2$ Schrodinger (degenerate)')
ax1.set_ylabel(r'binding energy offset $E-m_ec^2$ (eV)')
ax1.set_title('Hydrogen levels: Dirac vs Schrodinger (Z=1)')
ax1.set_xlim(0.4, 2.6)
ax1.set_ylim(-16.0, -2.0)
ax1.legend(loc='lower right', fontsize=8)
ax1.grid(True, alpha=0.25)

# 缩放进面板：n=2 精细结构（展宽 ~1e-4 eV 量级）
ax2 = fig.add_axes([0.14, 0.10, 0.74, 0.36])
ax2.axhline(E2_Schr, color='blue', ls='--', lw=1.4)
ax2.text(2.55, E2_Schr, r'Schrodinger $n=2$', color='blue', fontsize=8, va='center')
ax2.plot([0.6, 1.4], [E2_S, E2_S], 'r-', lw=2.4, label=r'$2S_{1/2}=2P_{1/2}$ (Dirac)')
ax2.plot([0.6, 1.4], [E2_P3, E2_P3], 'r-', lw=2.4, label=r'$2P_{3/2}$ (Dirac)')
ymin, ymax = -3.40130, -3.40112
ax2.set_ylim(ymin, ymax)
ax2.set_xlim(0.4, 2.8)
ax2.set_ylabel(r'$E-m_ec^2$ (eV)  [zoom]')
ax2.set_xlabel('level (schematic)')
ax2.set_title(r'$n=2$ fine-structure splitting')
ax2.legend(loc='lower right', fontsize=8)
ax2.grid(True, alpha=0.25)
# 标注 Dirac 简并 与 Lamb 位移
ax2.annotate(r'Dirac degeneracy: $2S_{1/2}=2P_{1/2}$',
             xy=(1.0, E2_S), xytext=(1.5, E2_S - 4e-6),
             fontsize=8, color='red',
             arrowprops=dict(arrowstyle='->', color='red'))
lamb_txt = 'Lamb shift (QED, ~1058 MHz ~ 4.4 ueV)\nlifts 2S1/2 above 2P1/2'
ax2.text(0.45, ymin + 0.5e-5, lamb_txt, fontsize=7.5, color='darkgreen')
ax2.text(1.05, (E2_S + E2_P3) / 2, r'$\Delta E_{\rm fs}\approx4.5\times10^{-5}$ eV',
         fontsize=8, va='center', color='black')

fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/狄拉克方程_氢原子精细结构.svg', format='svg')
print("saved: figures/狄拉克方程_氢原子精细结构.svg")
