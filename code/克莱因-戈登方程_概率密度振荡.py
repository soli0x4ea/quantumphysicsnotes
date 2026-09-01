# 克莱因-戈登方程_概率密度振荡.py
# 对应篇名：《克莱因-戈登方程（Klein-Gordon Equation）系统量子力学笔记》第 37 篇
# 对应公式：KG 守恒概率密度
#   rho = (i hbar / 2 m c^2)( phi^* d_t phi - phi d_t phi^* )
# 本脚本用自然单位 hbar = c = m = 1，演示箱（周期边界）中两个动量模式叠加时
# rho(x,t) 随时间的振荡，并展示其可正可负——即 KG 概率密度非正定困难。
# 依赖：numpy + matplotlib（仅此二者；不使用 scipy；不使用 numpy.trapz）

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# ---------- 自然单位 hbar = c = m = 1 下的两个箱动量模式 ----------
# 场：phi(x,t) = exp(i(k1 x - w1 t)) + beta * exp(-i(k2 x + w2 t))
# 其中 w_j = sqrt(k_j^2 + m^2) = sqrt(k_j^2 + 1)（m=1）。
k1 = 1.0
k2 = 3.0
beta = 0.9                      # 负能分量相对振幅（beta != 1 时密度不再恒正）
w1 = np.sqrt(k1**2 + 1.0)
w2 = np.sqrt(k2**2 + 1.0)

def field(x, t):
    return np.exp(1j * (k1 * x - w1 * t)) + beta * np.exp(-1j * (k2 * x + w2 * t))

# 密度按定义计算，避免手推符号错误：
# rho = (i/2)( phi^* d_t phi - phi d_t phi^* )，自然单位 hbar=m=1
def density(x, t):
    phi = field(x, t)
    dphi_dt = (-1j * w1) * np.exp(1j * (k1 * x - w1 * t)) \
              + (1j * w2 * beta) * np.exp(-1j * (k2 * x + w2 * t))
    return (1j / 2.0) * (np.conj(phi) * dphi_dt - phi * np.conj(dphi_dt))

# 解析形式（验证用，必须与上式一致）：
# rho = w1 - w2*beta^2 - beta*(w2 - w1)*cos((k1+k2)x + (w2-w1)t)
def density_analytic(x, t):
    return w1 - w2 * beta**2 - beta * (w2 - w1) * np.cos((k1 + k2) * x + (w2 - w1) * t)

# ---------- 网格 ----------
Lx = 2.0 * np.pi / (k1 + k2)            # 空间周期
Lt = 2.0 * np.pi / abs(w2 - w1)         # 时间周期（拍频）
x = np.linspace(0.0, Lx, 400)
t = np.linspace(0.0, Lt, 600)
X, T = np.meshgrid(x, t)
Rho = density(X, T).real
assert np.max(np.abs(Rho - density_analytic(X, T))) < 1e-12, "analytic mismatch"

# ---------- 关键数值结论 ----------
rho_min = float(np.min(Rho))
rho_max = float(np.max(Rho))
print("parameters: k1=%.2f, k2=%.2f, beta=%.2f -> w1=%.4f, w2=%.4f" % (k1, k2, beta, w1, w2))
print("rho period in time  T = 2*pi/|w2-w1| = %.4f (natural units)" % Lt)
print("rho_min = %.4f , rho_max = %.4f  (arb. units, hbar=c=m=1)" % (rho_min, rho_max))
print("density crosses zero: %s" % (rho_min < 0.0 < rho_max))
# 正数占比（箱平均意义上证明非正定）
frac_pos = float(np.sum(Rho > 0.0)) / Rho.size
print("fraction of grid where rho>0: %.3f ; fraction where rho<0: %.3f" % (frac_pos, 1.0 - frac_pos))

# ---------- 绘图（SVG 内全部英文图注）----------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 7.6))

# (a) 空间剖面：t=0 与 t=T/2
ax1.plot(x, density(x, 0.0).real, color='#1f77b4', lw=1.8, label=r'$t=0$')
ax1.plot(x, density(x, Lt / 2.0).real, color='#d62728', lw=1.8, ls='--', label=r'$t=T/2$')
ax1.axhline(0.0, color='black', lw=0.6)
ax1.set_xlabel(r'$x$  (natural units, one spatial period)')
ax1.set_ylabel(r'$\rho(x,t)$')
ax1.set_title('KG probability density: spatial profile at two times')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# (b) 时间序列：x=0 处 rho(t)
tt = np.linspace(0.0, Lt, 400)
ax2.plot(tt, density(0.0, tt).real, color='#2ca02c', lw=1.8)
ax2.axhline(0.0, color='black', lw=0.6)
ax2.set_xlabel(r'$t$  (natural units, one temporal period)')
ax2.set_ylabel(r'$\rho(0,t)$')
ax2.set_title('KG probability density at x=0: oscillation into negative values')
ax2.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/克莱因-戈登方程_概率密度振荡.svg', format='svg')
print("Saved: figures/克莱因-戈登方程_概率密度振荡.svg")
