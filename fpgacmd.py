import pycommon.bits as bits

SEQ_BIT_MASK = 0x80
WRITE_BIT_MASK = 0x40

def extract_reply(reply_data):
    # Make sure all bytes are present.
    assert len(reply_data) == 7;

    # Extract to a list of bytes.
    data_bytes = list(bytearray(reply_data));

    current_seq_byte = 0x80;

    # Check reply sequence.
    for i in xrange(7):
        assert ((SEQ_BIT_MASK & data_bytes[i]) != current_seq_byte);
        current_seq_byte = SEQ_BIT_MASK & data_bytes[i];

    # Extract data (payload) bits.
    data = bits.slice_int(data_bytes[2], 3, 0) << 28;
    data = data + (bits.slice_int(data_bytes[3], 6, 0) << 21);
    data = data + (bits.slice_int(data_bytes[4], 6, 0) << 14);
    data = data + (bits.slice_int(data_bytes[5], 6, 0) << 7);
    data = data + bits.slice_int(data_bytes[6], 6, 0);

    return data;
#   FPGA Serial Command Library
#
#   Description: A library containing functions for sending serial commands to FPGA.
#
#   Notes: None.
#   
#   Revision History:
#       Steven Okai     08/01/14    1) Initial revision.
# 

def pack_command(address, write, data):
    command_bytes = [];

    # Apply write flag if it is a write command.
    if (write):
        command_bytes.append(WRITE_BIT_MASK);
    else:
        command_bytes.append(0);
        
    # Compose address.
    command_bytes[0] = command_bytes[0] | bits.slice_int(address, 15, 10);
    command_bytes.append(bits.slice_int(address, 9, 3) | SEQ_BIT_MASK);
    command_bytes.append(bits.slice_int(address, 2, 0) << 4);

    # Compose data.
    command_bytes[2] = command_bytes[2] | bits.slice_int(data, 31, 28) | SEQ_BIT_MASK;
    command_bytes.append(bits.slice_int(data, 27, 21));
    command_bytes.append(bits.slice_int(data, 20, 14) | SEQ_BIT_MASK);
    command_bytes.append(bits.slice_int(data, 13, 7));
    command_bytes.append(bits.slice_int(data, 6, 0) | SEQ_BIT_MASK);

    return command_bytes;

def pack_write(address, data):
    return pack_command(address, True, data);

def pack_read(address, data):
    return pack_command(address, False, data);
