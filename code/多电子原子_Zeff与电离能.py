# 多电子原子_Zeff与电离能.py
# 对应笔记：第22篇《多电子原子与元素周期表》
# 段1：Slater 屏蔽规则计算有效核电荷 Z_eff（Na/K/F 等）
# 段2：前 20 号元素第一电离能周期性（NIST 实验值），展示壳层峰谷
# 运行：~/.workbuddy/binaries/python/envs/default/bin/python 多电子原子_Zeff与电离能.py
# 依赖：numpy, matplotlib （无 scipy）

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# Section 1: Slater shielding -> effective nuclear charge
# =========================================================
# config: list of (group_label, n_of_group, count) in Slater order
# group label encodes n via its leading integer; "2s2p" means n=2 combined group
# target index = which group holds the electron of interest

elements = [
    # symbol, Z, [(group, count), ...], target_group_index
    ("H",  1,  [("1s", 1)], 0),
    ("He", 2,  [("1s", 2)], 0),
    ("Li", 3,  [("1s", 2), ("2s2p", 1)], 1),
    ("Be", 4,  [("1s", 2), ("2s2p", 2)], 1),
    ("B",  5,  [("1s", 2), ("2s2p", 3)], 1),
    ("C",  6,  [("1s", 2), ("2s2p", 4)], 1),
    ("N",  7,  [("1s", 2), ("2s2p", 5)], 1),
    ("O",  8,  [("1s", 2), ("2s2p", 6)], 1),
    ("F",  9,  [("1s", 2), ("2s2p", 7)], 1),
    ("Ne", 10, [("1s", 2), ("2s2p", 8)], 1),
    ("Na", 11, [("1s", 2), ("2s2p", 8), ("3s3p", 1)], 2),
    ("Mg", 12, [("1s", 2), ("2s2p", 8), ("3s3p", 2)], 2),
    ("Al", 13, [("1s", 2), ("2s2p", 8), ("3s3p", 3)], 2),
    ("Si", 14, [("1s", 2), ("2s2p", 8), ("3s3p", 4)], 2),
    ("P",  15, [("1s", 2), ("2s2p", 8), ("3s3p", 5)], 2),
    ("S",  16, [("1s", 2), ("2s2p", 8), ("3s3p", 6)], 2),
    ("Cl", 17, [("1s", 2), ("2s2p", 8), ("3s3p", 7)], 2),
    ("Ar", 18, [("1s", 2), ("2s2p", 8), ("3s3p", 8)], 2),
    ("K",  19, [("1s", 2), ("2s2p", 8), ("3s3p", 8), ("4s4p", 1)], 3),
]

def slater_Zeff(Z, config, target):
    n_target = int(config[target][0][0])   # leading digit of group label
    sigma = 0.0
    for i, (grp, cnt) in enumerate(config):
        n_grp = int(grp[0])
        if i == target:
            others = cnt - 1
            if n_grp == 1:
                sigma += others * 0.30
            else:
                sigma += others * 0.35
        elif n_grp == n_target - 1:
            sigma += cnt * 0.85
        elif n_grp <= n_target - 2:
            sigma += cnt * 1.00
        # groups to the right (higher n) contribute 0 by Slater rule
    return Z - sigma

print("== Slater Z_eff (valence electron) ==")
Zeff_list = []
for sym, Z, cfg, tgt in elements:
    zeff = slater_Zeff(Z, cfg, tgt)
    Zeff_list.append(zeff)
    print(f"{sym:3s} Z={Z:2d}  Z_eff={zeff:.2f}")

# =========================================================
# Section 2: first ionization energy periodicity (NIST, eV)
# =========================================================
Z_seq = np.arange(1, 21)
I1 = np.array([13.598, 24.587, 5.392, 9.323, 8.298, 11.260, 14.534, 13.618,
               17.423, 21.565, 5.139, 7.646, 5.986, 8.152, 10.487, 10.360,
               12.968, 15.760, 4.341, 6.113])  # eV, NIST ASD

print("\n== First ionization energy (eV, NIST) ==")
print(f"peaks (noble gases): He={I1[1]:.2f} Ne={I1[9]:.2f} Ar={I1[17]:.2f}")
print(f"valleys (alkali):    Li={I1[2]:.2f} Na={I1[10]:.2f} K={I1[18]:.2f}")

# ---- Figure 1: Z_eff trend ----
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(Z_seq[:len(Zeff_list)], Zeff_list, "o-", color="#1f4e79", lw=1.8)
ax.set_xlabel("Atomic number Z")
ax.set_ylabel("Effective nuclear charge Z_eff")
ax.set_title("Slater Z_eff of valence electron")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/多电子原子_Zeff趋势.svg", dpi=140)
print("saved figures/多电子原子_Zeff趋势.svg")

# ---- Figure 2: ionization energy periodicity ----
fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(Z_seq, I1, "s-", color="#0b6e4f", lw=1.6, label="I1(Z)")
nobles = [1, 9, 17]
alkalis = [2, 10, 18]
ax.plot(Z_seq[nobles], I1[nobles], "r^", ms=9, label="noble gas (peak)")
ax.plot(Z_seq[alkalis], I1[alkalis], "kv", ms=9, label="alkali (valley)")
ax.set_xlabel("Atomic number Z")
ax.set_ylabel("First ionization energy (eV)")
ax.set_title("Periodicity of first ionization energy")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("../figures/多电子原子_电离能周期.svg", dpi=140)
print("saved figures/多电子原子_电离能周期.svg")
