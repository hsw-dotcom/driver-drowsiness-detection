"""Nov 22 three-event escalation; no face inference during a reaction.

1: wa.wav -> warning.wav
2: da.wav -> danger.wav -> quiz/STT
3: da.wav -> decibel.wav -> RMS loudness check, then reset counter.
"""
from dataclasses import dataclass
import time

@dataclass(frozen=True)
class ReactionResult:
    stage:int
    outcome:str
    detail:str=''

class WarningStages:
    def __init__(self,audio,config,quiz_fn,loudness_fn,sleep_fn=time.sleep):
        self.audio=audio
        self.config=config
        self.quiz_fn=quiz_fn
        self.loudness_fn=loudness_fn
        self.sleep_fn=sleep_fn
        self.warning_count=0
        self.busy=False

    def _sequence(self,clips):
        for i,clip in enumerate(clips):
            if i and self.config.clip_delay_seconds:
                self.sleep_fn(self.config.clip_delay_seconds)
            self.audio.play(clip)

    def _pause_before_activity(self):
        if self.config.before_reaction_delay_seconds:
            self.sleep_fn(self.config.before_reaction_delay_seconds)

    def on_alert(self):
        if self.busy:
            return ReactionResult(self.warning_count,'busy','skipped duplicate')
        self.busy=True
        self.warning_count=self.warning_count%3+1
        stage=self.warning_count
        try:
            if stage==1:
                self._sequence(('wa.wav','warning.wav'))
                return ReactionResult(stage,'warning-audio')
            if stage==2:
                self._sequence(('da.wav','danger.wav'))
                self._pause_before_activity()
                result=self.quiz_fn()
                return ReactionResult(stage,'quiz-correct' if result.correct else 'quiz-not-confirmed',result.transcript)
            self._sequence(('da.wav','decibel.wav'))
            self._pause_before_activity()
            answered=bool(self.loudness_fn())
            return ReactionResult(stage,'volume-response' if answered else 'volume-not-confirmed')
        except Exception as exc:
            # Stage should exit even on missing cloud credentials/audio device.
            print(f'[warning stage error {stage}] {exc}')
            return ReactionResult(stage,'error',type(exc).__name__)
        finally:
            self.busy=False
