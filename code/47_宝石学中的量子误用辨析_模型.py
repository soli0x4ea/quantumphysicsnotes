# -*- coding: utf-8 -*-
"""
47_宝石学中的量子误用辨析_模型.py

对应笔记：第 47 篇《宝石学中的量子误用辨析_系统量子力学笔记》
依赖：numpy + matplotlib（仅此二者，禁 scipy）
后端：matplotlib.use("Agg")   （无显示环境）

生成资产：
  figures/47_宝石学中的量子误用辨析_图1.svg  -- Bloch 球对照
      左：线性双折射后单光子偏振态仍为可分离纯态（|r|=1，球面上一点）
      右：纠缠 Bell 对的单端约化态为最大混态（r=0，球心）
      -> 直观证明「双折射不增纠缠」
  figures/47_宝石学中的量子误用辨析_图2.svg  -- 红宝石 Cr3+ 简化能级图
      锐 R 发射线（2E->4A2, 694.3 nm）vs 蓝绿宽吸收带（4A2->4T1,4T2）

常数为 CODATA 2018（2019 SI 重新定义后 h,c,e 为精确值）。
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  确保 3D 投影可用
from constants import C as CODATA  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）


# ---------------- 常数（CODATA 2018，精确值）----------------
H = CODATA["h"]        # J·s   普朗克常数（精确）
C = CODATA["c"]           # m/s   真空光速（精确）
E_CHARGE = CODATA["e"]  # C    元电荷（精确）


def energy_ev(wavelength_nm):
    """光子能量(eV)：E = hc/lambda。"""
    lam = wavelength_nm * 1e-9
    return (H * C / lam) / E_CHARGE


# ---------------- Pauli 矩阵与 Bloch 矢量 ----------------
SX = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SY = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def bloch_vector(rho):
    """由 2x2 密度矩阵求 Bloch 矢量 r = Tr(rho sigma)。"""
    rx = np.real(np.trace(rho @ SX))
    ry = np.real(np.trace(rho @ SY))
    rz = np.real(np.trace(rho @ SZ))
    return np.array([rx, ry, rz], dtype=float)


def von_neumann_entropy(r):
    """由 Bloch 矢量还原密度矩阵并求纠缠熵 S = -Tr(rho log2 rho)。"""
    rho = 0.5 * (np.eye(2, dtype=complex) + (r[0] * SX + r[1] * SY + r[2] * SZ))
    eig = np.linalg.eigvalsh(rho)
    eig = np.clip(eig, 1e-12, 1.0)
    return float(-np.sum(eig * np.log2(eig)))


def draw_bloch(ax, r, title, color):
    """在给定 3D 子图上画单位 Bloch 球并标出矢量 r。"""
    # 球线框
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, rstride=6, cstride=6,
                      color="lightgray", alpha=0.4, linewidth=0.4)
    # 坐标轴
    ax.plot([-1.2, 1.2], [0, 0], [0, 0], color="k", lw=0.6)
    ax.plot([0, 0], [-1.2, 1.2], [0, 0], color="k", lw=0.6)
    ax.plot([0, 0], [0, 0], [-1.2, 1.2], color="k", lw=0.6)
    ax.text(1.32, 0, 0, "H", fontsize=10)
    ax.text(0, 1.32, 0, "V", fontsize=10)
    # Bloch 矢量
    ax.quiver(0, 0, 0, r[0], r[1], r[2],
              color=color, arrow_length_ratio=0.12, linewidth=2)
    ax.scatter([r[0]], [r[1]], [r[2]], color=color, s=40)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_zlim(-1.35, 1.35)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_title(title, fontsize=10)
    S = von_neumann_entropy(r)
    ax.text2D(0.04, 0.94, f"S = {S:.3f} bit", transform=ax.transAxes,
              fontsize=9, color=color)


# ================= 图 1：Bloch 球对照 =================
fig = plt.figure(figsize=(9.0, 4.2))
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ax2 = fig.add_subplot(1, 2, 2, projection="3d")

# 左：双折射后单光子态 |psi(d)> = (|H> + e^{i d}|V>)/sqrt2，取 d=pi/2（右旋圆偏振）
delta = np.pi / 2.0
psi = np.array([1.0, np.exp(1j * delta)]) / np.sqrt(2.0)
rho_sep = np.outer(psi, psi.conj())
r_sep = bloch_vector(rho_sep)
draw_bloch(ax1, r_sep, "After linear birefringence\nsingle photon: PURE separable (|r|=1)",
           "tab:blue")

# 右：Bell 态 |Phi+> = (|HH>+|VV>)/sqrt2 的 A 子系约化态 = I/2 -> 球心
rho_ent = 0.5 * np.eye(2, dtype=complex)
r_ent = bloch_vector(rho_ent)
draw_bloch(ax2, r_ent, "Reduced state of entangled pair\nmaximally MIXED (center)",
           "tab:red")

fig.suptitle("Linear birefringence cannot create entanglement (Bloch-sphere view)",
             fontsize=12)
fig.tight_layout()

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(FIG_DIR, exist_ok=True)
f1 = os.path.join(FIG_DIR, "47_宝石学中的量子误用辨析_图1.svg")
fig.savefig(f1, format="svg", bbox_inches="tight")
plt.close(fig)


# ================= 图 2：红宝石 Cr3+ 能级图 =================
fig2, ax = plt.subplots(figsize=(7.5, 5.0))

# 能级（单位 cm^-1；简化但以文献量级为准 [24kr][24ks][24kt]）
E_4A2 = 0.0
E_2E_R1 = 14402.0    # 约 694.3 nm
E_2E_R2 = 14431.0    # 约 692.9 nm；R1/R2 零场分裂 ~29 cm^-1
E_4T2 = 18000.0      # 4A2->4T2 吸收 (~555 nm)
E_4T1 = 25000.0      # 4A2->4T1 吸收 (~400 nm)


def hline(y, x0, x1, label, color):
    ax.hlines(y, x0, x1, color=color, lw=2)
    ax.text(x0 - 0.45, y, label, ha="right", va="center", fontsize=9)


hline(E_4A2, 0.6, 3.4, "4A2 (ground)", "black")
hline(E_2E_R1, 1.2, 2.0, "2E R1", "crimson")
hline(E_2E_R2, 1.2, 2.0, "2E R2", "crimson")
hline(E_4T2, 0.6, 3.4, "4T2", "steelblue")
hline(E_4T1, 0.6, 3.4, "4T1", "steelblue")

# R 线发射箭头（向下：2E -> 4A2）
ax.annotate("", xy=(2.6, E_4A2), xytext=(2.6, E_2E_R1),
            arrowprops=dict(arrowstyle="->", color="crimson", lw=2))
ax.annotate("", xy=(2.4, E_4A2), xytext=(2.4, E_2E_R2),
            arrowprops=dict(arrowstyle="->", color="crimson", lw=2))
ax.text(3.05, (E_2E_R1 + E_4A2) / 2, "R-line\nemission\n694.3 nm",
        color="crimson", fontsize=8, va="center")

# 蓝绿宽吸收带（向上：4A2 -> 4T2, 4T1），用半透明矩形表示宽带
for Eexc in (E_4T2, E_4T1):
    ax.annotate("", xy=(1.2, Eexc), xytext=(1.2, E_4A2),
                arrowprops=dict(arrowstyle="->", color="darkgreen", lw=2))
    ax.add_patch(plt.Rectangle((1.02, E_4A2), 0.36, Eexc - E_4A2,
                               color="green", alpha=0.15))
ax.text(0.15, (E_4T2 + E_4A2) / 2, "broad absorption\n(blue-green)",
        color="darkgreen", fontsize=8, va="center")

# 2E 零场分裂标注
ax.annotate("", xy=(2.0, E_2E_R1), xytext=(2.0, E_2E_R2),
            arrowprops=dict(arrowstyle="<->", color="gray", lw=1))
ax.text(2.05, (E_2E_R1 + E_2E_R2) / 2, "Δ≈29 cm⁻¹\n(ZFS of 2E)",
        color="gray", fontsize=7, va="center")

ax.set_ylabel("Energy (cm⁻¹)", fontsize=10)
ax.set_xticks([])
ax.set_ylim(-1000, 26500)
ax.set_xlim(-0.7, 3.9)
ax.set_title("Ruby Cr3+ level scheme: sharp R emission vs broad blue-green absorption",
             fontsize=11)
fig2.tight_layout()
f2 = os.path.join(FIG_DIR, "47_宝石学中的量子误用辨析_图2.svg")
fig2.savefig(f2, format="svg", bbox_inches="tight")
plt.close(fig2)


# ---------------- 数值回显（验证计算）----------------
if __name__ == "__main__":
    print("R1 line (694.3 nm):")
    print("  E = %.4f eV" % energy_ev(694.3))
    print("  wavenumber = %.1f cm^-1" % (1e7 / 694.3))
    print("Bloch |r| separable (birefringence) = %.4f  -> pure, S=0" % np.linalg.norm(r_sep))
    print("Bloch |r| entangled reduced        = %.4f  -> mixed, S=1" % np.linalg.norm(r_ent))
    print("Saved:", f1)
    print("Saved:", f2)
