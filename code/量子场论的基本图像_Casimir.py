# 量子场论的基本图像_Casimir.py
# 篇名：量子场论的基本图像（Basics of Quantum Field Theory）系统量子力学笔记
# 对应公式：
#   式(8) 理想导体平行平板间的 Casimir 压强（吸引）
#          P(d) = - pi^2 hbar c / (240 d^4)         (d 为板间距)
#        其绝对值 |P| = |F|/A = pi^2 hbar c / (240 d^4)  ∝ d^{-4}
# 说明：脚本直接由式(8)数值计算 |F|/A 随 d 的变化，并在双对数坐标中验证 -4 次幂律。
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）

# ---- 常数（CODATA 2018；SI 单位）----
hbar = C["hbar"]   # J*s
c = C["c"]          # m/s
pi = np.pi

def casimir_pressure(d):
    """返回 Casimir 压强绝对值 |F|/A（单位 N/m^2 = Pa）；d 单位 m。"""
    return pi**2 * hbar * c / (240.0 * d**4)

# ---- 间距扫描：0.1 μm ~ 10 μm ----
d = np.logspace(-7, -4, 200)   # m
P = casimir_pressure(d)

# ---- 参考点数值 ----
for dd, tag in [(1e-7, '0.1 μm'), (1e-6, '1 μm'), (1e-5, '10 μm')]:
    val = casimir_pressure(dd)
    print("d = %s (%.1e m)  |F|/A = %.4e N/m^2 = %.4e Pa" % (tag, dd, val, val))

# 面积 A = 1 cm^2 时、d = 1 μm 的吸引力
A = 1.0e-4
F_1cm2 = casimir_pressure(1e-6) * A
print("Force on A = 1 cm^2 at d = 1 μm : %.4e N" % F_1cm2)

# ---- 局部幂律指数 d ln P / d ln d，应趋近 -4 ----
logd = np.log(d)
logP = np.log(P)
slope = (logP[1:] - logP[:-1]) / (logd[1:] - logd[:-1])

# ---- 绘图（SVG 内图注全英文）----
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0))

axes[0].loglog(d * 1e6, P, 'b-')
axes[0].set_xlabel('plate separation d (μm)')
axes[0].set_ylabel('|Casimir pressure| |F|/A (N/m^2)')
axes[0].set_title('(a) Casimir pressure vs separation (slope -4)')
axes[0].grid(True, which='both', ls=':')
axes[0].plot(1.0, casimir_pressure(1e-6), 'ro')
axes[0].annotate('d = 1 μm\n%.2e Pa' % casimir_pressure(1e-6),
                 xy=(1.0, casimir_pressure(1e-6)),
                 xytext=(1.6, casimir_pressure(1e-6) * 6.0),
                 arrowprops=dict(arrowstyle='->'))

axes[1].plot(d[:-1] * 1e6, slope, 'g-')
axes[1].axhline(-4.0, color='r', ls='--', label='ideal exponent -4')
axes[1].set_xlabel('plate separation d (μm)')
axes[1].set_ylabel('local slope d ln P / d ln d')
axes[1].set_title('(b) Local power-law exponent')
axes[1].legend()
axes[1].grid(True, ls=':')

fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子场论的基本图像_Casimir.svg', format='svg')
print("saved figure: 量子场论的基本图像_Casimir.svg")
