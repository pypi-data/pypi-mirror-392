from typing import Callable, Dict

from puid.chars import Chars, ValidChars
from puid.encoders.alpha import alpha
from puid.encoders.alpha import alpha_lower
from puid.encoders.alpha import alpha_upper
from puid.encoders.alphanum import alphanum
from puid.encoders.alphanum import alphanum_lower
from puid.encoders.alphanum import alphanum_upper
from puid.encoders.base16 import base16
from puid.encoders.base32 import base32
from puid.encoders.base32 import base32_hex
from puid.encoders.base32 import base32_hex_upper
from puid.encoders.crockford32 import crockford32
from puid.encoders.custom import custom
from puid.encoders.decimal import decimal
from puid.encoders.hex import hex_lower
from puid.encoders.hex import hex_upper
from puid.encoders.safe32 import safe32
from puid.encoders.safe64 import safe64
from puid.encoders.safe_ascii import safe_ascii
from puid.encoders.symbol import symbol
from puid.encoders.word_safe32 import word_safe32


_ENCODER_CACHE: Dict[str, Callable[[int], int]] = {}


def _init_encoder_map() -> Dict[str, Callable[[int], int]]:
    return {
        Chars.ALPHA.name: alpha(),
        Chars.ALPHA_LOWER.name: alpha_lower(),
        Chars.ALPHA_UPPER.name: alpha_upper(),
        Chars.ALPHANUM.name: alphanum(),
        Chars.ALPHANUM_LOWER.name: alphanum_lower(),
        Chars.ALPHANUM_UPPER.name: alphanum_upper(),
        Chars.BASE16.name: base16(),
        Chars.BASE32.name: base32(),
        Chars.BASE32_HEX.name: base32_hex(),
        Chars.BASE32_HEX_UPPER.name: base32_hex_upper(),
        Chars.CROCKFORD32.name: crockford32(),
        Chars.DECIMAL.name: decimal(),
        Chars.HEX.name: hex_lower(),
        Chars.HEX_UPPER.name: hex_upper(),
        Chars.SAFE32.name: safe32(),
        Chars.SAFE64.name: safe64(),
        Chars.SAFE_ASCII.name: safe_ascii(),
        Chars.SYMBOL.name: symbol(),
        Chars.WORD_SAFE32.name: word_safe32(),
    }


def encoder(chars: ValidChars) -> Callable[[int], int]:
    if not _ENCODER_CACHE:
        _ENCODER_CACHE.update(_init_encoder_map())
    
    encoder_fn = _ENCODER_CACHE.get(chars.name)
    if encoder_fn is not None:
        return encoder_fn
    return custom(chars)
