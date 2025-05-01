import numpy as np
import wave
import serial
import serial.tools.list_ports

class Menu():
    def __init__(self):
        self.current_mode = None
        self.current_format = None
        self.record_length = 0
        self.sample_rate = 5000;

        self.default_options = ["Mode Select"]
        self.default_functions = [self.mode_select]

        self.modes = ["Manual Recording Mode", "Distance Trigger Mode"]
        self.mode_func = [self.manual_record_menu, self.distance_trig_menu]
        self.formats = [".wav",".png",".csv"]

        self.manual_options = ["Start Recording", "Change Recording Length", "Format Select","Back to Main menu"]
        self.manual_functions = [self.record_audio, self.set_record_len, self.format_select, self.default]

        self.ser = None
        self.audio_data = []


    def default(self):
        print("---------- MAIN MENU ----------")
        for i in range(0,len(self.default_options)):
            print(f"{i+1}. {self.default_options[i]}")
        option = int(input("Select an option: "))
        print("")

        try:
            self.default_functions[option-1]()
        except IndexError:
            print("Invalid Option")
            self.default()

    def initate_stm_con(self):
        devices = serial.tools.list_ports.comports()

        for device in devices:
            print(device.device)
            if "STM" in str(device):
                stm = device.device
        self.ser = serial.Serial(stm, 115200)

    def activate_dist_trig(self):
        self.ser.write("data") #DEFINE A MESSAGE TO SEND TO THE PROCESSING STM

    def deactivate_dist_trig(self):
        self.ser.write("data") #DEFINE A MESSAGE TO SEND TO THE PROCESSING STM

    def distance_trig_menu(self):
        print("---------- DISTANCE TRIGGER MODE ----------")
        self.activate_dist_trig()
        self.record_audio()
        
        raise NotImplementedError

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
        length = int(input("How long would you like to record for (secs): "))
        print(f"\nRecording length change to {self.record_length}")

        self.record_length = length
        print
        
        if self.current_mode == "Manual Recording Mode":
            self.manual_record_menu()
        elif self.current_mode == "Distance Trigger Mode":
            self.distance_trig_menu()

    def mode_select(self):
        print("---------- MODE SELECT -----------")
        print(f"Current Mode: {self.current_mode}")
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
        print(f"\nFormat Changed to {self.current_format}")

        try:
            self.current_format = self.formats[format-1]
        except IndexError:
            print("Invalid Input")
            self.format_select()

        if self.current_mode == "Manual Recording Mode":
            self.manual_record_menu()
        elif self.current_mode == "Distance Trigger Mode":
            self.distance_trig_menu()

    def record_audio(self):
        if self.current_mode == self.modes[0]: #manual recording
            for _ in range(0, self.record_length*self.sample_rate):
                byte = self.ser.read(1)
                self.audio_data.append(byte[0])
            self.save_recording()

        elif self.current_mode == self.modes[1]:
            while True:
                byte = self.ser.read(1)
                self.audio_data.append(byte[0])



    def save_recording(self):
        with wave.open(f"music_file{self.current_format}", 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(self.audio_data.tobytes())
    
if __name__ == "__main__":
    menu1 = Menu()
    menu1.initate_stm_con()
    menu1.default()