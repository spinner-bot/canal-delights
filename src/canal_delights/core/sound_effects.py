"""Layered, code-synthesized stereo interaction sounds; no audio assets."""
from array import array
import io
import math
import threading
import wave

SAMPLE_RATE = 22050
EFFECT_DURATIONS = {
    'key': .28, 'scroll': 1.0, 'page': .6,
    'water': .8, 'stamp': .4, 'fresh': .6,
}


def _noise(count, seed):
    """Deterministic white noise, allowing identical builds and tests."""
    values = [0.] * count
    state = seed
    for index in range(count):
        state = (1664525 * state + 1013904223) & 0xffffffff
        values[index] = state / 2147483648. - 1.
    return values


def _filtered_noise(count, sample_rate, seed, fast_hz, slow_hz=0):
    raw = _noise(count, seed)
    fast = slow = 0.
    fast_a = min(1., math.tau * fast_hz / sample_rate)
    slow_a = min(1., math.tau * slow_hz / sample_rate) if slow_hz else 0.
    result = [0.] * count
    for index, value in enumerate(raw):
        fast += fast_a * (value - fast)
        if slow_hz:
            slow += slow_a * (value - slow)
            result[index] = fast - slow
        else:
            result[index] = fast
    return result


def _add_tone(left, right, sample_rate, onset, duration, frequency, amplitude,
              pan=.5, decay=4., sweep=0., harmonics=(1., .18, .06)):
    start, count = round(onset * sample_rate), round(duration * sample_rate)
    lg, rg = math.sqrt(1-pan), math.sqrt(pan)
    phase = 0.
    for index in range(min(count, len(left)-start)):
        t = index / sample_rate
        env = min(1., t/.008) * min(1., (duration-t)/.045) * math.exp(-decay*t)
        phase += math.tau * (frequency + sweep*t/max(duration, .001)) / sample_rate
        tone = sum(gain * math.sin(phase * partial) for partial, gain in enumerate(harmonics, 1))
        value = tone * env * amplitude
        left[start+index] += value*lg; right[start+index] += value*rg


def _paper_layer(left, right, sample_rate, seed, start, duration, amplitude, direction=1):
    count = round(duration * sample_rate)
    texture = _filtered_noise(count, sample_rate, seed, 2600, 260)
    onset = round(start * sample_rate)
    for index in range(min(count, len(left)-onset)):
        progress = index / max(1, count-1)
        # Two irregular cloth/paper swells avoid a generic white-noise "whoosh".
        shape = math.sin(math.pi*progress)**1.5 * (.72 + .28*math.sin(math.tau*3.1*progress)**2)
        pan = .18+.64*progress if direction > 0 else .82-.64*progress
        value = texture[index] * shape * amplitude
        left[onset+index] += value*math.sqrt(1-pan)
        right[onset+index] += value*math.sqrt(pan)


def _design_effect(kind, left, right, sample_rate, strength):
    duration = EFFECT_DURATIONS[kind]
    if kind == 'key':
        # Muted bamboo/wood tap: short fundamental, quieter upper resonance.
        _add_tone(left,right,sample_rate,0,.24,740,.25*strength,.46,13.,-38.,(1.,.15,.035))
        _add_tone(left,right,sample_rate,.018,.18,1110,.075*strength,.54,18.,-60.,(1.,.08))
    elif kind == 'scroll':
        _paper_layer(left,right,sample_rate,0x5107,0,duration,.34*strength,1)
        _paper_layer(left,right,sample_rate,0x8A31,.13,.70,.15*strength,-1)
        _add_tone(left,right,sample_rate,.04,.35,185,.075*strength,.38,7.,-22.,(1.,.2))
    elif kind == 'page':
        _paper_layer(left,right,sample_rate,0xFACE,0,.52,.38*strength,1)
        _paper_layer(left,right,sample_rate,0xB00C,.20,.34,.16*strength,-1)
        _add_tone(left,right,sample_rate,.38,.18,410,.055*strength,.72,14.,-90.,(1.,.1))
    elif kind == 'water':
        # Integral-cycle components join cleanly when this sustained chunk repeats.
        for index in range(len(left)):
            p = index / len(left)
            ripple = sum(g*math.sin(math.tau*cycles*p) for cycles,g in ((29,.42),(47,.27),(73,.14),(101,.07)))
            breathe = .82+.18*math.sin(math.tau*2*p)
            left[index] += ripple*breathe*.105*strength
            right[index] += (ripple*.84+math.sin(math.tau*37*p)*.16)*breathe*.105*strength
        for onset, pan in ((.17,.24),(.49,.72)):
            _add_tone(left,right,sample_rate,onset,.18,210,.035*strength,pan,12.,340.,(1.,.12))
    elif kind == 'stamp':
        # Felted impact + wooden body + brief paper contact.
        _add_tone(left,right,sample_rate,0,.32,92,.30*strength,.5,10.,-18.,(1.,.22,.06))
        _add_tone(left,right,sample_rate,.008,.18,286,.13*strength,.47,18.,-70.,(1.,.16))
        _paper_layer(left,right,sample_rate,0x57A9,0,.12,.10*strength,-1)
    else:  # fresh: airy D-major pentatonic chime, not a digital three-beep scale.
        for onset, frequency, pan in ((0,587.33,.30),(.12,739.99,.50),(.25,880.,.70)):
            _add_tone(left,right,sample_rate,onset,.34,frequency,.13*strength,pan,5.5,8.,(1.,.22,.08,.025))
        air = _filtered_noise(len(left), sample_rate, 0xC1EA, 900, 120)
        for index, value in enumerate(air):
            env = math.sin(math.pi*index/len(left))**2
            left[index] += value*env*.018*strength; right[index] += value*env*.021*strength


