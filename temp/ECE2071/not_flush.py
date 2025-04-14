import serial
import serial.tools.list_ports
import time

BAUD_RATE = 115200

devices = serial.tools.list_ports.comports()
for device in devices:
    # print(device.description) 
    if "STMicroelectronics STLink Virtual COM Port (COM3)" in device.description:
        STM_device = device.device

ser = serial.Serial(STM_device, BAUD_RATE, timeout = 1)
print(f"Connected to: {STM_device}")

data_send = input("Enter the data to send: ")
ser.write(data_send.encode().ljust(128, b'\0'))
time.sleep(1) # Give time for data to transmit

data_receive = ser.readline()

print(f"Received decoded: {data_receive.decode(errors='ignore')}") 

ser.close()