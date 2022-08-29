""" 
This file implements MELSEC Communication type 4E.
"""

import struct

from . import constants as const
from .type3e import Type3E


class Type4E(Type3E):
    """
    MELSEC Communication type 3E class.

    Type 4e is almost same to Type 3E. Difference is only subheader.
    So, Changed self.subhear and self._build_send_data()

    Arributes:
        subheader(int):         Subheader for MELSEC Communication
        subheader_serial(int):  Subheader serial for MELSEC Communication to identify client
    """
    subheader           = 0x5400
    subheader_serial    = 0X0000


    def set_subheader_serial(self, subheader_serial:int):
        """
        Change subheader serial

        Args:
            subheader_serial(int):   Subheader serial to change

        """
        if(0 <= subheader_serial <= 65535):
            self.subheader_serial = subheader_serial
        else:
            raise ValueError("subheader_serial must be 0 <= subheader_serial <= 65535") 
        return None


    def _get_response_data_index(self) -> int:
        """
        Get response data index from return data byte.
        4e type's data index is defferent from 3e type's.
        """
        if self.comm_type == const.COMMTYPE_BINARY:
            return 15
        else:
            return 30


    def _get_response_status_index(self) -> int:
        """
        Get command status index from return data byte.
        """
        if self.comm_type == const.COMMTYPE_BINARY:
            return 13
        else:
            return 26


    def _build_send_data(self, request_data:bytes) -> bytes:
        """
        Build send MELSEC Communication data.

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
        mc_data += self._encode_value(self.subheader_serial, const.DT.SWORD)
        mc_data += self._encode_value(0, const.DT.SWORD)
        mc_data += self._encode_value(self.network, const.DT.BIT)
        mc_data += self._encode_value(self.pc, const.DT.BIT)
        mc_data += self._encode_value(self.dest_moduleio, const.DT.SWORD)
        mc_data += self._encode_value(self.dest_modulesta, const.DT.BIT)
        #add self.timer size
        mc_data += self._encode_value(self._wordsize + len(request_data), const.DT.SWORD)
        mc_data += self._encode_value(self.timer, const.DT.SWORD)
        mc_data += request_data
        return mc_data
