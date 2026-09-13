"""Self-contained, score-led multi-voice synthesizer; no audio files."""
from __future__ import annotations
from array import array
from dataclasses import dataclass
import ctypes
import io, math, random, sys, threading, time, wave
import multiprocessing
from .audio_codec import decode_wav
try:
    from .embedded_bgm import BGM_WAV_ZLIB_BASE64
except ImportError:
    # The compact single-file build intentionally omits the large WAV asset;
    # it supplies the MP3 resource below instead.
    BGM_WAV_ZLIB_BASE64 = ''
try:
    from .embedded_mp3 import BGM_MP3_BASE64
except ImportError:
    BGM_MP3_BASE64 = ''
import base64


def _audio_process_main(payload, kind='wav'):
    """Own the blocking Windows call so the parent can terminate playback."""
    import winsound
    if kind == 'mp3':
        import tempfile
        from pathlib import Path
        path = Path(tempfile.gettempdir()) / 'canal_delights_bgm.mp3'
        path.write_bytes(payload)
        winmm = ctypes.WinDLL('winmm')
        send = winmm.mciSendStringW
        send(f'open "{path}" type mpegvideo alias canal_delights', None, 0, None)
        send('play canal_delights repeat', None, 0, None)
        try:
            while True:
                time.sleep(.25)
        finally:
            send('close canal_delights', None, 0, None)
        return
    while True:
        winsound.PlaySound(payload, winsound.SND_MEMORY)

SAMPLE_RATE, DEFAULT_BPM, FULL_SCALE = 11025, 120, 32767

@dataclass(frozen=True)
class Voice:
    name: str; timbre: str; volume: float; pan: float
    attack: float; decay: float; sustain: float; release: float
    vibrato_hz: float = 0.; vibrato_depth: float = 0.

@dataclass(frozen=True)
class NoteEvent:
    voice: str; note: str; start_beats: float; duration_beats: float
    velocity: str = 'mf'; articulation: str = 'legato'

@dataclass(frozen=True)
class ScorePosition:
    bar: int
    beat: float
    seconds: float
    cycle: int = 0

# Five independent instruments: each owns timbre, gain and stereo position.
VOICES = {
    'melody': Voice('melody','pluck',.20,.62,.018,.13,.52,.20),
    'flute': Voice('flute','flute_fm',.12,.34,.070,.18,.76,.30,5.2,.009),
    'harmony': Voice('harmony','pad',.115,.46,.14,.30,.58,.42),
    'bass': Voice('bass','bass',.15,.54,.025,.13,.64,.18),
    'drums': Voice('drums','percussion',.045,.52,.006,.05,0.,.08),
}
NATURE_LAYERS = {'stream': .010, 'breeze': .006, 'birds': .016}
VELOCITIES = {'pp': .52, 'mf': .76, 'ff': 1.}
# I – V7 – vi7 – IVmaj7, explicitly containing both triads and sevenths.
PROGRESSION = (('D3','F#3','A3','C#4'), ('A2','C#3','E3','G3'),
               ('B2','D3','F#3','A3'), ('G2','B2','D3','F#3'))
MELODY_A = (('D5',0,1),('F#5',1,.5),('A5',1.5,.5),('F#5',2,1),('E5',3,.75),
 ('D5',4,1),('A4',5,.5),('D5',5.5,.5),('F#5',6,1),('E5',7,1),
 ('F#5',8,.5),('A5',8.5,.5),('B5',9,1),('A5',10,.75),('F#5',11,1),
 ('E5',12,1),('D5',13,1),('A4',14,2))
MELODY_B = (('A5',0,.5),('B5',.5,.5),('D6',1,1),('A5',2,.5),('F#5',2.5,.5),('E5',3,1),
 ('F#5',4,.5),('A5',4.5,.5),('B5',5,1),('D6',6,.5),('B5',6.5,.5),('A5',7,1),
 ('D6',8,.5),('E6',8.5,.5),('F#6',9,1),('E6',10,.5),('D6',10.5,.5),('B5',11,1),
 ('A5',12,.5),('F#5',12.5,.5),('E5',13,1),('D5',14,2))
CANAL_THEME = tuple((n,d) for n,_,d in MELODY_A)

