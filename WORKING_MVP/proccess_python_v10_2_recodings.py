import numpy as np
import wave
import serial
import time

# Configuration
SAMPLE_RATE = 5000
PORT = 'COM3'
BAUD_RATE = 115200

def record_and_process():
    try:
        # Open serial port and record 10 seconds
        print(f"Recording 10 seconds from {PORT}...")
        ser = serial.Serial(PORT, BAUD_RATE, timeout=None)
        ser.reset_input_buffer()
        
        # Record data
        data = bytearray()
        target_bytes = SAMPLE_RATE * 10
        start_time = time.time()
        
        while len(data) < target_bytes:
            chunk = ser.read(min(1000, target_bytes - len(data)))
            if chunk:
                data.extend(chunk)
            if time.time() - start_time > 15:  # 15 second timeout
                break
                
        ser.close()
        print(f"Recorded {len(data)} samples in {time.time() - start_time:.1f} seconds")
        
        # Ensure we have exactly 10 seconds of audio
        if len(data) < target_bytes:
            data.extend([128] * (target_bytes - len(data)))
        elif len(data) > target_bytes:
            data = data[:target_bytes]
            
        # Process audio
        audio = np.frombuffer(data, dtype=np.uint8)
        processed = enhance_audio(audio)
        
        # Save 10-second version
        with wave.open('audio_10s.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(processed.tobytes())
        print("Saved 10-second recording: audio_10s.wav")
        
        # Save 5-second version (middle portion)
        middle = processed[SAMPLE_RATE*2:SAMPLE_RATE*7]
        with wave.open('audio_5s.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(middle.tobytes())
        print("Saved 5-second recording: audio_5s.wav")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Generating test audio instead...")
        
        # Generate test audio (sine wave)
        t = np.linspace(0, 10, SAMPLE_RATE*10)
        audio = (np.sin(2*np.pi*440*t) * 64 + 128).astype(np.uint8)
        processed = enhance_audio(audio)
        
        # Save test files
        with wave.open('test_audio_10s.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(processed.tobytes())
        print("Saved test audio: test_audio_10s.wav")
        
        with wave.open('test_audio_5s.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(processed[SAMPLE_RATE*2:SAMPLE_RATE*7].tobytes())
        print("Saved test audio: test_audio_5s.wav")

def enhance_audio(audio):
    """Enhanced audio processing with better de-muffling"""
    # Convert to float (-1 to 1 range)
    audio_float = (audio.astype(np.float32) - 128) / 128.0
    
    # 1. Flatten peaks (vectorized)
    threshold = 0.5
    mask = np.abs(audio_float) > threshold
    excess = np.abs(audio_float[mask]) - threshold
    audio_float[mask] = np.sign(audio_float[mask]) * (threshold + excess * 0.25)
    
    # 2. Enhanced de-muffling (stronger high frequency boost)
    # First-order difference (high-pass filter)
    diff1 = np.diff(audio_float, prepend=audio_float[0])
    # Second-order difference (emphasizes higher frequencies)
    diff2 = np.diff(diff1, prepend=diff1[0])
    
    # Apply both filters with careful weighting
    audio_boosted = audio_float + diff1 * 0.4 + diff2 * 0.1
    
    # 3. Normalize
    max_val = np.max(np.abs(audio_boosted))
    if max_val > 0:
        audio_boosted = audio_boosted / max_val * 0.95
    
    # Convert back to uint8
    return np.clip(audio_boosted * 127 + 128, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    record_and_process()