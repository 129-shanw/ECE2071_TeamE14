import numpy as np
import matplotlib.pyplot as plt
import wave

SAMPLE_RATE = 5000  # Hz

# Load raw signal (assumed saved from ADC as 0–255 values)
data = np.load("raw_signal.npy").astype(np.float32)

# --- STEP 1: Zero-center the signal ---
data -= np.mean(data)  # Remove DC offset

# --- STEP 2: Frequency-domain filtering ---
fft_data = np.fft.fft(data)
freqs = np.fft.fftfreq(len(data), 1 / SAMPLE_RATE)

low_cutoff = 30    # Hz
high_cutoff = 3000   # Hz
band_mask = (np.abs(freqs) > low_cutoff) & (np.abs(freqs) < high_cutoff)
fft_data[~band_mask] = 0

# --- STEP 3: Inverse FFT ---
filtered = np.fft.ifft(fft_data).real

# --- STEP 4: Normalize to 8-bit unsigned for WAV ---
# First, normalize to [-1, 1] range
filtered -= filtered.min()
filtered /= filtered.max()

# Then scale to [0, 255]
filtered = (filtered * 255).astype(np.uint8)

# Save as WAV
with wave.open("outputFiltered_fromNpy.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(1)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(filtered.tobytes())

# Plot
time_axis = np.arange(len(filtered)) / SAMPLE_RATE
plt.figure(figsize=(12, 4))
plt.plot(time_axis, filtered, color='green')
plt.title("Filtered Audio Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (0-255)")
plt.grid(True)
plt.tight_layout()
plt.savefig("waveformFiltered_fromNpy.png")
plt.close()