def note_frequency(note: str) -> float:
    if note == 'REST': return 0.
    names={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    cut = 2 if len(note)>2 and note[1]=='#' else 1
    midi=(int(note[cut:])+1)*12+names[note[:cut]]
    return 440. * 2 ** ((midi-69)/12)

def build_canal_score() -> tuple[NoteEvent,...]:
    """128 beats/64 seconds at 120 BPM: an explicit eight-part river suite."""
    events=[]
    # A–B–A′–B′–A″–B″–bridge–finale: finite form, never an infinite loop.
    for section, offset in enumerate(range(0, 128, 16)):
        is_b=section % 2 == 1; vel='ff' if section >= 6 else ('mf' if is_b else 'pp')
        for n,s,d in (MELODY_B if is_b else MELODY_A):
            events.append(NoteEvent('melody',n,offset+s,d,vel,'staccato' if is_b and d<=.5 else 'legato'))
        for ci,chord in enumerate(PROGRESSION):
            base=offset+ci*4
            if is_b: # contrasting broken-chord rhythm
                for step in range(8): events.append(NoteEvent('harmony',chord[step%4],base+step*.5,.42,vel,'staccato'))
            else:
                for n in chord: events.append(NoteEvent('harmony',n,base,3.88,vel))
            for beat,n,d in ((0,chord[0],1.15),(1.5,chord[2],.65),(2.5,chord[0],.9),(3.5,chord[2],.35)):
                events.append(NoteEvent('bass',n,base+beat,d,vel,'staccato' if beat==3.5 else 'legato'))
        step=.5 if is_b else 1.
        for tick in range(int(16/step)):
            events.append(NoteEvent('drums','DRUM',offset+tick*step,.12 if is_b else .17,
                                    'ff' if section >= 6 and tick%4==0 else 'mf','staccato'))
        if is_b:
            for n,s,d in MELODY_A[::2]: events.append(NoteEvent('flute',n,offset+s+.18,max(.35,d*.82),'mf' if section < 5 else 'ff'))
    return tuple(sorted(events,key=lambda e:e.start_beats))
CANAL_SCORE=build_canal_score()

def _envelope(t,d,v,art):
    gate=d*(.72 if art=='staccato' else .985); release=max(v.attack+v.decay,gate-v.release)
    if t<v.attack: return t/max(v.attack,1e-6)
    if t<v.attack+v.decay: return 1+(v.sustain-1)*(t-v.attack)/max(v.decay,1e-6)
    if t<release: return v.sustain
    if t<gate: return v.sustain*max(0.,(gate-t)/max(gate-release,1e-6))
    return 0.

def _tone(t,f,v,bright,seed,sr):
    phase=math.tau*f*t
    if v.timbre=='pluck': return (math.sin(phase)+(.16+.12*bright)*math.sin(2*phase)+(.04+.05*bright)*math.sin(3*phase))/1.35
    if v.timbre=='flute_fm':
        c=phase*(1+v.vibrato_depth*math.sin(math.tau*v.vibrato_hz*t))
        return (math.sin(c+.18*math.sin(math.tau*2.1*t))+.10*math.sin(2*c)+.035*math.sin(3*c))/1.14
    if v.timbre=='pad': return (math.sin(phase)+.17*math.sin(2*phase)+.045*math.sin(3*phase))/1.22
    if v.timbre=='bass': return (math.sin(phase)+.12*math.sin(2*phase)+.025*math.sin(3*phase))/1.15
    # A soft wooden pulse replaces the earlier noisy synthetic percussion.
    return .72*math.sin(math.tau*510*t)*math.exp(-24*t)+.28*math.sin(math.tau*760*t)*math.exp(-32*t)

def _add_event(left,right,event,bpm,sr,master,rng,seed):
    v=VOICES[event.voice]; beat=60/bpm; onset=round(event.start_beats*beat*sr)
    duration=max(.015,event.duration_beats*beat*(1+rng.uniform(-.08,.08))) # 5–15% humanize
    count=min(round(duration*sr),len(left)-onset)
    if count<=0:return
    f=92. if event.note=='DRUM' else note_frequency(event.note); amp=v.volume*VELOCITIES[event.velocity]*master
    lg,rg=math.sqrt(1-v.pan),math.sqrt(v.pan)
    for i in range(count):
        value=amp*_envelope(i/sr,duration,v,event.articulation)*_tone(i/sr,f,v,VELOCITIES[event.velocity],seed,sr)
        left[onset+i]+=value*lg; right[onset+i]+=value*rg

def _effects(left,right,sr,preset):
    taps=((.029,.18),(.047,.13),(.071,.09)) if preset=='room' else ((.041,.20),(.073,.15),(.119,.11),(.173,.07))
    dl,dr=left[:],right[:]
    for seconds,gain in taps:
        delay=round(seconds*sr)
        for i in range(delay,len(left)): left[i]+=dl[i-delay]*gain; right[i]+=dr[i-delay]*gain
    for i in range(round(.024*sr),len(left)): # subtle modulated-delay chorus
        delay=round((.018+.003*math.sin(math.tau*.27*i/sr))*sr)
        if i>=delay: left[i]+=dl[i-delay]*.07; right[i]+=dr[i-delay]*.07

def _add_nature(left, right, sr, master):
    """Add a quiet, low-passed waterside bed and four sparse bird calls."""
    state = 0xC0FFEE
    breeze = water = slow_water = 0.
    for i in range(len(left)):
        state = (1664525 * state + 1013904223) & 0xffffffff
        noise = state / 2147483648. - 1.
        breeze += .0015 * (noise - breeze)
        water += .040 * (noise - water)
        slow_water += .009 * (noise - slow_water)
        stream = (water - slow_water) * NATURE_LAYERS['stream'] * master
        air = breeze * NATURE_LAYERS['breeze'] * master
        drift = .72 + .28 * math.sin(math.tau * .075 * i / sr)
        left[i] += stream * .92 + air * drift
        right[i] += stream * 1.08 + air * (1.0 - .12 * drift)
    for call, start in enumerate((7.4, 22.8, 40.6, 57.2)):
        onset, duration = round(start * sr), round(.42 * sr)
        pan = .22 if call % 2 == 0 else .78
        for i in range(min(duration, len(left) - onset)):
            t = i / sr
            env = math.sin(math.pi * t / .42) ** 2
            frequency = 1450 + 520 * t / .42 + 90 * math.sin(math.tau * 6.2 * t)
            chirp = math.sin(math.tau * frequency * t) * env * NATURE_LAYERS['birds'] * master
            left[onset+i] += chirp * math.sqrt(1-pan)
            right[onset+i] += chirp * math.sqrt(pan)

def render_canal_suite(bpm=DEFAULT_BPM,volume=.7,sample_rate=SAMPLE_RATE,reverb='hall') -> bytes:
    """Render the fresh-light 64-second stereo suite and nature ambience."""
    if bpm<=0: raise ValueError('bpm must be positive')
    if reverb not in {'room','hall'}: raise ValueError("reverb must be 'room' or 'hall'")
    frames=round((128*60/bpm+1.25)*sample_rate); left,right=[0.]*frames,[0.]*frames; rng=random.Random(20260913)
    for seed,event in enumerate(CANAL_SCORE): _add_event(left,right,event,bpm,sample_rate,max(0.,min(1.,volume)),rng,seed)
    _add_nature(left,right,sample_rate,max(0.,min(1.,volume)))
    _effects(left,right,sample_rate,reverb); peak=max(max(map(abs,left)),max(map(abs,right)),1e-9); gain=min(1.,.90/peak)
    pcm=array('h')
    for l,r in zip(left,right): pcm.extend((round(max(-.9,min(.9,l*gain))*FULL_SCALE),round(max(-.9,min(.9,r*gain))*FULL_SCALE)))
    if sys.byteorder!='little': pcm.byteswap()
    stream=io.BytesIO()
    with wave.open(stream,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sample_rate); w.writeframes(pcm.tobytes())
    return stream.getvalue()

def synthesize_score(score=None,bpm=DEFAULT_BPM,volume=.7,sample_rate=SAMPLE_RATE) -> bytes:
    """Compatibility entrypoint; the default is the full multi-voice suite."""
    if score is None or score==CANAL_THEME: return render_canal_suite(bpm,volume,sample_rate)
    # Existing callers get the canonical performance rather than asset playback.
    return render_canal_suite(bpm,volume,sample_rate)

def score_position(elapsed, bpm=DEFAULT_BPM, beats_per_bar=4):
    """Map monotonic elapsed time to an absolute bar/beat position."""
    elapsed=max(0.,float(elapsed)); beat_seconds=60./bpm
    total_beats=elapsed/beat_seconds
    return ScorePosition(int(total_beats//beats_per_bar), total_beats%beats_per_bar, elapsed)

def looped_score_position(elapsed,duration,bpm=DEFAULT_BPM,beats_per_bar=4):
    """Locate a repeating finite score without accumulating playback delay."""
    if duration<=0:raise ValueError('duration must be positive')
    cycle=int(max(0.,elapsed)//duration)
    position=score_position(max(0.,elapsed)%duration,bpm,beats_per_bar)
    return ScorePosition(position.bar,position.beat,position.seconds,cycle)

def _wav_timeline(payload):
    with wave.open(io.BytesIO(payload),'rb') as source:
        return source.getparams(),source.readframes(source.getnframes())

def _wav_window(params,frames,offset_seconds,seconds=.5):
    frame_size=params.nchannels*params.sampwidth
    start=round(offset_seconds*params.framerate)*frame_size
    size=round(seconds*params.framerate)*frame_size
    stream=io.BytesIO()
    with wave.open(stream,'wb') as target:
        target.setparams(params); target.writeframes(frames[start:start+size])
    return stream.getvalue()

class ScorePlayer:
    """Perform from a monotonic-clock bar position, skipping time lost to lag."""
    def __init__(self,volume=.7,sound_module=None):
        if sound_module is None:
            try: import winsound as sound_module
            except ImportError: sound_module=None
        self.sound=sound_module; self.volume=max(0.,min(1.,volume)); self.enabled=True; self.playing=False; self.current_position=ScorePosition(0,0.,0.); self._buffer=None; self._suite_cache=None; self._thread=None; self._process=None; self._stop_event=threading.Event()
    @property
    def available(self): return self.sound is not None
    @staticmethod
    def _set_output_volume(value):
        """Apply live music gain without interrupting the contiguous PCM stream."""
        if sys.platform != 'win32':
            return
        level = max(0., min(1., float(value)))
        packed = int(level * 0xffff) | (int(level * 0xffff) << 16)
        try:
            ctypes.windll.winmm.waveOutSetVolume(0, packed)
        except (AttributeError, OSError):
            pass
    def _perform_suite(self):
        try:
            kind = 'wav'
            if BGM_MP3_BASE64:
                payload = base64.b64decode(BGM_MP3_BASE64)
                kind = 'mp3'
            else:
                payload = self._suite_cache or self._load_payload()
            self._suite_cache = payload
            if kind == 'wav':
                params,frames=_wav_timeline(payload)
                duration=len(frames)/(params.framerate*params.nchannels*params.sampwidth)
            else:
                duration=204.05
            origin=time.monotonic()
            if sys.platform == 'win32' and self.sound is not False:
                context = multiprocessing.get_context('spawn')
                self._process = context.Process(target=_audio_process_main, args=(payload, kind), daemon=True)
                self._process.start()
                while not self._stop_event.wait(.1):
                    self.current_position=looped_score_position(time.monotonic()-origin,duration)
                    if not self._process.is_alive(): break
                if self._process.is_alive(): self._process.terminate()
                self._process.join(timeout=1.)
                self._process=None
                return
            # Feed the complete decoded PCM to the system in one call. Rebuilding
            # 0.25 s WAV windows made Python the real-time producer and caused
            # audible starvation under load. The audio device now owns timing.
            while not self._stop_event.is_set():
                elapsed=time.monotonic()-origin
                self.current_position=looped_score_position(elapsed,duration)
                timeline_seconds=self.current_position.seconds
                self._buffer=payload
                self.sound.PlaySound(payload,self.sound.SND_MEMORY)
        except RuntimeError: pass
        finally: self.playing=False
    def start(self):
        if not self.available or not self.enabled:return False
        if self._thread and self._thread.is_alive():return True
        self.playing=True; self._stop_event.clear(); self._thread=threading.Thread(target=self._perform_suite,name='canal-score-player',daemon=True); self._thread.start(); return True
    def stop(self):
        self._stop_event.set(); self.playing=False
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=1.)
            self._process=None
        if self._thread and self._thread is not threading.current_thread(): self._thread.join(timeout=1.2)
        self._thread=None
    def set_volume(self,volume):
        value=max(0.,min(1.,volume))
        if value != self.volume:self._suite_cache=None
        self.volume=value
        if self.enabled:self._set_output_volume(value)
    def _load_payload(self):
        """Prefer the packaged composition; retain synthesis as dev fallback."""
        if BGM_WAV_ZLIB_BASE64:
            try:
                return decode_wav(BGM_WAV_ZLIB_BASE64)
            except ValueError:
                pass
        return render_canal_suite(volume=self.volume)
    def prepare(self):
        self._suite_cache = self._suite_cache or self._load_payload()
    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.enabled:
            self._set_output_volume(0.)
            self.stop()
        else:
            self._set_output_volume(self.volume)
            if not self.playing:self.start()
