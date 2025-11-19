import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------
N = 200000                         # number of bits
EbN0_dB = np.arange(0, 21, 2)      # 0 to 20 dB in 2 dB steps
ber_sim = []                       # to store simulated BER

# ----------------------------------------------------------
# SIMULATION: BPSK IN RAYLEIGH FADING (COHERENT DETECTION)
# ----------------------------------------------------------
for ebn0 in EbN0_dB:

    # Generate random bits (0/1)
    bits = np.random.randint(0, 2, N)

    # BPSK mapping: 0 → +1, 1 → -1
    x = 1 - 2*bits

    # Rayleigh fading channel: h = (real + j imag) / sqrt(2)
    h = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)

    # Convert Eb/N0 from dB to linear
    EbN0_lin = 10**(ebn0/10)

    # Noise variance: N0 = 1 / EbN0
    N0 = 1 / EbN0_lin

    # AWGN noise
    noise = np.sqrt(N0/2) * (np.random.randn(N) + 1j*np.random.randn(N))

    # Received signal
    y = h*x + noise

    # Coherent detection – equalization
    y_eq = y / h

    # Hard decision detection
    bits_hat = (np.real(y_eq) < 0).astype(int)

    # Count bit errors
    BER = np.mean(bits != bits_hat)
    ber_sim.append(BER)

# ----------------------------------------------------------
# THEORETICAL BER: BPSK OVER RAYLEIGH FADING
# ----------------------------------------------------------
EbN0_lin = 10**(EbN0_dB/10)
ber_th = 0.5 * (1 - np.sqrt(EbN0_lin / (1 + EbN0_lin)))


# ----------------------------------------------------------
# PLOTTING
# ----------------------------------------------------------
plt.figure(figsize=(8,6))
plt.semilogy(EbN0_dB, ber_sim, 'o-', label="Simulated BER")
plt.semilogy(EbN0_dB, ber_th, 's-', label="Theoretical BER")

plt.xlabel("Eb/N0 (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.title("BER Performance of a SISO System (BPSK, Rayleigh Fading, Coherent Detection)")
plt.grid(True, which='both')
plt.legend()
plt.tight_layout()
plt.show()
