"""Picamera2 adapter. 4-channel preview avoids earlier YUV420 cvtColor error."""
from contextlib import contextmanager

@contextmanager
def open_camera(cfg):
    from picamera2 import Picamera2
    picam2=Picamera2()
    config=picam2.create_preview_configuration(main={
        'size':(cfg.resolution_width,cfg.resolution_height),'format':cfg.pixel_format})
    picam2.configure(config)
    try:
        picam2.set_controls({'FrameRate':float(cfg.frame_rate)})
    except Exception as exc:
        print(f'[camera] FrameRate request not accepted: {exc}')
    picam2.start()
    try: yield picam2
    finally: picam2.stop(); picam2.close()


def convert_for_detector(frame,pixel_format):
    import cv2
    # Original conversation used BGR2GRAY while XBGR8888 frame was color.
    # cv2.COLOR_BGR2GRAY accepts either 3 or 4 channel BGR/BGRA buffers.
    if frame.ndim==2: return frame
    if pixel_format in ('RGB888','RGBA8888'):
        return cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    if pixel_format=='YUV420':
        # Packed planar I420: BGR2GRAY is incorrect for this shape.
        return cv2.cvtColor(frame,cv2.COLOR_YUV2GRAY_I420)
    return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)


def convert_for_display(frame,pixel_format):
    import cv2
    if frame.ndim==2:return cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR)
    if pixel_format in ('RGB888','RGBA8888'):
        return cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    if pixel_format=='YUV420':
        return cv2.cvtColor(frame,cv2.COLOR_YUV2BGR_I420)
    if frame.shape[2]==4:
        return cv2.cvtColor(frame,cv2.COLOR_BGRA2BGR)
    return frame.copy()
