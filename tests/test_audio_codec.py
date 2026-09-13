import pytest

from canal_delights.core.audio_codec import decode_wav, encode_wav


def test_wav_round_trip_through_packaging_codec():
    source = b'RIFF' + b'\x00' * 4 + b'WAVE' + b'payload'
    encoded = encode_wav(source)
    assert decode_wav(encoded) == source


def test_codec_rejects_bad_and_empty_payloads():
    assert decode_wav('') == b''
    with pytest.raises(ValueError):
        encode_wav(b'not wav')
    with pytest.raises(ValueError):
        decode_wav('bm90LXppcA==')
