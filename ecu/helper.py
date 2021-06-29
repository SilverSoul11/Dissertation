import can
from binascii import hexlify

def byte_arr_to_hex(byte_arr):
    ''' Takes a byte array and returns it's representation
    as a hex string beginning with 0x '''
    return '0x' + hexlify(byte_arr).decode('ascii')

def hex_to_byte_arr(hex_str):
    ''' Takes a hexadecimal string starting with 0x and returns the 
    equivelant byte array. Will also work without the 0x.'''
    if hex_str[0:2] == '0x':
        if len(hex_str) % 2 != 0:
            temp = '0' + hex_str[2:]
        else:
            temp = hex_str[2:]
        return bytearray.fromhex(temp)

def hex_to_decimal(hex_str):
    ''' Takes in a hex and returns the integer '''
    return int(hex_str, 16)

def decimal_to_byte_array(x):
    ''' takes in integer x and returns a byte array '''

def byte_arr_to_dec(byte_arr):
    return int('0x' + hexlify(byte_arr).decode('ascii'),16)
