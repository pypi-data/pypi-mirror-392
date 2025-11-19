import numpy as np
import matplotlib.pyplot as plt

# SNR values in dB
SNR_dB_list = [0, 10, 15, 20, 25]
B = 1e6  # Bandwidth in Hz
P = 1     # Transmit power

# Store results
capacity_results = {
    "1x1": [],
    "2x2": [],
    "4x4": []
}

# Function to compute capacity for given Nt, Nr
def compute_capacity(Nt, Nr, SNR_dB_list, B, P):
    capacities = []
    for SNR_dB in SNR_dB_list:
        SNR_linear = 10 ** (SNR_dB / 10)
        N0 = P / SNR_linear

        # Channel matrix H (complex Gaussian, Rayleigh fading)
        H_real = np.random.randn(Nr, Nt)
        H_imag = np.random.randn(Nr, Nt)
        H = (H_real + 1j * H_imag) / np.sqrt(2)

        # Capacity formula: C = B * log2(det(I + (P/NtN0) * H * Hᴴ))
        HHH = H @ H.conj().T
        I = np.eye(Nr)
        capacity = B * np.log2(np.linalg.det(I + (P / (Nt * N0)) * HHH))
        capacities.append(np.real(capacity))
    return capacities

# Compute for all configurations
capacity_results["1x1"] = compute_capacity(1, 1, SNR_dB_list, B, P)
capacity_results["2x2"] = compute_capacity(2, 2, SNR_dB_list, B, P)
capacity_results["4x4"] = compute_capacity(4, 4, SNR_dB_list, B, P)


# Plotting
plt.figure(figsize=(8, 5))
plt.plot(SNR_dB_list, np.array(capacity_results["1x1"]) / 1e6, 'o-', label='1x1 MIMO')
plt.plot(SNR_dB_list, np.array(capacity_results["2x2"]) / 1e6, 's-', label='2x2 MIMO')
plt.plot(SNR_dB_list, np.array(capacity_results["4x4"]) / 1e6, '^-', label='4x4 MIMO')

plt.title("MIMO Channel Capacity vs SNR")
plt.xlabel("SNR (dB)")
plt.ylabel("Capacity (bits/s/Hz)")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()



# To observe ergodic channel capacity for various antenna configurations