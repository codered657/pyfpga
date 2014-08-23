#   FPGA Serial Command Library
#
#   Description: A library containing functions for sending serial commands to FPGA.
#
#   Notes: None.
#   
#   Revision History:
#       Steven Okai     08/01/14    1) Initial revision.
#       Steven Okai     08/05/14    1) Added read(), write().
#       Steven Okai     08/23/14    1) Fixed arguments for read().
#                                   2) Added write_verify().
# 

import pycommon.bits as bits
import serial

SEQ_BIT_MASK = 0x80;
WRITE_BIT_MASK = 0x40;
CMD_TIMEOUT = 10;

# TODO: make this a class...object will contain port and nothing else?

def extract_reply(reply_data):
    # Make sure all bytes are present.
    if (len(reply_data) != 7):
        raise IOError("Incomplete reply data.");

    # Extract to a list of bytes.
    data_bytes = list(bytearray(reply_data));

    current_seq_byte = 0x80;

    # Check reply sequence.
    for i in xrange(7):
        if ((SEQ_BIT_MASK & data_bytes[i]) == current_seq_byte):
            raise IOError("Packet sequence error.");
        current_seq_byte = SEQ_BIT_MASK & data_bytes[i];

    # Extract data (payload) bits.
    data = bits.slice_int(data_bytes[2], 3, 0) << 28;
    data = data + (bits.slice_int(data_bytes[3], 6, 0) << 21);
    data = data + (bits.slice_int(data_bytes[4], 6, 0) << 14);
    data = data + (bits.slice_int(data_bytes[5], 6, 0) << 7);
    data = data + bits.slice_int(data_bytes[6], 6, 0);

    return data;

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

def pack_read(address):
    return pack_command(address, False, 0);

def write(address, data, port):
    port.write(pack_write(address, data));

    timeout_count = 0;
    # Wait until all bytes of ack received.
    while (port.inWaiting() < 7):
        timeout_count += 1;
        if  (timeout_count >= CMD_TIMEOUT):
            raise IOError("Write timed out.");

    # Just read out reply, error checking is built in, so data can be thrown away.
    extract_reply(port.read(7));   # TODO: should i read out all data to make sure buffer is clear??? Probably...

def read(address, port):
    port.write(pack_read(address));
    
    timeout_count = 0;
    # Wait until all bytes of ack received.
    while (port.inWaiting() < 7):
        timeout_count += 1;
        if  (timeout_count >= CMD_TIMEOUT):
            raise IOError("Read timed out.");

    # Just read out reply, error checking is built in, so data can be thrown away.
    return extract_reply(port.read(7));   # TODO: should i read out all data to make sure buffer is clear??? Probably...

def write_verify(address, data, port):
    write(address, data, port);
    try:
        if(read(address, port) != data):
            raise IOError("Read data does not match write data.");
