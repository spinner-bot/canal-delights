import wave
from io import BytesIO
import threading
import time

from canal_delights.core.music import CANAL_THEME, ScorePlayer, synthesize_score


def test_score_is_embedded_and_synthesizes_valid_wav():
    assert len(CANAL_THEME) >= 24
    payload = synthesize_score(score=(('D4', .02), ('REST', .02)), bpm=120)
    assert payload[:4] == b'RIFF'
    with wave.open(BytesIO(payload), 'rb') as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 22050
        assert wav.getnframes() > 0


class FakeSound:
    SND_MEMORY = 1

    def __init__(self):
        self.calls = []
        self.playing = threading.Event()

    def PlaySound(self, payload, flags):
        self.calls.append((payload, flags))
        self.playing.set()
        time.sleep(.01)


def test_player_performs_in_memory_and_reacts_to_volume():
    sound = FakeSound()
    player = ScorePlayer(volume=.2, sound_module=sound)
    assert player.start()
    assert sound.playing.wait(1)
    payload, flags = next(call for call in sound.calls if call[0] is not None)
    assert payload[:4] == b'RIFF'
    assert flags == sound.SND_MEMORY

    player.set_volume(0)
    assert player.volume == 0
    player.stop()
    assert not player.playing
