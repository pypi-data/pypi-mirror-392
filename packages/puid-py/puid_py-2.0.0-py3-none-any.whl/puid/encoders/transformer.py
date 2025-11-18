from math import ceil, log2
from typing import Callable, Tuple

from puid.bits import bitShifts, isPow2, value_at


def accept_value_for(chars: str) -> Callable[[int], Tuple[bool, int]]:
    """Create an accept/reject function for a character set."""
    n_chars = len(chars)
    n_bits_per_char = ceil(__import__('math').log2(n_chars))
    
    if isPow2(n_chars):
        def always_accept(value: int) -> Tuple[bool, int]:
            return (True, n_bits_per_char)
        return always_accept
    
    shifts = bitShifts(n_chars)
    
    def accept_value_func(value: int) -> Tuple[bool, int]:
        if value < n_chars:
            return (True, n_bits_per_char)
        
        if len(shifts) == 1:
            return (False, shifts[0][1])
        
        bit_shift = [bs for bs in shifts if value <= bs[0]]
        return (False, bit_shift[0][1])
    
    return accept_value_func


def encode(chars: str, byte_data: bytearray) -> str:
    """
    Encode bytes into a string using the provided character set.

    Example:
        >>> from puid import Chars
        >>> bytes_data = bytearray([0x09, 0x25, 0x84, 0x3c, 0xbd, 0xc0, 0x89, 0xeb,
        ...                         0x61, 0x75, 0x81, 0x65, 0x09, 0xb4, 0x9a, 0x54, 0x20])
        >>> encode(Chars.SAFE64, bytes_data)
        'CSWEPL3AiethdYFlCbSaVC'
    """
    n_bits_per_char = ceil(log2(len(chars)))
    n_entropy_bits = 8 * len(byte_data)

    if n_entropy_bits == 0:
        return ''

    # Support both ValidChars and raw string
    charset = chars.value if hasattr(chars, 'value') else chars
    char_codes = [ord(c) for c in charset]

    accept_func = accept_value_for(charset)

    offset = 0
    codes = []

    while offset + n_bits_per_char <= n_entropy_bits:
        v = value_at(offset, n_bits_per_char, byte_data)
        accept, shift = accept_func(v)
        offset += shift
        if accept:
            codes.append(char_codes[v])

    return ''.join(chr(code) for code in codes)


def decode(chars: str, text: str) -> bytearray:
    """
    Decode a string of characters back into bytes using the provided character set.
    Pads the final partial byte with zeros if the bit-length is not a multiple of 8.

    Example:
        >>> from puid import Chars
        >>> text = 'CSWEPL3AiethdYFlCbSaVC'
        >>> bytes_data = decode(Chars.SAFE64, text)
        >>> len(bytes_data)
        17
    """
    charset = chars.value if hasattr(chars, 'value') else chars
    n_bits_per_char = ceil(log2(len(charset)))

    if not text:
        return bytearray()

    char_map = {char: idx for idx, char in enumerate(charset)}

    acc = 0
    acc_bits = 0
    out = []

    for char in text:
        if char not in char_map:
            raise ValueError(f'Invalid character for charset: {char}')

        val = char_map[char]
        acc = (acc << n_bits_per_char) | val
        acc_bits += n_bits_per_char

        while acc_bits >= 8:
            shift = acc_bits - 8
            byte_val = (acc >> shift) & 0xff
            out.append(byte_val)
            acc_bits -= 8
            acc = acc & ((1 << acc_bits) - 1)

    if acc_bits > 0:
        out.append((acc << (8 - acc_bits)) & 0xff)

    return bytearray(out)
