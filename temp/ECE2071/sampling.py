import numpy as np
import serial.tools.list_ports
import wave
import serial
import matplotlib.pyplot as plt
import time
import csv


# Settings
BAUD_RATE = 115200
SAMPLE_RATE = 5000  # Matches STM32 sampling
DURATION_SECONDS = 20
SAMPLES_TO_COLLECT = SAMPLE_RATE * DURATION_SECONDS
CHUNK_SIZE = 2048

# Auto-detect STM32 port
STM_device = None
for device in serial.tools.list_ports.comports():
    if "STM32" in device.description or "STLink" in device.description:
        STM_device = device.device
        break

# Open serial connection
ser = serial.Serial(STM_device, BAUD_RATE, timeout=100)
print(f"Connected to: {STM_device}")

# Collect data
data = []
start_time = time.time()
print(f"Collecting {SAMPLES_TO_COLLECT} samples...")

while len(data) < SAMPLES_TO_COLLECT:
    chunk = ser.read(CHUNK_SIZE)
    print(f"Received chunk with size {len(chunk)} bytes")
    if len(chunk) > 0:
        data.extend(chunk)
    else:
        print("No data received, retrying...")

ser.close()
duration = time.time() - start_time
print(f"Collected {len(data)} samples in {duration:.2f} seconds.")

data = np.array(data)

# Save raw data to CSV
with open("raw_adc_data.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Index", "Raw_ADC_Value"])
    for i, val in enumerate(data):
        writer.writerow([i, val])
print("Saved: raw_adc_data.csv")

# Apply simple moving average filter
def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size)/window_size, mode='same')

# Apply filter with small window (e.g., 5 samples)
filtered_data = moving_average(data, window_size=3)

# Normalize for audio and convert to 8-bit
data = (data - data.min()) / data.max()
data = data * 255
data = data.astype(np.uint8)

# Save as WAV
with wave.open("outputwithoutfilter.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)         # mono
    wav_file.setsampwidth(1)         # 8-bit
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(data.tobytes())
print("Saved: output.wav")

# Normalize for audio and convert to 8-bit
# Normalize to 0–1
filtered_data = (filtered_data - filtered_data.min()) / (filtered_data.max() - filtered_data.min())

# Optional: Apply gain (boost volume) — clip to avoid wraparound
GAIN = 1.5  # Try 1.5–2.0; increase to make it louder
filtered_data = np.clip(filtered_data * GAIN, 0, 1)

# Convert to 8-bit
filtered_data = (filtered_data * 255).astype(np.uint8)


# Save as WAV
with wave.open("outputwithfilter.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)         # mono
    wav_file.setsampwidth(1)         # 8-bit
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(filtered_data.tobytes())
print("Saved: output.wav")

# Plot and save waveform
time_axis = np.arange(len(data)) / SAMPLE_RATE
plt.figure(figsize=(12, 4))
plt.plot(time_axis, data, color='blue')
plt.title("ADC Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (0-255)")
plt.grid(True)
plt.tight_layout()
plt.savefig("waveform.png")
plt.close()
print("Saved: waveform.png")

# Fourier Transform (FFT)
frequencies = np.fft.fftfreq(len(data), 1/SAMPLE_RATE)  # Frequency bins
fft_values = np.fft.fft(data)  # FFT of the signal
fft_magnitude = np.abs(fft_values)  # Magnitude of the FFT

# Remove the DC component (frequency 0)
frequencies_no_dc = frequencies[1:]  # Remove the 0 Hz component
fft_magnitude_no_dc = fft_magnitude[1:]  # Remove the DC magnitude

# Plot and save frequency spectrum (without DC component)
plt.figure(figsize=(12, 4))
plt.plot(frequencies_no_dc[:len(frequencies_no_dc)//2], fft_magnitude_no_dc[:len(frequencies_no_dc)//2], color='red')  # Only plot positive frequencies
plt.title("Frequency Spectrum (No DC Component)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("frequency_spectrum_no_dc.png")
plt.close()
print("Saved: frequency_spectrum_no_dc.png")

print(f"Effective sample rate: {len(data) / duration:.2f} Hz")