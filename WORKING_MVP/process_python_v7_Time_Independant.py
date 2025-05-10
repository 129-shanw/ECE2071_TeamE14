import time
import numpy as np
import wave
import serial

# --- Configuration ---
SAMPLE_RATE   = 5000             # samples/sec
RECORD_SECONDS = 15               # nominal length (for reference only)
NUM_SAMPLES   = SAMPLE_RATE * RECORD_SECONDS
PORT          = 'COM6'          # ← your Processing STM port
BAUD_RATE     = 115200
OUTPUT_WAV    = 'E14_Project.wav'
# ---------------------

def record_and_save():
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1.0)
    print(f"Opened {PORT} @ {BAUD_RATE}. Waiting for {RECORD_SECONDS} seconds at {SAMPLE_RATE} Hz")
    ser.reset_input_buffer()

    data = bytearray()
    start = time.time()

    # keep calling read() until we get exactly NUM_SAMPLES
    while len(data) < NUM_SAMPLES:
        to_read = NUM_SAMPLES - len(data)
        chunk = ser.read(to_read)
        if chunk:
            data.extend(chunk)
        # else: read() timed out, but keep looping indefinitely

    elapsed = time.time() - start
    ser.close()

    print(f"- Captured {len(data)}/{NUM_SAMPLES} samples in {elapsed:.3f}s")

    #calculate actual sample rate
    actual_sample_rate = int(len(data) / elapsed) if elapsed > 0 else 0
    print(f"- Actual sample rate: ~{actual_sample_rate} Hz")

    audio = np.frombuffer(data, dtype=np.uint8)
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8-bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio.tobytes())

    print(f"- Saved Audio File: {OUTPUT_WAV}")

if __name__ == '__main__':
    record_and_save()