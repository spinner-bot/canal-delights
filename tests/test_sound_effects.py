import struct
import wave
from io import BytesIO
from canal_delights.core.sound_effects import EFFECT_DURATIONS, SYNTHESIS_METHODS, EffectPlayer, synthesize_effect


def test_all_effects_are_embedded_short_wavs():
    assert set(EFFECT_DURATIONS) == {'key', 'scroll', 'page', 'water', 'stamp', 'fresh'}
    for name, seconds in EFFECT_DURATIONS.items():
        with wave.open(BytesIO(synthesize_effect(name)), 'rb') as wav:
            assert wav.getnchannels() == 2
            assert abs(wav.getnframes() / wav.getframerate() - seconds) < .002
    assert 'karplus-strong' in SYNTHESIS_METHODS


def test_effect_pcm_has_headroom_smooth_edges_and_unique_designs():
    fingerprints = set()
    for name in EFFECT_DURATIONS:
        with wave.open(BytesIO(synthesize_effect(name)), 'rb') as wav:
            raw = wav.readframes(wav.getnframes())
        values = struct.unpack(f'<{len(raw) // 2}h', raw)
        left, right = values[::2], values[1::2]
        assert max(map(abs, values)) <= 32767 * .75
        assert max(abs(a-b) for a,b in zip(left,left[1:])) < 32767 * .5
        assert max(abs(a-b) for a,b in zip(right,right[1:])) < 32767 * .5
        fingerprints.add(raw[:min(len(raw), 4096)])
    assert len(fingerprints) == len(EFFECT_DURATIONS)


def test_water_strength_tracks_boat_speed_ratio():
    quiet = synthesize_effect('water', water_level=.2)
    fast = synthesize_effect('water', water_level=1.)
    q = struct.unpack(f'<{(len(quiet)-44)//2}h', quiet[44:])
    f = struct.unpack(f'<{(len(fast)-44)//2}h', fast[44:])
    assert sum(abs(v) for v in f) > sum(abs(v) for v in q) * 3
    assert sum(abs(v) for v in q) > 0


def test_effect_cache_is_invalidated_when_volume_changes():
    player = EffectPlayer(volume=.8, sound_module=None)
    player._cache['key'] = b'old'
    player.set_volume(.3)
    assert player._cache == {}
