# -*- coding: utf-8 -*-
# 篇名：第36篇《腔量子电动力学与量子比特实现》
# 脚本：Jaynes-Cummings 模型 —— 共振真空 Rabi 振荡与缀饰态吸收谱分裂
# 对应公式：(1)(2)(3)(4)(5)(7) 真空 Rabi 频率 Omega_R = 2g；P_e(t)=cos^2(g t)；吸收谱双峰间距 2g
# 运行环境：隔离 venv（numpy + matplotlib，禁止 scipy，禁止其他第三方库）
# 用法：python 腔量子电动力学_JaynesCummings.py  ->  输出 figures/腔量子电动力学_真空Rabi.svg

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 无显示后端，便于服务器/自动化运行
import matplotlib.pyplot as plt

# ---- 参数（角频率均用 2*pi*频率 表示，频率单位 Hz）----
# 腔 QED（里德伯原子）代表值：g/2pi = 47 kHz
# 电路 QED（transmon）代表值：g/2pi = 5 MHz
f_g_cQED = 47e3        # Hz，单光子耦合频率（腔 QED）
f_g_circuit = 5e6      # Hz，单光子耦合频率（电路 QED）
g_cQED = 2 * np.pi * f_g_cQED
g_circuit = 2 * np.pi * f_g_circuit
Omega_R_cQED = 2 * g_cQED
Omega_R_circuit = 2 * g_circuit

# 输出关键数值（回写正文第三节/第六节）
print("=== Jaynes-Cummings key numbers ===")
for name, g, Om in [("cavity QED (Rydberg)", g_cQED, Omega_R_cQED),
                    ("circuit QED (transmon)", g_circuit, Omega_R_circuit)]:
    T_R = 2 * np.pi / Om  # 振荡周期 = 2pi/Omega_R = pi/g
    print(f"[{name}] g/2pi = {g/(2*np.pi)/1e3:.1f} kHz, "
          f"Omega_R/2pi = 2g/2pi = {Om/(2*np.pi)/1e3:.1f} kHz, "
          f"T_R = pi/g = {T_R*1e6:.3f} us")

# ============ 图1a：共振真空 Rabi 振荡 P_e(t) = cos^2(g t) = (1+cos Omega_R t)/2 ============
t_cQED = np.linspace(0, 6 * np.pi / Omega_R_cQED, 600)      # 画 3 个完整周期
t_circuit = np.linspace(0, 6 * np.pi / Omega_R_circuit, 600)
P_cQED = np.cos(g_cQED * t_cQED) ** 2
P_circuit = np.cos(g_circuit * t_circuit) ** 2

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

ax = axes[0]
ax.plot(t_cQED * 1e6, P_cQED, label=r"cavity QED: $g/2\pi=47$ kHz", color="#1f77b4")
ax.plot(t_circuit * 1e6, P_circuit, label=r"circuit QED: $g/2\pi=5$ MHz", color="#d62728")
ax.set_xlabel(r"time $t$ ($\mu$s)")
ax.set_ylabel(r"excitation probability $P_e(t)=\cos^2(gt)$")
ax.set_title("Vacuum Rabi oscillation (resonant, field vacuum)")
ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3)

# ============ 图1b：吸收谱（缀饰态双峰分裂，峰距 2g = Omega_R）============
# 弱探针透射/吸收 ~ 双洛伦兹：A(delta) = g^2/((delta-g)^2+(kappa/2)^2) + g^2/((delta+g)^2+(kappa/2)^2)
kappa = 2 * np.pi * 0.5e6   # 腔衰减率代表值 0.5 MHz（远小于 g，进入强耦合）
delta = np.linspace(-1.6 * g_circuit, 1.6 * g_circuit, 800)
def absorption(delta, g, kappa):
    return (g**2) / ((delta - g)**2 + (kappa/2)**2) + (g**2) / ((delta + g)**2 + (kappa/2)**2)

A_circuit = absorption(delta, g_circuit, kappa)
A_cQED = absorption(delta, g_cQED, 2*np.pi*5e3)  # 腔 QED 用更小 kappa 代表值

ax = axes[1]
# 横轴换算成 MHz 便于比较
ax.plot(delta / (2*np.pi*1e6), A_circuit / A_circuit.max(),
        label=r"circuit QED: split = $2g/2\pi=10$ MHz", color="#d62728")
# 腔 QED 曲线单独缩放到可见（其绝对频率尺度小 100x），仅示意峰位比例
delta2 = np.linspace(-1.6 * g_cQED, 1.6 * g_cQED, 800)
A2 = absorption(delta2, g_cQED, 2*np.pi*5e3)
ax.plot(delta2 / (2*np.pi*1e3), A2 / A2.max(),
        label=r"cavity QED: split = $2g/2\pi=94$ kHz (x-axis kHz)", color="#1f77b4")
ax.axvline(0, color="k", lw=0.6, ls="--")
ax.set_xlabel(r"probe detuning $\delta=\omega_{\rm probe}-\omega_c$ (MHz for red, kHz for blue)")
ax.set_ylabel("normalized absorption")
ax.set_title("Dressed-state normal-mode splitting (peak separation = $2g$)")
ax.legend(loc="upper right", fontsize=8)
ax.grid(True, alpha=0.3)

fig.tight_layout()
out = "figures/腔量子电动力学_真空Rabi.svg"
fig.savefig(out, format="svg")
print("Saved:", out)
