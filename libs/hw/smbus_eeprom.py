from math import ceil
from time import sleep

def write_to_16bit_eeprom(bus, address, data, bs=32, sleep_time=0.01):
    """
    Writes to a 16-bit EEPROM. Only supports starting from 0x0000, for now.
    (to add other start addresses, you'll want to improve the block splitting mechanism)
    Will raise an IOError with e.errno=121 if the EEPROM is write-protected.
    Default write block size is 32 bytes per write.
    By default, sleeps for 0.01 seconds between writes (otherwise, errors might occur).
    Pass sleep_time=0 to disable that (at your own risk).
    """
    b_l = len(data)
    # Last block may not be complete if data length not divisible by block size
    b_c = int(ceil(b_l/float(bs))) # Block count
    # Actually splitting our data into blocks
    blocks = [data[bs*x:][:bs] for x in range(b_c)]
    for i, block in enumerate(blocks):
        if sleep_time:
            sleep(sleep_time)
        start = i*bs
        hb, lb = start >> 8, start & 0xff
        data = [hb, lb]+block
        write = i2c_msg.write(address, data)
        bus.i2c_rdwr(write)

def read_from_16bit_eeprom(bus, address, count, bs=32):
    """
    Reads from a 16-bit EEPROM. Only supports starting from 0x0000, for now.
    (to add other start addresses, you'll want to improve the block splitting mechanism)
    Default read block size is 32 bytes per read.
    """
    data = [] # We'll add our reads to here
    # If read count is not divisible by block size,
    # we'll have one partial read at the last read
    full_reads, remainder = divmod(count, bs)
    if remainder: full_reads += 1 # adding that last read if needed
    for i in range(full_reads):
        start = i*bs # next block address
        hb, lb = start >> 8, start & 0xff # into high and low byte
        write = i2c_msg.write(address, [hb, lb])
        # If we're on last cycle and remainder != 0, not doing a full read
        count = remainder if (remainder and i == full_reads-1) else bs
        read = i2c_msg.read(address, count)
        bus.i2c_rdwr(write, read) # combined read&write
        data += list(read)
    return data

def read_from_8bit_eeprom(bus, address, count, bs=16):
    """
    Reads from an 8-bit EEPROM. Only supports starting from 0x00, for now.
    (to add other start addresses, you'll want to improve the address counting mechanism)
    Default read block size is 16 bytes per read.
    """
    data = [] # We'll add our reads to here
    # If read count is not divisible by block size,
    # we'll have one partial read at the last read
    full_reads, remainder = divmod(count, bs)
    if remainder: full_reads += 1 # adding that last read if needed
    for i in range(full_reads):
        start = i*bs # next block address
        # If we're on last cycle and remainder != 0, not doing a full read
        count = remainder if (remainder and i == full_reads-1) else bs
        read = bus.read_i2c_block_data(address, start, count)
        data += list(read)
    return data

def write_to_8bit_eeprom(bus, address, data, bs=16, sleep_time=0.01):
    """
    Writes to an 8-bit EEPROM. Only supports starting from 0x00, for now.
    (to add other start addresses, you'll want to improve the block splitting mechanism)
    Will raise an IOError with e.errno=121 if the EEPROM is write-protected.
    Uses 16-byte blocks by default.
    By default, sleeps for 0.01 seconds between writes (otherwise, errors might occur).
    Pass sleep_time=0 to disable that (at your own risk).
    """
    b_l = len(data)
    b_c = int(ceil(b_l/float(bs))) # Block count
    # Actually splitting our data into blocks
    blocks = [data[bs*x:][:bs] for x in range(b_c)]
    for i, block in enumerate(blocks):
        start = i*bs # and append address in front of each one
        # So, we're sending 17 bytes in total
        bus.write_i2c_block_data(address, start, block)
        if sleep_time:
            sleep(sleep_time)

if __name__ == "__main__":
    from smbus2 import SMBus, i2c_msg
    # 8-bit, 0x50 on i2c1
    bus = SMBus(1)
    mul=6
    str="never gonna give you up! "
    data = [ord(c) for c in str]*mul
    write_to_8bit_eeprom(bus, 0x50, data)
    result = read_from_8bit_eeprom(bus, 0x50, len(data))
    assert(result == data)
    # 16-bit, 0x50 on i2c0
    #bus = SMBus(0)
    #mul=10
    #str="never gonna give you up never gonna let you down! "
    #data = [ord(c) for c in str]*mul
    #write_to_16bit_eeprom(bus, 0x50, data)
    #result = read_from_16bit_eeprom(bus, 0x50, len(data))
    #assert(result == data)

