"""Short code-synthesized interaction sounds; no sampled audio assets."""
from array import array
import io
import math
import threading
import wave

EFFECT_DURATIONS = {'key': .18, 'scroll': 1.0, 'page': .6, 'water': .35, 'stamp': .4, 'fresh': .6}


def synthesize_effect(kind, volume=.8, sample_rate=11025, water_level=1.0):
    """Create one named UI effect as an in-memory PCM WAV."""
    if kind not in EFFECT_DURATIONS:
        raise ValueError(f'unknown effect: {kind}')
    duration = EFFECT_DURATIONS[kind]
    count = round(duration * sample_rate)
    level = max(0., min(1., volume)) * (.11 if kind == 'water' else .19)
    frames = array('h')
    for i in range(count):
        t = i / sample_rate
        env = min(1., t / .012) * min(1., (duration - t) / .07)
        noise = math.sin(i * 12.9898) * math.sin(i * 78.233)
        if kind == 'key':
            tone = math.sin(math.tau * 1240 * t) + .22 * math.sin(math.tau * 2480 * t)
        elif kind == 'scroll':
            tone = noise * (.65 + .35 * math.sin(math.tau * 7 * t))
        elif kind == 'page':
            tone = .55 * noise + .45 * math.sin(math.tau * (420 + 180 * t) * t)
        elif kind == 'water':
            tone = (.78 * noise + .22 * math.sin(math.tau * 145 * t)) * water_level
        elif kind == 'stamp':
            tone = math.sin(math.tau * 118 * t) * math.exp(-9 * t) + .28 * noise
        else:  # fresh: a rising, clear three-note chime
            frequency = (660, 830, 990)[min(2, int(t / .2))]
            tone = math.sin(math.tau * frequency * t) + .16 * math.sin(math.tau * frequency * 2 * t)
        frames.append(round(max(-.88, min(.88, level * env * tone)) * 32767))
    stream = io.BytesIO()
    with wave.open(stream, 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sample_rate); wav.writeframes(frames.tobytes())
    return stream.getvalue()


class EffectPlayer:
    """Non-blocking effect performer; water repeats only while the boat moves."""
    def __init__(self, volume=.8, sound_module=None):
        if sound_module is None:
            try: import winsound as sound_module
            except ImportError: sound_module = None
        self.sound, self.volume = sound_module, volume
        self.water_level = 0.
        self._stopped = threading.Event()
        self._water_thread = None

    def set_volume(self, volume): self.volume = max(0., min(1., volume))
    def play(self, kind):
        if not self.sound or self.volume <= 0: return
        payload = synthesize_effect(kind, self.volume)
        threading.Thread(target=lambda: self.sound.PlaySound(payload, self.sound.SND_MEMORY), daemon=True).start()
    def set_water_level(self, level):
        self.water_level = max(0., min(1., level))
        if self.water_level > .02 and (not self._water_thread or not self._water_thread.is_alive()):
            self._stopped.clear(); self._water_thread = threading.Thread(target=self._water_loop, daemon=True); self._water_thread.start()
    def _water_loop(self):
        while not self._stopped.is_set() and self.water_level > .02:
            if self.sound and self.volume > 0:
                self.sound.PlaySound(synthesize_effect('water', self.volume, water_level=self.water_level), self.sound.SND_MEMORY)
    def stop(self): self._stopped.set(); self.water_level = 0.
