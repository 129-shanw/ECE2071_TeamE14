import numpy as np
import wave
import serial
import time

# ——— Configuration ———
SAMPLE_RATE    = 5000               # samples per second
RECORD_SECONDS = 5                  # intended duration (for timeout guard)
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM3'             # ← adjust to your port
BAUD_RATE      = 115200
FILE_NAME      = 'audio_recording.wav'
# ————————————————————

def record_exactly_n():
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1.0)
    print(f"Opened {PORT} @ {BAUD_RATE}, waiting for STM to start…")
    time.sleep(0.5)
    ser.reset_input_buffer()

    data = bytearray()
    start = time.time()

    # keep reading until we have NUM_SAMPLES or a hard timeout
    while len(data) < NUM_SAMPLES:
        chunk = ser.read(NUM_SAMPLES - len(data))
        if chunk:
            data.extend(chunk)
        # optional safety: if it's taking more than RECORD_SECONDS+2 sec, break
        if time.time() - start > RECORD_SECONDS + 2:
            print("** Timeout waiting for samples **")
            break

    ser.close()
    return data

def save_wav(data):
    audio = np.frombuffer(data, dtype=np.uint8)
    with wave.open(FILE_NAME, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    print(f"Saved WAV to {FILE_NAME}")

if __name__ == '__main__':
    print(f"Recording until {NUM_SAMPLES} samples have arrived…")
    data = record_exactly_n()
    print(f"Captured {len(data)}/{NUM_SAMPLES} samples")
    if len(data) < NUM_SAMPLES:
        print("Warning: did not receive full sample count.")
    save_wav(data[:NUM_SAMPLES])