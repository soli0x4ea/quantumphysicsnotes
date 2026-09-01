# 量子计算_Grover搜索.py
# 对应篇名：第 34 篇《量子计算与量子算法》
# 公式：Grover 搜索成功概率 P(n) = sin^2((2n+1)*theta)，其中 sin(theta) = 1/sqrt(N)
# 任务：取 N = 1024，数值计算得到随迭代次数 n 的变化曲线，标出最优迭代次数 n* 与峰值概率。
# 运行：使用隔离 venv 的 python（已装 numpy + matplotlib），后端 Agg，输出 SVG 到 figures/。
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(ROOT, 'figures')
os.makedirs(FIGDIR, exist_ok=True)


def main():
    N = 1024                                  # 搜索空间大小（未标记项数）
    theta = np.arcsin(1.0 / np.sqrt(N))       # sin(theta)=1/sqrt(N)，theta 为旋转半角
    n_max = 60
    n = np.arange(0, n_max + 1)
    # 每迭代一次，态在 {|w>, |s_perp>} 子空间内旋转 2*theta；
    # |w> 振幅 = sin((2n+1)*theta)，成功概率为其平方。
    P = np.sin((2 * n + 1) * theta) ** 2

    # 最优迭代次数：使 (2n+1)*theta 最接近 pi/2
    n_opt = int(np.round(np.pi / (4 * theta) - 0.5))
    P_peak = float(P[n_opt])

    print('N =', N)
    print('theta (rad) =', theta)
    print('optimal iterations n* =', n_opt)
    print('peak success probability =', P_peak)
    print('classical query count ~ N/2 =', N // 2)
    print('quantum query count ~ (pi/4)*sqrt(N) =', np.pi / 4 * np.sqrt(N))

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(n, P, '-o', ms=3, color='#1f77b4',
            label=r'$P(n)=\sin^2((2n+1)\theta)$')
    ax.axvline(n_opt, color='#d62728', ls='--',
               label='optimal $n^*=%d$' % n_opt)
    ax.scatter([n_opt], [P_peak], color='#d62728', zorder=5)
    ax.annotate('peak P = %.4f' % P_peak, xy=(n_opt, P_peak),
                xytext=(n_opt + 6, 0.78),
                arrowprops=dict(arrowstyle='->', color='#d62728'))
    ax.set_xlabel('Iteration count n')
    ax.set_ylabel('Success probability P(n)')
    ax.set_title('Grover search success probability (N=1024)')
    ax.set_ylim(-0.02, 1.06)
    ax.set_xlim(0, n_max)
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    out = os.path.join(FIGDIR, '量子计算_Grover成功概率.svg')
    fig.savefig(out, format='svg')
    print('saved', out)


if __name__ == '__main__':
    main()
