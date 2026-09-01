# -*- coding: utf-8 -*-
"""Operator representations: Fourier duality of a Gaussian wave packet.

Demonstrates that the same quantum state has components in the position
representation psi(x)=<x|psi> and the momentum representation phi(p)=<p|psi>,
related by a unitary (Fourier) transform, and verifies the uncertainty-product
lower bound Delta x Delta p = hbar/2 for the minimum-uncertainty Gaussian.

Outputs: figures/operator_representations_gaussian_fourier_duality.svg
All labels in English to avoid CJK font issues in matplotlib.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def trapz(y, x):
    """Uniform-grid trapezoidal integral (numpy 2.x dropped np.trapz)."""
    dx = x[1] - x[0]
    return np.sum(y) * dx

# Use natural units hbar = 1 for a clean numerical check of Delta x Delta p = hbar/2
HBAR = 1.0

# Position grid
N = 4096
L = 40.0
x = np.linspace(-L/2, L/2, N)
dx = x[1] - x[0]

# Gaussian wave packet in position representation, width parameter sigma_x
sigma_x = 2.0
psi = (1.0 / (np.pi * sigma_x**2)**0.25) * np.exp(-x**2 / (2.0 * sigma_x**2))
psi = psi / np.sqrt(trapz(np.abs(psi)**2, x))  # normalize

# Momentum grid via FFT (centered)
p = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
p = np.fft.fftshift(p)
# FFT of psi with the convention phi(p) = (1/sqrt(2pi hbar)) int dx e^{-i p x/hbar} psi(x)
phi = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(psi))) * dx / np.sqrt(2.0 * np.pi * HBAR)
phi = phi / np.sqrt(trapz(np.abs(phi)**2, p))  # normalize

# Variances (density normalization assumed)
mean_x = trapz(x * np.abs(psi)**2, x)
var_x = trapz((x - mean_x)**2 * np.abs(psi)**2, x)
mean_p = trapz(p * np.abs(phi)**2, p)
var_p = trapz((p - mean_p)**2 * np.abs(phi)**2, p)
dx_std = np.sqrt(var_x)
dp_std = np.sqrt(var_p)
product = dx_std * dp_std

print(f"sigma_x (param)   = {sigma_x:.4f}")
print(f"Delta x           = {dx_std:.4f}  (expect sigma_x/sqrt(2) = {sigma_x/np.sqrt(2):.4f})")
print(f"Delta p           = {dp_std:.4f}  (expect hbar/(sqrt(2) sigma_x) = {HBAR/(np.sqrt(2)*sigma_x):.4f})")
print(f"Delta x Delta p   = {product:.4f}  (lower bound hbar/2 = {HBAR/2:.4f})")
print(f"ratio to bound    = {product/(HBAR/2):.4f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
ax = axes[0]
ax.plot(x, np.abs(psi)**2, color="#1f77b4", lw=2, label=r'$|\psi(x)|^2$')
ax.axvline(mean_x, color="#888888", ls="--", lw=1)
ax.set_xlabel("position  x")
ax.set_ylabel("probability density")
ax.set_title(f"Position representation  (Delta x = {dx_std:.3f})")
ax.set_xlim(-12, 12)
ax.legend(frameon=False)

ax = axes[1]
ax.plot(p, np.abs(phi)**2, color="#d62728", lw=2, label=r'$|\phi(p)|^2$')
ax.axvline(mean_p, color="#888888", ls="--", lw=1)
ax.set_xlabel("momentum  p")
ax.set_ylabel("probability density")
ax.set_title(f"Momentum representation  (Delta p = {dp_std:.3f})")
ax.set_xlim(-3, 3)
ax.legend(frameon=False)

fig.suptitle(f"Fourier duality of one state:  Delta x Delta p = {product:.3f} (bound hbar/2 = {HBAR/2:.3f})")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("figures/算符表象_高斯波包傅里叶对偶.svg", format="svg")
print("saved figures/算符表象_高斯波包傅里叶对偶.svg")
