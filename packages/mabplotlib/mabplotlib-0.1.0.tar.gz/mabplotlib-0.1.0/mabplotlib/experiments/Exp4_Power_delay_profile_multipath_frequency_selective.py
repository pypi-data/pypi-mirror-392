import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------
# PARAMETERS
# --------------------------------------------------------
delays = np.array([0, 50, 150, 300, 500])       # delays in ns
powers_dB = np.array([0, -3, -6, -8, -10])      # power levels in dB

# Convert dB to linear scale
powers_linear = 10 ** (powers_dB / 10)

# Normalize powers so that sum = 1 (required for PDP)
powers_norm = powers_linear / np.sum(powers_linear)

num_samples = 100000     # number of fading samples

# --------------------------------------------------------
# GENERATE MULTIPATH CHANNEL TAPS (COMPLEX GAUSSIAN)
# Each tap has Rayleigh amplitude (Gaussian real + imag)
# --------------------------------------------------------
h = np.zeros((len(delays), num_samples), dtype=complex)

for i, P in enumerate(powers_norm):
    real = np.random.normal(0, np.sqrt(P/2), num_samples)
    imag = np.random.normal(0, np.sqrt(P/2), num_samples)
    h[i, :] = real + 1j * imag     # complex Gaussian tap

# --------------------------------------------------------
# COMPUTE POWER DELAY PROFILE (PDP)
# PDP(τ) = E{|h(τ)|^2}
# --------------------------------------------------------
pdp = np.mean(np.abs(h)**2, axis=1)

# Normalize PDP (common practice)
pdp_normalized = pdp / np.max(pdp)

# --------------------------------------------------------
# PLOT PDP
# --------------------------------------------------------
plt.figure(figsize=(8,5))
plt.stem(delays, pdp_normalized, basefmt=" ")
plt.xlabel("Delay (ns)", fontsize=12)
plt.ylabel("Normalized PDP", fontsize=12)
plt.title("Power Delay Profile (PDP) for Frequency Selective Fading Channel", fontsize=14)
plt.grid(True)
plt.show()

# --------------------------------------------------------
# PRINT VALUES
# --------------------------------------------------------
print("Delays (ns):", delays)
print("Powers in dB:", powers_dB)
print("Linear powers:", powers_linear)
print("Normalized powers:", powers_norm)
print("Normalized PDP:", pdp_normalized)
