import numpy as np
import wave
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import csv
from scipy.signal import butter, filtfilt

class Menu():
    def __init__(self):
        self.current_mode = None
        self.current_format = None
        self.record_length = 0
        self.SAMPLE_RATE = 44100
        self.BAUD_RATE = 921600
        self.zero_count_end = 100
        self.ser = None
        self.start_bit_1 = 255
        self.start_bit_2 = 255
        self.buffer_size = 512

        self.menu_options = ["Mode Select", "Format Select","Change Recording Length"]
        self.menu_functions = [self.mode_select, self.format_select, self.set_record_len]

        self.modes = ["Manual Recording Mode", "Distance Trigger Mode"]
        self.mode_func = [self.manual_record_menu, self.distance_trig_menu]
        self.formats = [".wav",".png",".csv"]

        self.manual_options = ["Start Recording","Back to Main menu"]
        self.manual_functions = [self.record_audio, self.main_menu]

        self.dist_trig_options = ["Active Distance Trigger Mode", "Back to Main menu"]
        self.dist_trig_functions = [self.record_audio, self.main_menu]

        
        self.unprocessed_audio_data = []
        self.processed_audio_data = []
        self.filtered_data = []

    def default(self):
        self.current_format = self.formats[0] #default to .wav
        self.record_length = 5
        self.main_menu()

    def main_menu(self):
        
        print("---------- MAIN MENU ----------")
        for i in range(0,len(self.menu_options)):
            print(f"{i+1}. {self.menu_options[i]}")
        option = int(input("Select an option: "))
        print("")

        try:
            self.menu_functions[int(option)-1]()
        except IndexError:
            print("Invalid Option")
            self.main_menu()

    def initate_stm_con(self):
        devices = serial.tools.list_ports.comports()

        for device in devices:
            print(device.device)
            if "STM" in str(device):
                stm = device.device
        self.ser = serial.Serial(stm, self.BAUD_RATE)

    def distance_trig_menu(self):
        print("---------- DISTANCE TRIGGER MODE ----------")
        
        for i in range(0, len(self.dist_trig_options)):
            print(f"{i+1}. {self.dist_trig_options[i]}")

        choice = int(input("Please Select an option: "))
        try:
            self.dist_trig_functions[choice-1]()
        except IndexError:
            print("Invalid Choice")
            self.distance_trig_menu()

    def manual_record_menu(self):
        print("---------- MANUAL RECORDING MODE ----------")
        print(f"Current Format: {self.current_format}")
        print(f"Current Recording Length: {self.record_length}")

        for i in range(0, len(self.manual_options)):
            print(f"{i+1}. {self.manual_options[i]}")

        choice = int(input("Please Select an option: "))
        try:
            self.manual_functions[choice-1]()
        except IndexError:
            print("Invalid Choice")
            self.manual_record_menu()
 
    def set_record_len(self):
        print("---------- RECORDING LENGTH ADJUST ----------")
        print(f"Current Length: {self.record_length} seconds")
        length = int(input("How long would you like to record for (secs): "))
        self.record_length = length
        print(f"\nRecording length changed to {self.record_length} seconds")

        self.main_menu()

    def mode_select(self):
        print("---------- MODE SELECT -----------")
        for i in range(0,len(self.modes)):
            print(f"{i+1}. {self.modes[i]}")
        mode = int(input("Please Select a Mode: "))
        
        try:
            self.current_mode = self.modes[mode-1]
            self.mode_func[mode-1]()
        except IndexError:
            print("Invalid Choice")
            self.mode_select()
            
    def format_select(self):
        print("---------- FORMAT SELECT -----------")
        print(f"Current Format: {self.current_format}")
        for i in range(0,len(self.formats)):
            print(f"{i+1}. {self.formats[i]}")
        format = int(input("Please Select a Format: "))
        
        try:
            self.current_format = self.formats[format-1]
            print(f"\nFormat Changed to {self.current_format}")
        except IndexError:
            print("Invalid Input")
            self.format_select()

        self.main_menu()

    def record_audio(self):
        if self.current_mode == self.modes[0]: #manual recording
            for _ in range(0, int(self.record_length*self.SAMPLE_RATE/self.buffer_size*2.1)):
                while True:
                    start1 = self.ser.read(1)[0]
                    if start1 == self.start_bit_1:
                        start2 = self.ser.read(1)[0]
                        if start2 == self.start_bit_2:
                            self.ser.read(2) #read in the in_range bi1t
                            buffer = self.ser.read(self.buffer_size)
                            self.unprocessed_audio_data.extend(buffer)
                            break

            self.save_all()

        elif self.current_mode == self.modes[1]: #distance trig mode
            one_count = 0
            zero_count = 0
            first_activation = True
            self.ser.reset_input_buffer()
            while True:
                start1 = self.ser.read(1)[0]
                if start1 == self.start_bit_1:
                    start2 = self.ser.read(1)[0]
                    if start2 == self.start_bit_2:
                        in_range = self.ser.read(1)[0] #check if data is valid (was ultrasonic in range)
                        self.ser.read(1)
                        buffer = self.ser.read(self.buffer_size) #read the data after the range check

                        if in_range == 1: #in range
                            if one_count >= 75:
                                first_activation = False
                                self.unprocessed_audio_data.extend(buffer) #append data to list
                            else:
                                one_count += 1
                            
                        elif in_range == 0: #out of range
                            if first_activation == False:
                                zero_count += 1
                                self.unprocessed_audio_data.extend(buffer)
                                if zero_count == self.zero_count_end:
                                    while True:
                                        keep_going = input("\nOut of Range: Would you like to save the recording (Y/N): ")
                                        if keep_going == "Y" or keep_going == "y":
                                            self.save_all()
                                            return
                                        elif keep_going == "N" or keep_going == "n":
                                            zero_count = 0
                                            one_count = 0
                                            first_activation = True
                                            self.unprocessed_audio_data.clear() #delete all current data
                                            self.ser.reset_input_buffer() #
                                            break
                                        else:
                                            print("Invalid Input")
                                            pass

        print("Recording Saved!")

    def __process_raw_data(self):
        # Convert the received data to 12-bit values
        data = np.array(self.unprocessed_audio_data, dtype=np.uint8)
        # Reconstruct 12-bit values from the 16-bit chunks (LSB + MSB)
        for i in range(0, len(data), 2):  # Process two bytes (16 bits) per sample
            lsb = int(data[i])
            msb = int(data[i+1])
            # Combine the LSB and MSB to get a 12-bit sample (only lower 12 bits)
            sample = ((msb & 0x0F) << 8) | lsb  # The 4 MSB bits are discarded
            self.processed_audio_data.append(sample)
        self.processed_audio_data = np.array(self.processed_audio_data)

    def butter_filter(self, data, lowcut, highcut, sample_rate, filter_type="bandpass", order=5):
        nyquist = 0.5 * sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype=filter_type, analog=False)
        return filtfilt(b, a, data)

    def save_all(self):
        self.__process_raw_data()

        if len(self.processed_audio_data) != 0:
            samples = self.processed_audio_data
            samples = (samples - samples.min()) / (samples.max() - samples.min())
            samples = samples * 65535
            samples = samples.astype(np.uint16)
            self.processed_audio_data = samples
            self.filtered_data = self.butter_filter(self.processed_audio_data, 20, 20000, self.SAMPLE_RATE, filter_type="bandpass")
            with wave.open("E14_44_1ksps.wav", 'wb') as wav_file:
                wav_file.setnchannels(1)       # Mono audio
                wav_file.setsampwidth(2)       # 16-bit depth = 2 bytes
                wav_file.setframerate(self.SAMPLE_RATE)
                wav_file.writeframes(self.filtered_data.astype(np.uint16).tobytes())
            print("Saved as E14_44_1ksps.wav")

        
            time_axis = np.arange(len(self.filtered_data)) / self.SAMPLE_RATE
            plt.figure(figsize=(12, 4))
            plt.plot(time_axis, self.filtered_data, color='blue')
            plt.title("Filtered ADC Waveform (16-bit Depth)")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude (16-bit)")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig("E14_44_1ksps.png")
            plt.close()
            print("Saved as: E14_44_1ksps.png")

            # Save raw signal as .npy for later filtering
            np.save("filtered_signal16bit.npy", self.filtered_data)

            with open("E14_44_1ksps.csv", mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Sample Index", "16-bit Value"])
                for i, sample in enumerate(self.processed_audio_data):
                    writer.writerow([i, sample])
            print("Saved: E14_44_1ksps.csv")

        else:
            print("no data :(")
        
        self.__clear_data()

    def save_recording(self):
        self.__process_raw_data()

        if len(self.processed_audio_data) != 0:
            if self.current_format == self.formats[0]: #.wav
                samples = self.processed_audio_data
                samples = (samples - samples.min()) / (samples.max() - samples.min())
                samples = samples * 65535
                samples = samples.astype(np.uint16)
                self.processed_audio_data = samples
                self.filtered_data = self.butter_filter(self.processed_audio_data, 30, 10000, self.SAMPLE_RATE, filter_type="bandpass")
                with wave.open("E14_44_1ksps.wav", 'wb') as wav_file:
                    wav_file.setnchannels(1)       # Mono audio
                    wav_file.setsampwidth(2)       # 16-bit depth = 2 bytes
                    wav_file.setframerate(self.SAMPLE_RATE)
                    wav_file.writeframes(self.filtered_data.astype(np.uint16).tobytes())
                print("Saved as: E14_44_1ksps.wav")

            elif self.current_format == self.formats[1]: #.png
                samples = self.processed_audio_data
                samples = (samples - samples.min()) / (samples.max() - samples.min())
                samples = samples * 65535
                samples = samples.astype(np.uint16)
                self.processed_audio_data = samples
                self.filtered_data = self.butter_filter(self.processed_audio_data, 30, 10000, self.SAMPLE_RATE, filter_type="bandpass")
                time_axis = np.arange(len(self.filtered_data)) / self.SAMPLE_RATE
                plt.figure(figsize=(12, 4))
                plt.plot(time_axis, self.filtered_data, color='blue')
                plt.title("Filtered ADC Waveform (16-bit Depth)")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude (16-bit)")
                plt.grid(True)
                plt.tight_layout()
                plt.savefig("E14_44_1ksps.png")
                plt.close()
                print("Saved: E14_44_1ksps.png")

                # Save raw signal as .npy for later filtering
                np.save("filtered_signal16bit.npy", self.filtered_data)

            elif self.current_format == self.formats[2]: #.csv
                with open("E14_44_1ksps.csv", mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["Sample Index", "16-bit Value"])
                    for i, sample in enumerate(self.processed_audio_data):
                        writer.writerow([i, sample])
                print("Saved: E14_44_1ksps.csv")

        else:
            print("no data :(")
        
        self.__clear_data()

    def __clear_data(self):
        self.unprocessed_audio_data = []
        self.processed_audio_data = []
        self.filtered_data = []

if __name__ == "__main__":
    menu1 = Menu()
    menu1.initate_stm_con()
    menu1.default()