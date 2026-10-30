"""Reference demonstration; NOT archived 2023 original and NOT a road-safety device.

Reproduces the threshold concepts visible in test_v2.py, without audio or cloud APIs.
Run from the 01_reference_refactor directory on Raspberry Pi with Picamera2 and dlib.
"""
import argparse
from pathlib import Path
import time

from src.drowsiness_core import DrowsinessDetector, calculate_ear


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictor', type=Path, required=True, help='Path to shape_predictor_68_face_landmarks.dat')
    parser.add_argument('--no-display', action='store_true', help='Do not open an OpenCV window')
    parser.add_argument('--color-order', choices=['RGB','BGR'], default='RGB', help='Color order returned by your Picamera2 config')
    return parser.parse_args()


def run():
    args = cli()
    if not args.predictor.is_file():
        raise SystemExit('Landmark predictor missing: ' + str(args.predictor))
    import cv2
    import dlib
    from picamera2 import Picamera2

    detector = DrowsinessDetector()
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(str(args.predictor))
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={'size': (640,480), 'format': 'RGB888'}))
    camera.start()
    start = time.monotonic()
    prev_alert = False
    print('Prototype reference preview started; press ESC if display enabled. Ctrl+C to exit.')
    try:
        while True:
            frame = camera.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY if args.color_order=='RGB' else cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray)
            elapsed = time.monotonic() - start
            ear = level = None
            if len(faces):
                marks = shape_predictor(gray, faces[0])
                right_eye = [(marks.part(i).x, marks.part(i).y) for i in range(36,42)]
                left_eye = [(marks.part(i).x, marks.part(i).y) for i in range(42,48)]
                ear = (calculate_ear(right_eye)+calculate_ear(left_eye))/2
                # Match test_v2's average of landmarks 36 and 45 (image y increases downwards).
                level = (right_eye[0][1] + left_eye[3][1]) / 2
                if not args.no_display:
                    for x,y in right_eye + left_eye:
                        cv2.circle(frame,(x,y),1,(0,255,0),-1)
            state = detector.update(ear,level,elapsed)
            if state['alert'] and not prev_alert:
                print('ALERT: ' + state['reason'] + ' | elapsed=' + f'{elapsed:.1f}s')
            prev_alert = state['alert']
            if not args.no_display:
                cv2.putText(frame,'EAR=' + (f'{ear:.3f}' if ear is not None else 'N/A') + ' / ' + state['reason'],
                            (10,30),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
                # Image display assumes BGR conversion for RGB-frame previews; test on the actual camera.
                display = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR) if args.color_order=='RGB' else frame
                cv2.imshow('Drowsiness reference',display)
                if cv2.waitKey(1)==27:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()
        if not args.no_display:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    run()
