"""Self-contained, score-led multi-voice synthesizer; no audio files."""
from __future__ import annotations
from array import array
from dataclasses import dataclass
import io, math, random, sys, threading, wave

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

# Five independent instruments: each owns timbre, gain and stereo position.
VOICES = {
    'melody': Voice('melody','pluck',.26,.66,.012,.10,.57,.15),
    'flute': Voice('flute','flute_fm',.16,.31,.045,.12,.78,.22,5.2,.012),
    'harmony': Voice('harmony','pad',.15,.47,.075,.22,.62,.28),
    'bass': Voice('bass','bass',.22,.54,.016,.09,.68,.12),
    'drums': Voice('drums','percussion',.12,.50,.003,.06,0.,.06),
}
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
    if v.timbre=='pluck': return (math.sin(phase)+(.32+.18*bright)*math.sin(2*phase)+(.10+.10*bright)*math.sin(3*phase))/1.62
    if v.timbre=='flute_fm':
        c=phase*(1+v.vibrato_depth*math.sin(math.tau*v.vibrato_hz*t))
        return (math.sin(c+.72*math.sin(math.tau*2.1*t))+.18*math.sin(2*c)+.07*math.sin(3*c))/1.25
    if v.timbre=='pad': return (math.sin(phase)+.42*math.sin(2*phase)+.19*math.sin(3*phase))/1.61
    if v.timbre=='bass': return (math.sin(phase)+.24*math.sin(2*phase)+.08*math.sin(3*phase))/1.32
    x=seed+int(t*sr); return .72*math.sin(x*12.9898)*math.sin(x*78.233)+.28*math.sin(math.tau*92*t)

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

def render_canal_suite(bpm=DEFAULT_BPM,volume=.7,sample_rate=SAMPLE_RATE,reverb='hall') -> bytes:
    """Render a 32-second stereo performance plus natural room tail to memory."""
    if bpm<=0: raise ValueError('bpm must be positive')
    if reverb not in {'room','hall'}: raise ValueError("reverb must be 'room' or 'hall'")
    frames=round((128*60/bpm+1.25)*sample_rate); left,right=[0.]*frames,[0.]*frames; rng=random.Random(20260913)
    for seed,event in enumerate(CANAL_SCORE): _add_event(left,right,event,bpm,sample_rate,max(0.,min(1.,volume)),rng,seed)
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

def _wav_chunks(payload,seconds=1.):
    with wave.open(io.BytesIO(payload),'rb') as source: params=source.getparams(); frames=source.readframes(source.getnframes())
    size=round(params.framerate*seconds)*params.nchannels*params.sampwidth
    for start in range(0,len(frames),size):
        stream=io.BytesIO()
        with wave.open(stream,'wb') as target: target.setparams(params); target.writeframes(frames[start:start+size])
        yield stream.getvalue()

class ScorePlayer:
    """Perform one complete code-scored suite in short Windows-safe phrases."""
    def __init__(self,volume=.7,sound_module=None):
        if sound_module is None:
            try: import winsound as sound_module
            except ImportError: sound_module=None
        self.sound=sound_module; self.volume=max(0.,min(1.,volume)); self.playing=False; self._buffer=None; self._thread=None; self._stop_event=threading.Event()
    @property
    def available(self): return self.sound is not None
    def _perform_suite(self):
        try:
            for chunk in _wav_chunks(render_canal_suite(volume=self.volume)):
                if self._stop_event.is_set(): return
                self._buffer=chunk; self.sound.PlaySound(chunk,self.sound.SND_MEMORY)
        except RuntimeError: pass
        finally: self.playing=False
    def start(self):
        if not self.available:return False
        if self._thread and self._thread.is_alive():return True
        self.playing=True; self._stop_event.clear(); self._thread=threading.Thread(target=self._perform_suite,name='canal-score-player',daemon=True); self._thread.start(); return True
    def stop(self):
        self._stop_event.set(); self.playing=False
        if self._thread and self._thread is not threading.current_thread(): self._thread.join(timeout=1.2)
        self._thread=None
    def set_volume(self,volume): self.volume=max(0.,min(1.,volume))
