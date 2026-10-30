"""2026 reconstructed integrated drowsiness camera (NOT original 2023 deployment).

Running demo mode exercises alert sequencing without hardware; --no-display for
Raspberry Pi headless launch. Prototype only: not a certified safety system.
"""
import argparse
from pathlib import Path
import sys
import time

from drowsiness.config import Config
from drowsiness.vision import DrowsinessLogic,eye_metrics
from drowsiness.audio import Audio
from drowsiness.quiz import run_quiz
from drowsiness.loudness import wait_for_loud_reaction
from drowsiness.stages import WarningStages

HERE=Path(__file__).resolve().parent

def options():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=HERE/'config.ini')
    p.add_argument('--no-display',action='store_true')
    p.add_argument('--demo',action='store_true',help='no camera/audio/mic/cloud; run a scripted state trace')
    return p.parse_args()

def make_stages(cfg,simulation):
    audio=Audio(HERE/'assets'/'audio',cfg.sound_backend,dry_run=simulation)
    return WarningStages(audio,cfg,
        quiz_fn=lambda:run_quiz(cfg.quiz_record_seconds,cfg.quiz_backend,dry_run=simulation),
        loudness_fn=lambda:wait_for_loud_reaction(audio,cfg.loudness_threshold,cfg.loudness_seconds,
                  cfg.loudness_rate,cfg.loudness_chunk,cfg.loudness_max_attempts,dry_run=simulation),
        sleep_fn=(lambda seconds:None) if simulation else time.sleep)

def make_logic(cfg):
    return DrowsinessLogic(cfg.calibration_seconds,cfg.ear_ratio,
        cfg.closed_frames,cfg.eye_offset_px,cfg.cooldown_seconds,cfg.min_calibration_samples)

def demo(cfg):
    logic=make_logic(cfg)
    stages=make_stages(cfg,True)
    now=0.0
    for _ in range(max(3,cfg.min_calibration_samples)):
        print(f'[demo calibration] {logic.update(now,.3,200).status}')
        now+=max(.1,cfg.calibration_seconds/max(3,cfg.min_calibration_samples))
    now=max(now,cfg.calibration_seconds+.1)
    for stage in range(3):
        for frame in range(cfg.closed_frames):
            state=logic.update(now, .08, 200)
            now+=.05
            if state.trigger:
                event=stages.on_alert()
                print(f'[demo alert] stage {event.stage} => {event.outcome}')
                logic.finish_alert(now)
                break
        # Require recovery + cooldown before next event.
        now+=cfg.cooldown_seconds+.1
        print('[demo recovery]',logic.update(now,.3,200).status)
    print('[demo finished] 3 alert stages; next event will return to stage 1')

def run_real(cfg,no_display):
    import cv2
    import dlib
    from drowsiness.camera import open_camera,convert_for_detector,convert_for_display
    model=HERE/'assets'/'models'/'shape_predictor_68_face_landmarks.dat'
    if not model.is_file():
        raise FileNotFoundError(f'Missing dlib model: {model}. See assets/README.md')
    predictor=dlib.shape_predictor(str(model))
    face_detector=dlib.get_frontal_face_detector()
    stages=make_stages(cfg,False)
    logic=make_logic(cfg)
    print('[run] vision detection active; press ESC or Ctrl+C to exit')
    with open_camera(cfg) as camera:
        try:
            while True:
                # During synchronous stage execution below, no extra OpenCV detection
                # occurs. Camera remains streaming, capture resumes afterwards.
                frame=camera.capture_array()
                gray=convert_for_detector(frame,cfg.pixel_format)
                faces=face_detector(gray,0)
                metrics=None
                ear=eye_y=None
                if faces:
                    # Prefer largest visible face; original selected all faces.
                    face=max(faces,key=lambda r:r.width()*r.height())
                    metrics=eye_metrics(predictor(gray,face))
                    ear,eye_y=metrics[:2]
                now=time.monotonic()
                state=logic.update(now,ear,eye_y)
                if state.trigger:
                    print(f'[detected] {state.reason}, EAR={ear:.3f}, eye_y={eye_y:.1f}')
                    reaction=stages.on_alert()
                    print(f'[stage {reaction.stage}] {reaction.outcome} {reaction.detail}')
                    logic.finish_alert(time.monotonic())
                if not no_display:
                    color=convert_for_display(frame,cfg.pixel_format)
                    if metrics:
                        for px,py in metrics[2]+metrics[3]:
                            cv2.circle(color,(px,py),1,(0,255,0),-1)
                    label=f'{state.status}/{state.reason} EAR={ear:.3f}' if ear is not None else f'{state.status}/{state.reason}'
                    cv2.putText(color,label,(10,30),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)
                    cv2.putText(color,f'Warnings={stages.warning_count} Closed={state.closed_frames}',
                                (10,60),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)
                    cv2.imshow('Drowsiness reconstruction',color)
                    if cv2.waitKey(1)==27:break
        except KeyboardInterrupt: pass
        finally:
            if not no_display: cv2.destroyAllWindows()

def main():
    args=options()
    try: cfg=Config.load(args.config)
    except Exception as exc: raise SystemExit(str(exc)) from exc
    if args.demo: demo(cfg)
    else: run_real(cfg,args.no_display)

if __name__=='__main__': main()
