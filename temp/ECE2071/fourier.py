# fft_visualizer.py
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_RATE = 5000  # Hz — change if different

# Load the raw signal
data = np.load("raw_signal.npy").astype(np.float32)

# Remove DC offset
signal = data - np.mean(data)

# FFT
fft_data = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(signal), 1 / SAMPLE_RATE)

# Get magnitude (only positive frequencies)
half_len = len(freqs) // 2
magnitude = np.abs(fft_data[:half_len])
freqs = freqs[:half_len]

# Plot
plt.figure(figsize=(12, 5))
plt.plot(freqs, magnitude, color='purple')
plt.title("Magnitude Spectrum (FFT) — DC Removed")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("fft_spectrum.png")
