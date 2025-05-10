import numpy as np
import wave
import serial
import serial.tools.list_ports
import time

def initate_stm_con():
    devices = serial.tools.list_ports.comports()

    for device in devices:
        print(device.device)
        if "STM" in str(device):
            stm = device.device

    ser = serial.Serial(stm, 115200,timeout=100)

    return ser

if __name__ == "__main__":
    ser = initate_stm_con()
    ser.reset_input_buffer()
    while True:
        #start = ser.read(1)
        #length = ser.read(1)
        in_range = ser.read(1)
        #data = ser.read(1)
        print(in_range[0])
        #print(start,length,in_range,data)

        