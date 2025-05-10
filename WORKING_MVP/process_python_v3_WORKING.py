import numpy as np
import wave
import serial

# ---- Configuration -----
SAMPLE_RATE    = 5000        #Sample rate = 5000Hz
RECORD_SECONDS = 5           #Recording time
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM3'      # ← your Processing STM port
BAUD_RATE      = 115200
OUTPUT_WAV     = 'audio_recording.wav'
# ------------------------

def record_and_save():
    # 1) Open port in blocking mode
    ser = serial.Serial(PORT, BAUD_RATE, timeout=None)
    print(f"Opened {PORT} @ {BAUD_RATE}. Reading next {NUM_SAMPLES} samples…")

    # 2) Flush any old data
    ser.reset_input_buffer()

    # 3) Block until we get exactly NUM_SAMPLES bytes
    data = ser.read(NUM_SAMPLES)
    ser.close()

    got = len(data)
    print(f"Received {got}/{NUM_SAMPLES} samples")

    if got < NUM_SAMPLES:
        print("Warning: fewer samples than expected check STM side or wiring.")

    # 4) Wrap and write to WAV
    audio = np.frombuffer(data, dtype=np.uint8)
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8‑bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio.tobytes())

    print(f"Saved WAV: {OUTPUT_WAV}")

if __name__ == '__main__':
    record_and_save()