"""dlib 68점 중 눈 위치와 EAR만 사용한 졸음 감지."""
from math import dist
from config import (CALIBRATION_SECONDS, EAR_RATIO, CLOSED_FRAMES,
                    EYE_DROP_PX, IGNORE_SECONDS)


def eye_aspect_ratio(points):
    """6개 눈 랜드마크의 (A+B)/(2*C)."""
    a = dist(points[1], points[5])
    b = dist(points[2], points[4])
    c = dist(points[0], points[3])
    return (a + b) / (2 * c)


def eye_values(shape):
    right = [(shape.part(i).x, shape.part(i).y) for i in range(36, 42)]
    left = [(shape.part(i).x, shape.part(i).y) for i in range(42, 48)]
    ear = (eye_aspect_ratio(right) + eye_aspect_ratio(left)) / 2
    # 2023 test_v2.py: (42번 눈의 첫 점 + 36번 눈의 네 번째 점) / 2
    eye_y = int((left[0][1] + right[3][1]) / 2)
    return ear, eye_y


class EyeDetector:
    def __init__(self):
        self.started = None
        self.samples = []
        self.baseline = None
        self.closed_frames = 0
        self.ignore_until = 0

    def update(self, now, ear=None, eye_y=None):
        """새 졸음 감지 여부. 얼굴 미검출 시 False."""
        if self.started is None:
            self.started = now
        if self.baseline is None:
            if ear is not None and eye_y is not None and ear > 0:
                self.samples.append((ear, eye_y))
            if now - self.started < CALIBRATION_SECONDS or not self.samples:
                return False
            n = len(self.samples)
            self.baseline = (sum(e for e, y in self.samples) / n,
                             sum(y for e, y in self.samples) / n)
            self.samples.clear()
        if now < self.ignore_until:
            return False
        if ear is None or eye_y is None:
            self.closed_frames = 0
            return False

        avg_ear, avg_y = self.baseline
        self.closed_frames = self.closed_frames + 1 if ear <= avg_ear * EAR_RATIO else 0
        # 원본의 눈 감김 10프레임과 눈높이 +20px 감지.
        # 동일 눈높이 임계의 10프레임 누적은 즉시 감지에 포함되므로 중복하지 않는다.
        return self.closed_frames >= CLOSED_FRAMES or eye_y > avg_y + EYE_DROP_PX

    def after_warning(self, now):
        self.closed_frames = 0
        self.ignore_until = now + IGNORE_SECONDS
