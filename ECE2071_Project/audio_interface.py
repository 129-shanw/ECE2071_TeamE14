import numpy as np
import wave
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt

class Menu():
    def __init__(self):
        self.current_mode = None
        self.current_format = None
        self.record_length = 0
        self.SAMPLE_RATE = 5000;

        self.menu_options = ["Mode Select", "Format Select","Change Recording Length"]
        self.menu_functions = [self.mode_select, self.format_select, self.set_record_len]

        self.modes = ["Manual Recording Mode", "Distance Trigger Mode"]
        self.mode_func = [self.manual_record_menu, self.distance_trig_menu]
        self.formats = [".wav",".png",".csv"]

        self.manual_options = ["Start Recording","Back to Main menu"]
        self.manual_functions = [self.record_audio, self.main_menu]

        self.dist_trig_options = ["Active Distance Trigger Mode", "Back to Main menu"]
        self.dist_trig_functions = [self.record_audio(), self.main_menu]

        self.ser = None
        self.audio_data = []


    def default(self):
        self.current_format = self.formats[0] #default to .wav
        self.record_length = 60
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
        self.ser = serial.Serial(stm, 115200)

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
            for _ in range(0, self.record_length*self.SAMPLE_RATE):
                byte = self.ser.read(1)
                self.audio_data.append(byte[0])
            self.save_recording()

        elif self.current_mode == self.modes[1]: #distance trig mode
            zero_count = 0
            self.ser.read() #will block until it starts reading actual data
            while True:
                in_range = self.ser.read(1)[0] #check in data is valid (was ultrasonic in range)
                print(in_range)
                #byte = self.ser.read(1024) #read the data after the range check

                if in_range == 1: #in range
                    pass
                    #self.audio_data.append(byte[0]) #append data to list

                elif in_range == 0: #out of range
                    zero_count += 1
                    #do nothing with the data
                    if zero_count == 100:
                        while True:
                            keep_going = input("\nOut of Range: Would you like to save the recording (Y/N): ")
                            if keep_going == "Y" or keep_going == "y":
                                self.save_recording()
                                return
                            elif keep_going == "N" or keep_going == "n":
                                zero_count = 0
                                self.audio_data.clear() #delete all current data
                                self.ser.reset_input_buffer() #
                                break
                            else:
                                print("Invalid Input")
                                pass

        print("Recording Saved!")

    def save_recording(self):
        if len(self.audio_data) != 0:
            if self.current_format == self.formats[0]: #.wav
                data = np.array(self.audio_data)
                data = (data - data.min()) / data.max()
                data = data * 255
                data = data.astype(np.uint8)
                with wave.open(f"music_file.wav", 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(1)
                    wav_file.setframerate(self.SAMPLE_RATE)
                    wav_file.writeframes(data.tobytes())

            elif self.current_format == self.formats[1]: #.png
                time_axis = np.arange(len(self.audio_data)) / self.SAMPLE_RATE
                plt.figure(figsize=(12, 4))
                plt.plot(time_axis, self.audio_data, color='blue')
                plt.title("Filtered ADC Waveform (16-bit Depth)")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude (16-bit)")
                plt.grid(True)
                plt.tight_layout()
                plt.savefig("waveform_filtered.png")
                plt.close()
                print("Saved: waveform_filtered.png")
                
            elif self.current_format == self.formats[2]: #.csv
        else:
            print("no data :(")
if __name__ == "__main__":
    menu1 = Menu()
    menu1.initate_stm_con()
    menu1.default()