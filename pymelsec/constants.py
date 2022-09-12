"""
This file defines MELSEC Communication constant.
"""

from .exceptions import DataTypeError, DeviceCodeError

# PLC definition
Q_SERIES    = "Q"
L_SERIES    = "L"
QnA_SERIES  = "QnA"
iQL_SERIES  = "iQ-L"
iQR_SERIES  = "iQ-R"

# communication type
COMMTYPE_BINARY = "binary"
COMMTYPE_ASCII  = "ascii"

ENDIAN_NATIVE   = '='
ENDIAN_LITTLE   = '<'
ENDIAN_BIG      = '>'
ENDIAN_NETWORK  = '!'


# commands on page 38
class Commands:
    BATCH_READ          = 0x0401
    BATCH_WRITE         = 0x1401
    RANDOM_READ         = 0x0403
    RANDOM_WRITE        = 0x1402
    MONITOR_REG         = 0x0801
    MONITOR             = 0x0802
    REMOTE_RUN          = 0x1001
    REMOTE_STOP         = 0x1002
    REMOTE_PAUSE        = 0x1003
    REMOTE_LATCH_CLEAR  = 0x1005
    REMOTE_RESET        = 0x1006
    REMOTE_UNLOCK       = 0x1630
    REMOTE_LOCK         = 0x1631
    ERROR_LED_OFF       = 0x1617
    READ_CPU_MODEL      = 0x0101
    LOOPBACK_TEST       = 0x0619


# subcommands
class SubCommands:
    ZERO    = 0x0000
    ONE     = 0x0001
    TWO     = 0x0002
    THREE   = 0x0003
    FIVE    = 0x0005
    A       = 0x000A
    F       = 0x000F


# data types: https://docs.python.org/3/library/struct.html#format-characters
class DT:
    """
    This class defines MELSEC Communication data types.

    Attributes:
        D_DEVICE(int):  D devide code (0xA8)
    """

    BIT     = 'b' # bit (faking)
    SWORD   = 'h' # signed WORD (short)
    UWORD   = 'H' # unsigned WORD (short)
    SDWORD  = 'i' # signed DWORD (long)
    UDWORD  = 'I' # unsigned DWORD (long)
    FLOAT   = 'f' # FLOAT
    DOUBLE  = 'd' # DOUBLE
    SLWORD  = 'q' # signed LWORD (long long)
    ULWORD  = 'Q' # unsigned LWORD (unsigned long long)

    def __init__(self):
        """
        Constructor
        """
        pass


    def get_dt_name(data_type:str):
        """
        Get the data type name based on symbol

        Args:
            data_type(str): data type name
        """

        if data_type == 'b':
            return 'BIT'
        elif data_type == 'h':
            return 'SWORD'
        elif data_type == 'H':
            return 'UWORD'
        elif data_type == 'i':
            return 'SDWORD'
        elif data_type == 'I':
            return 'UDWORD'
        elif data_type == 'f':
            return 'FLOAT'
        elif data_type == 'd':
            return 'DOUBLE'
        elif data_type == 'q':
            return 'SLWORD'
        elif data_type == 'Q':
            return 'ULWORD'
        else:
            raise DataTypeError(f'Unknown data type "{data_type}"')


    def get_struct_dt(data_type:str) -> str:
        """
        Get struct.pack/unpack data type name

        Args:
            data_type(str): data type symbol
        """

        if data_type == 'BIT' or data_type == 'b':
            return 'b'
        elif data_type == 'SWORD' or data_type == 'h':
            return 'h'
        elif data_type == 'UWORD'or data_type == 'H':
            return 'H'
        elif data_type == 'SDWORD'or data_type == 'i':
            return 'i'
        elif data_type == 'UDWORD'or data_type == 'I':
            return 'I'
        elif data_type == 'FLOAT'or data_type == 'f':
            return 'f'
        elif data_type == 'DOUBLE'or data_type == 'd':
            return 'd'
        elif data_type == 'SLWORD'or data_type == 'q':
            return 'q'
        elif data_type == 'ULWORD'or data_type == 'Q':
            return 'Q'
        else:
            raise DataTypeError(f'Unknown data type "{data_type}"')


    def get_dt_size(data_type:str):
        """
        Get the data type size based on symbol

        Args:
            data_type(str): data type symbol
        """

        if (data_type == 'b' 
            or data_type == 'BIT'
            or data_type == 'h' 
            or data_type == 'SWORD'
            or data_type == 'H'
            or data_type == 'UWORD'
        ):
            return 2
        elif (
            data_type == 'i' 
            or data_type == 'SDWORD'
            or data_type == 'I' 
            or data_type == 'UDWORD'
            or data_type == 'f'
            or data_type == 'FLOAT'
        ):
            return 4
        elif (
            data_type == 'd' 
            or data_type == 'DOUBLE'
            or data_type == 'q' 
            or data_type == 'SLWORD'
            or data_type == 'Q'
            or data_type == 'ULWORD'
        ):
            return 8
        else:
            raise DataTypeError(f'Data type "{data_type}" is not supported.')


