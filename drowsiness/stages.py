"""Final presentation flow: warning -> question -> loudness -> warning.

Failed question/volume responses DO NOT advance the stage and are repeated
without an arbitrary attempt limit. Unavailable hardware/API raises an error;
an error is not mistaken for successful wake-up or stage completion.
"""
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class ReactionResult:
    stage: int
    outcome: str
    detail: str = ''


class WarningStages:
    def __init__(self, audio, config, quiz_fn, loudness_fn, sleep_fn=time.sleep):
        self.audio = audio
        self.config = config
        self.quiz_fn = quiz_fn
        self.loudness_fn = loudness_fn
        self.sleep_fn = sleep_fn
        self.warning_count = 0
        self.busy = False

    def _sequence(self, clips):
        for i, clip in enumerate(clips):
            if i and self.config.clip_delay_seconds:
                self.sleep_fn(self.config.clip_delay_seconds)
            self.audio.play(clip)

    def _pause_before_activity(self):
        if self.config.before_reaction_delay_seconds:
            self.sleep_fn(self.config.before_reaction_delay_seconds)

    def on_alert(self):
        if self.busy:
            return ReactionResult(self.warning_count % 3 + 1, 'busy', 'duplicate ignored')
        stage = self.warning_count % 3 + 1
        self.busy = True
        try:
            # 2023 vehicle-test video shows playy("detect.wav") after detection.
            # User confirmed the common detection alarm precedes ALL stages.
            self.audio.play('detect.wav')
            if stage == 1:
                self._sequence(('wa.wav', 'warning.wav'))
                outcome = 'warning-audio'
                detail = ''
            elif stage == 2:
                self._sequence(('da.wav', 'danger.wav'))
                self._pause_before_activity()
                # Presentation: an incorrect/unrecognized answer stays at the
                # question until it is solved. The supplied quiz runner also
                # repeats the SAME question internally, as original test1.py.
                while True:
                    answer = self.quiz_fn()
                    if answer.correct:
                        break
                outcome = 'quiz-correct'
                detail = answer.transcript
            else:
                self._sequence(('da.wav', 'decibel.wav'))
                self._pause_before_activity()
                # Presentation: below-threshold sound repeats without a cap.
                while not self.loudness_fn():
                    pass
                outcome = 'volume-response'
                detail = ''

            # Advance only after completing this stage; 3 -> 1 automatically.
            self.warning_count = stage
            return ReactionResult(stage, outcome, detail)
        except Exception as exc:
            # A genuine input/service failure is not a solved question or a
            # valid volume response. Keep this stage pending on next alert.
            print(f'[warning stage error {stage}] {type(exc).__name__}: {exc}')
            return ReactionResult(stage, 'error', type(exc).__name__)
        finally:
            self.busy = False
