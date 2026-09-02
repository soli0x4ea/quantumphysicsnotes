# 反粒子与狄拉克海_对产生阈值.py
# 篇名：反粒子与狄拉克海（Antiparticles and the Dirac Sea）系统量子力学笔记
# 对应公式：第六节 (a) e+e- 对产生阈值 E_th = 2 m_e c^2
#   在核库仑场（三体）中单光子产生对的严格阈值（含反冲修正）：
#   E_gamma,min = 2 m_e c^2 (1 + m_e / M_N)
# 依赖：numpy + matplotlib（numpy 2.x，禁用 scipy / numpy.trapz）
# 单位：SI；能量同时给出 J 与 MeV

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- CODATA 2018 基本常数（NIST），2019 SI 重新定义后 e、c 为精确值 ----
m_e = C["m_e"]      # kg   电子/正电子静止质量 (CODATA 2018)
c   = C["c"]           # m/s  真空中光速（精确）
e   = C["e"]       # C    基本电荷（精确）
m_p = C["m_p"]    # kg   质子质量（CODATA 2018），用于反冲修正示例
MeV = 1.0e6 * e             # 1 MeV 对应的焦耳数（精确，因为 e、1e6 为定义值）

# ---- 计算 ----
E_rest_J   = m_e * c**2                 # 单个电子/正电子静止能量 (J)
E_rest_MeV = E_rest_J / MeV            # 0.51099895000... MeV
E_thr_J    = 2.0 * E_rest_J            # 对产生阈值（无反冲近似）(J)
E_thr_MeV  = 2.0 * E_rest_MeV          # 1.02199790000... MeV

# 含核反冲的严格阈值（实验室系，核初始静止）：
# s = (p_gamma + p_N)^2 = M_N^2 + 2 M_N E_gamma  (c=1)
# 阈值末态为质量 M_N+2m_e 的单一系统：s_th = (M_N + 2m_e)^2
# => E_gamma,min = 2 m_e c^2 (1 + m_e / M_N)
E_thr_recoil_MeV = 2.0 * E_rest_MeV * (1.0 + m_e / m_p)

print("=== e+e- 对产生阈值数值结果（CODATA 2018）===")
print(f"m_e c^2        = {E_rest_J:.6e} J  = {E_rest_MeV:.11f} MeV")
print(f"2 m_e c^2      = {E_thr_J:.6e} J  = {E_thr_MeV:.11f} MeV")
print(f"阈值（无反冲）  = {E_thr_MeV:.6f} MeV  (≈ 1.022 MeV)")
print(f"阈值（质子靶反冲修正） = {E_thr_recoil_MeV:.6f} MeV")
print(f"反冲修正量      = {E_thr_recoil_MeV - E_thr_MeV:.6e} MeV")

# ---- 绘图：能量阈值示意图（SVG 内文字全英文）----
fig, ax = plt.subplots(figsize=(7.2, 5.0))

ymax = 1.25
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(0.0, ymax)
ax.axhline(0.0, color='black', lw=0.8)
ax.set_ylabel('Photon / pair energy  E  (MeV)')
ax.set_xticks([])
ax.set_title('e+e- pair-production threshold  E_th = 2 m_e c^2')

# 亚阈值区（淡红）：自由真空中单光子无法产生有质量对
ax.axhspan(0.0, E_thr_MeV, color='#f4cccc', alpha=0.5)
ax.text(0.0, E_thr_MeV*0.5, 'sub-threshold\n(no free pair creation\nin vacuum)',
        ha='center', va='center', fontsize=9, color='#990000')

# 阈值线
ax.axhline(E_thr_MeV, color='#1a73e8', lw=2.0)
ax.plot([-0.05, 0.05], [E_rest_MeV, E_rest_MeV], color='black', lw=1.5)
ax.text(0.15, E_rest_MeV, f'm_e c^2 = {E_rest_MeV:.3f} MeV\n(one lepton rest energy)',
        fontsize=9, va='center')
ax.text(0.15, E_thr_MeV, f'2 m_e c^2 = {E_thr_MeV:.3f} MeV\n(pair threshold)',
        fontsize=9, va='center', color='#1a73e8')

# 标注：阈值之上可成对产生
ax.annotate('', xy=(0.0, ymax), xytext=(0.0, E_thr_MeV),
            arrowprops=dict(arrowstyle='->', color='#0b8043', lw=1.5))
ax.text(0.0, ymax-0.05, 'above threshold:\nphoton + nucleus -> e+ + e- + nucleus',
        ha='center', va='top', fontsize=9, color='#0b8043')

ax.grid(axis='y', ls=':', alpha=0.4)
fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/反粒子与狄拉克海_对产生阈值.svg',
            format='svg')
print("Saved: figures/反粒子与狄拉克海_对产生阈值.svg")
