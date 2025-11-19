# ================================
# MIMO BER Simulation (ZF vs MMSE)
# ================================

import numpy as np
import matplotlib.pyplot as plt

# ---------- Parameters ----------
num_bits = 100000          # total bits
Nt = 2                     # number of transmit antennas
Nr = 2                     # number of receive antennas
SNR_dB = np.arange(0, 26, 2)  # SNR from 0 to 25 dB

ber_zf = []
ber_mmse = []

# ---------- BPSK Modulation: 0->-1, 1->+1 ----------
def bpsk_mod(bits):
    return 2*bits - 1

def bpsk_demod(symbols):
    return (symbols.real > 0).astype(int)

# ---------- Simulation ----------
for snr in SNR_dB:

    errors_zf = 0
    errors_mmse = 0
    noise_variance = 10**(-snr/10)

    # Generate random bits
    bits = np.random.randint(0, 2, (num_bits, Nt))
    x = bpsk_mod(bits)

    for i in range(0, num_bits, Nt):

        # Select 1 symbol per antenna (MIMO 2x2)
        x_symbol = x[i]

        # MIMO Channel (Rayleigh fading)
        H = (np.random.randn(Nr, Nt) + 1j*np.random.randn(Nr, Nt)) / np.sqrt(2)

        # Noise
        noise = np.sqrt(noise_variance/2) * (np.random.randn(Nr) + 1j*np.random.randn(Nr))

        # Received signal
        y = H @ x_symbol + noise

        # ---------- ZF Detector ----------
        W_zf = np.linalg.pinv(H)
        x_zf = W_zf @ y
        bits_zf = bpsk_demod(x_zf)
        errors_zf += np.sum(bits_zf != bits[i])

        # ---------- MMSE Detector ----------
        W_mmse = np.linalg.inv(H.conj().T @ H + noise_variance * np.eye(Nt)) @ H.conj().T
        x_mmse = W_mmse @ y
        bits_mmse = bpsk_demod(x_mmse)
        errors_mmse += np.sum(bits_mmse != bits[i])

    ber_zf.append(errors_zf / num_bits)
    ber_mmse.append(errors_mmse / num_bits)

    print(f"SNR={snr} dB -->  BER_ZF={ber_zf[-1]:.5f}   BER_MMSE={ber_mmse[-1]:.5f}")


# ---------- Plot ----------
plt.figure()
plt.semilogy(SNR_dB, ber_zf, marker='o')
plt.semilogy(SNR_dB, ber_mmse, marker='s')
plt.title("BER vs SNR for MIMO (2x2): ZF and MMSE Detectors")
plt.xlabel("SNR (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.grid(True, which='both')
plt.legend(["ZF Detector", "MMSE Detector"])
plt.show()
