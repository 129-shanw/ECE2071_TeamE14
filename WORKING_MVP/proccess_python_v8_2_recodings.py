import numpy as np
import wave
import serial
import time
import datetime
import scipy.signal as signal
from scipy.io import wavfile

# ——— Configuration ———
SAMPLE_RATE    = 5000        # samples/sec
RECORD_SECONDS = 10          # seconds to capture (increased to 10)
NUM_SAMPLES    = SAMPLE_RATE * RECORD_SECONDS
PORT           = 'COM12'      # ← your Processing STM port
BAUD_RATE      = 115200
OUTPUT_WAV_FULL = 'audio_recording_10s.wav'
OUTPUT_WAV_REDUCED = 'audio_recording_5s.wav'
# ————————————————————

def record_and_process():
    # 1) Open port in blocking mode
    ser = serial.Serial(PORT, BAUD_RATE, timeout=None)
    print(f"Opened {PORT} @ {BAUD_RATE}. Target: {RECORD_SECONDS} seconds at {SAMPLE_RATE} Hz")
    
    # 2) Flush any old data
    ser.reset_input_buffer()
    
    # 3) Record with timing
    start_time = time.time()
    
    # Read data in chunks to ensure we get exactly 10 seconds
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
    
    # 5) Process the audio to improve quality
    processed_audio = enhance_audio_quality(audio)
    
    # 6) Save the full 10-second recording
    save_wav(processed_audio, OUTPUT_WAV_FULL, SAMPLE_RATE)
    print(f"Saved full 10-second recording: {OUTPUT_WAV_FULL}")
    
    # 7) Create and save the 5-second version
    # Take the middle 5 seconds for best quality
    start_sample = SAMPLE_RATE * 2  # Start at 2 seconds in
    end_sample = start_sample + (SAMPLE_RATE * 5)  # Take 5 seconds
    reduced_audio = processed_audio[start_sample:end_sample]
    
    save_wav(reduced_audio, OUTPUT_WAV_REDUCED, SAMPLE_RATE)
    print(f"Saved reduced 5-second recording: {OUTPUT_WAV_REDUCED}")

def enhance_audio_quality(audio):
    """
    Enhance audio quality with multiple techniques:
    1. Convert to float for processing
    2. Apply dynamic range compression to flatten peaks
    3. Apply de-muffling EQ
    4. Normalize audio levels
    """
    print("Enhancing audio quality...")
    
    # Convert to float for processing (-1.0 to 1.0 range)
    audio_float = (audio.astype(np.float32) - 128) / 128.0
    
    # 1. Dynamic range compression (flatten peaks)
    print("Applying dynamic range compression...")
    # Threshold above which compression is applied
    threshold = 0.5
    # Ratio determines how much compression (higher = more compression)
    ratio = 4.0
    # Apply compression
    audio_compressed = np.copy(audio_float)
    mask = np.abs(audio_float) > threshold
    audio_compressed[mask] = np.sign(audio_float[mask]) * (
        threshold + (np.abs(audio_float[mask]) - threshold) / ratio
    )
    
    # 2. De-muffling EQ (boost high frequencies)
    print("Applying de-muffling EQ...")
    # Design a high-shelf filter to boost high frequencies
    # This helps counteract the muffling effect
    try:
        # Create a high-shelf filter to boost frequencies above 1000 Hz
        b, a = signal.butter(2, 1000/(SAMPLE_RATE/2), btype='high', analog=False)
        # Apply the filter
        audio_eq = signal.lfilter(b, a, audio_compressed)
        
        # Mix the original and EQ'd audio (70% EQ'd, 30% original)
        audio_eq = 0.7 * audio_eq + 0.3 * audio_compressed
    except Exception as e:
        print(f"EQ processing error: {e}")
        audio_eq = audio_compressed  # Fallback to compressed audio if EQ fails
    
    # 3. Noise gate to reduce background noise
    noise_threshold = 0.05
    gate_mask = np.abs(audio_eq) < noise_threshold
    audio_eq[gate_mask] *= 0.5  # Reduce noise by 50%
    
    # 4. Final normalization to use full dynamic range
    max_val = np.max(np.abs(audio_eq))
    if max_val > 0:  # Avoid division by zero
        audio_eq = audio_eq / max_val * 0.95  # Leave a little headroom
    
    # Convert back to uint8 range (0-255)
    audio_enhanced = np.clip(audio_eq * 127 + 128, 0, 255).astype(np.uint8)
    
    return audio_enhanced

def save_wav(audio_data, filename, sample_rate):
    """Save audio data as a WAV file"""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)               # mono
        wf.setsampwidth(1)               # 8-bit
        wf.setframerate(sample_rate)     # 5 kHz
        wf.writeframes(audio_data.tobytes())
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Saved WAV: {filename} at {timestamp}")

if __name__ == '__main__':
    try:
        # Check if scipy is installed
        import scipy
        record_and_process()
    except ImportError:
        print("This script requires scipy. Installing...")
        import subprocess
        try:
            subprocess.check_call(['pip', 'install', 'scipy'])
            print("scipy installed successfully. Running script...")
            import scipy.signal as signal
            from scipy.io import wavfile
            record_and_process()
        except Exception as e:
            print(f"Error installing scipy: {e}")
            print("Please install scipy manually with: pip install scipy")
            print("Then run this script again.")