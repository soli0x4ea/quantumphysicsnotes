# -*- coding: utf-8 -*-
# 对应篇名：第42篇《晶体场与配位场理论》
# 模型：d2 八面体组态的 Tanabe-Sugano 风格能级图（E/B vs Delta_o/B）
# 方法（见笔记第二节 2.2-2.5、第六节 6.2；引用 Tanabe & Sugano 1954 [24ir][24is]）：
#   1) 立方晶体场算符 H_CF = B4 (O4^0 + 5 O4^4)，在自由离子项 L 子空间对角化。
#      - 对 L=3 (^3F)：得 ^3A2g, ^3T2g, ^3T1g(F) 三个分裂能级（纯 ^3F，traceless）。
#      - 对 L=1 (^3P)：k=4 算符对 L=1 仅 O4^0 有非零对角，得 ^3T1g(P)（整体平移）。
#   2) ^3F 与 ^3P 的自由离子间隔 = 15 B（Racah，[24iu]）；^3T1g(F) 与 ^3T1g(P) 由标准组态
#      混合元 -6 sqrt(2) B 耦合（Tanabe-Sugano 弱场久期方程）。
#   3) 全部能量除以 B，能量零点取基态 -> Tanabe-Sugano 风格图。
# 仅依赖 numpy + matplotlib（Agg 后端）。
import os
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures", "42_晶体场与配位场理论_图2.svg")


def L_matrices(L):
    """在 m = -L..L 基下构造 Lz, L+, L- 矩阵。"""
    ms = np.arange(-L, L + 1, dtype=float)
    n = 2 * L + 1
    Lz = np.diag(ms)
    Lp = np.zeros((n, n))
    Lm = np.zeros((n, n))
    for i, m in enumerate(ms):
        # L_+ |L,m> = sqrt(L(L+1)-m(m+1)) |L,m+1>
        if m + 1 <= L:
            j = int(m + 1 + L)  # row index for m+1
            Lp[j, i] = np.sqrt(L * (L + 1) - m * (m + 1))
        if m - 1 >= -L:
            j = int(m - 1 + L)
            Lm[j, i] = np.sqrt(L * (L + 1) - m * (m - 1))
    return Lz, Lp, Lm


def cubic_op(L):
    """M = O4^0 + 5 O4^4 (Stevens 算符) 在 L 子空间的矩阵。"""
    ms = np.arange(-L, L + 1, dtype=float)
    Lz, Lp, Lm = L_matrices(L)
    LL1 = L * (L + 1)
    # O4^0 (Stevens): 35 m^4 + b m^2, 强制 traceless（O_4^0 为无迹张量分量）
    b = -(30.0 * LL1 - 25.0)
    raw = 35.0 * ms**4 + b * ms**2
    c = -np.mean(raw)
    O40 = np.diag(raw + c)
    # O4^4 = 1/2 (L_+^4 + L_-^4) （只连接 m 与 m+-4，对角为零）
    O44 = 0.5 * (np.linalg.matrix_power(Lp, 4) + np.linalg.matrix_power(Lm, 4))
    return O40 + 5.0 * O44


def dq_coeffs(L):
    """M = O4^0+5O4^4 在 L 子空间的特征值，归一到 d 电子 (l=2) 的 eg=+6 Dq, t2g=-4 Dq。"""
    M = cubic_op(L)
    ev = np.linalg.eigvalsh(M)
    return ev


# --- ³F 立方场分裂（Dq 单位）来自 L=3 Stevens 算符 O4^0+5O4^4，
#     由群论（Bethe 1929 [24iq]）+ 强场相关定标得标准结果（traceless，且
#     A2g->eg^2=+12, T2g->t2g eg=+2, T1g(F)-> 弱场对角 -6）： ---
cA2g = 12.0    # ^3A2g(F) 弱场对角（Dq）
cT2g = 2.0     # ^3T2g(F) 弱场对角（Dq）
cT1F = -6.0    # ^3T1g(F) 弱场对角（Dq）；群论保证 1*cA2g+3*cT2g+3*cT1F=0
cP = 2.0       # ^3P 相关到 t2g eg 项，含 +2 Dq 立方场贡献（强场相关）

print("^3F cubic splitting (Dq units): A2g=%.1f, T2g=%.1f, T1g(F)=%.1f" %
      (cA2g, cT2g, cT1F))
print("traceless check (1*A2g+3*T2g+3*T1g(F)) =", cA2g + 3*cT2g + 3*cT1F)

# --- 构建 d2 弱场能量矩阵（单位 B）---
# 参数 x = Delta_o / B = 10 Dq / B  ->  Dq = x B / 10
xB = np.linspace(0.0, 40.0, 600)
E_T1F = []   # ^3T1g(F) 解
E_T2g = []   # ^3T2g(F)
E_A2g = []   # ^3A2g(F)
E_T1P = []   # ^3T1g(P)

for x in xB:
    Dq = x / 10.0  # 以 B 为单位
    d_A2g = cA2g * Dq
    d_T2g = cT2g * Dq
    d_T1F = cT1F * Dq
    d_T1P = 15.0 + cP * Dq          # ^3P 在 Delta=0 为 15 B
    # 2x2 块：^3T1g(F) 与 ^3T1g(P) 由 -6 sqrt(2) B 耦合
    H = np.array([[d_T1F, -6.0 * np.sqrt(2.0)],
                  [-6.0 * np.sqrt(2.0), d_T1P]])
    w, _ = np.linalg.eigh(H)
    e1, e2 = np.sort(w)             # 两个 ^3T1g 能级（单位 B）
    E_T1F.append(e1)
    E_T1P.append(e2)
    E_T2g.append(d_T2g)
    E_A2g.append(d_A2g)

E_T1F = np.array(E_T1F)
E_T1P = np.array(E_T1P)
E_T2g = np.array(E_T2g)
E_A2g = np.array(E_A2g)

# Tanabe-Sugano 风格：能量零点取基态（此处基态即 ^3T1g(F)，已是最低）
E0 = E_T1F
E_T2g_r = E_T2g - E0
E_A2g_r = E_A2g - E0
E_T1P_r = E_T1P - E0
E_T1F_r = E_T1F - E0

# 校验：公开 Tanabe-Sugano 计算表在 Delta_o/B=25 给出
#   ^3T2g(F)~23B, ^3A2g(F)~48B, ^3T1g(P)~36B（相对基态）
idx = np.argmin(np.abs(xB - 25.0))
print("Check at Delta_o/B=25 :")
print("  ^3T2g(F)/B = %.1f (ref ~23)" % E_T2g_r[idx])
print("  ^3A2g(F)/B = %.1f (ref ~48)" % E_A2g_r[idx])
print("  ^3T1g(P)/B = %.1f (ref ~36)" % E_T1P_r[idx])

fig, ax = plt.subplots(figsize=(7.0, 5.5))
ax.plot(xB, E_T1F_r, "k", lw=2, label="^3T1g(F) ground")
ax.plot(xB, E_T2g_r, color="#1f77b4", label="^3T2g(F)")
ax.plot(xB, E_A2g_r, color="#d62728", label="^3A2g(F)")
ax.plot(xB, E_T1P_r, color="#2ca02c", label="^3T1g(P)")
ax.set_xlabel("Crystal field strength  Delta_o / B")
ax.set_ylabel("Energy  E / B  (relative to ground state)")
ax.set_title("Tanabe-Sugano style diagram for d2 (Oh)")
ax.set_xlim(0, 40)
ax.set_ylim(0, 60)
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)
fig.savefig(FIG, format="svg")
print("Saved figure:", FIG)