def synthesize_effect(kind, volume=.8, sample_rate=SAMPLE_RATE, water_level=1.0):
    """Create a polished named effect as safe, click-free stereo PCM."""
    if kind not in EFFECT_DURATIONS: raise ValueError(f'unknown effect: {kind}')
    count = round(EFFECT_DURATIONS[kind]*sample_rate)
    left, right = [0.]*count, [0.]*count
    strength = max(0.,min(1.,volume)) * (max(0.,min(1.,water_level)) if kind=='water' else 1.)
    _design_effect(kind,left,right,sample_rate,strength)
    # Non-looping sounds end exactly at silence; water is periodic by construction.
    if kind != 'water':
        fade = max(1, round(.018*sample_rate))
        for index in range(fade):
            gain = index/fade; left[index]*=gain; right[index]*=gain
            gain = (fade-index-1)/fade; left[-index-1]*=gain; right[-index-1]*=gain
    peak=max(max(map(abs,left)),max(map(abs,right)),1e-9); gain=min(1.,.72/peak)
    frames=array('h')
    for l,r in zip(left,right): frames.extend((round(l*gain*32767),round(r*gain*32767)))
    stream=io.BytesIO()
    with wave.open(stream,'wb') as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(sample_rate); wav.writeframes(frames.tobytes())
    return stream.getvalue()


class EffectPlayer:
    """Non-blocking effect performer; water follows normalized boat speed."""
    def __init__(self,volume=.8,sound_module=None):
        if sound_module is None:
            try: import winsound as sound_module
            except ImportError: sound_module=None
        self.sound,self.volume=sound_module,volume; self.enabled=True; self.water_level=0.; self._cache={}; self._stopped=threading.Event(); self._water_thread=None
    def set_volume(self,volume):
        value=max(0.,min(1.,volume))
        if value != self.volume:self._cache.clear()
        self.volume=value
    def _perform(self,payload):
        try: self.sound.PlaySound(payload,self.sound.SND_MEMORY)
        except RuntimeError: pass
    def play(self,kind):
        if not self.sound or not self.enabled or self.volume<=0:return
        payload=self._cache.get(kind) or synthesize_effect(kind,self.volume)
        threading.Thread(target=self._perform,args=(payload,),daemon=True).start()
    def set_water_level(self,level):
        self.water_level=max(0.,min(1.,level))
        if self.water_level>.02 and (not self._water_thread or not self._water_thread.is_alive()):
            self._stopped.clear(); self._water_thread=threading.Thread(target=self._water_loop,daemon=True); self._water_thread.start()
    def _water_loop(self):
        while not self._stopped.is_set() and self.water_level>.02:
            if self.sound and self.enabled and self.volume>0:self._perform(synthesize_effect('water',self.volume,water_level=self.water_level))
    def stop(self): self._stopped.set(); self.water_level=0.
    def prepare(self):
        for kind in EFFECT_DURATIONS:
            if kind != 'water':self._cache[kind]=synthesize_effect(kind,self.volume)
    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.enabled:self.stop()
