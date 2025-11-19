import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
num_rx_values = [1, 2, 3, 4]    # Number of receiver antennas
num_bits = 100000               # Number of bits
ebno_db = np.arange(0, 21, 2)   # Eb/No values in dB

# ------------------------------------------------------------
# STORE RESULTS SEPARATELY FOR TWO GRAPHS
# ------------------------------------------------------------
MRC_RESULTS = {}
EGC_RESULTS = {}

# ------------------------------------------------------------
# MAIN SIMULATION
# ------------------------------------------------------------
for num_rx in num_rx_values:

    bits = np.random.randint(0, 2, num_bits)
    x = 2 * bits - 1     # BPSK symbols: -1 and +1

    ber_mrc = []
    ber_egc = []

    for db in ebno_db:

        ebno = 10**(db / 10)
        N0 = 1 / ebno

        # Rayleigh channel
        h = (np.random.randn(num_rx, num_bits) + 1j*np.random.randn(num_rx, num_bits)) / np.sqrt(2)

        # AWGN noise
        n = np.sqrt(N0/2) * (np.random.randn(num_rx, num_bits) + 1j*np.random.randn(num_rx, num_bits))

        # Received signals
        y = h * x + n

        # -----------------------------
        # MRC
        # -----------------------------
        y_mrc = np.sum(np.conj(h) * y, axis=0)
        x_cap_mrc = np.sign(np.real(y_mrc))
        ber_mrc.append(np.mean(x_cap_mrc != x))

        # -----------------------------
        # EGC (phase-only correction)
        # -----------------------------
        epsilon = 1e-10
        h_phase = np.conj(h) / (np.abs(h) + epsilon)
        y_egc = np.sum(h_phase * y, axis=0)
        x_cap_egc = np.sign(np.real(y_egc))
        ber_egc.append(np.mean(x_cap_egc != x))

    MRC_RESULTS[num_rx] = ber_mrc
    EGC_RESULTS[num_rx] = ber_egc

# ------------------------------------------------------------
# GRAPH 1 → ONLY MRC
# ------------------------------------------------------------
plt.figure(figsize=(9,6))
for num_rx in num_rx_values:
    plt.semilogy(ebno_db, MRC_RESULTS[num_rx], marker='o', label=f"MRC (Nrx={num_rx})")

plt.xlabel("Eb/No (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.title("SIMO BPSK BER Performance (MRC Combining)")
plt.grid(True, which='both')
plt.legend()
plt.ylim([1e-5, 1])
plt.xlim([0,20])
plt.show()

# ------------------------------------------------------------
# GRAPH 2 → ONLY EGC
# ------------------------------------------------------------
plt.figure(figsize=(9,6))
for num_rx in num_rx_values:
    plt.semilogy(ebno_db, EGC_RESULTS[num_rx], marker='^', linestyle='--', label=f"EGC (Nrx={num_rx})")

plt.xlabel("Eb/No (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.title("SIMO BPSK BER Performance (EGC Combining)")
plt.grid(True, which='both')
plt.legend()
plt.ylim([1e-5, 1])
plt.xlim([0,20])
plt.show()
