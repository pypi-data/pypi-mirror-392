from math import ceil, log2, sqrt, trunc
from typing import Union

from puid.chars import ValidChars
from puid.chars_error import InvalidChars
from puid.puid_error import TotalRiskError


def bits_for_total_risk(total: Union[int, float], risk: Union[int, float]) -> float:
    """
    Entropy bits necessary to produce a `total` `puid`s with given `risk` of repeat

    :param total: int
    :param risk: int
    :return float

    >>> bits_for_total_risk(100_000, 1e12)
    72.08241808752197
    """

    def non_neg_int_or_float(value):
        if isinstance(value, int) and 0 <= value:
            return True
        if isinstance(value, float) and value.is_integer() and 0.0 <= value:
            return True
        return False

    if not non_neg_int_or_float(total) or not non_neg_int_or_float(risk):
        raise TotalRiskError('total and risk must be an non-negative integers')

    if total in [0, 1]:
        return 0

    if risk in [0, 1]:
        return 0

    return log2(total) + log2(total - 1) + log2(risk) - 1


def bits_per_char(chars: ValidChars) -> float:
    """
    Entropy bits per character for either a predefined Chars enum or a string of characters

    :param chars: Either a Chars enum or a string

    raises CharsError subclass if `chars` is invalid

    >>> bits_per_char(Chars.BASE32)
    5.0

    >>> bits_per_char('dingosky_me')
    3.4594316186372973
    """
    if isinstance(chars, ValidChars):
        return log2(len(chars))
    else:
        raise InvalidChars('chars must be an instance of ValidChars')


def bits_for_len(chars: ValidChars, len: int) -> int:
    """
    Bits necessary for a `puid` of length `len` using characters `chars`

    :param chars: Either a Chars enum or a string
    :param len: Desired length of `puid`

    raises CharsError subclass if `chars` is invalid

    >>> bits_for_len('dingosky', 14)
    42
    """
    return trunc(len * bits_per_char(chars))


def len_for_bits(chars: ValidChars, bits: Union[int, float]) -> int:
    """
    Length necessary for a `puid` of `bits` using characters `chars`

    :param chars: Either a Chars enum or a string
    :param bits: Desired `bits` of `puid`

    raises CharsError subclass if `chars` is invalid

    >>> len_for_bits(Chars.SAFE_ASCII, 97)
    15
    """
    return ceil(bits / bits_per_char(chars))


def risk_for_entropy(bits: Union[int, float], total: Union[int, float]) -> Union[int, float]:
    """
    Risk given entropy `bits` after `total` IDs.

    This approximation is conservative and will underestimate the true risk.

    :param bits: Entropy bits
    :param total: Total number of IDs
    :return: Risk of repeat (conservative approximation)

    >>> risk_for_entropy(96, 1.0e7)
    1584563250285288.0
    """
    if total in [0, 1]:
        return 0

    if bits <= 0:
        return 0

    n = log2(total) + log2(total - 1)
    return 2 ** (bits - n + 1)


def total_for_entropy(bits: Union[int, float], risk: Union[int, float]) -> Union[int, float]:
    """
    Total possible IDs given entropy `bits` and repeat `risk`.

    This exact inversion with flooring is conservative and will underestimate the true total.

    :param bits: Entropy bits
    :param risk: Risk of repeat
    :return: Total possible IDs (conservative approximation)

    >>> total_for_entropy(64, 1e9)
    192077.0
    """
    if bits <= 0:
        return 0

    if risk in [0, 1]:
        return 0

    c = 2 ** (bits + 1) / risk
    return (1 + sqrt(1 + 4 * c)) / 2


if __name__ == '__main__':  # pragma: no cover
    import doctest

    doctest.testmod()
