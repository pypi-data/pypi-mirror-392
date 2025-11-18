from enum import Enum
from typing import Dict, NamedTuple
from math import ceil, log2, pow

from puid.chars_error import InvalidChars, NonUniqueChars, TooFewChars, TooManyChars

MIN_CHARS = 2
MAX_CHARS = 256
VALID_CHAR_MIN_CODE = 160
INVALID_CHAR_THRESHOLD = ord('~')


def valid_chars(chars):
    """
    Tests whether characters are valid.

    raises A CharsError subclass if characters are not valid.

    >>> valid_chars(Chars.HEX)
    True

    >>> valid_chars('dingosky')
    True
    """
    if isinstance(chars, Chars):
        return True

    if not isinstance(chars, str):
        raise InvalidChars('Characters must be a str')

    min_len = MIN_CHARS
    max_len = MAX_CHARS

    if len(chars) < min_len:
        raise TooFewChars(f'Must have at least {min_len} characters')

    if 256 < len(chars):
        raise TooManyChars(f'Exceeded max of {max_len} characters')

    if len(chars) != len(set(chars)):
        raise NonUniqueChars('Characters are not unique')

    for char in chars:
        if not _valid_char(char):
            raise InvalidChars(f'Invalid character with code: {ord(char)}')

    return True


def _valid_char(char):
    code_point = ord(char)

    if VALID_CHAR_MIN_CODE < code_point:
        return True

    if char == '!':
        return True
    if code_point < ord('#'):
        return False
    if char == "'":
        return False
    if char == '\\':
        return False
    if char == '`':
        return False
    if INVALID_CHAR_THRESHOLD < code_point:
        return False

    return True


class Chars(Enum):
    """
    Predefined Characters

    These enums are intended to be passed to the `Puid` class initializer for configuration
    """

    ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    ALPHA_LOWER = 'abcdefghijklmnopqrstuvwxyz'
    ALPHA_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ALPHANUM = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ALPHANUM_LOWER = 'abcdefghijklmnopqrstuvwxyz0123456789'
    ALPHANUM_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    BASE16 = '0123456789ABCDEF'
    BASE32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    BASE32_HEX = '0123456789abcdefghijklmnopqrstuv'
    BASE32_HEX_UPPER = '0123456789ABCDEFGHIJKLMNOPQRSTUV'
    CROCKFORD32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
    DECIMAL = '0123456789'
    HEX = '0123456789abcdef'
    HEX_UPPER = '0123456789ABCDEF'
    SAFE_ASCII = '!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}~'
    SAFE32 = '2346789bdfghjmnpqrtBDFGHJLMNPQRT'
    SAFE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    SYMBOL = '!#$%&()*+,-./:;<=>?@[]^_{|}~'
    WORD_SAFE32 = '23456789CFGHJMPQRVWXcfghjmpqrvwx'

    def __len__(self):
        return len(self.value)


class ValidChars:
    """Base class for PredefinedChars and CustomChars"""

    __slots__ = ('name', 'value')

    def __repr__(self):
        return "{0} -> '{1}'".format(self.name, self.value)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)


class PredefinedChars(ValidChars):
    """
    Class for Predefined Chars

    raises InvalidChars if initialized with anything other than a predefined Chars enum

    >>> hex_upper = PredefinedChars(Chars.HEX_UPPER)

    This class is intended for internal use
    """

    def __init__(self, chars):
        """
        Create a PredefinedChars for Chars enum

        :param chars: Chars enum
        """
        if isinstance(chars, Chars):
            self.name = chars.name
            self.value = chars.value
        else:
            raise InvalidChars('PredefinedChars only accepts members of the Chars enum')


class CustomChars(ValidChars):
    """
    Class for Custom Chars

    raises CharsError if initialized with an string of characters that are invalid
    raises InvalidChars if initialized with a predefined Chars enum

    >>> dingosky = CustomChars('dingosky')

    This class is intended for internal use
    """

    def __init__(self, chars):
        """
        Create a CustomChars for a string of characters

        :param chars: A valid string of characters
        """
        if isinstance(chars, Chars):
            raise InvalidChars('Use class PredefinedChars for members of the Chars enum')
        else:
            valid_chars(chars)
            self.name = 'Custom'
            self.value = chars


class CharMetrics(NamedTuple):
    """Metrics for a character set including entropy transform efficiency."""
    avg_bits: float
    ere: float
    ete: float


def _bits_consumed_on_reject(
    charset_size: int, total_values: int, shifts: list
) -> int:
    """Calculate total bits consumed when rejecting values."""
    sum_bits = 0
    for value in range(charset_size, total_values):
        bit_shift = None
        for bs in shifts:
            if value <= bs[0]:
                bit_shift = bs
                break
        if bit_shift is None:
            raise ValueError('Invalid bit_shifts: missing range')
        sum_bits += bit_shift[1]
    return sum_bits


def _avg_bytes_per_char(chars: str) -> float:
    """Calculate average byte size per character for a string."""
    total_bytes = len(chars.encode('utf-8'))
    return total_bytes / len(chars)


def metrics(chars: str) -> CharMetrics:
    """
    Calculate entropy metrics for a character set.

    Returns a CharMetrics object with:
    - avgBits: Average bits consumed per character during generation
    - ere: Entropy representation efficiency (0 < ERE ≤ 1.0)
    - ete: Entropy transform efficiency (0 < ETE ≤ 1.0)

    Example:
        >>> metrics(Chars.SAFE64.value).ete
        1.0
    """
    from puid.bits import isPow2, bitShifts

    charset_size = len(chars)
    bits_per_char = ceil(log2(charset_size))
    theoretical_bits = log2(charset_size)
    shifts = bitShifts(charset_size)

    avg_rep_bits_per_char = _avg_bytes_per_char(chars) * 8
    ere = theoretical_bits / avg_rep_bits_per_char

    if isPow2(charset_size):
        return CharMetrics(
            avg_bits=float(bits_per_char),
            ere=round(ere, 4),
            ete=1.0
        )

    total_values = pow(2, bits_per_char)
    prob_accept = charset_size / total_values
    prob_reject = 1 - prob_accept

    reject_count = total_values - charset_size
    reject_bits = _bits_consumed_on_reject(charset_size, int(total_values), shifts)

    avg_bits_on_reject = reject_bits / reject_count
    avg_bits = bits_per_char + (prob_reject / prob_accept) * avg_bits_on_reject

    ete = theoretical_bits / avg_bits

    return CharMetrics(
        avg_bits=avg_bits,
        ere=round(ere, 4),
        ete=round(ete, 4)
    )


if __name__ == '__main__':  # pragma: no cover
    import doctest

    doctest.testmod()
