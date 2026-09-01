"""
量子密钥分发 (QKD) - BB84 渐近密钥率 vs 误码率 (QBER)
=========================================================
计算并绘制 BB84 在"单向后处理"下的渐近安全密钥率

    R(Q) = 1 - 2 * h(Q)        (bit / pulse, 渐近极限)

其中 h(p) 为二元香农熵 (以 2 为底), Q 为量子比特误码率 QBER。
安全当且仅当 R > 0, 即 Q < 11.0% (单向, h(0.11) ~ 0.5)。

说明:
- 本图只画单向 (one-way) 后处理情形, 对应 Shor-Preskill 2000 的 BB84 安全率。
- 双向后处理 (优势蒸馏 + 双向保密放大) 阈值可升至约 12.6%, 但对应不同的
  速率公式, 不在本曲线内; 详见正文 2.5 与 5.4 节。
- 图内文字全部使用英文, 以规避 matplotlib 缺中文字体导致的豆腐块。

运行:
    python code/量子密钥分发_BB84密钥率.py
输出:
    figures/量子密钥分发_密钥率vs误码率.svg
"""

import numpy as np

import matplotlib
matplotlib.use("Agg")  # 无显示环境
import matplotlib.pyplot as plt


def binary_entropy(p):
    """二元香农熵 h(p) = -p log2 p - (1-p) log2(1-p), 以 2 为底。"""
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    mask = (p > 0.0) & (p < 1.0)
    out[mask] = -p[mask] * np.log2(p[mask]) - (1 - p[mask]) * np.log2(1 - p[mask])
    return out


def main():
    Q = np.linspace(0.0, 0.25, 600)          # QBER 取值 0% ~ 25%
    R = 1.0 - 2.0 * binary_entropy(Q)        # 单向渐近密钥率

    Q_oneway = 0.11                          # 单向安全阈值
    R_oneway = 1.0 - 2.0 * binary_entropy(Q_oneway)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    # 安全区填充 (Q <= 11%)
    ax.fill_between(Q * 100.0, np.clip(R, 0, None), 0,
                    where=(Q <= Q_oneway), color="#1f4e79", alpha=0.12,
                    label="secure region (R > 0)")

    # 密钥率曲线
    ax.plot(Q * 100.0, R, color="#1f4e79", lw=2.4,
            label="R(Q) = 1 - 2 h(Q)  (one-way)")

    # 阈值线
    ax.axvline(Q_oneway * 100.0, color="#b00020", lw=1.5, ls="--")
    ax.axhline(0.0, color="gray", lw=0.8, ls=":")

    ax.annotate(f"one-way threshold Q = 11%\nR(11%) = {R_oneway:.3f}",
                xy=(Q_oneway * 100.0, R_oneway),
                xytext=(13.5, 0.30), fontsize=9, color="#b00020",
                arrowprops=dict(arrowstyle="->", color="#b00020"))

    ax.set_xlim(0, 25)
    ax.set_ylim(-0.25, 1.05)
    ax.set_xlabel("QBER  Q  (%)")
    ax.set_ylabel("Asymptotic secret key rate  R  (bit / pulse)")
    ax.set_title("BB84 asymptotic key rate vs quantum bit error rate")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    out_path = "figures/量子密钥分发_密钥率vs误码率.svg"
    fig.savefig(out_path, format="svg")
    print(f"[ok] saved {out_path}")
    print(f"[check] Q={Q_oneway*100:.1f}% -> R={R_oneway:.4f}  (should be ~0)")
    print(f"[check] h(0.11)={binary_entropy(0.11):.5f}  (should be ~0.5)")
    print(f"[check] R(0%)={1-2*binary_entropy(0.0):.3f}  R(0.5%)={1-2*binary_entropy(0.005):.3f}")


if __name__ == "__main__":
    main()
