# 量子场论的基本图像_模式量子化.py
# 篇名：量子场论的基本图像（Basics of Quantum Field Theory）系统量子力学笔记
# 对应公式：
#   式(5) 一维单原子链声学支色散  omega_k = 2 (v/a) |sin(k a / 2)|
#   式(6) 各模零点能（真空能）      E0 = sum_k (1/2) hbar omega_k
#   式(7) 玻色-爱因斯坦平衡占据数  <n_k> = 1 / (exp(hbar omega_k / (k_B T)) - 1)
# 说明：把一条 N 个格点的谐振子链当作「一维场」的离散模式；每个模式即一个量子谐振子，
#       量子化后零点能正比于模式频率之和。把格点间距 a 当作紫外截断，
#       可直观显示场论零点能在无截断时按 1/a^2 发散（即真空能/宇宙学常数问题的来源之一）。
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# ---- 常数（CODATA 2018 推荐值；SI 单位）----
hbar = 1.054571817e-34   # J*s   约化普朗克常数（2019 重定义后精确值）
kB   = 1.380649e-23       # J/K   玻尔兹曼常数（2019 重定义后精确值）

# ---- 一维单原子链参数 ----
N = 50                      # 格点数（无量纲整数）
a = 5.00e-10                # 晶格常数 m（0.5 nm，典型原子间距量级）
v = 1.00e3                  # 声速 m/s（典型晶格声速量级）

# 由近邻弹性常数 K 与质量 m 的关系 v = a sqrt(K/m) 得色散
omega_max = 2.0 * v / a    # 带宽上限 s^-1
m_idx = np.arange(-N // 2, N // 2)              # 整数指标
k = 2.0 * np.pi * m_idx / (N * a)               # 波矢 m^-1
omega = omega_max * np.abs(np.sin(k * a / 2.0)) # 式(5)；m_idx=0 给出零模 omega=0

# ---- 零点能（式6）----
E0_per_mode = 0.5 * hbar * omega
E0_total = float(np.sum(E0_per_mode))           # J
E0_per_site = E0_total / N                       # J / site
L_chain = N * a                                   # 链长 m
u0 = E0_total / L_chain                           # 零点能密度 J/m

# ---- 紫外截断扫描：把 a_lat 当作连续化紫外截断，固定 N，看零点能密度 ----
def E0_chain(a_lat, Nlat=50):
    kk = 2.0 * np.pi * np.arange(-Nlat // 2, Nlat // 2) / (Nlat * a_lat)
    ww = (2.0 * v / a_lat) * np.abs(np.sin(kk * a_lat / 2.0))
    return float(np.sum(0.5 * hbar * ww))

a_list = np.array([5e-10, 5e-11, 5e-12, 5e-13])   # 截断间距递减 -> 紫外上限增大
E0_scan = np.array([E0_chain(aa) for aa in a_list])
u_scan = E0_scan / (50.0 * a_list)                 # 对应能量密度 J/m

# ---- 玻色-爱因斯坦平衡占据数（式7）----
T_vals = [10.0, 300.0]                             # K
nk = {}
for T in T_vals:
    x = hbar * omega / (kB * T)
    with np.errstate(divide='ignore'):
        occ = 1.0 / (np.exp(x) - 1.0)
    occ[omega == 0.0] = 0.0                         # 零模（omega=0）无热激发
    nk[T] = occ

# 最小非零模对应的下标（m_idx = -1 或 +1，取决于 arange 顺序）
nonzero = np.where(omega > 0.0)[0]
idx_small = nonzero[np.argmin(np.abs(k[nonzero]))]   # 最小 |k| 非零模
idx_large = nonzero[np.argmax(np.abs(k[nonzero]))]  # 最大 |k| 模

# ---- 输出（供笔记回写具体数字）----
print("N =", N, " a =", a, " v =", v)
print("omega_max = %.4e s^-1 (%.4f THz)" % (omega_max, omega_max / 1e12))
print("E0_total   = %.4e J  = %.4e eV" % (E0_total, E0_total / 1.602176634e-19))
print("E0_per_site= %.4e J  = %.4e eV" % (E0_per_site, E0_per_site / 1.602176634e-19))
print("u0 (zero-point energy density) = %.4e J/m" % u0)
print("cutoff scan (a_lat [m], E0 [J], u [J/m]):")
for aa, e0, uu in zip(a_list, E0_scan, u_scan):
    print("   a=%.1e  E0=%.4e  u=%.4e" % (aa, e0, uu))
print("scale check u * a^2 =", ["%.3e" % (uu * aa**2) for aa, uu in zip(a_list, u_scan)],
      " (应近似常数 => u ∝ 1/a^2)")
print("nk[T=300K] at smallest nonzero k (idx %d) = %.4e ; at largest k (idx %d) = %.4e"
      % (idx_small, nk[300.0][idx_small], idx_large, nk[300.0][idx_large]))
print("nk[T=10K ] at smallest nonzero k (idx %d) = %.4e ; at largest k (idx %d) = %.4e"
      % (idx_small, nk[10.0][idx_small], idx_large, nk[10.0][idx_large]))

# ---- 绘图（SVG 内图注全英文）----
fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.0))

axes[0].plot(k / a, omega / 1e12, 'b-')
axes[0].set_xlabel('k a / (2 pi)  (dimensionless)')
axes[0].set_ylabel('omega (THz)')
axes[0].set_title('(a) Dispersion of 1D oscillator chain')
axes[0].grid(True, ls=':')

axes[1].plot(np.arange(N), E0_per_mode / 1e-22, 'g.-')
axes[1].set_xlabel('mode index')
axes[1].set_ylabel('per-mode zero-point energy (1e-22 J)')
axes[1].set_title('(b) Per-mode zero-point energy')
axes[1].grid(True, ls=':')

for T in T_vals:
    axes[2].plot(k / a, nk[T], label='T = %g K' % T)
axes[2].set_xlabel('k a / (2 pi)  (dimensionless)')
axes[2].set_ylabel('mean occupation <n_k>')
axes[2].set_title('(c) Bose-Einstein occupation')
axes[2].legend()
axes[2].grid(True, ls=':')

fig.tight_layout()
fig.savefig('/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子场论的基本图像_模式量子化.svg', format='svg')
print("saved figure: 量子场论的基本图像_模式量子化.svg")
