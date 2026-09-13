import struct
import wave
from io import BytesIO

from canal_delights.core.music import CANAL_SCORE, DEFAULT_BPM, FULL_SCALE, NATURE_LAYERS, PROGRESSION, VOICES, looped_score_position, note_frequency, render_canal_suite, score_position


def _values(payload):
    with wave.open(BytesIO(payload), 'rb') as wav:
        params = wav.getparams()
        data = wav.readframes(wav.getnframes())
    return params, struct.unpack(f'<{len(data) // 2}h', data)


def test_score_is_complete_multivoice_composition():
    assert {event.voice for event in CANAL_SCORE} >= {'melody', 'harmony', 'bass', 'drums'}
    assert len(VOICES) >= 4
    assert len(PROGRESSION[0]) == len(PROGRESSION[1]) == 4
    assert max(event.start_beats + event.duration_beats for event in CANAL_SCORE) >= 127
    assert note_frequency('A4') == 440.0
    assert DEFAULT_BPM == 120


def test_stereo_pcm_is_safe_and_long_enough():
    params, values = _values(render_canal_suite(sample_rate=3000, reverb='room'))
    assert params.nchannels == 2 and params.sampwidth == 2
    assert params.nframes / params.framerate >= 60
    assert max(map(abs, values)) <= FULL_SCALE * .95
    assert max(abs(a - b) for a, b in zip(values, values[1:])) < FULL_SCALE * .5
    assert values[::2] != values[1::2]


def test_effect_presets_and_voice_contracts_are_explicit():
    assert render_canal_suite(sample_rate=2000, reverb='room') != render_canal_suite(sample_rate=2000, reverb='hall')
    assert {'pluck', 'flute_fm', 'percussion'} <= {voice.timbre for voice in VOICES.values()}
    assert all(0 <= voice.pan <= 1 and voice.attack >= 0 and voice.release >= 0 for voice in VOICES.values())
    assert set(NATURE_LAYERS) == {'stream', 'breeze', 'birds'}
    assert max(NATURE_LAYERS.values()) < min(voice.volume for voice in VOICES.values())


def test_score_position_is_derived_from_absolute_clock_time():
    position = score_position(9.25, bpm=120)
    assert position.bar == 4
    assert position.beat == 2.5
    # A two-second stall seeks to the new bar instead of queuing old bars.
    after_stall = score_position(11.25, bpm=120)
    assert after_stall.bar == 5
    assert after_stall.beat == 2.5

    looped = looped_score_position(66.25, duration=65.25, bpm=120)
    assert looped.cycle == 1
    assert looped.bar == 0 and looped.beat == 2
