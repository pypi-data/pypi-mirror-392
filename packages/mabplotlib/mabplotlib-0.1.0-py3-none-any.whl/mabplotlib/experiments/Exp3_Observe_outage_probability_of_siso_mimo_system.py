#  observe outage probability of siso mimo system  

# code wiht no graph 

import numpy as np
import math
from math import factorial

print("\n================ SISO OUTAGE PROBABILITY ================\n")

# ------------------------
# SISO PARAMETERS
# ------------------------
samples = 100000
yth = 10**(0.5)          # Threshold SNR
yavg = 10**(1.5)         # Average SNR (linear)

# ------------------------
# SISO theoretical
# ------------------------
Pout_siso_theory = 1 - math.exp(-yth / yavg)
print(f"Theoretical SISO Outage Probability   = {Pout_siso_theory:.6f}")

# ------------------------
# SISO simulation
# ------------------------
h = (np.random.randn(samples) + 1j*np.random.randn(samples))
gain = np.abs(h)**2
instant_snr = yavg * gain / 2
Pout_siso_sim = np.mean(instant_snr < yth)

print(f"Simulated SISO Outage Probability     = {Pout_siso_sim:.6f}")


print("\n================ MIMO (2x2) OUTAGE PROBABILITY ================\n")

# ------------------------
# MIMO PARAMETERS
# ------------------------
num_tx = 2
num_rx = 2
L = num_tx * num_rx          # Diversity branches

avg_snr_lin = 10**(1.5)
yth_mimo = 10**(0.5)
samples_mimo = 100000

# ------------------------
# THEORETICAL MIMO OUTAGE using Gamma CDF
# ------------------------
ratio = yth_mimo / avg_snr_lin
sum_term = 0

for k in range(L):
    sum_term += (ratio**k) / factorial(k)

Pout_mimo_theory = 1 - np.exp(-ratio) * sum_term

print(f"Theoretical MIMO (2x2) Outage Probability = {Pout_mimo_theory:.6f}")

# ------------------------
# MIMO SIMULATION
# ------------------------
instantaneous_snr_mimo = np.zeros(samples_mimo)

for i in range(samples_mimo):
    h_real = np.random.randn(num_tx, num_rx)
    h_imag = np.random.randn(num_tx, num_rx)
    h = h_real + 1j*h_imag

    total_gain = np.sum(np.abs(h)**2)
    snr_per_branch = avg_snr_lin / L
    instantaneous_snr_mimo[i] = snr_per_branch * total_gain / 2

Pout_mimo_sim = np.mean(instantaneous_snr_mimo < yth_mimo)

print(f"Simulated MIMO (2x2) Outage Probability = {Pout_mimo_sim:.6f}")



# code with graph 

