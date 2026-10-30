"""Sequential alerts: camera stays active but analysis pauses during reactions."""
from pathlib import Path
import subprocess
import time

class Audio:
    def __init__(self,audio_dir:Path,backend='aplay',dry_run=False):
        self.audio_dir=Path(audio_dir)
        self.backend=backend
        self.dry_run=dry_run

    def play(self,name:str):
        if self.dry_run or self.backend=='disabled':
            print(f'[audio simulation] {name}')
            return
        path=self.audio_dir/name
        if not path.is_file():
            raise FileNotFoundError(f'Required historical alert WAV not available: {path}')
        if self.backend=='aplay':
            try:
                subprocess.run(['aplay','-q',str(path)],check=True,timeout=30)
            except (OSError,subprocess.SubprocessError) as exc:
                print(f'[audio playback error] {exc}')
        elif self.backend=='playsound':
            try:
                from playsound import playsound
                playsound(str(path),block=True)
            except Exception as exc:
                print(f'[audio playback error] {exc}')
        else:
            raise ValueError('Unknown audio backend')

    def sequence(self,names,delay_seconds:float):
        for index,name in enumerate(names):
            if index and delay_seconds:
                time.sleep(delay_seconds if not self.dry_run else 0)
            self.play(name)
