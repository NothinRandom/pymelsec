"""
This file is a collection of MELSEC Communication error.
"""

class MCError(Exception):
    """
    Device code error

    Attributes:
        plc_type(str):      PLC type. "Q", "L" or "iQ"
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)
    """

    def __init__(self, errorcode):
        self.errorcode =  f'0x{str(errorcode).rjust(4, "0").upper()}'


    def __str__(self):
        # page 42 of developer guide
        if self.errorcode == 0x0050:
            return (f'{self.errorcode}: When "Communication Data Code" is set to'
            'ASCII Code, ASCII code data that cannot be converted to binary were received.')
        elif self.errorcode >= 0x0051 and self.errorcode <= 0x0054:
            return (f'{self.errorcode}: The number of read or write points is '
            'outside the allowable range.')
        elif self.errorcode == 0x0055:
            return (f'{self.errorcode}: Although online change is disabled, the connected '
            'device requested the RUN-state CPU module for data writing.')
        elif self.errorcode == 0xC056:
            return f'{self.errorcode}: The read or write request exceeds the maximum address.'
        elif self.errorcode == 0xC058:
            return (f'{self.errorcode}: The request data length after ASCII-to-binary conversion '
            'does not match the data size of the character area (a part of text data).')
        elif self.errorcode == 0xC059:
            return (f'{self.errorcode}:  The command and/or subcommand are specified incorrectly. '
            'The CPU module does not support the command and/or subcommand.')
        elif self.errorcode == 0xC05B:
            return (f'{self.errorcode}: The CPU module cannot read data from or write data to the '
            'specified device.')
        elif self.errorcode == 0xC05C:
            return (f'{self.errorcode}: The request data is incorrect. (e.g. reading or writing data '
            'in units of bits from or to a word device)')
        elif self.errorcode == 0xC05D:
            return f'{self.errorcode}: No monitor registration'
        elif self.errorcode == 0xC05F:
            return f'{self.errorcode}: The request cannot be executed to the CPU module.'
        elif self.errorcode == 0xC060:
            return (f'{self.errorcode}: The request data is incorrect. (ex. incorrect specification '
            'of data for bit devices)')
        elif self.errorcode == 0xC061:
            return (f'{self.errorcode}: The request data length does not match the number of data in '
            'the character area (a part of text data).')
        elif self.errorcode == 0xC06F:
            return (f'{self.errorcode}: The CPU module received a request message in ASCII format when '
            '"Communication Data Code is set to Binary Code, or received it in '
            'binary format when the setting is set to ASCII Code. (This error code '
            'is only registered to the error history, and no abnormal response is '
            'returned.)')
        elif self.errorcode == 0xC070:
            return (f'{self.errorcode}: The device memory extension cannot be specified for the '
            'target station.')
        elif self.errorcode == 0xC0B5:
            return f'{self.errorcode}: The CPU module cannot handle the data specified.'
        elif self.errorcode == 0xC200:
            return f'{self.errorcode}: The remote password is incorrect.'
        elif self.errorcode == 0xC201:
            return (f'{self.errorcode}: The port used for communication is locked with the remote '
            'password. Or, because of the remote password lock status with '
            '"Communication Data Code" set to ASCII Code, the subcommand '
            'and later part cannot be converted to a binary code.')
        elif self.errorcode == 0xC204:
            return (f'{self.errorcode}: The connected device is different from the one that requested for '
            'unlock processing of the remote password.')


class DataTypeError(Exception):
    """
    This data type is not supported by the module you connected.
    """
    def __init__(self, message:str):
        self.msg = message

    def __str__(self):
        return f'{self.msg}'


class DeviceCodeError(Exception):
    """
    Device code error: device does not exist.

    Attributes:
        plc_type(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)

    """
    def __init__(self, plc_type:str, devicename:str):
        self.plc_type = plc_type
        self.devicename = devicename

    def __str__(self):
        error_txt = (f'devicename: "{self.devicename}" is not support "{self.plc_type}" series PLC. '
                    'If you enter hexadecimal device(X, Y, B, W, SB, SW, DX, DY, ZR) with only alphabet number '
                    '(such as XFFF, device name is "X", device number is "FFF"),'
                    'please insert 0 between device name and device number (e.g. XFFF → X0FFF)'
                    )
        return error_txt


class CommTypeError(Exception):
    """
    Communication type error. Communication type must be "binary" or "ascii"
    """
    def __init__(self):
        pass

    def __str__(self):
        return 'communication type must be "binary" or "ascii"'


class PLCTypeError(Exception):
    """
    PLC type error. PLC type must be"Q", "L", "QnA", "iQ-L", "iQ-R"
    """
    def __init__(self):
        pass

    def __str__(self):
        return 'PLC type must be "Q", "L", "QnA" "iQ-L" or "iQ-R"'
