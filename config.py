"""최종 발표와 당시 개발 기록에서 확인된 핵심 설정."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / 'audio'  # 별도 확보해야 하는 당시 WAV 파일
MODEL_FILE = BASE_DIR / 'shape_predictor_68_face_landmarks.dat'

FRAME_SIZE = (640, 480)
PIXEL_FORMAT = 'XBGR8888'
FRAME_RATE = 60
CALIBRATION_SECONDS = 3
EAR_RATIO = 0.8
CLOSED_FRAMES = 10
EYE_DROP_PX = 20
IGNORE_SECONDS = 1
QUIZ_SECONDS = 10
VOLUME_SECONDS = 5
VOLUME_THRESHOLD = 70  # 정규화/교정된 실제 SPL이 아닌 PCM RMS 기반 값
