import numpy as np
import wave
import serial
import time

# ——— Configuration ———
SAMPLE_RATE     = 5000        # samples per second
RECORD_SECONDS  = 5           # recording length in seconds
NUM_SAMPLES     = SAMPLE_RATE * RECORD_SECONDS
PORT            = 'COM3'      # ← adjust to your port
BAUD_RATE       = 115200
FILE_NAME       = 'audio_recording.wav'
# ————————————————————

def record_and_save():
    # 1) Open serial port with longer timeout
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1.0)
    print(f"Opened {PORT} @ {BAUD_RATE}, waiting for STM to start…")

    # 2) Give the STM a moment to power up & start TX
    time.sleep(0.5)
    ser.reset_input_buffer()  # drop any initial garbage

    # 3) Start reading exactly NUM_SAMPLES bytes
    data = bytearray()
    start = time.time()
    while len(data) < NUM_SAMPLES and (time.time() - start) < (RECORD_SECONDS + 3):
        # read up to remaining bytes; will block up to timeout
        chunk = ser.read(NUM_SAMPLES - len(data))
        if chunk:
            data.extend(chunk)
    ser.close()

    print(f"Captured {len(data)}/{NUM_SAMPLES} samples")

    if not data:
        print("No data received—check wiring and that the STM is transmitting.")
        return

    # 4) Wrap in NumPy and write WAV
    audio = np.frombuffer(data, dtype=np.uint8)
    with wave.open(FILE_NAME, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    print(f"Saved WAV to {FILE_NAME}")

if __name__ == '__main__':
    record_and_save()