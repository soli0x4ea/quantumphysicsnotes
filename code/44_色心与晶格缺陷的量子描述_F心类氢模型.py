# -*- coding: utf-8 -*-
# 44_色心与晶格缺陷的量子描述_F心类氢模型.py
# 配套：第 44 篇《色心与晶格缺陷的量子描述》第六节省型模型 (b)
# 模型：F 心（卤化物阴离子空位俘获一个电子）的类氢有效质量近似
# 有效玻尔半径 a* = eps_inf * a_0；有效里德伯 R* = R_H / eps_inf^2
# 1s -> 2p 跃迁能量 ΔE = (3/4) R*，对应 F 吸收带
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 本文件
# 依赖：numpy, matplotlib（禁用 scipy）；matplotlib 后端 Agg
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

# ---- CODATA 2018 常数 ----
a0 = 5.29177210903e-11       # 玻尔半径 [m]
R_H_eV = 13.605693009        # 氢原子里德伯能量 [eV]（R_inf * hc，CODATA 2018）
HC_eV_nm = 1239.841984       # hc（用于 eV -> nm 换算）[eV·nm]

# ---- 各卤化物：光学介电常数 eps_inf ≈ n_opt^2 与实验 F 带（峰值）能量 ----
# eps_inf 取高频（光学）介电常数；实验 F 带为文献汇编值（Fowler 1968 [24jm]; Klick & Schulman 1957 [24jq]）
# 注意：本类氢模型仅为零阶估计，仅对大晶格量级的 KCl 等接近实验，小晶格（LiF、NaCl）偏差显著，
#       正文据此引出点离子模型与 Mollwo-Ivey 经验律 E_F ∝ a^{-1.84}。
salts = [
    # 名称,  eps_inf,   E_F_exp [eV], lattice const a [Angstrom]（标准晶体学数据，仅用于标注）
    ("LiF",  1.93, 5.08, 4.03),
    ("NaF",  1.74, 3.70, 4.63),
    ("NaCl", 2.38, 2.75, 5.64),
    ("KCl",  2.22, 2.30, 6.29),
    ("KBr",  2.43, 2.06, 6.60),
    ("KI",   2.65, 1.87, 7.07),
]


def hydrogenic_F(eps_inf):
    """类氢有效质量近似（取 m* = m_e）：
    返回有效玻尔半径 a* [m]、有效里德伯 R* [eV]、1s->2p 跃迁能量 ΔE [eV] 与波长 [nm]"""
    a_star = eps_inf * a0
    R_star = R_H_eV / (eps_inf ** 2)     # 因 m*≈m_e，无质量修正项
    dE = 0.75 * R_star                    # 1s(1) -> 2p(1/4) 差 = (1 - 1/4) R*
    lam = HC_eV_nm / dE
    return a_star, R_star, dE, lam


rows = []
for name, eps, Eexp, a in salts:
    a_star, R_star, dE, lam = hydrogenic_F(eps)
    rows.append((name, eps, a, Eexp, HC_eV_nm / Eexp, a_star, R_star, dE, lam))

# 打印对照表
print("%-5s %6s %7s %8s %8s %10s %9s %8s %9s" %
      ("salt", "eps_inf", "a[A]", "E_exp", "lam_exp", "a*[m]", "R*[eV]", "dE[eV]", "lam[nm]"))
for name, eps, a, Eexp, lam_exp, a_star, R_star, dE, lam in rows:
    print("%-5s %6.2f %7.2f %8.2f %8.0f %10.2e %9.2f %8.2f %9.0f" %
          (name, eps, a, Eexp, lam_exp, a_star, R_star, dE, lam))

# 与实验的比值（说明模型偏差）
print("\n模型波长 / 实验波长（>1 表示模型低估能量、波长偏长）：")
for name, eps, a, Eexp, lam_exp, a_star, R_star, dE, lam in rows:
    print("  %-5s : %.2f" % (name, lam / lam_exp))

# ---- 图 1：KCl 的 1s / 2p 能级示意图 ----
kcl = [r for r in rows if r[0] == "KCl"][0]
name, eps, a, Eexp, lam_exp, a_star, R_star, dE, lam = kcl
fig1, ax1 = plt.subplots(figsize=(4.2, 5.2))
levels = [("2p (T_1u)", 0.0), ("1s (A_1g)", -R_star)]
for lbl, E in levels:
    ax1.hlines(E, 0.3, 1.7, color="#1f4e79", lw=2.0)
    ax1.text(1.8, E, lbl, fontsize=10, va="center")
ax1.annotate("", xy=(1.0, 0.0), xytext=(1.0, -R_star),
             arrowprops=dict(arrowstyle="<->", color="#b00020", lw=1.4))
ax1.text(2.0, -R_star / 2.0, "$\\Delta E=%.2f$ eV\n($\\lambda\\approx%d$ nm)\nmodel vs\nexp $\\approx%d$ nm"
         % (dE, round(lam), round(lam_exp)), fontsize=9, color="#b00020", va="center")
ax1.set_xlim(0, 3.2)
ax1.set_ylim(-R_star * 1.12, 0.4)
ax1.set_ylabel("Energy (eV)")
ax1.set_xticks([])
ax1.set_title("F-center hydrogenic levels (KCl)\n$a^*=%.2f\\,a_0$,  $R^*=%.2f$ eV" % (eps, R_star))
fig1.tight_layout()
out1 = "figures/44_色心与晶格缺陷的量子描述_F心能级.svg"
fig1.savefig(out1, format="svg", dpi=150)
print("\n已写出:", out1)

# ---- 图 2：各盐模型波长 vs 实验 F 带波长（柱状对比）----
names = [r[0] for r in rows]
lam_model = [r[8] for r in rows]
lam_exp = [r[4] for r in rows]
x = np.arange(len(names))
width = 0.38
fig2, ax2 = plt.subplots(figsize=(8.4, 4.8))
ax2.bar(x - width / 2, lam_model, width, label="Hydrogenic model $\\lambda$", color="#1f4e79")
ax2.bar(x + width / 2, lam_exp, width, label="Experimental F-band $\\lambda$", color="#b00020")
ax2.set_xticks(x)
ax2.set_xticklabels(names)
ax2.set_ylabel("F-band wavelength (nm)")
ax2.set_title("F-center 1s->2p transition: hydrogenic-model vs experimental F-band")
ax2.legend()
for i, (lm, le) in enumerate(zip(lam_model, lam_exp)):
    ax2.text(i - width / 2, lm + 5, "%d" % round(lm), ha="center", fontsize=8)
    ax2.text(i + width / 2, le + 5, "%d" % round(le), ha="center", fontsize=8)
ax2.set_ylim(0, max(lam_model + lam_exp) * 1.15)
fig2.tight_layout()
out2 = "figures/44_色心与晶格缺陷的量子描述_F心波长对比.svg"
fig2.savefig(out2, format="svg", dpi=150)
print("已写出:", out2)
