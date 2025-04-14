import serial
import serial.tools.list_ports

BAUD_RATE = 115200
NUM_OF_DATA_POINTS = 9

#Serial port
devices = serial.tools.list_ports.comports()
for device in devices:
    print(device.description)
    if (device.description == "STM32 STLink"):
        STM_device = device.device

ser = serial.Serial(STM_device, BAUD_RATE)  

# # Send message
data_send = "E"
# data_send = input("Enter data: ")
# ser.write(data_send.encode())  
# print(f"Sent request: {data_send}")

# Receive message 
# data_receive = ser.readline().decode()
# print(f"Received: {data_receive}")

# Receive set number of data points and write into file
file = "data.txt"
f = open("data.txt", "w")
for i  in range(NUM_OF_DATA_POINTS):
    ser.write(data_send.encode()) 
    data_receive = ser.readline().decode()
    f.write(data_receive)

# f = open("data.txt", "w")
# ser.write(data_send.encode()) 
# data_receive = ser.readline().decode()
# f.write(data_receive)

# Close
f.close()
ser.close()
