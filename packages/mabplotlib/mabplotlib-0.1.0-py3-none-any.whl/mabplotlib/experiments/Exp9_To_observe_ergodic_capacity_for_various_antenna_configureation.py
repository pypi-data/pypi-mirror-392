#  siso 




import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp

# Parameters
num_channels_list = [100, 1000, 10000, 50000]
SNR_dB_values = np.arange(0, 21, 1)
SNR_linear_values = 10 ** (SNR_dB_values / 10)
bandwidth = 1

# Create a color gradient for clarity
colors = plt.cm.viridis(np.linspace(0, 1, len(num_channels_list)))

plt.figure(figsize=(10, 6))

for idx, num_channels in enumerate(num_channels_list):
    ergodic_capacity_values = []
    for SNR_linear in SNR_linear_values:
        h_real = np.random.randn(num_channels)
        h_imag = np.random.randn(num_channels)
        h_sq = (h_real**2 + h_imag**2) / 2
        instantaneous_capacity = bandwidth * np.log2(1 + h_sq * SNR_linear)
        ergodic_capacity_values.append(np.mean(instantaneous_capacity))

    plt.plot(
        SNR_dB_values,
        ergodic_capacity_values,
        '-o',
        color=colors[idx],
        label=f'{num_channels} Channels',
        linewidth=2,
        markersize=5
    )

# Theoretical (infinite channel realizations)
theoretical_capacity = np.log2(np.e) * np.exp(1 / SNR_linear_values) * sp.expi(1 / SNR_linear_values)
plt.plot(SNR_dB_values, theoretical_capacity, 'k--', linewidth=2.5, label='Theoretical (∞ Channels)')

# Plot settings
plt.xlabel("Average SNR (dB)")
plt.ylabel("Ergodic Capacity (bits/s/Hz)")
plt.title("Ergodic Capacity for SISO Rayleigh Fading Channel")
plt.grid(True, which="both", linestyle='--', linewidth=0.6)
plt.legend(title="Number of Channel Realizations", fontsize=9)
plt.tight_layout()
plt.show()




# Simo 

# For SIMO (1x2) channel ergodic capacity
# formula
# C = E(w*log(base 2)(1 + x*SNR))
# C = channel capacity , E = expecitation/Mean , w = bandwidth , x = [sum of (from i = 1 to num_rx)(sum of |random channel gain coefficient|^2 for each receive antenna)]

import numpy as np
import matplotlib.pyplot as plt
import math

num_channels_list = [100 ,1000 ,10000 ,50000]
SNR_dB_values_to_print = [0, 15, 20]
SNR_dB_values_plot = np.arange(0, 21, 1)
bandwidth = 1
num_rx_values = [2,3,4,5] # Renamed to avoid conflict and represent a list of values

plt.figure(figsize=(10, 5))

# Iterate through different numbers of receive antennas
for num_rx in num_rx_values:
    print(f"\n--- Simulating for 1x{num_rx} SIMO ---")
    for num_channels in num_channels_list:
        ergodic_capacity_values_plot = []
        capacity_for_print = {}

        for SNR_dB in SNR_dB_values_plot:

            SNR_linear = 10**(SNR_dB / 10)
            h_sq_sum = np.zeros(num_channels)
            for _ in range(num_rx): # Use the current integer value from the outer loop
                h_real = np.random.randn(num_channels)
                h_imag = np.random.randn(num_channels)
                h_sq = (h_real**2 + h_imag**2) / 2
                h_sq_sum += h_sq

            # instantaneous capacity for each channel
            instantaneous_capacity = bandwidth * np.log2(1 + h_sq_sum * SNR_linear)

            # ergodic capacity
            ergodic_capacity = np.mean(instantaneous_capacity)
            ergodic_capacity_values_plot.append(ergodic_capacity)


            if SNR_dB in SNR_dB_values_to_print:
                capacity_for_print[SNR_dB] = ergodic_capacity

        print(f"no. of channels = {num_channels}")
        for snr in SNR_dB_values_to_print:
            print(f"for SNR {snr}db -> capacity {capacity_for_print[snr]:.4f}")
        print("-" * 20)
        # Plotting for each number of channel realizations for the current num_rx
        plt.plot(SNR_dB_values_plot, ergodic_capacity_values_plot, '-o', label=f'{num_channels} Channels (1x{num_rx})')


# Plotting settings
plt.xlabel("Average SNR (dB)")
plt.ylabel("Ergodic Capacity (bits/s/Hz)")
plt.title(f"Ergodic Channel Capacity for SIMO Rayleigh Fading Channel vs. Number of Channel Realizations and Rx Antennas")
plt.grid(True)
plt.legend()
plt.show()


