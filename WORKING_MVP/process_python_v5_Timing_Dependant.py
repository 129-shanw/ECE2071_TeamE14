import numpy as np
import wave
import serial
import time

# ——— Configuration ———
SAMPLE_RATE    = 5000        # samples/sec
RECORD_SECONDS = 5           # seconds to capture
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM3'     # ← your Processing STM port
BAUD_RATE      = 115200
OUTPUT_WAV     = 'audio_recording.wav'
# ————————————————————

def record_and_save():
    # 1) Open port with a short timeout so we can poll
    ser = serial.Serial(PORT, BAUD_RATE, timeout=0.1)
    print(f"Opened {PORT} @ {BAUD_RATE}, recording for {RECORD_SECONDS}s…")
    ser.reset_input_buffer()

    data = bytearray()
    start = time.time()

    # 2) Read continuously until 5s elapsed or buffer full
    while (time.time() - start) < RECORD_SECONDS and len(data) < NUM_SAMPLES:
        to_read = ser.in_waiting
        if to_read:
            chunk = ser.read(min(to_read, NUM_SAMPLES - len(data)))
            data.extend(chunk)

    # 3) One final non-blocking byte, if available
    if len(data) < NUM_SAMPLES and ser.in_waiting:
        data.extend(ser.read(1))

    elapsed = time.time() - start
    ser.close()

    got = len(data)
    print(f"Time recorded: {elapsed:.3f}s — Captured {got}/{NUM_SAMPLES} samples")

    if got < NUM_SAMPLES:
        print("Warning: fewer samples than expected—check STM side or wiring.")

    # 4) Clip/pad to exactly NUM_SAMPLES
    audio = np.frombuffer(data.ljust(NUM_SAMPLES, b'\x80')[:NUM_SAMPLES], dtype=np.uint8)

    # 5) Write to WAV
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8-bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio.tobytes())

    print(f"Saved WAV: {OUTPUT_WAV}")

if __name__ == '__main__':
    record_and_save()