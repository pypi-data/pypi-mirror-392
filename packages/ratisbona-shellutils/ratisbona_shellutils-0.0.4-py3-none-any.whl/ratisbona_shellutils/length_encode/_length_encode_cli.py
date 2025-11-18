import sys

import click

from ratisbona_shellutils.length_encode._length_encode import (
    encode_rep_text,
    decode_rep_text,
)
from ratisbona_utils import binary
from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint


@click.group()
def length_encode_cli():
    errprint(blue_dosbox("Ratisbona Length-Encode CLI"))


@length_encode_cli.command()
def to_int16():
    """
    Reads binary data from stdin and outputs it as a list of int16 values, which it prints to stdout.
    """
    bindata = sys.stdin.buffer.read()
    print(", ".join(str(x) for x in binary.to_int16(bindata)))


@length_encode_cli.command()
def encode():
    text = sys.stdin.read()
    encoded_data = encode_rep_text(text)
    sys.stdout.buffer.write(encoded_data)


@length_encode_cli.command()
def decode():
    bytes = sys.stdin.buffer.read()
    text = decode_rep_text(bytes)
    sys.stdout.write(text)

@length_encode_cli.command()
def to_short_program():
    """
    Reads binary data from stdin and outputs it as a list of int16 values, which it prints to stdout.
    """
    bindata = sys.stdin.buffer.read()
    length = int.from_bytes(bindata[:4], byteorder="little")
    char_map_bytes = bindata[4: length + 4]
    char_map = char_map_bytes.decode("utf8")
    bytecodes = bindata[length + 4:]
    int16s = ",".join([str(x) for x in binary.to_int16(bytecodes)])
    print(f"s={repr(char_map)}")
    print(f"for d in [{int16s}]:")
    print(" print(s[d>>4&15]*(d&15),end=s[d>>12&15]*(d>>8&15))")




@length_encode_cli.command()
def to_program():
    binary_data = sys.stdin.buffer.read()
    int16s = ",".join([str(x) for x in binary.to_int16(binary_data)])
    print(f"raw_data=[{int16s}]")
    print(
        """\
    
import sys
    
def utf8_num_bytes(the_first_byte: int) -> int:
    for count in range(0, 5):
        if not (the_first_byte & 0x80):
            if count == 0:
                return 1
            return count
        the_first_byte = (the_first_byte << 1) & 0xFF
    return 1

def nth_char_offset(the_bytes: bytes | bytearray, n: int, offset=0):
    for count in range(0, n + 1):
        if count >= n:
            return offset
        offset += utf8_num_bytes(the_bytes[offset])
        if offset >= len(the_bytes):
            raise IndexError(f"Index out of range. Cannot find {n} characters in byte array.")
    raise AssertionError("Code should never reach this point!")    
    
the_bytecode = bytearray([a_byte for number in raw_data for a_byte in [number & 0xFF, (number >> 8) & 0xFF]])
len_charmap = int.from_bytes(the_bytecode[0:4], 'little')

for a_byte in the_bytecode[4 + len_charmap:]:
    char_id = (a_byte >> 4) & 0x0F
    repeat_count = a_byte & 0x0F
    idx = nth_char_offset(the_bytecode, char_id, 4)
    lth = utf8_num_bytes(the_bytecode[idx])
    for _ in range(0, repeat_count):
        sys.stdout.buffer.write(the_bytecode[idx : idx + lth])
"""
    )


@length_encode_cli.command()
def to_obfuscated_program():
    binary_data = encode_rep_text(sys.stdin.read())
    int16s = ",".join([str(x) for x in binary.to_int16(binary_data)])
    print(f"import sys\n__,_3=sys,[{int16s}]")
    print(
        """\
_3,__=bytearray([_2 for _1 in _3 for _2 in [_1&255,(_1>>8)&255]]),__.stdout
def _2(_0):
 for _1 in range(0,8):
  if not(_0&0x80):return 1 if _1==0 else _1
  _0=(_0<<1)&0xFF
__=__.buffer
def _4(_0,_1=0):
 for _5 in range(0,_0+1):
  if _5>=_0:return _1
  _1+=_2(_3[_1])
__=__.write
for _0 in _3[4+(((((_3[3]<<8)+_3[2])<<8+_3[1])<<8)+_3[0]):]:
 _1,_5=(_0>>4)&0xF,_0&0xF
 for _6 in range(0, _5):
  _7=_4(_1,4)
  _8=_2(_3[_7])
  _9=__(_3[_7:_7+_8])
    """
    )
