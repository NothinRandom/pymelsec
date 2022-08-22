# pymelsec
A Python3 implementation of MELSEC Communication Protocol that allows you to interact with a Mitsubishi PLC.

## Installation 
```console 
pip3 install pymelsec
```

## Protocol type
pymelsec natively supports MELSEC Communication 3E type.  
4E type is implemented. But not tested.  
1C~4C type is not supported.  

## Supported PLC series
- Q Series
- L Series
- QnA Series
- iQ-L Series
- iQ-R Series

A and FX series are not supportted because they does not support 3E or 4E type.

## How to use mc protocol 
### 1. Set up PLC
You need to open PLC's port for MELSEC Communication by GxWorks2 or GxWorks3 software.  
1. Set IP address for PLC. PLC manuals: https://www.mitsubishielectric.com/app/fa/download/search.do?kisyu=/plcr&mode=manual
  1. Default port should be 5007

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
    Tag(device="X0", type=DT.BIT),      # Test BIT
    Tag(device="X1", type=DT.BIT),      # Test BIT
    Tag(device="X2", type=DT.BIT),      # Test BIT
    Tag(device="X3", type=DT.BIT),      # Test BIT
    Tag(device="D200", type=DT.sWORD),  # Test WORD signed
    Tag(device="D201", type=DT.uWORD),  # Test WORD unsigned
    Tag(device="D202", type=DT.sDWORD), # Test DWORD signed
    Tag(device="D204", type=DT.uDWORD), # Test DWORD unsigned
    Tag(device="D206", type=DT.FLOAT),  # Test FLOAT
    Tag(device="D208", type=DT.DOUBLE), # Test DOUBLE
]

__WRITE_TAGS = [
    Tag(device="X0", value=0, type=DT.BIT),                     # Test BIT
    Tag(device="X1", value=1, type=DT.BIT),                     # Test BIT
    Tag(device="X2", value=0, type=DT.BIT),                     # Test BIT
    Tag(device="X3", value=1, type=DT.BIT),                     # Test BIT
    Tag(device="D200", value=-20000, type=DT.sWORD),            # Test WORD signed
    Tag(device="D201", value=20100, type=DT.uWORD),             # Test WORD unsigned
    Tag(device="D202", value=-20200000, type=DT.sDWORD),        # Test DWORD signed
    Tag(device="D204", value=20400000, type=DT.uDWORD),         # Test DWORD unsigned
    Tag(device="D206", value=-206.206206, type=DT.FLOAT),       # Test FLOAT
    Tag(device="D208", value=208.208208208208, type=DT.DOUBLE), # Test DOUBLE
]

### NOTE:
# LWORD (signed/unsigned) is not available in Mitsubishi,
# but we can technically support since it occupies 8 bytes like a DOUBLE.

__HOST = '192.168.1.15' # REQUIRED
__PORT = 5007           # OPTIONAL: default is 5007
__PLC_TYPE = 'iQ-R'     # OPTIONAL: default is 'Q'
                        # options: 'L', 'QnA', 'iQ-L', 'iQ-R'

with Type4E(host=__HOST, port=__PORT, plc_type=__PLC_TYPE) as plc:
    # Use ascii byte communication, (Default is "binary")
    # plc.set_access_opt(comm_type="ascii")

    # read 5 contiguous words starting from "D0" to "D4"
    # Returns a list of int (e.g. [0, 10, 20, 30, 40])
    read_result = plc.batch_read_words(ref_device="D0", read_size=5)

    # read 5 contiguous bits starting from "X0" to "X10"
    # Returns a list of int (e.g. [0, 1, 1, 1, 1])
    # 0 is False, 1 is True
    read_result = plc.batch_read_bits(ref_device="X0", read_size=5)

    # write from "D0" to "D4"
    plc.batch_write_words(ref_device="D0", values=[0, 10, 20, 30, 40])

    # write from "Y0" to "Y4"
    plc.batch_write_bits(ref_device="Y0", values=[0, 1, 0, 1, 0])

    # read WORDS "D1000" and "D2000", and DWORD "D3000".
    word_result, dword_result = plc.random_read(word_devices=["D1000", "D2000"], dword_devices=["D3000"])

    # write 10 to "D10", 20 to "D20", and 655362 to DWORD "D3000"
    plc.random_write(
        word_devices=["D1000", "D1002"],
        word_values=[1000, 2000], 
        dword_devices=["D1004"],
        dword_values=[655362]
    )

    # write 1(ON) to "X0", 0(OFF) to "X10"
    plc.random_write_bits(bit_devices=["X0", "X10"], values=[1, 0])

    # write randomly mixed data types
    plc.write(devices=__WRITE_TAGS)

    # read randomly mixed data types
    read_result = plc.read(devices=__READ_TAGS)
```

### 4.  Utility Functions
If you connect to your system by E71 module, Ethernet communication module,  
These commands are available.  

If you connect to PLC directly, C059 error returns.
```python
with Type4E(host=__HOST, port=__PORT, plc_type=__PLC_TYPE) as plc:

    # Unlock PLC
    # Except iQ-R, password is 4 character.
    plc.remote_unlock(password="1234")
    # If you want to hide password from program
    # You can enter password directly
    plc.remote_unlock(request_input=True)

    # Lock PLC
    plc.remote_lock(password="1234")
    plc.remote_lock(request_input=True)

    # remote run, clear all device
    plc.remote_run(clear_mode=2, force_exec=True)

    # remote stop
    plc.remote_stop()

    # remote latch clear. (have to PLC be stopped)
    plc.remote_latch_clear()

    # remote pause
    # force to pause with force_exec=True
    plc.remote_pause(force_exec=False)

    # remote reset
    plc.remote_reset()

    # read PLC type
    # returns a tuple
    cpu_info = plc.read_cpu_type()
    # access name: cpu_info.type (e.g. 'R08ENCPU')
    # access code: cpu_info.code (e.g. '4806')

    # read PLC status -> returns a tuple
    cpu_state = plc.read_cpu_status()
    # access status: cpu_state.status (e.g. 'Stop')
    # access cause: cpu_state.cause (e.g. 'By Error')

    # turn off error led
    plc.error_led_off()

    # turn off indicator error led
    # Q/L series:
    # * turn off channel 1: channel=1 (default)
    # * turn off channel 2: channel=2
    # * turn off channel 1/2: channel=3
    plc.indicator_led_off(channel=1)

    # read PLC physical switch
    plc_status = plc.read_switch_status()

    # read PLC time
    # returns datetime object
    plc_time = plc.read_plc_time()

    # sync PLC time
    # returns the set time
    # set to host time: utc=False (default)
    # set to UTC time: utc=True
    synced_time = plc.sync_plc_time(utc=False)

    # set PLC time
    # input takes dattime object
    # returns the set time
    # set to current host time: dt=datetime.now()
    # set to utc time: dt=datetime.utcnow()
    set_time = plc.set_plc_time(dt=datetime.now())

    # request loopback test
    # input only accepts ASCII characters
    # returns tuple
    loopback_result = plc.loopback_test(echo_data="hello")
    # access data length: loopback_result.length
    # access data string: loopback_result.data

```