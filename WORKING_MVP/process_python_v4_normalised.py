import numpy as np
import wave
import serial

# ——— Configuration ———
SAMPLE_RATE    = 5000        # samples/sec
RECORD_SECONDS = 5           # seconds to capture
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM3'      # ← your Processing STM port
BAUD_RATE      = 115200
OUTPUT_WAV     = 'audio_recording_normalized.wav'
# ————————————————————

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
    
    # Save original audio for comparison
    with wave.open('audio_recording_original.wav', 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8‑bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio.tobytes())
    
    print(f"Saved original WAV: audio_recording_original.wav")
    
    # Normalize audio to use full dynamic range
    print("Applying audio normalization...")
    
    # Convert to float for processing
    audio_float = audio.astype(np.float32)
    
    # Center around zero and expand range
    audio_float = (audio_float - 128) * 2
    
    # Find maximum absolute value for normalization
    max_val = np.max(np.abs(audio_float))
    if max_val > 0:  # Avoid division by zero
        # Normalize to full range, then shift back to 0-255 range
        audio_normalized = np.clip(audio_float / max_val * 127 + 128, 0, 255).astype(np.uint8)
    else:
        audio_normalized = audio  # If audio is silent, keep as is
    
    # Save normalized audio
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8‑bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio_normalized.tobytes())

    print(f"Saved normalized WAV: {OUTPUT_WAV}")
    
    # Print some stats about the normalization
    print(f"Original audio range: {np.min(audio)} to {np.max(audio)}")
    print(f"Normalized audio range: {np.min(audio_normalized)} to {np.max(audio_normalized)}")

if __name__ == '__main__':
    record_and_save()