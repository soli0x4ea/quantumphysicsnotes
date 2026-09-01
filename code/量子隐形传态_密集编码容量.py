# -*- coding: utf-8 -*-
"""
量子隐形传态_密集编码容量.py
对应篇目: 第33篇《量子隐形传态与密集编码》系统量子力学笔记
对应公式: 第二节式(10) 密集编码容量 I_total(p) = 1 + max(0, S(rho_B) - S(rho_AB))

物理模型
--------
Alice 与 Bob 预先共享一个两量子比特资源态
    rho(p) = p |Phi+><Phi+| + (1 - p) * I/4 ,   p in [0, 1]

密集编码(Holevo 界 + 纠缠增益):
    单量子比特经量子信道独立发送时，由 Holevo 界最多携带 1 经典比特。
    若 Alice 先与 Bob 共享 1 ebit，再发送 1 量子比特，Bob 做联合贝尔测量可
    读取 2 经典比特。纠缠提供的"额外容量"为（superdense coding 公式）
        C_extra = S(rho_B) - S(rho_AB)
    其中 S 为冯·诺依曼熵，rho_B = Tr_A(rho_AB)。总可达互信息
        I_total = 1 + max(0, C_extra)      （单位: 经典比特/发送量子比特）

对本资源态:
    rho_B = I/2  ->  S(rho_B) = 1 bit
    rho(p) 的特征值:  lambda0 = (3p+1)/4 (重数1),  lambda1=2=3 = (1-p)/4 (各重数1)
    S(rho(p)) = -[ lambda0 log2 lambda0 + 3 * (1-p)/4 log2((1-p)/4) ]
边界:
    p = 1  (纯贝尔)   S=0      -> C_extra = 1 -> I_total = 2 bit
    p = 0  (最大混合) S=2 bit  -> C_extra<0 -> I_total = 1 bit (=Holevo 界)
脚本绘制 I_total(p) 及其退化为随信道纯度 p 变化，并标出 Holevo 界 1 bit 与
最大 2 bit 线。所有文字使用英文，文件名使用中文。
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def vn_entropy(p):
    """Von Neumann entropy (bits) of rho(p) = p|Phi+><Phi+| + (1-p)I/4."""
    lam0 = (3.0 * p + 1.0) / 4.0      # eigenvalue on |Phi+>
    lam1 = (1.0 - p) / 4.0            # eigenvalue on each of the other 3 Bell states
    # guard against log2(0)
    s = np.zeros_like(p, dtype=float)
    mask0 = lam0 > 0
    mask1 = lam1 > 0
    s[mask0] += -lam0[mask0] * np.log2(lam0[mask0])
    s[mask1] += -3.0 * lam1[mask1] * np.log2(lam1[mask1])
    return s

p = np.linspace(0.0, 1.0, 401)
S_rho = vn_entropy(p)
S_B = 1.0                                  # S(rho_B) = 1 bit
C_extra = np.maximum(0.0, S_B - S_rho)     # entanglement-added capacity (bits)
I_total = 1.0 + C_extra                   # total accessible classical bits / sent qubit

# 关键数值（回写正文）
I_perfect = I_total[p >= 1.0 - 1e-9][-1] if np.any(p >= 1.0 - 1e-9) else 2.0
I_mixed = I_total[p <= 1e-9][0] if np.any(p <= 1e-9) else 1.0

print("Dense coding capacity I_total(p) = 1 + max(0, S(rho_B) - S(rho))")
print("  p=1   (pure Bell)      I_total = %.6f bit  (2 bits: 1 ebit + 1 qubit)" % I_perfect)
print("  p=0   (maximally mixed) I_total = %.6f bit  (Holevo bound = 1 bit)" % I_mixed)
print("  S(rho) at p=1   = %.6f bit" % S_rho[p >= 1.0 - 1e-9][-1])
print("  S(rho) at p=0   = %.6f bit" % S_rho[p <= 1e-9][0])

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=120)
ax.plot(p, I_total, color="#1f5fa8", linewidth=2.4, label=r"$I_{\rm total}(p)$")

# Holevo 界水平线 (无纠缠)
ax.axhline(1.0, color="#c0392b", linestyle="--", linewidth=1.6,
           label=r"Holevo bound = 1 bit (no entanglement)")
# 最大容量水平线
ax.axhline(2.0, color="#2e7d32", linestyle=":", linewidth=1.4,
           label=r"max capacity = 2 bits")

ax.plot(1.0, 2.0, "o", color="#2e7d32", markersize=7)
ax.plot(0.0, 1.0, "o", color="#c0392b", markersize=7)
ax.annotate(r"$p=1,\ I_{\rm total}=2$",
            xy=(1.0, 2.0), xytext=(0.55, 1.92),
            arrowprops=dict(arrowstyle="->", color="#2e7d32"), fontsize=11)
ax.annotate(r"$p=0,\ I_{\rm total}=1$",
            xy=(0.0, 1.0), xytext=(0.08, 1.30),
            arrowprops=dict(arrowstyle="->", color="#c0392b"), fontsize=11)

ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.85, 2.10)
ax.set_xlabel(r"Bell weight $p$ of shared channel $\rho(p)=p|\Phi^+\rangle\langle\Phi^+|+(1-p)I/4$", fontsize=11)
ax.set_ylabel(r"accessible classical bits per sent qubit $I_{\rm total}$", fontsize=11)
ax.set_title("Dense coding capacity vs channel Bell weight", fontsize=12)
ax.legend(loc="lower right", fontsize=10)
ax.grid(True, alpha=0.3)

fig.tight_layout()
out = "/Users/soli/.workbuddy/skills/机械姬Soli/WORKS/量子力学正式版/figures/量子隐形传态_密集编码容量.svg"
fig.savefig(out, format="svg")
print("Saved:", out)
