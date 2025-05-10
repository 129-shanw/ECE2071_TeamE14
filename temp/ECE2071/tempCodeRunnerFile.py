import numpy as np
import serial.tools.list_ports
import wave
import serial
import matplotlib.pyplot as plt
import time

data = []

BAUD_RATE = 115200
SAMPLE_RATE = 5000
TIME_RANGE = 10