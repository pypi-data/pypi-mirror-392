import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# Simulation parameters
# --------------------------------------------------------------

# Number of bits/samples to simulate for each experiment
samples_list = [10000, 100000, 1000000]

# SNR values (in dB) from 0 dB to 10 dB
SNR_dB_values = np.arange(0, 11, 1)

# Marker styles for each plot
markers = ['o', 's', '^']


# --------------------------------------------------------------
# MAIN LOOP - Run simulation for each samples value
# --------------------------------------------------------------

for i, samples in enumerate(samples_list):

    BER_values = []  # will store BER for each SNR

    # Loop for each SNR point
    for SNR_dB in SNR_dB_values:

        # Convert SNR from dB → linear
        SNR_linear = 10 ** (SNR_dB / 10)

        # --------------------------------------------------------------
        # Generate random bits and map to BPSK symbols (+1 / -1)
        # --------------------------------------------------------------

        # Generate 2 bits per codeword → Alamouti encodes 2 symbols
        Bin = np.random.randint(0, 2, samples * 2)

        # BPSK mapping: 0 → -1, 1 → +1
        BPSK = 2 * Bin - 1

        # Reshape symbols into pairs: (s1, s2)
        s = BPSK.reshape(-1, 2)


        # --------------------------------------------------------------
        # Generate Rayleigh fading channels h1 and h2 (CN(0,1))
        # --------------------------------------------------------------

        h1 = (np.random.randn(samples) + 1j * np.random.randn(samples)) / np.sqrt(2)
        h2 = (np.random.randn(samples) + 1j * np.random.randn(samples)) / np.sqrt(2)


        # --------------------------------------------------------------
        # Generate AWGN noise
        # --------------------------------------------------------------

        N0 = 1 / SNR_linear
        noise = (np.sqrt(N0 / 2)) * (
            np.random.randn(samples, 2) + 1j * np.random.randn(samples, 2)
        )


        # --------------------------------------------------------------
        # Alamouti STBC Transmission:
        #
        # Tx1 sends:  s1     ,  -s2*
        # Tx2 sends:  s2     ,   s1*
        #
        # Received:
        # r1 = h1*s1 + h2*s2 + n1
        # r2 = h1*(-s2*) + h2*(s1*) + n2
        # --------------------------------------------------------------

        r1 = h1 * s[:, 0] + h2 * s[:, 1] + noise[:, 0]
        r2 = h1 * (-np.conj(s[:, 1])) + h2 * np.conj(s[:, 0]) + noise[:, 1]


        # --------------------------------------------------------------
        # Alamouti Decoding
        #
        # y1 =  h1* r1 + h2 r2*
        # y2 =  h2* r1 - h1 r2*
        #
        # Final decision: divide by (|h1|² + |h2|²)
        # --------------------------------------------------------------

        y1 = np.conj(h1) * r1 + h2 * np.conj(r2)
        y2 = np.conj(h2) * r1 - h1 * np.conj(r2)

        denom = np.abs(h1)**2 + np.abs(h2)**2 + 1e-12  # avoid divide by zero

        s1_hat = y1 / denom
        s2_hat = y2 / denom


        # --------------------------------------------------------------
        # BPSK Detection: sign(real(value))
        # --------------------------------------------------------------

        decision_s1 = np.sign(np.real(s1_hat))
        decision_s2 = np.sign(np.real(s2_hat))

        # Convert back to sequence of bits
        decision_symbols = np.stack((decision_s1, decision_s2), axis=-1).flatten()
        decision_bits = (decision_symbols + 1) / 2


        # --------------------------------------------------------------
        # Compute BER
        # --------------------------------------------------------------

        errors = np.sum(decision_bits != Bin)
        BER = errors / (samples * 2)
        BER_values.append(BER)


    # --------------------------------------------------------------
    # Plot BER vs SNR for THIS samples value
    # --------------------------------------------------------------

    plt.figure(figsize=(8, 5))
    plt.semilogy(
        SNR_dB_values,          # FIXED VARIABLE NAME
        BER_values,
        marker=markers[i % len(markers)],
        linestyle='-',
        label=f'Samples per symbol period = {samples}'
    )

    plt.xlabel("SNR (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.title(f"BER Performance for {samples} Samples per Symbol Period\n(2x1 MISO Alamouti STBC in Rayleigh Fading)")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.show()
