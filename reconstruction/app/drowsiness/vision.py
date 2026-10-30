"""EAR, calibration and alert gating independent of camera hardware.

Nov 22 settings supersede the Nov 11 defaults; unlike the earlier 30-second
prototype, the final conversation had calibration_seconds=3.
"""
from dataclasses import dataclass
from math import dist
from typing import Optional


def ear_for_eye(points):
    if len(points)!=6:
        raise ValueError('six eye landmarks are required')
    horizontal=dist(points[0],points[3])
    if horizontal<=0:
        raise ValueError('invalid zero-width eye')
    return (dist(points[1],points[5])+dist(points[2],points[4]))/(2*horizontal)


def eye_metrics(shape):
    # Indices 36..41 and 42..47 from the original dlib 68-point predictor.
    right=[(shape.part(n).x,shape.part(n).y) for n in range(36,42)]
    left=[(shape.part(n).x,shape.part(n).y) for n in range(42,48)]
    ear=(ear_for_eye(right)+ear_for_eye(left))/2
    eye_y=(right[0][1]+left[3][1])/2  # test_v2.py logic
    return ear,eye_y,right,left

@dataclass(frozen=True)
class FrameResult:
    status: str
    reason: str
    trigger: bool = False
    ear: Optional[float] = None
    baseline_ear: Optional[float] = None
    baseline_eye_y: Optional[float] = None
    closed_frames: int = 0

class DrowsinessLogic:
    def __init__(self, calibration_seconds=3., ear_ratio=.8, closed_frames=10,
                 eye_offset_px=20., cooldown_seconds=1., min_calibration_samples=3):
        self.calibration_seconds=calibration_seconds
        self.ear_ratio=ear_ratio
        self.closed_frame_threshold=closed_frames
        self.eye_offset_px=eye_offset_px
        self.cooldown_seconds=cooldown_seconds
        self.min_calibration_samples=min_calibration_samples
        self.started_at=None
        self.ears=[]
        self.eye_levels=[]
        self.baseline_ear=None
        self.baseline_eye_y=None
        self.closed_count=0
        self.latched=False
        self.cooldown_until=float('-inf')

    def _reset_count(self):
        self.closed_count=0

    def finish_alert(self, now: float):
        """Called AFTER blocking audio/quiz/loudness. Prevent immediate retriggers."""
        self.cooldown_until=now+self.cooldown_seconds
        self.closed_count=0
        self.latched=True  # require normal observation to re-arm

    def update(self, now:float, ear:Optional[float], eye_y:Optional[float]):
        if self.started_at is None:
            self.started_at=now
        if self.baseline_ear is None:
            if ear is not None and eye_y is not None and ear>0:
                self.ears.append(float(ear))
                self.eye_levels.append(float(eye_y))
            if now-self.started_at < self.calibration_seconds or len(self.ears)<self.min_calibration_samples:
                return FrameResult('calibrating','waiting-for-baseline',ear=ear)
            self.baseline_ear=sum(self.ears)/len(self.ears)
            self.baseline_eye_y=sum(self.eye_levels)/len(self.eye_levels)
        kw=dict(ear=ear,baseline_ear=self.baseline_ear,baseline_eye_y=self.baseline_eye_y,closed_frames=self.closed_count)
        if now<self.cooldown_until:
            return FrameResult('cooldown','post-warning-ignore',**kw)
        if ear is None or eye_y is None:
            self._reset_count()
            # No face cannot prove alert or recovery; stay latched if previously triggered.
            return FrameResult('no-face','face-not-detected',**{**kw,'closed_frames':0})
        eye_closed=ear<=self.baseline_ear*self.ear_ratio
        head_down=eye_y>self.baseline_eye_y+self.eye_offset_px
        self.closed_count=self.closed_count+1 if eye_closed else 0
        abnormal=self.closed_count>=self.closed_frame_threshold or head_down
        if not abnormal:
            self.latched=False
            return FrameResult('normal','normal',**{**kw,'closed_frames':self.closed_count})
        reason='closed-eyes' if self.closed_count>=self.closed_frame_threshold else 'head-or-eye-drop'
        if self.latched:
            return FrameResult('latched',reason,**{**kw,'closed_frames':self.closed_count})
        self.latched=True
        return FrameResult('alert',reason,trigger=True,**{**kw,'closed_frames':self.closed_count})
