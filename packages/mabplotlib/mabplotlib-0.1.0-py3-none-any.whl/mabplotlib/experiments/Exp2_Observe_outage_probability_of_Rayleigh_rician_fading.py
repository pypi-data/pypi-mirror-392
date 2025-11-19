#  observe outage probability of rayliegh and rician fading channel 
# code without graph 

import numpy as np
from scipy.integrate import quad
from scipy.special import i0
import math

# ---------------------------------------------------------
# RAYLEIGH OUTAGE PROBABILITY
# ---------------------------------------------------------
def outage_rayleigh(gamma_th, gamma_bar):
    # Rayleigh: Pout = 1 - exp(-gamma_th / gamma_bar)
    return 1 - np.exp(-gamma_th / gamma_bar)


# ---------------------------------------------------------
# MARCUM Q1 FOR RICIAN
# ---------------------------------------------------------
def marcum_q1(a, b):
    def integrand(t):
        return t * np.exp(-(t**2 + a**2) / 2) * i0(a * t)
    result, _ = quad(integrand, b, 50, epsabs=1e-8, epsrel=1e-8)
    return result


# ---------------------------------------------------------
# RICIAN OUTAGE PROBABILITY
# ---------------------------------------------------------
def outage_rician(K, gamma_th, gamma_bar):
    Pout = []
    a = np.sqrt(2 * K)

    for gb in gamma_bar:
        b = np.sqrt(2 * (K + 1) * gamma_th / gb)
        Q1 = marcum_q1(a, b)
        Pout.append(1 - Q1)

    return np.array(Pout)


# ---------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------
gamma_th = 0.1                        # threshold SNR
gamma_bar = np.array([1, 2, 5, 10, 15, 20])   # SNR values for printing
K = 5                                 # Rician K-factor


# ---------------------------------------------------------
# COMPUTE OUTAGE VALUES
# ---------------------------------------------------------
rayleigh_values = outage_rayleigh(gamma_th, gamma_bar)
rician_values = outage_rician(K, gamma_th, gamma_bar)


# ---------------------------------------------------------
# PRINT THEORETICAL VALUES
# ---------------------------------------------------------
print("\n=== OUTAGE PROBABILITY RESULTS (THEORETICAL) ===")
print("Gamma_th =", gamma_th)
print("K =", K)
print("--------------------------------------------------")
print(" Avg SNR      Rayleigh P_out        Rician P_out ")
print("--------------------------------------------------")

for i in range(len(gamma_bar)):
    print(f"  {gamma_bar[i]:<10}  {rayleigh_values[i]:<18.6f}  {rician_values[i]:.6f}")

print("--------------------------------------------------")




# code with graph 


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.special import erfc, i0
import math

# ---------------------------------------------------------
# 1) RAYLEIGH OUTAGE PROBABILITY
# ---------------------------------------------------------
def outage_rayleigh(gamma_th, gamma_bar):
    # Rayleigh outage: Pout = 1 - exp(-gamma_th / gamma_bar)
    return 1 - np.exp(-gamma_th / gamma_bar)


# ---------------------------------------------------------
# 2) MARCUM Q1 FUNCTION FOR RICIAN
# ---------------------------------------------------------
def marcum_q1(a, b):
    # Integrand for Marcum Q1
    def integrand(t):
        return t * np.exp(-(t**2 + a**2)/2) * i0(a * t)

    # Numerical integration
    result, _ = quad(integrand, b, 50, epsabs=1e-8, epsrel=1e-8)
    return result


# ---------------------------------------------------------
# 3) RICIAN OUTAGE PROBABILITY
# ---------------------------------------------------------
def outage_rician(K, gamma_th, gamma_bar):
    Pout = []
    a = np.sqrt(2*K)

    for gb in gamma_bar:
        b = np.sqrt(2*(K+1)*gamma_th / gb)
        Q1 = marcum_q1(a, b)
        Pout.append(1 - Q1)

    return np.array(Pout)


# ---------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------
gamma_th = 0.1                             # threshold SNR
gamma_bar = np.linspace(0.1, 20, 200)      # avg SNR range
K = 5                                       # Rician K-factor


# ---------------------------------------------------------
# COMPUTE RAYLEIGH & RICIAN OUTAGE
# ---------------------------------------------------------
Pout_rayleigh = outage_rayleigh(gamma_th, gamma_bar)
Pout_rician = outage_rician(K, gamma_th, gamma_bar)


# ---------------------------------------------------------
# PLOT RESULTS
# ---------------------------------------------------------
plt.figure(figsize=(9,6))
plt.plot(gamma_bar, Pout_rayleigh, 'b', label="Rayleigh Fading", linewidth=2)
plt.plot(gamma_bar, Pout_rician, 'r', label=f"Rician Fading (K={K})", linewidth=2)

plt.xlabel("Average SNR (γ̄)", fontsize=12)
plt.ylabel("Outage Probability", fontsize=12)
plt.title("Outage Probability for Rayleigh and Rician Fading Channels", fontsize=14)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
