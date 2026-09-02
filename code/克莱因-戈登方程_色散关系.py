# 克莱因-戈登方程_色散关系.py
# 对应篇名：《克莱因-戈登方程（Klein-Gordon Equation）系统量子力学笔记》第 37 篇
# 对应公式：自由克莱因-戈登方程色散关系 E = +/- sqrt(p^2 c^2 + m^2 c^4)
# 单位制：SI 计算，绘图坐标以 MeV 与 MeV/c 呈现（CODATA 2018 输入常数）
# 依赖：numpy + matplotlib（仅此二者；不使用 scipy；不使用 numpy.trapz）

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---------- CODATA 2018 输入（来源：NIST 2018 CODATA adjustment）----------
c = C["c"]                 # 光速，m/s，精确
m_e = C["m_e"]          # 电子质量，kg，CODATA 2018: 9.1093837015(28)e-31
eV = C["e"]            # 1 eV = 1.602176634e-19 J，精确（2019 SI 定义）
MeV = 1.0e6 * eV                # 1 MeV in J

m0_MeV = (m_e * c**2) / MeV     # 电子静能 m_e c^2，单位 MeV
print("m_e c^2 = %.11f MeV  (CODATA 2018: 0.51099895000(15) MeV)" % m0_MeV)

# ---------- 色散关系 E = +/- sqrt((pc)^2 + (m c^2)^2) ----------
# 设 p_MeVc = p·c / (1 MeV)，则 (p c) 以 MeV 为单位，于是
# E_MeV^2 = p_MeVc^2 + m0_MeV^2
p = np.linspace(-2.0, 2.0, 2000)        # p·c 以 MeV 为单位 -> x 轴标为 MeV/c
E_pos = np.sqrt(p**2 + m0_MeV**2)       # 正能支
E_neg = -np.sqrt(p**2 + m0_MeV**2)      # 负能支

# 非相对论近似 E_NR = m c^2 + p^2/(2m)，单位 MeV
E_NR = m0_MeV + (p**2) / (2.0 * m0_MeV)

# ---------- 关键数值结论 ----------
# (1) p=0 处阈值
print("p = 0            -> E = +%.6f MeV / -%.6f MeV (质量阈值 mc^2)" % (m0_MeV, m0_MeV))
# (2) p·c = m c^2 处（p = m c，相对论性拐点）
pc_thr = m0_MeV
E_thr = np.sqrt(pc_thr**2 + m0_MeV**2)
E_NR_thr = m0_MeV + pc_thr**2 / (2.0 * m0_MeV)
print("p·c = m c^2 = %.6f MeV -> E = %.6f MeV  (非相对论近似 %.6f MeV)" % (pc_thr, E_thr, E_NR_thr))
# (3) 高能极限 p·c = 10 MeV
pc_hi = 10.0
E_hi = np.sqrt(pc_hi**2 + m0_MeV**2)
E_NR_hi = m0_MeV + pc_hi**2 / (2.0 * m0_MeV)
print("p·c = 10 MeV          -> E = %.6f MeV  (非相对论近似 %.6f MeV)" % (E_hi, E_NR_hi))
# (4) 极端相对论极限下 E ≈ |p|c，质量项可忽略
print("极端相对论 (p·c >> mc^2): E ≈ |p|c, 质量阈值占比 ~ (mc^2/E)^2 = %.4e" % ((m0_MeV/E_hi)**2))

# ---------- 绘图（SVG 内全部英文图注）----------
fig, ax = plt.subplots(figsize=(7.2, 5.0))
ax.plot(p, E_pos, color='#1f77b4', lw=1.8, label=r'$E = +\sqrt{(pc)^2 + (mc^2)^2}$')
ax.plot(p, E_neg, color='#d62728', lw=1.8, label=r'$E = -\sqrt{(pc)^2 + (mc^2)^2}$')
ax.plot(p, E_NR, color='#2ca02c', lw=1.2, ls='--', label=r'NR approx. $mc^2 + p^2/(2m)$')
ax.axhline(m0_MeV, color='gray', lw=0.8, ls=':')
ax.axhline(-m0_MeV, color='gray', lw=0.8, ls=':')
ax.axvline(0.0, color='black', lw=0.6)
ax.text(0.05, m0_MeV + 0.02, r'$+mc^2 = +%.4f$ MeV' % m0_MeV, color='gray', fontsize=9)
ax.text(0.05, -m0_MeV - 0.10, r'$-mc^2 = -%.4f$ MeV' % m0_MeV, color='gray', fontsize=9)
ax.set_xlabel(r'$p\,c$  (MeV)   —   x-axis: momentum in MeV/$c$')
ax.set_ylabel(r'$E$  (MeV)')
ax.set_title('Klein-Gordon dispersion: two energy branches (electron, $m_ec^2=0.511$ MeV)')
ax.set_xlim(-2.0, 2.0)
ax.set_ylim(-2.2, 2.2)
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/克莱因-戈登方程_色散关系.svg', format='svg')
print("Saved: figures/克莱因-戈登方程_色散关系.svg")
