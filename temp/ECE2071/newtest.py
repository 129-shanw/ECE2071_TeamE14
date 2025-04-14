import serial
import serial.tools.list_ports
import time

BAUD_RATE = 115200

# Find STM32 COM port
devices = serial.tools.list_ports.comports()
STM_device = None
for device in devices:
    if "STMicroelectronics STLink Virtual COM Port" in device.description:
        STM_device = device.device

if STM_device is None:
    raise Exception("STM32 device not found.")

ser = serial.Serial(STM_device, BAUD_RATE, timeout=1)
print(f"Connected to: {STM_device}")

# Step 1: Flush with '\0' until we get a non-empty response
print("Flushing with \\0...")
while True:
    ser.write(b'\x00')  # send null byte
    ser.flush()
    time.sleep(0.05)  # wait briefly
    response = ser.readline()
    if response:
        print(f"Received during flush: {response.decode(errors='ignore')}")
        break

# Step 2: Send your actual message
data_send = "ZBCDEFGHIJKLMNOPQRSTUVWXYZ123456"
ser.write(data_send.encode())
ser.flush()
print(f"Sent actual message: {data_send}")

# Step 3: Receive response
data_receive = ser.readline()
print(f"Received raw: {data_receive}")
print(f"Received decoded: {data_receive.decode(errors='ignore')}")

ser.close()
