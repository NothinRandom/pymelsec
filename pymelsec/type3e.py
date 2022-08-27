"""
This file implements MELSEC Communication type 3E.
"""

import logging
import re
import socket
import struct
import time

from datetime import datetime
from . import constants as const
from .exceptions import (
    CommTypeError,
    DataTypeError, 
    DeviceCodeError,
    MCError,
    PLCTypeError
)
from .tag import (
    Tag,
    CPUModel,
    CPUStatus,
    LoopbackTest
)


def get_device_number(device:str) -> str:
    """
    Extract device number.

    Args:
        device(str):    device memory space (e.g. "D1000")
    Returns:
        device_index(str): device memory index (e.g. "1000")
    Example:
        "D1000" -> "1000"
        "X0x1A" -> "0x1A
    """
    device_num = re.search(r"\d.*", device)
    if device_num is None:
        raise ValueError(f'Invalid device number "{device}"')
    else:
        device_index = device_num.group(0)

    return device_index


class Type3E:
    """
    MELSEC Communication type 3E class.

    Attributes:
        plc_type(str):          connect PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
        comm_type(str):         communication type. "binary" or "ascii". (Default: "binary") 
        subheader(int):         Subheader for MELSEC Communication
        network(int):           network No. of an access target. (0<= network <= 255)
        pc(int):                network module station No. of an access target. (0<= pc <= 255)
        dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                specify the start input/output number of a multidrop connection source module.
                                the CPU module of the multiple CPU system and redundant system.
        dest_modulesta(int):    accessing a multidrop connection station via network, 
                                specify the station No. of aaccess target module
        timer(int):             time to raise Timeout error(/250msec). default=4(1sec)
                                If PLC elapsed this time, PLC returns Timeout response.
                                Note: python socket timeout is always set timer+1sec. To recieve Timeout response.
    """
    plc_type        = const.Q_SERIES
    comm_type       = const.COMMTYPE_BINARY
    subheader       = 0x5000
    network         = 0
    pc              = 0xFF
    dest_moduleio   = 0X3FF
    dest_modulesta  = 0X0
    timer           = 4 # MELSEC Communication timeout.
                        # 250msec * 4 = 1 sec 
    sock_timeout    = 2 # 2 sec
    _is_connected   = False
    _SOCKBUFSIZE    = 4096
    _wordsize       = 2 #how many byte is required to describe word value 
                        #binary: 2, ascii:4.
    _debug          = False
    endian          = const.ENDIAN_LITTLE

    __log = logging.getLogger(f"{__module__}.{__qualname__}")


    def __init__(self, host:str, port:int=5007, plc_type="Q"):
        """
        Constructor
        """

        self._set_plc_type(plc_type)
        # specify host and port
        if host:
            self.host = host
            self.port = port


    def __enter__(self):
        """
        Used by with statement: https://peps.python.org/pep-0343/
        """

        self.connect(ip=self.host, port=self.port)

        return self


    # used by with statement
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Used by with statement: https://peps.python.org/pep-0343/
        """

        try:
            self.close()
        except:
            self.__log.exception("Error closing connection.")
            return False
        else:
            if not exc_type:
                return True
            self.__log.exception("Unhandled Client Error", exc_info=(exc_type, exc_val, exc_tb))
            return False


    def _set_debug(self, enable:bool=False):
        """
        Set debug mode
        """
        self._debug = enable


    def connect(self, ip:str, port:int):
        """
        Connect to PLC.

        Args:
            ip (str):           ip address(IPV4) to connect PLC
            port (int):         port number of connect PLC   
            timeout (float):    timeout second in communication
        """

        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.sock_timeout)
        self._sock.connect((ip, port))
        self._is_connected = True


    def close(self):
        """
        Close connection.
        """

        self._sock.close()
        self._is_connected = False


    def _send(self, send_data:bytes):
        """
        Send data 

        Args:
            send_data(bytes): MELSEC Communication data
        """

        if self._is_connected:
            if self._debug:
                self.__log.debug(send_data.hex())
            self._sock.send(send_data)
        else:
            raise Exception("socket is not connected. Please use connect method")


    def _recv(self):
        """
        Receive data

        Returns:
            recv_data
        """

        recv_data = self._sock.recv(self._SOCKBUFSIZE)

        return recv_data


    def _set_plc_type(self, plc_type:str):
        """
        Check PLC type. If plc_type is valid, set self.comm_type.

        Args:
            plc_type(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        """

        if plc_type == "Q":
            self.plc_type = const.Q_SERIES
        elif plc_type == "L":
            self.plc_type = const.L_SERIES
        elif plc_type == "QnA":
            self.plc_type = const.QnA_SERIES
        elif plc_type == "iQ-L":
            self.plc_type = const.iQL_SERIES
        elif plc_type == "iQ-R":
            self.plc_type = const.iQR_SERIES
        else:
            raise PLCTypeError()


    def _set_comm_type(self, comm_type:str):
        """
        Check communication type. If comm_type is valid, set self.comm_type.

        Args:
            comm_type(str):      communication type. "binary" or "ascii". (Default: "binary")
        """

        if comm_type == "binary":
            self.comm_type = const.COMMTYPE_BINARY
            self._wordsize = 2
        elif comm_type == "ascii":
            self.comm_type = const.COMMTYPE_ASCII
            self._wordsize = 4
        else:
            raise CommTypeError()


    def _get_response_data_index(self) -> int:
        """
        Get response data index from return data byte.

        Returns:
            index(int)
        """

        if self.comm_type == const.COMMTYPE_BINARY:
            return 11
        else:
            return 22


    def _get_response_status_index(self) -> int:
        """
        Get command status index from return data byte.

        Returns:
            index(int)
        """

        if self.comm_type == const.COMMTYPE_BINARY:
            return 9
        else:
            return 18


    def set_access_opt(self,
        comm_type=None,
        network=None, 
        pc=None,
        dest_moduleio=None, 
        dest_modulesta=None,
        timer_sec=None
    ):
        """
        Set access option.

        Args:
            comm_type(str):         communication type. "binary" or "ascii". (Default: "binary") 
            network(int):           network No. of an access target. (0<= network <= 255)
            pc(int):                network module station No. of an access target. (0<= pc <= 255)
            dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                    specify the start input/output number of a multidrop connection source module.
                                    the CPU module of the multiple CPU system and redundant system.
            dest_modulesta(int):    accessing a multidrop connection station via network, 
                                    specify the station No. of aaccess target module
            timer_sec(int):         Time out to return Timeout Error from PLC. 
                                    MELSEC Communication time is per 250msec, but for ease, set_access_opt requires per sec.
                                    Socket time out is set timer_sec + 1 sec.
        """

        if comm_type:
            self._set_comm_type(comm_type)
        if network:
            try:
                self.network = struct.pack('<B', network)
            except:
                raise ValueError("network must be 0 <= network <= 255")
        if pc:
            try:
                self.pc = struct.pack('<B', pc)
            except:
                raise ValueError("pc must be 0 <= pc <= 255") 
        if dest_moduleio:
            try:
                self.dest_moduleio = struct.pack('<H', dest_moduleio)
            except:
                raise ValueError("dest_moduleio must be 0 <= dest_moduleio <= 65535") 
        if dest_modulesta:
            try:
                self.dest_modulesta = struct.pack('<B', dest_modulesta)
            except:
                raise ValueError("dest_modulesta must be 0 <= dest_modulesta <= 255") 
        if timer_sec:
            try:
                self.timer = struct.pack('<H', timer_sec * 4)
                self.sock_timeout = timer_sec + 1
                if self._is_connected:
                    self._sock.settimeout(self.sock_timeout)
            except:
                raise ValueError("timer_sec must be 0 <= timer_sec <= 16383, / sec")

        return None


    def _build_send_data(self, request_data:bytes) -> bytes:
        """
        Build send data.

        Args:
            request_data(bytes): MELSEC Communication request data. 
                                data must be converted according to self.comm_type

        Returns:
            mc_data(bytes):     send MELSEC Communication data
        """

        mc_data = bytes()
        # subheader is big endian
        if self.comm_type == const.COMMTYPE_BINARY:
            mc_data += struct.pack('>H', self.subheader)
        else:
            mc_data += f'{self.subheader:04x}'.upper().encode()
        mc_data += self._encode_value(self.network, const.DT.BIT)
        mc_data += self._encode_value(self.pc, const.DT.BIT)
        mc_data += self._encode_value(self.dest_moduleio, const.DT.sWORD)
        mc_data += self._encode_value(self.dest_modulesta, const.DT.BIT)
        #add self.timer size
        mc_data += self._encode_value(self._wordsize + len(request_data), const.DT.sWORD)
        mc_data += self._encode_value(self.timer, const.DT.sWORD)
        mc_data += request_data

        return mc_data


    def _build_command_data(self, command:int, subcommand:int) -> bytes:
        """
        Build command data from command and subcommand data.

        Args:
            command(int):           command code
            subcommand(int):        subcommand code

        Returns:
            command_data(bytes):    command data
        """

        command_data = bytes()
        command_data += self._encode_value(command, const.DT.sWORD)
        command_data += self._encode_value(subcommand, const.DT.sWORD)

        return command_data


    def _build_device_data(self, device:str) -> bytes:
        """
        Build device data from device code and device number.

        Args:
            device(str): device. (ex: "D1000", "Y1")

        Returns:
            device_data(bytes): device data
        """

        device_data = bytes()

        device_type = re.search(r"\D+", device)
        if device_type is None:
            raise ValueError("Invalid device")
        else:
            device_type = device_type.group(0)

        if self.comm_type == const.COMMTYPE_BINARY:
            device_code, device_base = const.DeviceConstants.get_binary_device_code(
                plc_type=self.plc_type,
                device_name=device_type
                )
            device_number = int(get_device_number(device), device_base)
            if self.plc_type is const.iQR_SERIES:
                device_data += struct.pack(f'{self.endian}IH', device_number, device_code)
            else:
                if self.endian == const.ENDIAN_LITTLE:
                    device_data += struct.pack('<I', device_number)[:-1]
                else:
                    device_data += struct.pack('>I', device_number)[1:]
                device_data += struct.pack(f'{self.endian}B', device_code)
        else:
            device_code, device_base = const.DeviceConstants.get_ascii_device_code(
                plc_type=self.plc_type,
                device_name=device_type
                )
            device_number = str(int(get_device_number(device), device_base))
            if self.plc_type is const.iQR_SERIES:
                device_data += device_code.encode()
                device_data += f'{device_number:08x}'.upper().encode()
            else:
                device_data += device_code.encode()
                device_data += f'{device_number:06x}'.upper().encode()

        return device_data


    def _encode_value(self, value:int, mode:str=const.DT.sWORD, isSigned:bool=False) -> bytes:
        """
        Encode value data to byte.

        Args: 
            value(int):     read size, write value, and so on.
            mode(str):      value type.
            isSigned(bool): convert as signed value

        Returns:
            value_byte(bytes):  value data
        """

        try:
            if not isSigned:
                mode = mode.upper()
            value_byte = struct.pack(f'{self.endian}{mode}', value)
            if self.comm_type != const.COMMTYPE_BINARY:
                if mode.lower() == const.DT.BIT:
                    value_byte = f'{value_byte:02x}'.upper().encode()
                elif mode.lower() == const.DT.sWORD:
                    value_byte = f'{value_byte:04x}'.upper().encode()
                elif mode.lower() == const.DT.sDWORD:
                    value_byte = f'{value_byte:08x}'.upper().encode()
        except:
            raise ValueError("Exceeded device value range")

        return value_byte


    def _decode_value(self, byte_array:bytes, mode:str=const.DT.sWORD, isSigned:bool=False) -> int:
        """
        Decode byte array to value.

        Args:
            byte_array(bytes):  read size, write value, and so on.
            mode(str):          value type.
            isSigned(bool):     convert as signed value  

        Returns:
            value(int):  value data
        """

        try:
            if not isSigned:
                mode = mode.upper()
            # convert hexstring to bytes
            if self.comm_type != const.COMMTYPE_BINARY:
                byte_array = bytes.fromhex(byte_array)
            value = struct.unpack(f'{self.endian}{mode}', byte_array)[0]
        except:
            raise ValueError("Could not decode byte to value")

        return value


    def _check_command_response(self, recv_data:bytes):
        """
        Check command response. Raise error if response status is not 0.

        Args:
            recv_data(bytes): Data buffer response
        """

        response_status_index = self._get_response_status_index()
        response_status = self._decode_value(
            byte_array=recv_data[response_status_index:response_status_index+self._wordsize]
            )
        self._check_mc_error(status=response_status)

        return None


    def _check_mc_error(self, status:int):
        """
        Check MELSEC Communication command error.
        Raise error if status is not 0.

        Args:
            status(int): 
        """

        if status == 0:
            return None
        else:
            raise MCError(status)


    def batch_read_words(self, ref_device:str, read_size:int, decode:bool=True) -> list:
        """
        Batch read in word units.

        Args:
            ref_device(str):    Reference device address. (ex: "D1000")
            read_size(int):     Number of device points

        Returns:
            word_values(list[int]):  word units value list
        """

        command = const.Commands.BATCH_READ
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._build_device_data(ref_device)
        request_data += self._encode_value(read_size)
        send_data = self._build_send_data(request_data)
        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        word_values = []
        data_index = self._get_response_data_index()
        if decode:
            for _ in range(read_size):
                wordvalue = self._decode_value(
                    byte_array=recv_data[data_index:data_index+self._wordsize],
                    isSigned=True
                    )
                word_values.append(wordvalue)
                data_index += self._wordsize

        else:
            for _ in range(read_size):
                wordvalue = recv_data[data_index:data_index+self._wordsize]
                word_values.append(wordvalue)
                data_index += self._wordsize

        return word_values


    def batch_read_bits(self, ref_device:str, read_size:int) -> list:
        """
        Batch read in bit units.

        Args:
            ref_device(str):    Reference device address. (ex: "X1")
            size(int):          Number of device points

        Returns:
            bits_values(list[int]):  bit units value(0 or 1) list
        """

        command = const.Commands.BATCH_READ
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.THREE
        else:
            subcommand = const.SubCommands.ONE

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._build_device_data(ref_device)
        request_data += self._encode_value(read_size)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        bit_values = []
        if self.comm_type == const.COMMTYPE_BINARY:
            for i in range(read_size):
                data_index = i//2 + self._get_response_data_index()
                value = struct.unpack('<B', recv_data[data_index:data_index+1])[0]
                #if i//2==0, bit value is 4th bit
                if(i%2==0):
                    bitvalue = 1 if value & (1<<4) else 0
                else:
                    bitvalue = 1 if value & (1<<0) else 0
                bit_values.append(bitvalue)
        else:
            data_index = self._get_response_data_index()
            byte_range = 1
            for i in range(read_size):
                bitvalue = int(recv_data[data_index:data_index+byte_range].decode())
                bit_values.append(bitvalue)
                data_index += byte_range

        return bit_values


    def batch_write_words(self, ref_device:str, values:list):
        """
        Batch write in word units.

        Args:
            ref_device(str):    Reference device address. (ex: "D1000")
            values(list[int]):  List of values.
        """

        write_size = len(values)

        command = const.Commands.BATCH_WRITE
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._build_device_data(ref_device)
        request_data += self._encode_value(write_size)
        for value in values:
            request_data += self._encode_value(value=value, isSigned=True)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def batch_write_bits(self, ref_device:str, values:list):
        """
        Batch read in bit units.

        Args:
            ref_device(str):    Reference device address. (ex: "X10")
            values(list[int]):  List of values: 0 (OFF) or 1 (ON).
        """

        write_size = len(values)
        # check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 (OFF) or 1 (ON).")

        command = const.Commands.BATCH_WRITE
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.THREE
        else:
            subcommand = const.SubCommands.ONE

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._build_device_data(ref_device)
        request_data += self._encode_value(write_size)
        if self.comm_type == const.COMMTYPE_BINARY:
            #every value is 0 or 1.
            #Even index's value turns on or off 4th bit, odd index's value turns on or off 0th bit.
            #First, create send data list. Length must be ceil of len(values).
            bit_data = [0 for _ in range((len(values) + 1)//2)]
            for index, value in enumerate(values):
                #calc which index data should be turns on.
                value_index = index//2
                #calc which bit should be turns on.
                bit_index = 4 if index%2 == 0 else 0
                #turns on or off value of 4th or 0th bit, depends on value
                bit_value = value << bit_index
                #Take or of send data
                bit_data[value_index] |= bit_value
            request_data += bytes(bit_data)
        else:
            for value in values:
                request_data += str(value).encode()
        send_data = self._build_send_data(request_data)
                    
        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def randomread(self, word_devices:list, dword_devices:list, decode:bool=True) -> tuple:
        """
        Read word units and dword units randomly.
        Moniter condition is not supported.

        Args:
            word_devices(list[str]):    Read device word units. (ex: ["D1000", "D1010"])
            dword_devices(list[str]):   Read device dword units. (ex: ["D1000", "D1012"])

        Returns:
            word_values(list[int]):     word units value list
            dword_values(list[int]):    dword units value list

        """
        command = const.Commands.RANDOM_READ
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO

        word_size = len(word_devices)
        dword_size = len(dword_devices)
        
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(word_size, mode=const.DT.BIT)
        request_data += self._encode_value(dword_size, mode=const.DT.BIT)
        for word_device in word_devices:
            request_data += self._build_device_data(word_device)
        for dword_device in dword_devices:
            request_data += self._build_device_data(dword_device)        
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)
        data_index = self._get_response_data_index()
        word_values= []
        dword_values= []
        if decode:
            for word_device in word_devices:
                wordvalue = self._decode_value(
                    byte_array=recv_data[data_index:data_index+self._wordsize],
                    isSigned=True
                    )
                word_values.append(wordvalue)
                data_index += self._wordsize
            for dword_device in dword_devices:
                dwordvalue = self._decode_value(
                    byte_array=recv_data[data_index:data_index+self._wordsize*2],
                    mode=const.DT.sDWORD,
                    isSigned=True
                    )
                dword_values.append(dwordvalue)
                data_index += self._wordsize*2
        else:
            for word_device in word_devices:
                wordvalue = recv_data[data_index:data_index+self._wordsize]
                word_values.append(wordvalue)
                data_index += self._wordsize
            for dword_device in dword_devices:
                dwordvalue = recv_data[data_index:data_index+self._wordsize*2]
                dword_values.append(dwordvalue)
                data_index += self._wordsize*2

        return word_values, dword_values


    def random_write(
        self,
        word_devices:list,
        word_values:list,
        dword_devices:list,
        dword_values:list
    ):
        """
        Write word units and dword units randomly.

        Args:
            word_devices(list[str]):    Write word devices. (ex: ["D1000", "D1020"])
            word_values(list[int]):     Values for each word devices. (ex: [100, 200])
            dword_devices(list[str]):   Write dword devices. (ex: ["D1000", "D1020"])
            dword_values(list[int]):    Values for each dword devices. (ex: [100, 200])
        """

        if len(word_devices) != len(word_values):
            raise ValueError("word_devices and word_values must be same length")
        if len(dword_devices) != len(dword_values):
            raise ValueError("dword_devices and dword_values must be same length")
            
        word_size = len(word_devices)
        dword_size = len(dword_devices)

        command = const.Commands.RANDOM_WRITE
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO
        
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(word_size, mode=const.DT.BIT)
        request_data += self._encode_value(dword_size, mode=const.DT.BIT)
        for word_device, word_value in zip(word_devices, word_values):
            request_data += self._build_device_data(word_device)
            request_data += self._encode_value(word_value, mode=const.DT.sWORD, isSigned=True)
        for dword_device, dword_value in zip(dword_devices, dword_values):
            request_data += self._build_device_data(dword_device)   
            request_data += self._encode_value(dword_value, mode="long", isSigned=True)     
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def random_write_bits(self, bit_devices:list, values:list):
        """
        Write bit units randomly.

        Args:
            bit_devices(list[str]):    Write bit devices. (ex: ["X10", "X20"])
            values(list[int]):         Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.
        """

        if len(bit_devices) != len(values):
            raise ValueError("bit_devices and values must be same length")
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        command = const.Commands.RANDOM_WRITE
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.THREE
        else:
            subcommand = const.SubCommands.ONE
        
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(write_size, mode=const.DT.BIT)
        for bit_device, value in zip(bit_devices, values):
            request_data += self._build_device_data(bit_device)
            #byte value for iQ-R requires 2 byte data
            if self.plc_type == const.iQR_SERIES:
                request_data += self._encode_value(value, mode=const.DT.sWORD, isSigned=True)
            else:
                request_data += self._encode_value(value, mode=const.DT.BIT, isSigned=True)
        send_data = self._build_send_data(request_data)
                    
        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def read(self, devices:list) -> list:
        """
        Read a list of mixed data types of mixed device types
        using improvised random read function.

        Monitor condition does not support.

        Args:
            devices(list[NamedTuple]): Read device elements.
            Example: Tag(device="D1000", value=Any, datatype="INT", error:"")

        Returns:
            output(list[Tag]): Tag value list

        """

        command = const.Commands.RANDOM_READ
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO

        # get the words equivalent in size
        words_count = 0
        for element in devices:
            try:
                words_count +=const.DT.get_dt_size(data_type=element.type) // 2
            except DataTypeError as e:
                # self.__log.exception(e)
                continue

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(value=words_count, mode=const.DT.BIT)
        request_data += self._encode_value(value=0, mode=const.DT.BIT) # DWORD replace
        
        for element in devices:
            # get element size in words
            try:
                element_size =const.DT.get_dt_size(data_type=element.type) // 2
            except DataTypeError as e:
                # self.__log.exception(e)
                continue
            # create artificial index
            # example: D200, D201 to represent DWORD, FLOAT
            # example: D200, D201, D202, D203 to represent DOUBLE
            if element_size > 1:
                tag_name = element.device
                device_type = re.search(r"\D+", tag_name).group(0)
                device_index = int(re.search(r"\d+", tag_name).group(0))
                for index in range(element_size):
                    temp_tag_name = f"{device_type}{device_index}"
                    request_data += self._build_device_data(device=temp_tag_name)
                    device_index += 1
            else:
                request_data += self._build_device_data(device=element.device)

        # can skip
        if words_count < 1:
            return None

        send_data = self._build_send_data(request_data)
        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        # output result
        output = []
        try:
            self._check_command_response(recv_data)
        except MCError:
            return output
        data_index = self._get_response_data_index()
        for element in devices:
            # get data type from list
            try:
                size =const.DT.get_dt_size(data_type=element.type)
            except DataTypeError as e:
                # self.__log.exception(e)
                tag = element._replace(error=e)
                output.append(tag)
                continue
            # recast as uWORD
            if element.type ==const.DT.BIT:
                value = struct.unpack_from('H', recv_data, data_index)[0]
                # extract bit0 from uWORD
                value = True if value & (1<<0) else False
            else:
                value = struct.unpack_from(element.type, recv_data, data_index)[0]
            # format float to have 6 digits decimal at most
            if element.type == 'f':
                value = float(f"{value:.6f}".rstrip("0"))
            # update value
            tag = element._replace(value=value, type=const.DT.get_dt_name(element.type), error="Success")
            output.append(tag)
            data_index += size

        return output


    def write(self, devices:list) -> list:
        """
        Write a list of mixed data types of mixed device types
        using improvised random read function.

        Args:
            devices(list[NamedTuple]): Write device elements
            Example: Tag(device="D1000", value=1200, datatype=const.DT.sWORD)
        """

        command =const.Commands.RANDOM_WRITE
        if self.plc_type == const.iQR_SERIES:
            subcommand = const.SubCommands.TWO
        else:
            subcommand = const.SubCommands.ZERO

        # get the words equivalent in size
        words_count = 0
        for element in devices:
            # can't combine if bit
            if element.type ==const.DT.BIT:
                continue
            try:
                words_count +=const.DT.get_dt_size(data_type=element.type) // 2
            except DataTypeError:
                # self.__log.exception(e)
                continue


        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(value=words_count, mode=const.DT.BIT)
        request_data += self._encode_value(value=0, mode=const.DT.BIT) # DWORD replace

        output = []
        for element in devices:
            # can't combine if bit
            if element.type ==const.DT.BIT:
                self.batch_write_bits(ref_device=element.device, values=[element.value])
                continue
            # get element size in words
            try:
                element_size =const.DT.get_dt_size(data_type=element.type) // 2
            except DataTypeError as e:
                tag = element._replace(error=e)
                output.append(tag)
                # self.__log.exception(e)
                continue
            # build sure unsigned is not negative
            if element.type ==const.DT.uWORD or element.type ==const.DT.uDWORD:
                if element.value < 0:
                    element = element._replace(value=element.value * -1)
            # create artificial index
            # example: D200, D201 to represent DWORD, FLOAT
            # example: D200, D201, D202, D203 to represent DOUBLE
            # slightly trickier here since we need to squeeze after each device
            # example: D200, \x00\x01, D201, \x02\x03
            if element_size > 1:
                tag_name = element.device
                device_type = re.search(r"\D+", tag_name).group(0)
                device_index = int(re.search(r"\d+", tag_name).group(0))
                temp_tag_value = struct.pack(element.type, element.value)
                data_index = 0
                for index in range(element_size):
                    temp_tag_name = f"{device_type}{device_index}"
                    request_data += self._build_device_data(device=temp_tag_name)
                    request_data += temp_tag_value[data_index:data_index+self._wordsize]
                    data_index += self._wordsize
                    device_index += 1
            else:
                request_data += self._build_device_data(device=element.device)
                request_data += struct.pack(element.type, element.value)

        # only wrote bits, exit
        if words_count < 1:
            return None

        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        if len(output) < 1:
            return None

        return output


    def error_led_off(self):
        """
        Initialize LED display and error information of 
        buffer memory, and recover the supported device.
        """

        command = const.Commands.ERROR_LED_OFF
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)
        data_index = self._get_response_data_index()

        return None


    def indicator_led_off(self, channel:int=1):
        """
        Initialize LED display and error information of 
        buffer memory, and recover the supported device.

        Args:
            channel(int): CH1, CH2, CH1&2 (3)
        """

        command = const.Commands.ERROR_LED_OFF

        if self.plc_type is const.iQR_SERIES:
            subcommand = const.SubCommands.ONE
        else: # Q/L series
            if channel == 1:
                subcommand = const.SubCommands.FIVE
            elif channel == 2:
                subcommand = const.SubCommands.A
            elif channel == 3: # both channels
                subcommand = const.SubCommands.F

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)
        data_index = self._get_response_data_index()

        return None


    def remote_run(self, clear_mode:int=0, force_exec:bool=False):
        """
        Run PLC

        Args:
            clear_mode(int):    0: does not clear
                                1: clear except latch device
                                2: clear all
            force_exec(bool):   Force to execute if PLC is operated remotely by other device.

        """

        if not (clear_mode == 0 or  clear_mode == 1 or clear_mode == 2):
            raise ValueError("clear_device must be 0, 1 or 2. 0: does not clear. 1: clear except latch device. 2: clear all.")
        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        command = const.Commands.REMOTE_RUN
        subcommand = const.SubCommands.ZERO

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(mode, mode=const.DT.sWORD)
        request_data += self._encode_value(clear_mode, mode=const.DT.BIT)
        request_data += self._encode_value(0, mode=const.DT.BIT)
        send_data = self._build_send_data(request_data)
        # send data
        self._send(send_data)
        
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def remote_stop(self):
        """
        Stop PLC.
        """

        command = const.Commands.REMOTE_STOP
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(0x0001, mode=const.DT.sWORD) #fixed value
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def remote_pause(self, force_exec=False):
        """
        Pause PLC.

        Args:
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.
        """

        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        command = const.Commands.REMOTE_PAUSE
        subcommand = const.SubCommands.ZERO

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(mode, mode=const.DT.sWORD)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def remote_latch_clear(self):
        """
        Clear PLC latch.
        PLC must be stop when use this command.
        """

        command = const.Commands.REMOTE_LATCH_CLEAR
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(0x0001, mode=const.DT.sWORD) #fixed value 
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def remote_reset(self):
        """
        Reset PLC.
        PLC must be stop when use this command.
        """

        command = const.Commands.REMOTE_RESET
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(0x0001, mode=const.DT.sWORD) #fixed value
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        # set time out 1 seconds. Because remote reset may not return data since clone socket
        try:
            self._sock.settimeout(1)
            recv_data = self._recv()
            self._check_command_response(recv_data)
        except:
            self._is_connected = False
            # after wait 1 sec
            # try reconnect
            time.sleep(1)
            self.connect(self._ip, self._port)

        return None


    def remote_unlock(self, password:str="", request_input:bool=False):
        """
        Unlock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """

        if request_input:
            password = input("Please enter password\n")
        try:
            password.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError("password must be only ascii code")
        if self.plc_type is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")

        command = const.Commands.REMOTE_UNLOCK
        subcommand = const.SubCommands.ZERO
        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(len(password), mode=const.DT.sWORD) 
        request_data += password.encode()

        send_data = self._build_send_data(request_data)

        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def remote_lock(self, password:str="", request_input:bool=False):
        """
        Lock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """

        if request_input:
            password = input("Please enter password\n")
        try:
            password.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError("password must be only ascii code")

        if self.plc_type is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")

        command = const.Commands.REMOTE_LOCK
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(len(password), mode=const.DT.sWORD) 
        request_data += password.encode()

        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        return None


    def read_cpu_model(self) -> CPUModel:
        """
        Read CPU model.

        Returns:
            CPUModel(NamedTuple): (CPU name(str), CPU code(str))
        """

        command = const.Commands.READ_CPU_MODEL
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)
        data_index = self._get_response_data_index()
        cpu_name_length = 16
        cpu_name = recv_data[data_index:data_index+cpu_name_length].decode()
        cpu_name = cpu_name.replace("\x20", "")
        if self.comm_type == const.COMMTYPE_BINARY:
            cpu_code = struct.unpack('<H', recv_data[data_index+cpu_name_length:])[0]
            cpu_code = f'{cpu_code:04x}'
        else:
            cpu_code = recv_data[data_index+cpu_name_length:].decode()

        return CPUModel(cpu_name, cpu_code)


    def read_cpu_status(self) -> CPUStatus:
        """
        Read CPU status.

        Returns:
            CPUStatus(NamedTuple): (CPU status(str), Stop/Pause Cause (str))
        """

        try:
            response = self.batch_read_words(ref_device="SD203", read_size=1)[0]
            status = response & ((1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 15))
            # get status
            if status == 0:
                cpu_status = "Run"
            elif status == 1:
                cpu_status = "Step Run"
            elif status == 2:
                cpu_status = "Stop"
            elif status == 3:
                cpu_status = "Pause"
            else:
                cpu_status = None
            # get stop/pause cause
            cause = response & ((1 << 4) | (1 << 5) | (1 << 6) | (1 << 7) | (1 << 15))
            cause = cause >> 4
            if cause == 0:
                cause_reason = "By Switch"
            elif cause == 1:
                cause_reason = "Remote Relay"
            elif cause == 2:
                cause_reason = "Remote Device"
            elif cause == 3:
                cause_reason = "By Program"
            elif cause == 4:
                cause_reason = "By Error"
            else:
                cause_reason = None
            
            return CPUStatus(cpu_status, cause_reason)
        except Exception:
            return CPUStatus("Unknown", "Unknown")

    
    def read_switch_status(self) -> str:
        """
        Read the status of the physical switch.

        Returns:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """

        try:
            status = self.batch_read_words(ref_device="SD200", read_size=1)[0]
            if status == 0:
                return "Run"
            elif status == 1:
                return "Stop"
            elif status == 2:
                return "Latch Clear"
            else:
                return None
        except Exception:
            return "Unknown"


    def read_plc_time(self) -> datetime:
        """
        Read PLC time.

        Returns:
            datetime:   datetime object of PLC
        """

        # enable write time in special relay
        self.batch_write_bits(ref_device="SM213", values=[1])
        # read output registers in special register
        result = self.batch_read_words(ref_device="SD210", read_size=8)
        # disable write time in special relay
        self.batch_write_bits(ref_device="SM213", values=[0])

        # result outputs [yyyy, mm, dd, hh, mm, ss, dow, ?]
        return datetime(
            year = result[0],
            month = result[1],
            day = result[2],
            hour = result[3],
            minute = result[4],
            second = result[5]
        )


    def sync_plc_time(self, utc:bool=False) -> datetime:
        """
        Sync PLC time to host time.

        Args:
            utc(bool):   use UTC time (True) or local time (False)
        """

        if utc:
            now = datetime.utcnow()
        else:
            now = datetime.now()

        self.set_plc_time(dt=now)

        return now


    def set_plc_time(self, dt:datetime) -> str:
        """
        Set PLC time by specifying datetime object.

        Args:
            dt(datetime):   datetime object (e.g. datetime.now())
        """

        dtValues = [
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.weekday(),
            0 # now sure what last word is for
        ]

        # disable write time in special relay
        self.random_write_bits(bit_devices=["SM211","SM213"], values=[0,0])
        # read output registers in special register
        result = self.batch_write_words(ref_device="SD210", values=dtValues)
        # disable->enable->disable write time in special relay
        self.batch_write_bits(ref_device="SM210", values=[0])
        self.batch_write_bits(ref_device="SM210", values=[1])
        self.batch_write_bits(ref_device="SM210", values=[0])

        return f"set_plc_time() to {dt}"


    def loopback_test(self, echo_data:str) -> LoopbackTest:
        """
        Do echo test. Send data and response_ data should be same.

        Args:
            echo_data(str): send data to PLC

        Returns:
            length(int):    response data length from PLC
            data(str):      response data from PLC
        """

        echo_data_len = len(echo_data)
        if echo_data.isalnum() is False:
            raise ValueError("echo_data must be only alphabet or digit code")
        if not ( 1 <= echo_data_len <= 960):
            raise ValueError("echo_data length must be from 1 to 960")

        command = const.Commands.LOOPBACK_TEST
        subcommand = const.SubCommands.ZERO

        request_data = bytes()
        request_data += self._build_command_data(command, subcommand)
        request_data += self._encode_value(echo_data_len, mode=const.DT.sWORD) 
        request_data += echo_data.encode()

        send_data = self._build_send_data(request_data)

        # send data
        self._send(send_data)
        # receive data
        recv_data = self._recv()
        self._check_command_response(recv_data)

        data_index = self._get_response_data_index()

        response_len = self._decode_value(byte_array=recv_data[data_index:data_index+self._wordsize]) 
        response = recv_data[data_index+self._wordsize:].decode()

        if response_len != echo_data_len:
            raise ValueError(f'echo_data_len({echo_data_len}) does not match response_len({response_len})')

        return LoopbackTest(response_len, response)