class DeviceConstants:
    """
    This class defines MELSEC Communication device constant.

    Attributes:
        D_DEVICE(int):  D devide code (0xA8)
    """

    # These device supports all series
    SM_DEVICE = 0x91
    SD_DEVICE = 0xA9
    X_DEVICE  = 0x9C
    Y_DEVICE  = 0x9D
    M_DEVICE  = 0x90
    L_DEVICE  = 0x92
    F_DEVICE  = 0x93
    V_DEVICE  = 0x94
    B_DEVICE  = 0xA0
    D_DEVICE  = 0xA8
    W_DEVICE  = 0xB4
    TS_DEVICE = 0xC1
    TC_DEVICE = 0xC0
    TN_DEVICE = 0xC2
    SS_DEVICE = 0xC7
    SC_DEVICE = 0xC6
    SN_DEVICE = 0xC8
    CS_DEVICE = 0xC4
    CC_DEVICE = 0xC3
    CN_DEVICE = 0xC5
    SB_DEVICE = 0xA1
    SW_DEVICE = 0xB5
    DX_DEVICE = 0xA2
    DY_DEVICE = 0xA3
    R_DEVICE  = 0xAF
    ZR_DEVICE = 0xB0

    # These device supports only "iQ-R" series
    LTS_DEVICE  = 0x51
    LTC_DEVICE  = 0x50
    LTN_DEVICE  = 0x52
    LSTS_DEVICE = 0x59
    LSTC_DEVICE = 0x58
    LSTN_DEVICE = 0x5A
    LCS_DEVICE  = 0x55
    LCC_DEVICE  = 0x54
    LCN_DEVICE  = 0x56
    LZ_DEVICE   = 0x62
    RD_DEVICE   = 0x2C

    BIT_DEVICE  = "bit"
    WORD_DEVICE = "word"
    DWORD_DEVICE= "dword"

    
    def __init__(self):
        """
        Constructor
        """
        pass
    
    @staticmethod
    def get_binary_device_code(plc_type:str, device_name:str):
        """
        Static method that returns device_code from device name.

        Args:
            plc_type(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            device_name(str):   Device name. (ex: "D", "X", "Y")

        Returns:
            device_code(int):    Device code defined MELSEC Communication (ex: "D" → 0xA8)
            Base number:        Base number for each device name
        """

        if device_name == "SM":
            return DeviceConstants.SM_DEVICE, 10
        elif device_name == "SD":
            return DeviceConstants.SD_DEVICE, 10
        elif device_name == "X":
            return DeviceConstants.X_DEVICE, 16
        elif device_name == "Y":
            return DeviceConstants.Y_DEVICE, 16
        elif device_name == "M":
            return DeviceConstants.M_DEVICE, 10
        elif device_name == "L":
            return DeviceConstants.L_DEVICE, 10
        elif device_name == "F":
            return DeviceConstants.F_DEVICE, 10
        elif device_name == "V":
            return DeviceConstants.V_DEVICE, 10
        elif device_name == "B":
            return DeviceConstants.B_DEVICE, 16
        elif device_name == "D":
            return DeviceConstants.D_DEVICE, 10
        elif device_name == "W":
            return DeviceConstants.W_DEVICE, 16
        elif device_name == "TS":
            return DeviceConstants.TS_DEVICE, 10
        elif device_name == "TC":
            return DeviceConstants.TC_DEVICE, 10
        elif device_name == "TN":
            return DeviceConstants.TN_DEVICE, 10
        elif device_name == "STS":
            return DeviceConstants.SS_DEVICE, 10
        elif device_name == "STC":
            return DeviceConstants.SC_DEVICE, 10
        elif device_name == "STN":
            return DeviceConstants.SN_DEVICE, 10
        elif device_name == "CS":
            return DeviceConstants.CS_DEVICE, 10
        elif device_name == "CC":
            return DeviceConstants.CC_DEVICE, 10
        elif device_name == "CN":
            return DeviceConstants.CN_DEVICE, 10
        elif device_name == "SB":
            return DeviceConstants.SB_DEVICE, 16
        elif device_name == "SW":
            return DeviceConstants.SW_DEVICE, 16
        elif device_name == "DX":
            return DeviceConstants.DX_DEVICE, 16
        elif device_name == "DY":
            return DeviceConstants.DY_DEVICE, 16
        elif device_name == "R":
            return DeviceConstants.R_DEVICE, 10
        elif device_name == "ZR":
            return DeviceConstants.ZR_DEVICE, 16
        elif (device_name == "LTS") and (plc_type == iQR_SERIES):
            return DeviceConstants.LTS_DEVICE, 10
        elif (device_name == "LTC") and (plc_type == iQR_SERIES):
            return DeviceConstants.LTC_DEVICE, 10
        elif (device_name == "LTN") and (plc_type == iQR_SERIES):
            return DeviceConstants.LTN_DEVICE, 10
        elif (device_name == "LSTS") and (plc_type == iQR_SERIES):
            return DeviceConstants.LSTS_DEVICE, 10
        elif (device_name == "LSTN") and (plc_type == iQR_SERIES):
            return DeviceConstants.LSTN_DEVICE, 10
        elif (device_name == "LCS") and (plc_type == iQR_SERIES):
            return DeviceConstants.LCS_DEVICE, 10
        elif (device_name == "LCC") and (plc_type == iQR_SERIES):
            return DeviceConstants.LCC_DEVICE, 10
        elif (device_name == "LCN") and (plc_type == iQR_SERIES):
            return DeviceConstants.LCN_DEVICE, 10
        elif (device_name == "LZ") and (plc_type == iQR_SERIES):
            return DeviceConstants.LZ_DEVICE, 10
        elif (device_name == "RD") and (plc_type == iQR_SERIES):
            return DeviceConstants.RD_DEVICE, 10
        else:
            raise DeviceCodeError(plc_type, device_name)

    @staticmethod
    def get_ascii_device_code(plc_type:str, device_name:str):
        """
        Static method that returns device_code from device name.

        Args:
            plc_type(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            device_name(str):   Device name. (ex: "D", "X", "Y")

        Returns:
            device_code(int):   Device code defined MELSEC Communication (ex: "D" → "D*")
            Base number:        Base number for each device name
        """

        if plc_type == iQR_SERIES:
            padding = 4
        else:
            padding = 2
        if device_name == "SM":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "SD":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "X":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "Y":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "M":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "L":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "F":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "V":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "B":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "D":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "W":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "TS":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "TC":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "TN":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "STS":
            if plc_type == iQR_SERIES:
                return "STS".ljust(padding, "*"), 10
            else:    
                return "SS".ljust(padding, "*"), 10
        elif device_name == "STC":
            if plc_type == iQR_SERIES:
                return "STC".ljust(padding, "*"), 10
            else:    
                return "SC".ljust(padding, "*"), 10
        elif device_name == "STN":
            if plc_type == iQR_SERIES:
                return "STN".ljust(padding, "*"), 10
            else:    
                return "SN".ljust(padding, "*"), 10
        elif device_name == "CS":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "CC":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "CN":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "SB":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "SW":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "DX":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "DY":
            return device_name.ljust(padding, "*"), 16
        elif device_name == "R":
            return device_name.ljust(padding, "*"), 10
        elif device_name == "ZR":
            return device_name.ljust(padding, "*"), 16
        elif (device_name == "LTS") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LTC") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LTN") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LSTS") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LSTN") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LCS") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LCC") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LCN") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "LZ") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        elif (device_name == "RD") and (plc_type == iQR_SERIES):
            return device_name.ljust(padding, "*"), 10
        else:
            raise DeviceCodeError(plc_type, device_name)

    @staticmethod
    def get_device_type(plc_type, device_name):
        """
        Static method that returns device type "bit" or "word" type.

        Args:
            plc_type(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            device_name(str):   Device name. (ex: "D", "X", "Y")

        Returns:
            device_tyoe(str):   Device type: "bit" or "word"
        """

        if device_name == "SM":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "SD":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "X":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "Y":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "M":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "L":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "F":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "V":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "B":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "D":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "W":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "TS":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "TC":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "TN":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "STS":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "STC":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "STN":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "CS":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "CC":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "CN":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "SB":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "SW":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "DX":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "DY":
            return DeviceConstants.BIT_DEVICE
        elif device_name == "R":
            return DeviceConstants.WORD_DEVICE
        elif device_name == "ZR":
            return DeviceConstants.WORD_DEVICE
        elif (device_name == "LTS") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LTC") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LTN") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LSTS") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LSTN") and (plc_type == iQR_SERIES):
            return DeviceConstants.DWORD_DEVICE
        elif (device_name == "LCS") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LCC") and (plc_type == iQR_SERIES):
            return DeviceConstants.BIT_DEVICE
        elif (device_name == "LCN") and (plc_type == iQR_SERIES):
            return DeviceConstants.DWORD_DEVICE
        elif (device_name == "LZ") and (plc_type == iQR_SERIES):
            return DeviceConstants.DWORD_DEVICE
        elif (device_name == "RD") and (plc_type == iQR_SERIES):
            return DeviceConstants.WORD_DEVICE
        else:
            raise DeviceCodeError(plc_type, device_name)
