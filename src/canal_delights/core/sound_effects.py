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
SYNTHESIS_METHODS = ('karplus-strong', 'filtered-noise', 'cyclic-texture')


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


def _add_karplus(left, right, sample_rate, onset, duration, frequency, amplitude,
                 pan=.5, damping=.992, seed=0xA11CE):
    """Noise-excited Karplus–Strong body: a struck object, not a sine tone."""
    start, count = round(onset * sample_rate), round(duration * sample_rate)
    lg, rg = math.sqrt(1-pan), math.sqrt(pan)
    delay = max(2, round(sample_rate / frequency))
    ring = _noise(delay, seed)
    position = 0
    for index in range(min(count, len(left)-start)):
        t = index / sample_rate
        value = ring[position]
        following = ring[(position+1) % delay]
        ring[position] = (value+following)*.5*damping
        position = (position+1) % delay
        env = min(1.,t/.004)*min(1.,(duration-t)/.025)
        value *= env*amplitude
        left[start+index] += value*lg; right[start+index] += value*rg


def _cyclic_texture(size, seed):
    """A seamless random control ring used for non-oscillator water texture."""
    return _noise(size, seed)


def _paper_layer(left, right, sample_rate, seed, start, duration, amplitude, direction=1):
    count = round(duration * sample_rate)
    texture = _filtered_noise(count, sample_rate, seed, 2600, 260)
    onset = round(start * sample_rate)
    for index in range(min(count, len(left)-onset)):
        progress = index / max(1, count-1)
        # Two irregular cloth/paper swells avoid a generic white-noise "whoosh".
        arch = 4*progress*(1-progress)
        flutter = (progress*3.1) % 1
        flutter = 4*flutter*(1-flutter)
        shape = arch**1.5 * (.72 + .28*flutter*flutter)
        pan = .18+.64*progress if direction > 0 else .82-.64*progress
        value = texture[index] * shape * amplitude
        left[onset+index] += value*math.sqrt(1-pan)
        right[onset+index] += value*math.sqrt(pan)


def _design_effect(kind, left, right, sample_rate, strength):
    duration = EFFECT_DURATIONS[kind]
    if kind == 'key':
        # Two noise-excited wooden bodies create an unmistakable percussion hit.
        _add_karplus(left,right,sample_rate,0,.24,310,.27*strength,.45,.985,0xB4A0)
        _add_karplus(left,right,sample_rate,.012,.16,520,.085*strength,.56,.978,0xB4A1)
    elif kind == 'scroll':
        _paper_layer(left,right,sample_rate,0x5107,0,duration,.34*strength,1)
        _paper_layer(left,right,sample_rate,0x8A31,.13,.70,.15*strength,-1)
        _add_karplus(left,right,sample_rate,.04,.35,185,.075*strength,.38,.994,0x5108)
    elif kind == 'page':
        _paper_layer(left,right,sample_rate,0xFACE,0,.52,.38*strength,1)
        _paper_layer(left,right,sample_rate,0xB00C,.20,.34,.16*strength,-1)
        _add_karplus(left,right,sample_rate,.38,.18,410,.055*strength,.72,.982,0xFACF)
    elif kind == 'water':
        # Seamless interpolated random rings: flowing texture without oscillators.
        broad, detail = _cyclic_texture(37,0xA0A0), _cyclic_texture(83,0xA0A1)
        def sample_ring(ring, progress):
            position=progress*len(ring); base=int(position)%len(ring); mix=position-int(position)
            mix=mix*mix*(3-2*mix)
            return ring[base]*(1-mix)+ring[(base+1)%len(ring)]*mix
        for index in range(len(left)):
            p = index / len(left)
            ripple=.72*sample_ring(broad,p)+.28*sample_ring(detail,p)
            breathe=.84+.16*(1-abs(2*((p*2)%1)-1))
            left[index] += ripple*breathe*.105*strength
            right[index] += (ripple*.84+sample_ring(detail,p)*.16)*breathe*.105*strength
        for onset, pan in ((.17,.24),(.49,.72)):
            _add_karplus(left,right,sample_rate,onset,.18,260,.035*strength,pan,.987,0xA0B0+int(onset*100))
    elif kind == 'stamp':
        # Felted impact + wooden body + brief paper contact.
        _add_karplus(left,right,sample_rate,0,.32,96,.30*strength,.5,.996,0x57A0)
        _add_karplus(left,right,sample_rate,.008,.18,286,.13*strength,.47,.986,0x57A1)
        _paper_layer(left,right,sample_rate,0x57A9,0,.12,.10*strength,-1)
    else:  # fresh: airy D-major pentatonic chime, not a digital three-beep scale.
        for onset, frequency, pan in ((0,587.33,.30),(.12,739.99,.50),(.25,880.,.70)):
            _add_karplus(left,right,sample_rate,onset,.34,frequency,.13*strength,pan,.994,0xC100+int(onset*100))
        air = _filtered_noise(len(left), sample_rate, 0xC1EA, 900, 120)
        for index, value in enumerate(air):
            progress = index/len(left)
            env = (4*progress*(1-progress))**2
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
