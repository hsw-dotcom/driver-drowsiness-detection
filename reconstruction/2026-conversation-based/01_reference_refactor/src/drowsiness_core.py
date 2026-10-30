"""2026 reference-only separation of the thresholds seen in 2023 `test_v2.py`.

Not the original deployed code. Pure Python, with no camera or cloud API dependencies.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DrowsinessDetector:
    calibration_seconds: float = 30.0
    ear_ratio: float = 0.8
    eye_level_offset_px: float = 20.0
    closed_frame_threshold: int = 10
    sample_ear: list[float] = field(default_factory=list)
    sample_eye_level: list[float] = field(default_factory=list)
    closed_frames: int = 0

    def update(self, ear: Optional[float], eye_level: Optional[float], elapsed: float) -> dict:
        calibrated = elapsed >= self.calibration_seconds
        if ear is not None and eye_level is not None and not calibrated:
            self.sample_ear.append(float(ear))
            self.sample_eye_level.append(float(eye_level))

        if not self.sample_ear or not self.sample_eye_level:
            return {'ready': False, 'alert': False, 'reason': 'no-calibration', 'closed_frames': self.closed_frames}

        mean_ear = sum(self.sample_ear) / len(self.sample_ear)
        mean_eye_level = sum(self.sample_eye_level) / len(self.sample_eye_level)
        closed_ear = mean_ear * self.ear_ratio
        threshold_level = mean_eye_level + self.eye_level_offset_px
        alert = False
        reason = 'calibrating' if not calibrated else 'normal'
        if calibrated:
            if ear is None or eye_level is None:
                self.closed_frames = 0
                reason = 'face-not-detected'
            else:
                self.closed_frames = (self.closed_frames + 1) if ear <= closed_ear else 0
                if self.closed_frames >= self.closed_frame_threshold:
                    alert = True
                    reason = 'eyes-closed'
                if eye_level > threshold_level:
                    alert = True
                    reason = 'eye-level'
        return {
            'ready': calibrated, 'alert': alert, 'reason': reason,
            'closed_frames': self.closed_frames, 'mean_ear': round(mean_ear, 4),
            'closed_ear': round(closed_ear, 4),
            'mean_eye_level': round(mean_eye_level, 2),
            'threshold_eye_level': round(threshold_level, 2),
        }


def calculate_ear(points):
    """Compute eye aspect ratio from six (x,y) landmarks, same formula as source."""
    from math import dist
    if len(points) != 6:
        raise ValueError('one eye must have six points')
    width = dist(points[0], points[3])
    if width <= 0:
        raise ValueError('eye horizontal width must be nonzero')
    return (dist(points[1], points[5]) + dist(points[2], points[4])) / (2.0 * width)
