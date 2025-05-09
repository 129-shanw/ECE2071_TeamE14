import numpy as np
import wave
import serial
import time
import datetime

# ——— Configuration ———
SAMPLE_RATE    = 5000        # samples/sec
RECORD_SECONDS = 5           # seconds to capture
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM12'      # ← your Processing STM port
BAUD_RATE      = 115200
OUTPUT_WAV     = 'audio_recording_v6.wav'
# ————————————————————

def record_and_save():
    # 1) Open port in blocking mode
    ser = serial.Serial(PORT, BAUD_RATE, timeout=None)
    print(f"Opened {PORT} @ {BAUD_RATE}. Target: {RECORD_SECONDS} seconds at {SAMPLE_RATE} Hz")
    
    # 2) Flush any old data
    ser.reset_input_buffer()
    
    # 3) Record with timing
    start_time = time.time()
    
    # Read data in chunks to ensure we get exactly 5 seconds
    data = bytearray()
    bytes_per_second = SAMPLE_RATE  # 8-bit samples = 1 byte per sample
    target_bytes = RECORD_SECONDS * bytes_per_second
    
    # Keep reading until we've collected enough data or timed out
    timeout_seconds = RECORD_SECONDS * 1.5  # 50% extra time as safety margin
    while len(data) < target_bytes and (time.time() - start_time) < timeout_seconds:
        # Calculate remaining bytes needed
        remaining = target_bytes - len(data)
        # Read in smaller chunks for better timing control
        chunk = ser.read(min(remaining, 1000))
        if chunk:
            data.extend(chunk)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Close the serial connection
    ser.close()
    
    # Calculate actual sample rate
    got = len(data)
    actual_sample_rate = int(got / elapsed) if elapsed > 0 else 0
    
    print(f"Recording complete:")
    print(f"  - Time elapsed: {elapsed:.2f} seconds")
    print(f"  - Samples received: {got}/{target_bytes}")
    print(f"  - Actual sample rate: ~{actual_sample_rate} Hz")
    
    if got < target_bytes:
        print("Warning: fewer samples than expected. Check STM side or wiring.")
    
    # Trim or pad data to exact length if needed
    if got > target_bytes:
        print(f"Trimming {got - target_bytes} excess samples")
        data = data[:target_bytes]
    elif got < target_bytes:
        print(f"Padding with {target_bytes - got} silence samples")
        # Pad with middle value (128) for silence
        data.extend([128] * (target_bytes - got))
    
    # 4) Convert to numpy array
    audio = np.frombuffer(data, dtype=np.uint8)
    
    # 5) Improve sound quality through normalization
    print("Enhancing audio quality...")
    
    # Convert to float for processing
    audio_float = audio.astype(np.float32)
    
    # Center around zero and expand range
    audio_float = (audio_float - 128) * 2
    
    # Apply a simple noise reduction (optional)
    # This sets very quiet sounds to zero
    noise_threshold = 5.0
    audio_float[np.abs(audio_float) < noise_threshold] = 0
    
    # Find maximum absolute value for normalization
    max_val = np.max(np.abs(audio_float))
    if max_val > 0:  # Avoid division by zero
        # Normalize to full range, then shift back to 0-255 range
        audio_normalized = np.clip(audio_float / max_val * 127 + 128, 0, 255).astype(np.uint8)
    else:
        audio_normalized = audio  # If audio is silent, keep as is
    
    # 6) Save as WAV file
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8-bit
        wf.setframerate(SAMPLE_RATE)     # 5 kHz
        wf.writeframes(audio_normalized.tobytes())
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Saved enhanced WAV: {OUTPUT_WAV} at {timestamp}")
    print(f"Audio duration: exactly {RECORD_SECONDS} seconds")

if __name__ == '__main__':
    record_and_save()