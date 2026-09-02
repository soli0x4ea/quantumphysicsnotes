# 篇名：狄拉克方程（Dirac Equation）系统量子力学笔记 第 38 篇
# 公式编号：对应正文 (15) 自由狄拉克能谱 E = +/- sqrt(p^2 c^2 + m^2 c^4)
# 依赖：numpy, matplotlib（numpy 2.x；不使用 scipy / numpy.trapz）
# 产物：figures/狄拉克方程_能谱.svg

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- 常数（CODATA 2018，见参考文献 24hk）----
MEV = C["me_c2_MeV"]          # 电子静能 m_e c^2，单位 MeV
# 自然单位下取 c=1；动量 p 以 MeV/c 输入，则 p*c 数值上等于 p (MeV)

# ---- Dirac（标准）表象下的 alpha_z 与 beta（4x4，无量纲）----
_sz = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_I2 = np.eye(2, dtype=complex)
_zero = np.zeros((2, 2), dtype=complex)
alpha_z = np.block([[_zero, _sz], [_sz, _zero]])   # α_z = [[0,σ_z],[σ_z,0]]
beta = np.block([[_I2, _zero], [_zero, -_I2]])      # β   = diag(I,-I)

def H_free(p):
    """自由狄拉克哈密顿量 H = c α_z p + β m c^2，p 单位 MeV/c，返回能量单位 MeV。"""
    return p * alpha_z + MEV * beta

# ---- 数值对角化验证：自由粒子 4 个解 ----
eig0 = np.linalg.eigh(H_free(0.0))[0]   # p=0：±m c^2，各 2 重
eig1 = np.linalg.eigh(H_free(1.0))[0]   # p=1 MeV/c
print("p = 0 MeV/c 本征值 (MeV):", np.round(eig0, 6))
print("p = 1 MeV/c 本征值 (MeV):", np.round(eig1, 6))
print("解析 E = sqrt(p^2 + m^2) 在 p=1:", np.sqrt(1.0**2 + MEV**2))

# ---- 扫描动量，绘制能谱四支 ----
p = np.linspace(0.0, 3.0, 400)
E_num = np.array([np.linalg.eigh(H_free(pp))[0] for pp in p])   # shape (N,4)
E_analytic = np.sqrt(p**2 + MEV**2)     # 正能支大小（两支简并）
mass_gap = 2.0 * MEV                    # 正负能支间距 = 2 m c^2

fig, ax = plt.subplots(figsize=(7.2, 5.0))
# 数值四支
for k in range(4):
    ax.plot(p, E_num[:, k], color='tab:blue', lw=1.3, alpha=0.85)
# 解析：正负能包络 + 简并标注
ax.plot(p, E_analytic, 'k--', lw=1.2, label=r'analytic $|E|=\sqrt{p^2c^2+m^2c^4}$')
ax.plot(p, -E_analytic, 'k--', lw=1.2)
ax.axhline(0.0, color='grey', lw=0.6)
ax.axhspan(-mass_gap/2, mass_gap/2, color='tab:red', alpha=0.06)
ax.set_xlabel('momentum  $p$  (MeV/$c$)')
ax.set_ylabel('energy  $E$  (MeV)')
ax.set_title('Free Dirac energy spectrum  $E(p)$')
ax.text(2.4, MEV + 0.15, r'positive-energy branch ($2\times$ spin)', fontsize=9)
ax.text(2.4, -MEV - 0.45, r'negative-energy branch ($2\times$ spin)', fontsize=9)
ax.annotate(r'mass gap $=2m_ec^2=1.022$ MeV',
            xy=(0.0, 0.0), xytext=(0.6, 0.0),
            fontsize=9, ha='left', va='center',
            arrowprops=dict(arrowstyle='<->', color='tab:red'))
ax.set_xlim(0, 3.0)
ax.set_ylim(-2.6, 2.6)
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/狄拉克方程_能谱.svg', format='svg')
print("saved: figures/狄拉克方程_能谱.svg")
