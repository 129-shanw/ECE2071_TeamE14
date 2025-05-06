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
DURATION_SECONDS = 60
SAMPLES_TO_COLLECT = SAMPLE_RATE * DURATION_SECONDS
CHUNK_SIZE = 2048

# Detect STM32 port
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
    if len(chunk) > 0:
        data.extend(chunk)
    else:
        print("No data received, retrying...")

ser.close()
duration = time.time() - start_time
print(f"Collected {len(data)} samples in {duration:.2f} seconds.")

data = np.array(data)

# Normalize for audio and convert to 8-bit
data = (data - data.min()) / data.max()
data = data * 255
data = data.astype(np.uint8)

# Save as WAV
with wave.open("output.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)         # mono
    wav_file.setsampwidth(1)         # 8-bit
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(data.tobytes())
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

# Save raw signal as .npy for later filtering
np.save("raw_signal.npy", np.array(data, dtype=np.uint8))
print("Saved: raw_signal.npy")

print(f"Effective sample rate: {len(data) / duration:.2f} Hz")