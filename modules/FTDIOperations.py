import ftd2xx as ftdi
from ftd2xx.ftd2xx import DeviceInfoDetail
from typing import Callable
import os
from hexdump import hexdump
from sys import exit
import ctypes as c
import time

# List of supported devices and their EEPROM size
FTDIDeviceTypes = {
    0:  [  "FT232BM"    , 256],
    1:  [  "FT232AM"    , 0] ,
    4:  [  "FT2232C/D"  , 256],
    5:  [  "FT232R"     , 128],
    6:  [  "FT2232H"    , 256],
    7:  [  "FT4232H"    , 256],
    8:  [  "FT232H"     , 256],
    9:  [  "FTX_SERIES" , 1024], 
    19: [  "FT2232HP"   , 256], 
    20: [  "FT4232HP"   , 256], 
    22: [  "FT232HP"    , 256], 
    23: [  "FT2232HA"   , 256], 
    24: [  "FT4232HA"   , 256],
}     

# Representation of an operation type
class FTDIOperationType:
    def __init__(self, type : str):
        self.type = type
    def is_write(self):
        return self.type == 'w'
    def is_read(self):
        return self.type == 'r'
    def is_erase(self):
        return self.type == 'e'
    def is_quit(self):
        return self.type == 'q'

# Class implementing the actual calls to the D2XX library. Implements read, write and erase operations.
class FTDIOperations:
    def __init__(self, verbose : bool = True):
        self.verbose = verbose
    
    # Execute a single operation (fetch device selection, operation selection and file selection, then execute)
    # Note that the callbacks are injected, so this function can be used to make the program either interactive or argument-based (batch mode)
    def execute(self, 
                operationFunc : Callable[[], FTDIOperationType], 
                deviceFunc : Callable[[list[DeviceInfoDetail]], DeviceInfoDetail],
                fileFunc : Callable[[str], tuple[bool, str]],
                confirmFunc : Callable[[str], bool]
                ):
        # Request which FTDI to use from the user
        device = None
        while device is None:
            num_devices = ftdi.createDeviceInfoList() # Create the list of available FTDI devices
            if num_devices < 1:
                print("No devices connected. Exiting...")
                exit(-1)
            devices : list[DeviceInfoDetail] = []
            for i in range(num_devices):
                devices.append(ftdi.getDeviceInfoDetail(i, update=False))
            device = deviceFunc(devices)

        # Request the operation from the user and execute it
        operation = operationFunc()
        if operation.is_quit():
            # No operation
            print("Exiting...")
            exit()

        elif operation.is_read():
            # Do read
            read_file = None
            while read_file is None:
                (can_retry, file) = fileFunc("Specify target binary file on disk.")
                if file != '' and file != None:
                    read_file = file
            
            confirmed = True
            if os.path.isfile(file):
                confirmed = confirmFunc(f"WARNING: A file already exists at {file} and will be overwritten.")
            if confirmed:        
                self.read_eeprom(device, read_file)
            else:
                if self.verbose:
                    print("Read operation aborted.")
                
        elif operation.is_write():
            # Do write
            write_file = None
            while write_file is None:
                (can_retry, file) = fileFunc("Specify source binary file on disk.")
                if not os.path.isfile(file):
                    print("Invalid source file.\n")
                    if not can_retry:
                        print("Exiting...")
                        exit(-1)
                else:
                    write_file = file
            confirmed = confirmFunc(f"CAUTION: Writing an invalid EEPROM file can cause enumeration failures and hence brick the device!\nBy proceeding, the EEPROM contents will be overwritten with the data of the file located at\n{os.path.abspath(write_file)}")
            if confirmed:
                self.write_eeprom(device, write_file)
            else:
                if self.verbose:
                    print("Write operation aborted.")

        elif operation.is_erase():
            # Do erase
            confirmed = confirmFunc(f"NOTE: Erasing the EEPROM will reset the device to all of its default settings (including serial number and port functions).")
            if confirmed:
                self.erase_eeprom(device)
            else:
                if self.verbose:
                    print("Erase operation aborted")

        if self.verbose:
            print('\nDone. Ready for next operation...')

    # Write the EEPROM of the passed device based on the contents of a given file
    def write_eeprom(self, device_info : DeviceInfoDetail, file : str):
        with open(file, 'rb') as bin:
            # Open the selected FTDI device
            device = ftdi.open(device_info["index"])
            if device == None:
                print('Cannot open FTDI device. Exiting...')
                exit(-1)

            # Open the input file, prepare to write
            eeprom_size = self._get_eeprom_size(device_info)
            data = bin.read()
            if len(data) != eeprom_size:
                print(f"Input file size mismatch, expecting EEPROM size of {eeprom_size} bytes, got {len(data)} bytes.")
                exit(-1)

            # Write all 16-bit words in a loop
            for i in range(int(eeprom_size / 2)):
                # Unfortunately the FTD2XX Python package doesn't implement the necessary FT_ReadEE/FT_WriteEE command for raw byte access, so we need to
                # hack into the package to make this possible (This might break in future versions)
                word = data[i * 2] + 256 * data[i * 2 + 1]
                ftdi.call_ft(ftdi.ftd2xx._ft.FT_WriteEE, device.handle, i, word)
            
            if self.verbose:
                print("Write done. Current EEPROM dump:")
                print(hexdump(self.ft.read_eeprom(0, len(data))))
            
            # 'Cycle' the USB device to make the changes active
            if self.verbose:
                print("Cycling the USB port. Please wait...")
            device.cyclePort()
            time.sleep(3)
            device.close()

    # Read the EEPROM of the passed device into a given target file
    def read_eeprom(self, device_info : DeviceInfoDetail, file : str):
        with open(file, 'wb') as bin:
            device = ftdi.open(device_info["index"])
            if device == None:
                print('Cannot open FTDI device. Exiting...')
                exit(-1)

            eeprom_size = self._get_eeprom_size(device_info)
            buf = [0] * eeprom_size
            for i in range(int(eeprom_size / 2)):
                # Unfortunately the FTD2XX Python package doesn't implement the necessary FT_ReadEE/FT_WriteEE command for raw byte access, so we need to
                # hack into the package to make this possible (This might break in future versions)
                word_read = ftdi.ftd2xx._ft.WORD()
                ftdi.call_ft(ftdi.ftd2xx._ft.FT_ReadEE, device.handle, i, c.byref(word_read))
                buf[i*2+0] = word_read.value & 0xFF
                buf[i*2+1] = word_read.value >> 8

            bin.write(bytes(buf))
            if self.verbose:
                print(hexdump(buf))
                print(f'Read done. Saved to {os.path.abspath(file)}.')

            device.close()

    # Erase the EEPROM of the passed device
    def erase_eeprom(self, device_info : DeviceInfoDetail):
        # Open the selected FTDI device
        device = ftdi.open(device_info["index"])
        if device == None:
            print('Cannot open FTDI device. Exiting...')
            exit(-1)

        # Perform the erase
        eeprom_size = self._get_eeprom_size(device_info)
        ftdi.call_ft(ftdi.ftd2xx._ft.FT_EraseEE, device.handle)

        # 'Cycle' the USB device to make the changes active
        if self.verbose:
            print("Cycling the USB port. Please wait...")
        device.cyclePort()
        time.sleep(3)
        device.close()

    def _get_eeprom_size(self, device_info : DeviceInfoDetail):
        device_type = device_info['type']
        if not (device_type in FTDIDeviceTypes):
            print(f'Unknown or unsupported FTDI device type {device_type}. Exiting...')
            exit(-1)
        eeprom_size = FTDIDeviceTypes[device_type][1]
        if self.verbose:
            print(f'\nDetected FTDI device {FTDIDeviceTypes[device_type][0]} which has an EEPROM size of {eeprom_size} bytes.\n')
        if eeprom_size <= 0:
            print("This device has no EEPROM. Exiting...")
            exit(-1)
        return eeprom_size