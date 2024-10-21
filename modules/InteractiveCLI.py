from ftd2xx.ftd2xx import DeviceInfoDetail
from .FTDIOperations import FTDIOperations, FTDIOperationType
from sys import exit

class InteractiveCLI:
    def __init__(self, op : FTDIOperations):
        self.op = op

    # Run the interactive command line interface
    def run(self):
        print("FTDI EEPROM Cloner Utility")
        print("==========================")

        while True:
            # Run the operation chain
            self.op.execute(lambda : self.select_operation(),
                            lambda devices : self.select_device(devices),
                            lambda p : self.select_file(p),
                            lambda p : self.confirm(p))

    # Print the devices currently connected to the computer
    def print_connected_devices(self, devices : list[DeviceInfoDetail]) -> None:
        if len(devices) < 1:
            print("No FTDI devices found.")
        else:
            print("\nConnected FTDI devices:\n")
            print(f"  {'Index'.ljust(8)}{'Description'.ljust(32)}{'VID'.ljust(8)}{'PID'.ljust(8)}{'Serial number'.ljust(15)}")

            for i in range(len(devices)):
                description = devices[i]['description'].decode()
                id = devices[i]['id']
                vid = (f"{id >> 16 : #04x}").strip()
                pid = (f"{id & 0xFFFF : #04x}").strip()
                serial_number = devices[i]['serial'].decode()
                if serial_number == None:
                    serial_number = "<None>"

                print(f"  {i : <8}{description : <32}{vid : <8}{pid : <8}{serial_number : <10}")
    
    # Callback returning an DeviceInfoDetail, requests input from the user
    def select_device(self, devices : list[DeviceInfoDetail]) -> DeviceInfoDetail:
        selected_device = None
        self.print_connected_devices(devices)

        while(selected_device is None):
            print("\nSelect index of target device, (r)efresh (q)uit:")
            user_input = input()
            if user_input.lower() == 'q':
                print("Exiting...")
                exit()
            if user_input.lower() == 'r':
                return None

            try:
                user_input_int = int(user_input, 0)
                if user_input_int >= 0 and user_input_int < len(devices):
                    selected_device = devices[user_input_int]
                else:
                    print("Please select a valid device index.")
            except:
                print("Not a valid number.")
        return selected_device
    
    # Callback returning an FTDIOperationType, requests input from the user
    def select_operation(self) -> FTDIOperationType:
        selected_operation = None
        while(selected_operation is None):
            print("\nSelect operation on device:")
            print("  (R)ead EEPROM contents of device")
            print("  (W)rite EEPROM contents of device")
            print("  (E)rase EEPROM contents of device")
            print("  (Q)uit program")
            user_input = input().strip().lower()
            if user_input == 'r' or user_input == 'w' or user_input == 'e' or user_input == 'q':
                selected_operation = FTDIOperationType(user_input)
            else:
                print("Please select a valid option.")
        return selected_operation
    
    # Callback returning a file path, requests input from the user
    def select_file(self, prompt : str) -> str:
        print(prompt)
        print("Path:")
        user_input = input().strip()
        return (user_input != '', user_input) # allow retry if not an empty string, and return user input
    
    # Callback returning a bool to confirm or reject a request from the program
    def confirm(self, prompt : str) -> bool:
        print(prompt)
        print("Continue? (y)es or (n)o:")
        response = None
        while response is None:
            user_input = input().strip().lower()
            if user_input == 'y' or user_input == 'yes':
                response = True
            elif user_input == 'n' or user_input == 'no':
                response = False
            else:
                print("Please enter y, yes, n or no:")
        return response