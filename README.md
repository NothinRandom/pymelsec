# pymelsec
A Python3 implementation of MELSEC Communication Protocol that allows you to interact with a Mitsubishi PLC.  This library was inspired by [pymcprotocol](https://github.com/senrust/pymcprotocol), but has been
rewritten to have additional features and be more flexible.

## Installation 
```console 
pip3 install pymelsec
```

## Protocol type
pymelsec natively supports MELSEC Communication 3E type.  Type 4E is implemented but has not been fully tested.  
Type 1C~4C is not supported.  

## Supported PLC series
- Q Series
- L Series
- QnA Series
- iQ-L Series
- iQ-R Series

A and FX series are not supportted because they does not support 3E or 4E type.

## How to use pymelsec 
### 1. Set up PLC
You need to open PLC's port for MELSEC Communication by GxWorks2 or GxWorks3 software.  
1. [Mitsubishi PLC manuals](https://www.mitsubishielectric.com/app/fa/download/search.do?kisyu=/plcr&mode=manual)
    1. Set IP address for PLC.
    1. Set network port for PLC, but default port should be 5007.

| Port Number | Application |
| --- | --- |
| 0x1388 (5000) | For future extension (For Q series Ethernet modules, this port number is used for "Auto Open UDP Port".) |
| 0x1389 (5001) | For future extension (For Q series Ethernet modules, this port number is used for "over UDP/IP and Ethernet module".) |
| 0x138A (5002) | For future extension (For Q series Ethernet modules, this port number is used for "over TCP/IP and Ethernet module".) |
| 0x138B (5003) to 0x138D (5005) | For future extension |
| 0x138E (5006) | MELSOFT communication port (over UDP/IP and CPU module) |
| 0x138F (5007) | MELSOFT communication port (over TCP/IP and CPU module) |
| 0x1390 (5008) | MELSOFT direct connection port (over CPU module |
| 0x1391 (5009) | For future extension |


### 2. Connect and Send Commands
```python
from datetime import datetime
from pymelsec import Type3E, Type4E
from pymelsec.constants import DT
from pymelsec.tag import Tag


__READ_TAGS = [
    Tag(device="X0", type=DT.BIT),      # BIT
    Tag(device="X1", type=DT.BIT),      # BIT
    Tag(device="X2", type=DT.BIT),      # BIT
    Tag(device="X3", type=DT.BIT),      # BIT
    Tag(device="D200", type=DT.SWORD),  # WORD signed
    Tag(device="D201", type=DT.UWORD),  # WORD unsigned
    Tag(device="D202", type=DT.SDWORD), # DWORD signed
    Tag(device="D204", type=DT.UDWORD), # DWORD unsigned
    Tag(device="D206", type=DT.FLOAT),  # FLOAT
    Tag(device="D208", type=DT.DOUBLE), # DOUBLE
    Tag(device="D300", type=DT.SLWORD), # LWORD signed (unofficial)
    Tag(device="D304", type=DT.ULWORD), # LWORD unsigned (unofficial)
]

__WRITE_TAGS = [
    Tag(device="X0", value=0, type=DT.BIT),                     # BIT
    Tag(device="X1", value=1, type=DT.BIT),                     # BIT
    Tag(device="X2", value=0, type=DT.BIT),                     # BIT
    Tag(device="X3", value=1, type=DT.BIT),                     # BIT
    Tag(device="D200", value=-20000, type=DT.SWORD),            # WORD signed
    Tag(device="D201", value=20100, type=DT.UWORD),             # WORD unsigned
    Tag(device="D202", value=-20200000, type=DT.SDWORD),        # DWORD signed
    Tag(device="D204", value=20400000, type=DT.UDWORD),         # DWORD unsigned
    Tag(device="D206", value=-206.206206, type=DT.FLOAT),       # FLOAT
    Tag(device="D208", value=208.208208208208, type=DT.DOUBLE), # DOUBLE
    Tag(device="D300", value=-10000000, type=DT.SLWORD),        # LWORD signed (unofficial)
    Tag(device="D304", value=10000000, type=DT.ULWORD),         # LWORD unsigned (unofficial)
]

__HOST = '192.168.1.15' # REQUIRED
__PORT = 5007           # OPTIONAL: default is 5007
__PLC_TYPE = 'iQ-R'     # OPTIONAL: default is 'Q'
                        #   options: 'L', 'QnA', 'iQ-L', 'iQ-R'

with Type4E(host=__HOST, port=__PORT, plc_type=__PLC_TYPE) as plc:
    """
    Set communication access mode option
        example: read 5 contiguous words starting from "D0" to "D4"

    Args:
        comm_type(str)[Optional]: the communication access mode option
            example: comm_type="binary" (default)
                     comm_type="ascii"
    """
    plc.set_access_opt(comm_type="binary")



    """
    Write mixed devices
        example: write randomly mixed data types

    Args:
        devices(list[Tag])[Required]: list of data class Tag
            example: devices=__WRITE_TAGS
    Returns:
        result(list[Tag]): list of incorrectly defined Tag
            example:
                [
                    Tag(
                        device='X0',
                        value=1,
                        type='X',
                        error=DataTypeError('Data type "X" is not supported.')
                    )
                ]
    Notes:
        look at __WRITE_TAGS to understand named tuple setup
    """
    plc.write(devices=__WRITE_TAGS)



    """
    Read mixed devices
        example: read randomly mixed data types

    Args:
        devices(list[Tag])[Required]: list of data class Tag
            example: devices=__WRITE_TAGS
    Returns:
        result(list[Tag]): list of Tag
            example:
                [
                    Tag(device='X0',value=False,type='BIT',error=''),
                    ...
                    Tag(device='D208',value=208.208208208208,type='DOUBLE',error='')
                ]
    Notes:
        look at __READ_TAGS to understand named tuple setup
        error status shows error reason
            example:
                [
                    Tag(
                        device='X0',
                        value=None,
                        type='X',
                        error=DataTypeError('Data type "X" is not supported.')
                    )
                ]
        to access the fields of each entry in result
            for tag in read_result:
                print((f'device:{tag.device}, '
                        f'value:{tag.value}, '
                        f'data_type:{tag.type}, '
                        f'status:{tag.error}'))
    """
    read_result = plc.read(devices=__READ_TAGS)



    """
    Write a sequence of data types
        example: write 5 consecutive signed words starting at "D100"

    Args:
        ref_device(str)[Required]: the reference device
            example: ref_device="D100"
        read_size(int)[Required]: number of points to read
            example: read_size=5
        data_type(str)[Required]: data type
            example: data_type=DT.SWORD
    Notes:
        look at __READ_TAGS to understand named tuple setup
        error status shows error reason
            example:
                [
                    Tag(
                        device='X0',
                        value=None,
                        type='X',
                        error=DataTypeError('Data type "X" is not supported.')
                    )
                ]
        to access the fields of each entry in result
            for tag in read_result:
                print((f'device:{tag.device}, '
                        f'value:{tag.value}, '
                        f'data_type:{tag.type}, '
                        f'status:{tag.error}'))
    """
    plc.batch_write(
        ref_device="D100",
        values=[-100,100,-1000,1000,10000],
        data_type=DT.SWORD
    )
    # additional examples:
    plc.batch_write(
        ref_device="D100",
        values=[-100.0,100.1,-1000.2,1000.3,10000.4],
        data_type=DT.FLOAT
    )
    # any of these bit representation is valid
    plc.batch_write(
        ref_device="X0",
        values=[False,True,False,True,False],
        data_type=DT.BIT
    )
    plc.batch_write(
        ref_device="X0",
        values=[0,1,0,1,0],
        data_type=DT.BIT
    )
    plc.batch_write(
        ref_device="X0",
        values=[False,1,0,True,0],
        data_type=DT.BIT
    )


    """
    Read a sequence of data types
        example: read 5 consecutive signed words starting at "D100"

    Args:
        ref_device(str)[Required]: the reference device
            example: ref_device="D100"
        read_size(int)[Required]: number of points to read
            example: read_size=5
        data_type(str)[Required]: data type
            example: data_type=DT.SWORD
        bool_encode(bool): encode boolean value when reading bits
            example: bool_encode=False (default)
                     bool_encode=True
        decode(bool): decode data or keep as raw bytes
            example: decode=True (default)
                     decode=False
    Returns:
        result(list[Tag]): list of Tag
            example:
                [
                    Tag(device='D100',value=-100,type='SWORD',error=''),
                    ...
                    Tag(device='D104',value=10000,type='SWORD',error='')
                ]
    Notes:
        look at __READ_TAGS to understand named tuple setup
        error status shows error reason
            example:
                [
                    Tag(
                        device='X0',
                        value=None,
                        type='X',
                        error=DataTypeError('Data type "X" is not supported.')
                    )
                ]
        to access the fields of each entry in result
            for tag in read_result:
                print((f'device:{tag.device}, '
                        f'value:{tag.value}, '
                        f'data_type:{tag.type}, '
                        f'status:{tag.error}'))
    """
    read_result = plc.batch_read(
        ref_device="D100", 
        read_size=5, 
        data_type=DT.SWORD
    )
    # additional examples:
    # read raw bytes
    read_result = plc.batch_read(
        ref_device="D100", 
        read_size=5, 
        data_type=DT.SWORD, 
        decode=False
    )
    # read bits and return type boolean
    read_result = plc.batch_read(
        ref_device="X0", 
        read_size=5, 
        data_type=DT.BIT, 
        bool_encode=True
    )

```

### 4.  Utility Functions
These commands are available if you connect via Ethernet communication module (E71 module).  
If you connect to PLC directly, C059 error returns.

```python
with Type4E(host=__HOST, port=__PORT, plc_type=__PLC_TYPE) as plc:
    """
    Unlock PLC

    Args:
        password(str):          password in clear text to be sent (unencrypted)
            example: password="1234"
        request_input(bool):    enter password interactively instead of hardcoded
            example: request_input=False (default)
                     request_input=True to enter password directly from user input
    Notes:
        Except iQ-R, password is 4 characters.
    """
    plc.remote_unlock(password="1234")
    plc.remote_unlock(password="", request_input=True)



    """
    Lock PLC

    Args:
        password(str)[Optional]:        password in clear text to be sent (unencrypted)
            example: password="1234"
        request_input(bool)[Optional]:  set password interactively instead of hardcoded
            example: request_input=False (default)
                     request_input=True to set password directly from user input
    Notes:
        Except iQ-R, password is 4 characters.
    """
    plc.remote_lock(password="1234")
    plc.remote_lock(request_input=True)



    """
    Set PLC to run

    Args:
        clear_mode(int): clear memory mode
            example: clear_mode=0 (default) do not clear
                     clear_mode=1 clear except latch device
                     clear_mode=2 clear all
        force_exec(bool): Force execution if controlled by other devices.
            example: force_exec=False (default)
                     force_exec=True
    """
    plc.remote_run(clear_mode=2, force_exec=True)



    """
    Set PLC to stop
    """
    plc.remote_stop()



    """
    Clear latched memory

    Notes:
        PLC must be stop when use this command.
    """
    plc.remote_latch_clear()



    """
    Set PLC to pause

    Args:
        force_exec(bool): boolean to signal force execution
    Notes:
        default is False
    """
    plc.remote_pause(force_exec=False)



    """
    Set PLC to be reset

    Notes:
        PLC must be stop when use this command.
    """
    plc.remote_reset()



    """
    Read CPU model

    Returns:
        CPUModel(named tuple): contains fields "name" and "code"
        example: CPUModel(name='R08ENCPU', code='4806')
    Notes:
        to access field name: cpu_model.name (e.g. 'R08ENCPU')
        to access field code: cpu_model.code (e.g. '4806')
    """
    cpu_model = plc.read_cpu_model()



    """
    Read PLC status

    Returns:
        CPUStatus(named tuple): contains fiels "status" and "cause"
        example: CPUStatus(status='Stop', cause='By Error')
    Notes:
        to access field status: cpu_state.status (e.g. 'Stop')
        to access field cause: cpu_state.cause (e.g. 'By Error')
    """
    cpu_state = plc.read_cpu_status()



    """
    Initialize LED display and error information of 
    buffer memory, and recover the supported device.
    """
    plc.error_led_off()



    """
    Turn off indicator error led

    Args:
       channel(int): the channel to control
           example: channel=1 (default) to turn off channel 1
                    channel=2 to turn off channel 2
                    channel=3 to turn off channel 1 & 2
    Notes:
        Channels are only applicable for Q/L series
    """
    plc.indicator_led_off(channel=1)



    """
    Read PLC physical switch status

    Returns:
        status(str): status of the switch
            example: "Run"
    """
    plc_switch_status = plc.read_switch_status()



    """
    Read PLC time

    Returns:
        datetime object
            example: 2022-08-23 00:07:34
    Notes:
        PLC only has precision at seconds level
    """
    plc_time = plc.read_plc_time()



    """
    Synchronize PLC time to PC

    Args:
        utc(bool):  flag to set to UTC time       
            exaple: utc=False   (default) to set to PC time
                    utc=True    to set to UTC time
    Returns:
        PLC time as a datetime object
            example: 2022-08-23 07:18:42.888054
    Notes:
        PLC only has precision at seconds level
    """
    synced_time = plc.sync_plc_time(utc=False)



    """
    Set PLC time

    Args:
        dt(datetime): datetime object
            example: dt=datetime.now()      to use current PC time
                     dt=datetime.utcnow()   to use UTC time
                     dt=datetime(2022, 8, 22, 10, 11, 12)
    Returns:
        The datetime object used
            example: 2022-08-23 07:18:42.888054
    Notes:
        PLC only has precision at seconds level
    """
    set_time = plc.set_plc_time(dt=datetime.now())



    """
    Request loopback test

    Args:
        echo_data(str): payload to be echo'd back.
            example: echo_data='testing'
    Returns:
        LoopbackTest(NamedTuple): the result and its length
            example: LoopbackTest(length=7, data='testing')
    Notes:
        echo_data only accepts ASCII chars
        to access data length: loopback_result.length (e.g. 7)
        to aaccess data string: loopback_result.data (e.g. 'testing')
    """
    loopback_result = plc.loopback_test(echo_data="testing")

```