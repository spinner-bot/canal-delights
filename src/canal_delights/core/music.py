"""Code-scored, runtime-synthesized background music with no audio assets."""

from array import array
import io
import math
import threading
import wave


# A restrained D-pentatonic theme: note name, duration in beats.  The melody
# lives in source code and is synthesized at runtime, so the final program
# remains self-contained rather than loading a recording.
CANAL_THEME = (
    ('D4', 1), ('F4', .5), ('G4', .5), ('A4', 1.5), ('G4', .5),
    ('F4', 1), ('D4', 1), ('REST', 1),
    ('D4', .5), ('F4', .5), ('G4', 1), ('A4', 1), ('C5', 1),
    ('A4', 1.5), ('G4', .5), ('F4', 1), ('REST', 1),
    ('A4', .5), ('C5', .5), ('D5', 1), ('C5', 1), ('A4', 1),
    ('G4', 1.5), ('F4', .5), ('D4', 1), ('REST', 1),
    ('F4', 1), ('G4', 1), ('A4', .5), ('C5', .5), ('A4', 1),
    ('G4', 1), ('F4', 1), ('D4', 2),
)

NOTE_FREQUENCIES = {
    'D4': 293.66, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00,
    'C5': 523.25, 'D5': 587.33,
}


def synthesize_score(score=CANAL_THEME, bpm=92, volume=.7, sample_rate=22050) -> bytes:
    """Synthesize a soft plucked-timbre mono WAV entirely in memory."""
    beat_seconds = 60.0 / bpm
    level = max(0.0, min(1.0, volume)) * .22
    samples = array('h')
    for note, beats in score:
        duration = max(.02, float(beats) * beat_seconds)
        count = max(1, round(duration * sample_rate))
        frequency = NOTE_FREQUENCIES.get(note)
        for index in range(count):
            if frequency is None:
                value = 0.0
            else:
                t = index / sample_rate
                attack = min(1.0, t / .028)
                release = min(1.0, (duration - t) / .16)
                decay = math.exp(-1.15 * t / duration)
                envelope = max(0.0, attack * release * decay)
                # Fundamental plus quiet harmonics suggests a plucked string
                # without the harshness of a raw square-wave beep.
                tone = (
                    math.sin(math.tau * frequency * t)
                    + .24 * math.sin(math.tau * frequency * 2 * t)
                    + .08 * math.sin(math.tau * frequency * 3 * t)
                )
                value = level * envelope * tone / 1.32
            samples.append(max(-32767, min(32767, round(value * 32767))))

    stream = io.BytesIO()
    with wave.open(stream, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())
    return stream.getvalue()


class ScorePlayer:
    """Perform score notes in sequence on a worker so Tk never waits."""

    def __init__(self, volume=.7, sound_module=None):
        if sound_module is None:
            try:
                import winsound as sound_module
            except ImportError:
                sound_module = None
        self.sound = sound_module
        self.volume = max(0.0, min(1.0, volume))
        self.playing = False
        self._buffer = None
        self._thread = None
        self._stop_event = threading.Event()

    @property
    def available(self):
        return self.sound is not None

    def _perform_loop(self):
        # winsound deliberately rejects SND_MEMORY | SND_ASYNC.  A daemon
        # worker gives us asynchronous UI behaviour. Performing one short note
        # per call also keeps shutdown responsive and is literally score-led
        # performance rather than playback of one pre-rendered recording.
        while not self._stop_event.is_set():
            for note, beats in CANAL_THEME:
                if self._stop_event.is_set():
                    return
                if note == 'REST' or self.volume <= 0:
                    self._stop_event.wait(float(beats) * 60 / 92)
                    continue
                payload = synthesize_score(
                    score=((note, beats),), bpm=92, volume=self.volume,
                )
                self._buffer = payload
                try:
                    self.sound.PlaySound(payload, self.sound.SND_MEMORY)
                except RuntimeError:
                    # Audio device availability should never take down the app.
                    self.playing = False
                    return

    def start(self):
        if not self.available:
            return False
        if self._thread and self._thread.is_alive():
            return True
        self.playing = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._perform_loop,
            name='canal-score-player',
            daemon=True,
        )
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()
        self.playing = False
        thread = self._thread
        if thread and thread is not threading.current_thread():
            # The longest score event is two beats (about 1.3 seconds).
            thread.join(timeout=1.5)
        self._thread = None

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        # The worker reads the latest value before synthesizing every note, so
        # moving the slider never performs audio work on the UI thread.
