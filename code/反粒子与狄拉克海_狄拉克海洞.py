# 反粒子与狄拉克海_狄拉克海洞.py
# 篇名：反粒子与狄拉克海（Antiparticles and the Dirac Sea）系统量子力学笔记
# 对应公式：第六节 (b) 狄拉克海"洞"的电荷/能量符号演示
#   负能电子态（电荷 -e，能量 -E，E>0）被泡利原理填满；
#   缺位（洞）携带：电荷 = +e，能量 = +E，质量 = m_e  -> 表现为正电子。
# 依赖：numpy + matplotlib（numpy 2.x，禁用 scipy / numpy.trapz）
# 图注全英文。

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# ---- CODATA 2018 基本常数 ----
m_e = 9.1093837011e-31      # kg
c   = 299792458.0           # m/s
e   = 1.602176634e-19       # C
MeV = 1.0e6 * e
E0_MeV = (m_e * c**2) / MeV # 0.51099895... MeV，取作示例洞的 |E|

# ---- 数值表（打印到 stdout；不进入 SVG）----
print("=== 狄拉克海：电子态 vs 洞态（电荷/能量符号）===")
print(f"{'量':<18}{'电子 (负能态)':<22}{'洞 (缺位)':<22}")
print(f"{'电荷 Q':<18}{'-e = -'+format(e,'.3e')+' C':<22}{'+e = +'+format(e,'.3e')+' C':<22}")
print(f"{'能量 E (相对满海)':<18}{'-'+format(E0_MeV,'.3f')+' MeV':<22}{'+'+format(E0_MeV,'.3f')+' MeV':<22}")
print(f"{'质量':<18}{'m_e':<22}{'m_e (正电子)':<22}")
print("结论：洞 = 带正电、正能量、质量 m_e 的粒子 = 正电子 (e+)。")

# ---- 绘图：狄拉克海示意图 ----
rng = np.random.default_rng(20260901)
fig, ax = plt.subplots(figsize=(7.2, 5.4))

# 能量轴范围
E_bounds = 1.30
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-E_bounds, E_bounds)
ax.set_ylabel('Energy  E  (MeV)')
ax.set_xticks([])

# 负能连续谱（狄拉克海，已填满）-- 淡蓝阴影
ax.axhspan(-E_bounds, 0.0, color='#cfe2f3', alpha=0.55)
ax.text(0.0, -E_bounds+0.08, 'Filled negative-energy continuum  (Dirac sea)',
        ha='center', va='bottom', fontsize=9, color='#073763')

# 正能连续谱
ax.axhspan(0.0, E_bounds, color='#fff2cc', alpha=0.45)
ax.text(0.0, E_bounds-0.08, 'Positive-energy continuum  (ordinary particles)',
        ha='center', va='top', fontsize=9, color='#7f6000')

# 费米能级 E=0
ax.axhline(0.0, color='black', lw=1.2)
ax.text(-1.15, 0.02, 'E = 0 (Fermi level of the sea)', fontsize=8.5, va='bottom')

# 在负能海中绘制许多已占据态（点）
N = 90
y_fill = rng.uniform(-E_bounds+0.05, -0.05, N)
x_fill = rng.uniform(-0.9, 0.9, N)
ax.scatter(x_fill, y_fill, s=14, color='#073763', alpha=0.8, zorder=2)

# 选一个被"移走"的负能电子，形成洞：位于 -E0_MeV
hole_y = -E0_MeV
hole_x = 0.0
ax.scatter([hole_x], [hole_y], s=120, facecolors='none',
           edgecolors='#cc0000', linewidths=2.2, zorder=5)
ax.text(hole_x+0.12, hole_y, f'missing electron\n(Q=-e, E=-{E0_MeV:.3f} MeV)',
        fontsize=8.5, color='#cc0000', va='center')

# 洞对应的正电子：从 0 向上到 +E0_MeV 的箭头，标注 +e
ax.annotate('', xy=(hole_x, +E0_MeV), xytext=(hole_x, 0.0),
            arrowprops=dict(arrowstyle='->', color='#cc0000', lw=2.0), zorder=4)
ax.text(hole_x+0.12, +E0_MeV, f'hole = positron (e+)\n(Q=+e, E=+{E0_MeV:.3f} MeV, m=m_e)',
        fontsize=8.5, color='#cc0000', va='center')

# 一个普通正能电子（蓝点，位于 +E0_MeV 上方）
ax.scatter([0.6], [0.85], s=40, color='#073763', zorder=5)
ax.text(0.72, 0.85, 'electron (Q=-e)', fontsize=8.5, color='#073763', va='center')

ax.set_title('Dirac sea: a hole in the filled negative-energy states is a positron')
ax.grid(axis='y', ls=':', alpha=0.4)
fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/反粒子与狄拉克海_狄拉克海洞.svg',
            format='svg')
print("Saved: figures/反粒子与狄拉克海_狄拉克海洞.svg")
