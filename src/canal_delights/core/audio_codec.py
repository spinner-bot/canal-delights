"""WAV <-> zlib <-> Base64 codec used for single-file audio packaging."""
from __future__ import annotations

import base64
import binascii
import zlib


def encode_wav(wav_bytes: bytes, level: int = 9) -> str:
    """Compress a complete WAV payload and return an ASCII-safe constant."""
    if (not isinstance(wav_bytes, (bytes, bytearray))
            or bytes(wav_bytes)[:4] != b'RIFF'
            or bytes(wav_bytes)[8:12] != b'WAVE'):
        raise ValueError('expected a RIFF/WAV byte payload')
    return base64.b64encode(zlib.compress(bytes(wav_bytes), level)).decode('ascii')


def decode_wav(encoded: str) -> bytes:
    """Decode and validate an embedded Base64(zlib(WAV)) payload."""
    if not encoded:
        return b''
    try:
        payload = zlib.decompress(base64.b64decode(encoded, validate=True))
    except (binascii.Error, zlib.error, ValueError) as exc:
        raise ValueError('invalid embedded audio payload') from exc
    if payload[:4] != b'RIFF' or payload[8:12] != b'WAVE':
        raise ValueError('embedded payload is not a WAV file')
    return payload
