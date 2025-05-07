import numpy as np
import wave
import serial
import time

SAMPLE_RATE = 5000
RECORD_SECONDS = 5
PORT = 'COM12'  # Change this to match your system
BAUD_RATE = 115200
FILE_NAME = 'audio_recording.wav'

data = []

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

print(f"Recording {RECORD_SECONDS} seconds of audio data...")
start_time = time.time()

# Record data for specified duration
while time.time() - start_time < RECORD_SECONDS:
    if ser.in_waiting > 0:
        byte_data = ser.read(1)
        data.append(byte_data[0])

print(f"Recorded {len(data)} samples")

if data:
    data_array = np.array(data)
    data_array = (data_array - data_array.min()) / (data_array.max() - data_array.min() + 1e-10)
    data_array = data_array * 255
    data_array = data_array.astype(np.uint8)
    
    # Save as WAV file
    with wave.open(FILE_NAME, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Single channel audio
        wav_file.setsampwidth(1)  # One byte per sample
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(data_array.tobytes())
    
    print(f"Audio saved to {FILE_NAME}")
else:
    print("No data received")

ser.close()