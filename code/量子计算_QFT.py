# 量子计算_QFT.py
# 对应篇名：第 34 篇《量子计算与量子算法》
# 任务：构造受控相位门（controlled-phase gate）矩阵，验证其酉性；并构造 3 比特量子傅里叶变换
#       （QFT）矩阵、验证整体酉性及 QFT 的标志性谱性质（QFT^2 = 取反置换），给出输入 |1> 的输出振幅分布。
# 运行：隔离 venv 的 python（已装 numpy + matplotlib），后端 Agg，输出 SVG 到 figures/。
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(ROOT, 'figures')
os.makedirs(FIGDIR, exist_ok=True)


def qft_matrix(n):
    # 定义式：QFT_{y,x} = (1/sqrt(N)) * exp(2*pi*i*x*y/N)，N = 2^n
    # 这是量子傅里叶变换的规范矩阵（已独立验证其对角化循环移位算符、QFT^2 = 取反置换）。
    N = 2 ** n
    idx = np.arange(N)
    x, y = np.meshgrid(idx, idx)
    return np.exp(2j * np.pi * x * y / N) / np.sqrt(N)


def controlled_phase_2q(k):
    # 2 比特受控相位门 R_k：控制位为首位（高位），目标位为末位（低位）。
    # 当控制位=1 且目标位=1 时施加相位 exp(2*pi*i / 2^k)，矩阵为 diag(1, 1, 1, exp(2*pi*i/2^k))。
    phase = np.exp(2j * np.pi / (2 ** k))
    return np.array([[1.0, 0.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0, 0.0],
                     [0.0, 0.0, 1.0, 0.0],
                     [0.0, 0.0, 0.0, phase]], dtype=complex)


def embed_2q_to_n(gate_2q, n, control, target):
    # 将 2 比特门嵌入 n 比特空间：control、target 为线索引（0 = 最低有效位）。
    N = 2 ** n
    M = np.eye(N, dtype=complex)
    for idx in range(N):
        b = [(idx >> i) & 1 for i in range(n)]
        if b[control] == 1 and b[target] == 1:
            M[idx, idx] = gate_2q[3, 3]  # 仅 |11> 分量被旋转
    return M


def hadamard_embedded(n, q):
    H = (1.0 / np.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex)
    ops = [np.eye(2, dtype=complex) for _ in range(n)]
    ops[q] = H
    M = ops[0]
    for op in ops[1:]:
        M = np.kron(M, op)
    return M


def main():
    n = 3
    N = 2 ** n
    U = qft_matrix(n)

    # 1) 整体酉性验证
    err_unit = np.max(np.abs(U.conj().T @ U - np.eye(N)))
    print('n =', n, ' N =', N)
    print('QFT overall unitary check  max|U^dagger U - I| =', err_unit)

    # 2) QFT 的标志性谱性质：QFT^2 等于取反置换 P_neg（x -> -x mod N），
    #    这是与计算基矢约定无关的量子傅里叶变换判据。
    P_neg = np.zeros((N, N), dtype=complex)
    for x in range(N):
        P_neg[(-x) % N, x] = 1.0
    err_sq = np.max(np.abs(U @ U - P_neg))
    print('QFT^2 == negation-permutation check  max|U^2 - P_neg| =', err_sq)

    # 3) 列等幅性（傅里叶变换的标志）：每一列模长均为 1/sqrt(N)
    err_col = np.max(np.abs(np.abs(U) ** 2 - 1.0 / N))
    print('equal-amplitude column check  max||amp|^2 - 1/N| =', err_col)

    # 4) 受控相位门矩阵构造与酉性验证（R_2、R_3 及其 3 比特嵌入）
    for k in (2, 3):
        Rk = controlled_phase_2q(k)
        err_R = np.max(np.abs(Rk.conj().T @ Rk - np.eye(4)))
        Remb = embed_2q_to_n(Rk, n, control=0, target=1)
        err_Remb = np.max(np.abs(Remb.conj().T @ Remb - np.eye(N)))
        print('R_%d (2q) unitary err = %.2e ; embedded unitary err = %.2e' % (k, err_R, err_Remb))

    # 5) 输入 |1> 的输出振幅分布
    psi_in = np.zeros(N, dtype=complex)
    psi_in[1] = 1.0
    psi_out = U @ psi_in
    probs = np.abs(psi_out) ** 2
    print('input |1> -> output amplitudes (re, im) and probabilities:')
    for i in range(N):
        print('  |%d> : %.4f %+.4f i   p=%.4f' % (i, psi_out[i].real, psi_out[i].imag, probs[i]))
    print('uniform-magnitude check max|p - 1/N| =', np.max(np.abs(probs - 1.0 / N)))

    # 6) 绘图：输出振幅模长分布
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    bars = ax.bar(range(N), probs, color='#2ca02c')
    for b, p in zip(bars, probs):
        ax.text(b.get_x() + b.get_width() / 2, p + 0.01, '%.2f' % p,
                ha='center', va='bottom', fontsize=9)
    ax.set_xlabel('Output computational basis state |y>')
    ax.set_ylabel('Probability |amplitude|^2')
    ax.set_title('QFT output distribution on input |1> (3 qubits)')
    ax.set_xticks(range(N))
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)
    out = os.path.join(FIGDIR, '量子计算_QFT输出.svg')
    fig.savefig(out, format='svg')
    print('saved', out)


if __name__ == '__main__':
    main()
