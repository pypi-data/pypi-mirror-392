# Exp 1 --> plot free space path loss model vs distance graph and observe how its change

import numpy as np
import matplotlib.pyplot as plt
import math

# Constants
pi = math.pi
c = 3e8                      # Speed of light (m/s)

# Distances from 1 to 1000 meters
d = np.linspace(1, 1000, 500)

# Three example frequencies (you can change them)
frequencies_MHz = [100, 500, 1000]   # MHz

plt.figure(figsize=(8,6))

# Loop through each frequency
for f_MHz in frequencies_MHz:
    f = f_MHz * 1e6                 # Convert MHz → Hz
    
    # Free Space Path Loss calculation
    FSL = (4 * pi * d * f) / c
    FSPL = FSL**2
    FSPL_dB = 10 * np.log10(FSPL)    # Convert linear → dB

    # Plot
    plt.plot(d, FSPL_dB, label=f"{f_MHz} MHz")

# Plot formatting
plt.title("Free Space Path Loss vs Distance")
plt.xlabel("Distance (m)")
plt.ylabel("FSPL (dB)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()




#  another plot code 

import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

# Constants
pi = math.pi
f = 100 * (10**6)      # 100 MHz
d = 1000               # distance
c = 3 * (10**8)        # speed of light

print("Pi:", pi)

# Free Space Path Loss at d = 1000 m
FSL = (4 * pi * d * f) / c
FSPL = (FSL)**2
print("FSPL at d = 1000 m:", FSPL)

# Markdown text
markdown_text = """
We have considered d = 1000 meters
"""
display(Markdown(markdown_text))

# Plot FSPL vs distance
dnew = np.linspace(1, 1000, 10)
FSL_new = (4 * pi * dnew * f) / c
FSPL_new = (FSL_new)**2

print("Distance array:", dnew)

plt.figure(figsize=(7,5))
plt.plot(dnew, FSPL_new, marker='o')

# Axis labels and title
plt.xlabel("Distance (meters)")
plt.ylabel("Free Space Path Loss (linear scale)")
plt.title("Free Space Path Loss vs Distance (f = 100 MHz)")
plt.grid(True)

plt.show()

