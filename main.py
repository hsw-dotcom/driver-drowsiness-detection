"""졸음운전 감지 카메라 — 2023년 캡스톤디자인 핵심 기능 정리 코드."""
import argparse
import time

from config import AUDIO_DIR, MODEL_FILE, FRAME_SIZE, PIXEL_FORMAT, FRAME_RATE
from detection import EyeDetector, eye_values
from voice import ask_until_correct
from decibel import confirm_loudness


def play_audio(filename):
    from playsound import playsound
    path = AUDIO_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f'경고음 파일 없음: {path}')
    playsound(str(path))


def run_stage(stage, play=play_audio, quiz=ask_until_correct, loud=confirm_loudness):
    """졸음 감지 시 공통 경고음 후 1→2→3→1 순서로 진행."""
    if stage not in (1, 2, 3):
        raise ValueError('잘못된 경고 단계')
    play('detect.wav')
    if stage == 1:
        play('wa.wav')
        play('warning.wav')
    elif stage == 2:
        play('da.wav')
        play('danger.wav')
        quiz(play)
    else:
        play('da.wav')
        play('decibel.wav')
        loud(play)
    return stage % 3 + 1


def demo():
    detector = EyeDetector()
    for second in (0., 1., 2., 3.):
        detector.update(second, 0.30, 200)
    stage = 1
    def print_clip(name):
        print('  재생:', name)
    for _ in range(4):
        when = detector.ignore_until + 4
        for i in range(10):
            triggered = detector.update(when + i * 0.05, 0.10, 200)
            if triggered:
                print('감지 →', stage, '단계')
                stage = run_stage(stage, print_clip, lambda _: print('  문제 정답 (모의)'),
                                  lambda _: print('  음량 통과 (모의)'))
                detector.after_warning(when + i * 0.05)
                break
        else:
            raise AssertionError('졸음 감지 모의 실행 실패')
    assert stage == 2
    print('단계 순환: 1 → 2 → 3 → 1 확인 (하드웨어 미사용)')


def run_camera():
    import cv2
    import dlib
    from picamera2 import Picamera2
    if not MODEL_FILE.is_file():
        raise FileNotFoundError(f'dlib 68점 모델 파일이 없습니다: {MODEL_FILE}')

    face_detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(str(MODEL_FILE))
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(
        main={'size': FRAME_SIZE, 'format': PIXEL_FORMAT}))
    camera.set_controls({'FrameRate': FRAME_RATE})
    camera.start()
    detection = EyeDetector()
    stage = 1
    try:
        while True:
            frame = camera.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray)
            ear, eye_y = (None, None)
            if faces:
                ear, eye_y = eye_values(predictor(gray, faces[0]))
            if detection.update(time.monotonic(), ear, eye_y):
                print('졸음 감지:', stage, '단계')
                try:
                    stage = run_stage(stage)
                finally:
                    detection.after_warning(time.monotonic())
            cv2.imshow('Drowsiness Camera', frame)
            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.stop()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='장치 없는 단계 흐름 확인')
    args = parser.parse_args()
    demo() if args.demo else run_camera()
