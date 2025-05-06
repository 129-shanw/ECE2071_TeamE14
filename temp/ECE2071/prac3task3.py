import numpy as np
import serial.tools.list_ports
import wave
import serial
import matplotlib.pyplot as plt
import time
import csv

data = []

BAUD_RATE = 115200
SAMPLE_RATE = 5000
TIME_RANGE = 5

devices = serial.tools.list_ports.comports()
for device in devices:
    if "STM32 STLink" in device.description:
        STM_device = device.device

ser = serial.Serial(STM_device, BAUD_RATE, timeout=0.001)
print(f"Connected to: {STM_device}")

start_time = time.time()

for _ in range(TIME_RANGE * SAMPLE_RATE):
    byte = ser.read(1)
    if byte:
        data.append(byte[0])

duration = time.time() - start_time
ser.close()
print(f"Collected {len(data)} samples in {duration:.2f} seconds.")

data = np.array(data)

# Normalize for audio and convert to 8-bit
normalized_data = (data - data.min()) / data.max()
normalized_data = normalized_data * 255
normalized_data = normalized_data.astype(np.uint8)

# Save to WAV file
with wave.open("outputWO.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(1)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(normalized_data.tobytes())

print("Audio has been saved!!!")

# Save waveform as PNG
time_axis = np.arange(len(normalized_data)) / SAMPLE_RATE
plt.figure(figsize=(12, 4))
plt.plot(time_axis, normalized_data, color='blue')
plt.title("ADC Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("waveformWO.png")
plt.close()

print("Waveform has been saved!!!")

# Save raw data to CSV
with open("raw_adc_dataWO.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Index", "Raw_Value"])
    for i, val in enumerate(data):
        writer.writerow([i, val])

print("CSV of raw data has been saved!!!")
