import wave
from io import BytesIO
from canal_delights.core.sound_effects import EFFECT_DURATIONS, synthesize_effect


def test_all_effects_are_embedded_short_wavs():
    assert set(EFFECT_DURATIONS) == {'key', 'scroll', 'page', 'water', 'stamp', 'fresh'}
    for name, seconds in EFFECT_DURATIONS.items():
        with wave.open(BytesIO(synthesize_effect(name)), 'rb') as wav:
            assert wav.getnchannels() == 1
            assert abs(wav.getnframes() / wav.getframerate() - seconds) < .002
