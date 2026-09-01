# -*- coding: utf-8 -*-
# 篇名：第36篇《腔量子电动力学与量子比特实现》
# 脚本：受驱量子比特 Rabi 振荡 P_e(t)=exp(-t/T2)*sin^2(Omega_R t/2)，对比各平台相干尺度
# 对应公式：(10)(11) 退相干包络 e^{-t/T2}
# 运行环境：隔离 venv（numpy + matplotlib，禁止 scipy，禁止其他第三方库）
# 用法：python 腔量子电动力学_量子比特Rabi.py  ->  输出 figures/腔量子电动力学_量子比特Rabi.svg

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 统一驱动频率（仅为尺度对比，不代表各平台真实工作频率）
f_drive = 1e6            # Hz, Omega_R^(drive)/2pi = 1 MHz
Om = 2 * np.pi * f_drive

# 各平台代表性相干时间（量级，见正文第三节/第五节；此处用于尺度对比）
platforms = {
    "Ion trap (171Yb+ / 40Ca+)": 1.0,          # 秒量级
    "Superconducting transmon":   50e-6,        # 50 us 量级
    "NV center (room T)":         1e-3,        # 1 ms 量级
}

print("=== Driven-qubit Rabi: coherent oscillations within T2 ===")
for name, T2 in platforms.items():
    N = Om * T2 / np.pi    # 相干时间内可完成的振荡次数 ~ Omega_R*T2/pi
    print(f"[{name}] T2 = {T2*1e3 if T2>=1e-3 else T2*1e6:.3g} "
          f"{'ms' if T2>=1e-3 else 'us'}, N_osc ~ {N:.2e}")

fig, ax = plt.subplots(figsize=(9, 5))
t_max = {"Ion trap (171Yb+ / 40Ca+)": 4e-3,
         "Superconducting transmon":   200e-6,
         "NV center (room T)":         4e-3}
colors = {"Ion trap (171Yb+ / 40Ca+)": "#2ca02c",
          "Superconducting transmon":   "#d62728",
          "NV center (room T)":        "#9467bd"}

for name, T2 in platforms.items():
    t = np.linspace(0, t_max[name], 2000)
    P = np.exp(-t / T2) * np.sin(Om * t / 2) ** 2
    ax.plot(t * 1e6, P, label=f"{name}  (T2={T2*1e6:.0f} us)" if T2 < 1 else
            f"{name}  (T2={T2*1e3:.0f} ms)", color=colors[name], lw=1.6)

ax.set_xlabel(r"time $t$ ($\mu$s)")
ax.set_ylabel(r"$P_e(t)=e^{-t/T_2}\sin^2(\Omega_R t/2)$")
ax.set_title("Resonantly driven qubit Rabi oscillation with decoherence envelope")
ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.05, 1.05)

# ---- 量级表（文字标注，英文）----
txt = ("Order-of-magnitude coherence times:\n"
       "Ion trap:  ~1-10 s\n"
       "Superconducting transmon:  ~10-100 us\n"
       "NV center (room T):  ~1 ms; (low T, isotopically purified): up to ~s")
ax.text(0.02, 0.30, txt, transform=ax.transAxes, fontsize=8,
        bbox=dict(boxstyle="round", fc="wheat", alpha=0.25))

fig.tight_layout()
out = "figures/腔量子电动力学_量子比特Rabi.svg"
fig.savefig(out, format="svg")
print("Saved:", out)
