"""Runtime parameters and defaults traceable to the 2023 conversation."""
from dataclasses import dataclass
from configparser import ConfigParser
from pathlib import Path

@dataclass(frozen=True)
class Config:
    calibration_seconds: float = 3.0  # 2023-11-22 version; 2023-11-11 was 30s
    ear_ratio: float = 0.8
    closed_frames: int = 10
    eye_offset_px: float = 20.0
    cooldown_seconds: float = 1.0
    resolution_width: int = 640
    resolution_height: int = 480
    frame_rate: float = 60.0
    pixel_format: str = 'XBGR8888'  # confirmed camera trial; hardware format should be checked
    min_calibration_samples: int = 3  # implementation safeguard, not measured historical value
    clip_delay_seconds: float = 4.0  # transition used in 2023-11-22 discussion
    before_reaction_delay_seconds: float = 4.0
    sound_backend: str = 'aplay'  # different from original playsound; runtime substitution
    quiz_backend: str = 'google'  # can be 'disabled' for offline tests
    quiz_record_seconds: float = 5.0  # inference; original 222.py experiment used 1 second
    loudness_rate: int = 44100
    loudness_chunk: int = 1024
    loudness_seconds: float = 5.0
    loudness_threshold: float = 70.0  # 20*log10(raw_PCM_RMS), NOT calibrated dB SPL
    loudness_max_attempts: int = 3  # new fail-safe; historical max attempts unknown

    @classmethod
    def load(cls, path: Path):
        p=ConfigParser()
        if not path.is_file():
            raise FileNotFoundError(f'Missing config file: {path}')
        p.read(path,encoding='utf-8')
        if 'drowsiness' not in p:
            raise ValueError('Expected [drowsiness] in config.ini')
        defaults=cls()
        values={}
        for key,default in vars(defaults).items():
            if isinstance(default,int) and not isinstance(default,bool):
                val=p.getint('drowsiness',key,fallback=default)
            elif isinstance(default,float):
                val=p.getfloat('drowsiness',key,fallback=default)
            else:
                val=p.get('drowsiness',key,fallback=default)
            values[key]=val
        c=cls(**values)
        if c.calibration_seconds<0 or not 0<c.ear_ratio<=1 or c.closed_frames<1 or c.min_calibration_samples<1:
            raise ValueError('Invalid detection thresholds')
        if c.loudness_max_attempts<1 or c.loudness_seconds<=0 or c.cooldown_seconds<0:
            raise ValueError('Invalid timing or loudness settings')
        if c.quiz_backend not in ('google','disabled'):
            raise ValueError('quiz_backend should be google or disabled')
        if c.sound_backend not in ('aplay','playsound','disabled'):
            raise ValueError('sound_backend should be aplay, playsound or disabled')
        return c
