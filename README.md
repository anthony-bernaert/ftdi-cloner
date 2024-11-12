# FTDI EEPROM cloner
This simple Python program makes EEPROM dumps of FTDI-based devices, and can restore the entire EEPROM from a file on your computer.

Besides backup and analysis purposes, this program also allows to clone devices that use an FTDI chip with a proprietary signature in their EEPROM. This signature often prevents using custom FTDI-based boards with specific software such as FPGA toolchains, even though the software perfectly supports the FTDI chip.

Note that only raw EEPROM data is manipulated. The program currently has no checks on the correctness of the EEPROM contents you read or write. It does NOT update the checksum nor does it automatically generate serial numbers for your device.

>[!IMPORTANT]
>Use this utility at your own risk. Writing an invalid file to the EEPROM may result in a subsequent enumeration failure, bricking your device until you replace the EEPROM chip!

## How to use
### Python virtual environment
The recommended way is to create a virtual environment from which the program is run. Dependencies are automatically loaded based on the package configuration files. For this, run the `install.sh`/`install.bat` (depending on your OS) from the repository's root folder.

You can then launch the program through the `run.sh`/`run.bat` file, or directly launch the executable created in the 'dist' folder.

### Manually run from ftdi-cloner.py
If you prefer to directly invoke the Python script using `python ftdi-cloner.py`, you need to install the following dependencies first using `pip`:
- `ftd2xx=1.3.8`
- `simple-hexdump`

### Interactive CLI
Currently, the program only runs interactively from the command line. On-screen instructions guide you through the backup/restore process.