# miso 

# for MISO

# For SIMO (1x2) channel ergodic capacity
# formula
# C = E(w*log(base 2)(1 + x*SNR))
# C = channel capacity , E = expecitation/Mean , w = bandwidth , x = [sum of (from i = 1 to num_rx)(sum of |random channel gain coefficient|^2 for each receive antenna)]

import numpy as np
import matplotlib.pyplot as plt
import math

num_channels_list = [100 ,1000 ,10000 ,50000]
SNR_dB_values_to_print = [0, 15, 20]
SNR_dB_values_plot = np.arange(0, 21, 1)
bandwidth = 1
num_tx_values = [2,3,4,5] # Renamed to num_tx_values and made a list

plt.figure(figsize=(10, 5))

# Iterate through different numbers of transmit antennas
for num_tx in num_tx_values:
    print(f"\n--- Simulating for {num_tx}x1 MISO ---")
    for num_channels in num_channels_list:
        ergodic_capacity_values_plot = []
        capacity_for_print = {}

        for SNR_dB in SNR_dB_values_plot:

            SNR_linear = 10**(SNR_dB / 10)
            h_sq_sum = np.zeros(num_channels)
            for _ in range(num_tx): # Use the current integer value from the outer loop
                h_real = np.random.randn(num_channels)
                h_imag = np.random.randn(num_channels)
                h_sq = (h_real**2 + h_imag**2) / 2
                h_sq_sum += h_sq

            # instantaneous capacity for each channel
            instantaneous_capacity = bandwidth * np.log2(1 + h_sq_sum * SNR_linear)

            # ergodic capacity
            ergodic_capacity = np.mean(instantaneous_capacity)
            ergodic_capacity_values_plot.append(ergodic_capacity)


            if SNR_dB in SNR_dB_values_to_print:
                capacity_for_print[SNR_dB] = ergodic_capacity

        print(f"no. of channels = {num_channels}")
        for snr in SNR_dB_values_to_print:
            print(f"for SNR {snr}db -> capacity {capacity_for_print[snr]:.4f}")
        print("-" * 20)




#  for mimo 

import numpy as np
import matplotlib.pyplot as plt
import math

num_channels_list = [100, 1000, 10000] # Reduced list for faster simulation
SNR_dB_values_to_print = [0, 10, 15, 20]
SNR_dB_values_plot = np.arange(0, 26, 1) # Extend SNR range for better visualization
bandwidth = 1

# MIMO configurations (Nt x Nr)
mimo_configs = [(2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]

plt.figure(figsize=(12, 8))

for Nt, Nr in mimo_configs:
    print(f"\n--- Simulating for {Nt}x{Nr} MIMO ---")
    for num_channels in num_channels_list:
        ergodic_capacity_values_plot = []
        capacity_for_print = {}

        for SNR_dB in SNR_dB_values_plot:
            SNR_linear = 10**(SNR_dB / 10)
            P_total_over_N0 = SNR_linear

            instantaneous_capacities = []
            for _ in range(num_channels):
                # Generate MIMO channel matrix (Nr x Nt)
                H = (np.random.randn(Nr, Nt) + 1j * np.random.randn(Nr, Nt)) / np.sqrt(2) # Normalize

                HH_conj_transpose = np.conj(H).T

                # Term inside the determinant: I_Nr + (P_total_over_N0/Nt) * H * H^H
                term = (P_total_over_N0 / Nt) * np.dot(H, HH_conj_transpose)
                Inr = np.eye(Nr)
                matrix_for_determinant = Inr + term

                det_matrix = np.linalg.det(matrix_for_determinant)

                # Instantaneous capacity
                C_inst = bandwidth * math.log2(np.maximum(np.real(det_matrix), 1e-12))
                instantaneous_capacities.append(C_inst)

            # Ergodic capacity is the average of instantaneous capacities
            ergodic_capacity = np.mean(instantaneous_capacities)
            ergodic_capacity_values_plot.append(ergodic_capacity)

            if SNR_dB in SNR_dB_values_to_print:
                capacity_for_print[SNR_dB] = ergodic_capacity

        print(f"no. of channels = {num_channels}")
        for snr in SNR_dB_values_to_print:
            # Check if snr is in capacity_for_print keys before accessing
            if snr in capacity_for_print:
                 print(f"for SNR {snr}db -> capacity {capacity_for_print[snr]:.4f}")
            else:
                 print(f"for SNR {snr}db -> capacity N/A (not in plot range)")
        print("-" * 20)
