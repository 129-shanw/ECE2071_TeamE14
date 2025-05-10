import numpy as np
import serial.tools.list_ports
import wave
import serial
import matplotlib.pyplot as plt
import time
import csv
from scipy.signal import butter, filtfilt


# Settings
BAUD_RATE = 921600
SAMPLE_RATE = 44138  # Matches STM32 sampling
DURATION_SECONDS = 10
SAMPLES_TO_COLLECT = SAMPLE_RATE * DURATION_SECONDS
CHUNK_SIZE = 100

# Detect STM32 port
STM_device = None
for device in serial.tools.list_ports.comports():
    if "STM32" in device.description or "STLink" in device.description:
        STM_device = device.device
        break

# Open serial connection
ser = serial.Serial(STM_device, BAUD_RATE, timeout=2)
print(f"Connected to: {STM_device}")

# Collect data
data = []

print(f"Collecting {SAMPLES_TO_COLLECT} samples...")
start_time = time.time()
while len(data) < SAMPLES_TO_COLLECT:
    chunk = ser.read(CHUNK_SIZE)
    if len(chunk) > 0:
        data.extend(chunk)
    else:
        print("No data received, retrying...")
duration = time.time() - start_time
ser.close()
# Save raw signal as .npy for later filtering
np.save("data.npy", data)
print("Saved: data.npy")
print(f"Collected {len(data)} data in {duration:.2f} seconds.")

# Convert the received data to 12-bit values
data = np.array(data, dtype=np.uint8)

# Reconstruct 12-bit values from the 16-bit chunks (LSB + MSB)
samples = []
for i in range(0, len(data), 2):  # Process two bytes (16 bits) per sample
    lsb = int(data[i])
    msb = int(data[i+1])
    # Combine the LSB and MSB to get a 12-bit sample (only lower 12 bits)
    sample = ((msb & 0x0F) << 8) | lsb  # The 4 MSB bits are discarded
    samples.append(sample)
samples = np.array(samples)

# Save original 16-bit values to CSV (before scaling)
with open("raw_16bit_values.csv", mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Sample Index", "16-bit Value"])
    for i, sample in enumerate(samples):
        writer.writerow([i, sample])
print("Saved: raw_16bit_values.csv")

# Normalize for audio and convert to 16-bit (for saving as 16-bit WAV file)
samples = samples.astype(np.uint16) << 4

# Frequency filter parameters
# High-pass filter to remove low-frequency noise (e.g., below 20 Hz)
# Low-pass filter to remove high-frequency noise (e.g., above 2000 Hz)
def butter_filter(data, lowcut, highcut, sample_rate, filter_type="bandpass", order=5):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype=filter_type, analog=False)
    return filtfilt(b, a, data)

# Apply the filter: 20 Hz - 2000 Hz bandpass filter
filtered_samples = butter_filter(samples, 40, 16000, SAMPLE_RATE, filter_type="bandpass")

# Save as 16-bit WAV
with wave.open("output16bit_filtered.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)       # Mono audio
    wav_file.setsampwidth(2)       # 16-bit depth = 2 bytes
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(filtered_samples.astype(np.uint16).tobytes())
print("Saved: output16bit_filtered.wav")

# Plot and save waveform
time_axis = np.arange(len(filtered_samples)) / SAMPLE_RATE
plt.figure(figsize=(12, 4))
plt.plot(time_axis, filtered_samples, color='blue')
plt.title("Filtered ADC Waveform (16-bit Depth)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (16-bit)")
plt.grid(True)
plt.tight_layout()
plt.savefig("waveform_filtered.png")
plt.close()
print("Saved: waveform_filtered.png")

# Save raw signal as .npy for later filtering
np.save("filtered_signal16bit.npy", filtered_samples)
print("Saved: filtered_signal16bit.npy")

print(f"Effective sample rate: {len(filtered_samples) / duration:.2f} Hz")
