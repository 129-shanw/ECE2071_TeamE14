# ADC Audio Sampling Project

This project demonstrates how to sample audio data using the STM32L432KC microcontroller's ADC and transmit it over UART to a Python script for saving as a WAV file.

## Hardware Setup

### Components Required
- STM32L432KC Nucleo board
- 3.5mm TRRS aux jack
- 2x 10kΩ resistors
- 1x 0.1μF capacitor
- Breadboard and jumper wires

### Biasing Circuit
The audio signal from a 3.5mm aux jack typically ranges from -150mV to +150mV, which is outside the ADC's input range (0V to 3.3V). We need to bias this signal to center it around 1.65V.

Build the following circuit on your breadboard:
1. Connect the tip (left audio channel) of the 3.5mm jack to one end of the 0.1μF capacitor
2. Connect the other end of the capacitor to the ADC input pin (PA0)
3. Create a voltage divider with two 10kΩ resistors between 3.3V and GND
4. Connect the midpoint of the voltage divider (1.65V) to the ADC input pin (PA0)
5. Connect the sleeve (ground) of the 3.5mm jack to the STM32's GND

This circuit will bias the audio signal to be centered around 1.65V, making it suitable for the ADC input range.

## Software Setup

### STM32 Configuration
1. Create a new project in STM32CubeIDE
2. Configure the ADC1 with 8-bit resolution
3. Configure USART2 with 115200 baud rate
4. Configure the ADC input pin (PA0) as analog input

### Python Script
The Python script (`test_mvp.py`) reads the audio samples from the UART connection and saves them as a WAV file.

## How to Use
1. Build and flash the STM32 code to your Nucleo board
2. Connect the 3.5mm aux jack to an audio source (phone, computer, etc.)
3. Run the Python script with the correct COM port:
   ```
   python test_mvp.py
   ```
4. The script will record audio for 5 seconds and save it as `audio_recording.wav`
5. You can play back the recorded audio using any media player

## Troubleshooting
- If you don't hear any audio in the recording, check your biasing circuit connections
- If the Python script can't connect to the COM port, make sure you've specified the correct port
- If the audio is distorted, try adjusting the volume of your audio source

## Notes
- The sample rate is set to 5000 Hz in the Python script
- The ADC is configured for 8-bit resolution, giving values from 0 to 255
- The UART is configured for 115200 baud rate, which is sufficient for the 5000 Hz sample rate