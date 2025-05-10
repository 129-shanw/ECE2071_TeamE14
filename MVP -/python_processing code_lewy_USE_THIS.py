"""
Audio Capture Script for STM32 Dual Audio Processing System

This script receives processed audio samples from the Processing STM32 via
UART and saves them as a WAV file.
"""

import serial
import numpy as np
import wave
import struct
import time

# Configuration
SERIAL_PORT = 'COM3'  # Update with your serial port (e.g., '/dev/ttyUSB0' for Linux)
BAUD_RATE = 115200
SAMPLE_RATE = 5000  # 5 kHz sampling rate
BIT_DEPTH = 8       # 8-bit audio samples
RECORD_DURATION = 5  # Recording duration in seconds (hard-coded)
OUTPUT_FILENAME = 'recorded_audio.wav'

def main():
    # Calculate total samples based on duration and sample rate
    total_samples = int(RECORD_DURATION * SAMPLE_RATE)
    
    # Create buffer to store samples
    audio_buffer = np.zeros(total_samples, dtype=np.uint8)
    
    try:
        # Open serial connection
        print(f"Opening serial port {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print(f"Starting audio capture for {RECORD_DURATION} seconds...")
        start_time = time.time()
        
        # Read samples from serial port
        for i in range(total_samples):
            # Read one byte (8-bit sample)
            sample = ser.read(1)
            if sample:
                # Convert to integer and store in buffer
                audio_buffer[i] = struct.unpack('B', sample)[0]
            
            # Optional progress reporting
            if i % 500 == 0:
                elapsed = time.time() - start_time
                percentage = (i / total_samples) * 100
                print(f"Progress: {percentage:.1f}% ({elapsed:.1f}s)")
        
        # Close serial connection
        ser.close()
        
        # Convert 8-bit unsigned samples to proper format for WAV file
        # Remap from [0, 255] to [-128, 127] for 8-bit PCM
        audio_data = audio_buffer.astype(np.uint8)
        
        # Save as WAV file
        print(f"Saving audio to {OUTPUT_FILENAME}...")
        with wave.open(OUTPUT_FILENAME, 'wb') as wav_file:
            # Configure WAV file parameters
            wav_file.setnchannels(1)               # Mono
            wav_file.setsampwidth(1)               # 1 byte = 8 bits
            wav_file.setframerate(SAMPLE_RATE)     # Sample rate
            
            # Write raw audio data
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"Audio recording complete! Saved to {OUTPUT_FILENAME}")
        print(f"- Duration: {RECORD_DURATION} seconds")
        print(f"- Sample rate: {SAMPLE_RATE} Hz")
        print(f"- Bit depth: {BIT_DEPTH} bits")
        
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()