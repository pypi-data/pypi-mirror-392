# BPSK 
import numpy as np
import matplotlib.pyplot as plt
import itertools

# ML detector function
def ml_detect(H, y, candidates):
    Hs = H @ candidates.T                 # shape (Nr, Nc)
    diff = y.reshape(-1,1) - Hs
    dist = np.sum(np.abs(diff)**2, axis=0)
    return candidates[np.argmin(dist)]

def run_bpsk_ml_mimo():
    mimo_configs = [(2,2), (4,4), (8,8)]
    SNR_dB_values = np.arange(0, 21, 2)
    num_bits = 20000

    plt.figure(figsize=(10,5))

    for Nt, Nr in mimo_configs:
        print(f"\n=== BPSK ML : Simulating {Nt}x{Nr} MIMO ===")

        # ML candidate set (2^Nt)
        num_comb = 2**Nt
        bin_rep = ((np.arange(num_comb)[:,None] >> np.arange(Nt)) & 1)
        cand = 2*bin_rep - 1    # -1, +1
        cand = cand.astype(np.float64)

        ber_values = []

        for SNR_dB in SNR_dB_values:
            SNR_linear = 10**(SNR_dB/10)
            N0 = Nt / SNR_linear

            bits = np.random.randint(0,2,num_bits)
            symbols = 2*bits - 1

            symbols = symbols[:(num_bits//Nt)*Nt]
            bits = bits[:(num_bits//Nt)*Nt]

            symbols = symbols.reshape(-1, Nt)
            Nsym = symbols.shape[0]

            errors = 0

            for i in range(Nsym):
                s = symbols[i]

                H = (np.random.randn(Nr,Nt) + 1j*np.random.randn(Nr,Nt))/np.sqrt(2)
                noise = np.sqrt(N0/2)*(np.random.randn(Nr)+1j*np.random.randn(Nr))
                y = H @ s + noise

                s_hat = ml_detect(H,y,cand)

                bits_hat = (s_hat+1)//2
                bits_org = (s+1)//2
                errors += np.sum(bits_hat != bits_org)

            ber_values.append(errors/(Nsym*Nt))

        plt.semilogy(SNR_dB_values, ber_values,'-o',label=f"BPSK {Nt}x{Nr}")

    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.grid(True,which='both')
    plt.legend()
    plt.title("ML-MIMO BER (BPSK)")
    plt.show()


run_bpsk_ml_mimo()





# QPSK 

import numpy as np
import matplotlib.pyplot as plt
import itertools

# ML detector
def ml_detect(H, y, candidates):
    Hs = H @ candidates.T
    diff = y.reshape(-1,1) - Hs
    dist = np.sum(np.abs(diff)**2, axis=0)
    return candidates[np.argmin(dist)]

def run_qpsk_ml_mimo():
    SNR_dB_values = np.arange(0, 21, 2)
    mimo_configs = [(2,2), (4,4)]
    num_bits = 20000

    # Normalized QPSK constellation
    qpsk = np.array([1+1j,1-1j,-1+1j,-1-1j]) / np.sqrt(2)

    bits_to_sym = {
        (0,0): qpsk[0],
        (0,1): qpsk[1],
        (1,0): qpsk[2],
        (1,1): qpsk[3],
    }

    sym_to_bits = {
        0:(0,0),
        1:(0,1),
        2:(1,0),
        3:(1,1)
    }

    plt.figure(figsize=(10,6))

    for Nt, Nr in mimo_configs:
        print(f"\n=== QPSK ML : Simulating {Nt}x{Nr} MIMO ===")

        # ML candidate symbols 4^Nt
        idx_grid = np.array(list(itertools.product(range(4),repeat=Nt)))
        candidates = qpsk[idx_grid]

        ber_values = []

        for SNR_dB in SNR_dB_values:
            SNR_lin = 10**(SNR_dB/10)
            N0 = Nt / SNR_lin

            bits = np.random.randint(0,2,num_bits)
            bits = bits[: (num_bits//(2*Nt))*(2*Nt)]

            b2 = bits.reshape(-1,Nt,2)
            Nsym = b2.shape[0]

            s_tx = np.zeros((Nsym,Nt),dtype=complex)
            for i in range(Nsym):
                for j in range(Nt):
                    s_tx[i,j] = bits_to_sym[tuple(b2[i,j])]

            errors = 0

            for i in range(Nsym):
                s = s_tx[i]
                
                H = (np.random.randn(Nr,Nt)+1j*np.random.randn(Nr,Nt))/np.sqrt(2)
                noise = np.sqrt(N0/2)*(np.random.randn(Nr)+1j*np.random.randn(Nr))
                y = H @ s + noise

                s_hat = ml_detect(H,y,candidates)

                for k in range(Nt):
                    d = np.abs(qpsk - s_hat[k])**2
                    idx = np.argmin(d)
                    bits_est = sym_to_bits[idx]
                    bits_org = tuple(b2[i,k])
                    errors += sum(be!=bo for be,bo in zip(bits_est,bits_org))

            ber_values.append(errors/(Nsym*Nt*2))

        plt.semilogy(SNR_dB_values,ber_values,'-s',label=f"QPSK {Nt}x{Nr}")

    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.grid(True,which='both')
    plt.title("ML-MIMO BER (QPSK)")
    plt.legend()
    plt.show()


run_qpsk_ml_mimo()

# 16 QAM  

import numpy as np
import matplotlib.pyplot as plt
import itertools

def ml_detect(H,y,candidates):
    Hs = H @ candidates.T
    diff = y.reshape(-1,1) - Hs
    dist = np.sum(np.abs(diff)**2, axis=0)
    return candidates[np.argmin(dist)]

def run_16qam_ml_mimo():
    SNR_dB_values = np.arange(0, 25, 3)
    mimo_configs = [(2,2)]
    num_bits = 20000

    # Gray-coded PAM4
    pam_bits_to_level = {
        (0,0):-3,
        (0,1):-1,
        (1,1): 1,
        (1,0): 3
    }
    norm = np.sqrt(10)

    qam_const = []
    qam_bits = []
    for bq in pam_bits_to_level:
        for bi in pam_bits_to_level:
            I = pam_bits_to_level[bi]
            Q = pam_bits_to_level[bq]
            qam_const.append((I + 1j*Q)/norm)
            qam_bits.append(bq+bi)

    qam_const = np.array(qam_const)
    qam_bits = np.array(qam_bits)

    bits_to_sym = { tuple(qam_bits[i]): qam_const[i] for i in range(16) }
    sym_to_bits = { i:tuple(qam_bits[i]) for i in range(16) }

    plt.figure(figsize=(10,5))

    for Nt,Nr in mimo_configs:
        print(f"\n=== 16-QAM ML : Simulating {Nt}x{Nr} ===")

        idx_grid = np.array(list(itertools.product(range(16), repeat=Nt)))
        candidates = qam_const[idx_grid]

        ber_values = []

        for SNR_dB in SNR_dB_values:
            SNR_lin = 10**(SNR_dB/10)
            N0 = Nt / SNR_lin

            bits = np.random.randint(0,2,num_bits)
            bits = bits[: (num_bits//(4*Nt))*(4*Nt)]

            b4 = bits.reshape(-1,Nt,4)
            Nsym = b4.shape[0]

            s_tx = np.zeros((Nsym,Nt),dtype=complex)
            for i in range(Nsym):
                for j in range(Nt):
                    s_tx[i,j] = bits_to_sym[tuple(b4[i,j])]

            errors = 0

            for i in range(Nsym):
                s = s_tx[i]

                H = (np.random.randn(Nr,Nt)+1j*np.random.randn(Nr,Nt))/np.sqrt(2)
                noise = np.sqrt(N0/2)*(np.random.randn(Nr)+1j*np.random.randn(Nr))
                y = H @ s + noise

                s_hat = ml_detect(H,y,candidates)

                for k in range(Nt):
                    d = np.abs(qam_const - s_hat[k])**2
                    idx = np.argmin(d)
                    bits_est = sym_to_bits[idx]
                    bits_org = tuple(b4[i,k])
                    errors += sum(be!=bo for be,bo in zip(bits_est,bits_org))

            ber_values.append(errors/(Nsym*Nt*4))

        plt.semilogy(SNR_dB_values, ber_values,'-x',label=f"16QAM {Nt}x{Nr}")

    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.title("ML-MIMO BER (16-QAM)")
    plt.grid(True,which='both')
    plt.legend()
    plt.show()


run_16qam_ml_mimo()
