"""5초 녹음 전체의 RMS를 사용한 3단계 음량 확인."""
from array import array
from math import log10, sqrt
import sys

from config import VOLUME_SECONDS, VOLUME_THRESHOLD


def pcm_level(data):
    """2023년 원본 대화의 20*log10(RMS/1). 실제 음압 dB SPL이 아니다."""
    samples = array('h')
    samples.frombytes(data)
    if sys.byteorder != 'little':
        samples.byteswap()
    if not samples:
        return float('-inf')
    rms = sqrt(sum(x * x for x in samples) / len(samples))
    return 20 * log10(rms) if rms else float('-inf')


def record_level(seconds=VOLUME_SECONDS):
    import pyaudio
    rate, chunk = 44100, 1024
    device = pyaudio.PyAudio()
    stream = None
    try:
        stream = device.open(format=pyaudio.paInt16, channels=1, rate=rate,
                             input=True, frames_per_buffer=chunk)
        frames = [stream.read(chunk, exception_on_overflow=False)
                  for _ in range(int(rate / chunk * seconds))]
        return pcm_level(b''.join(frames))
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        device.terminate()


def confirm_loudness(play_audio, measure=record_level):
    while True:
        if measure() > VOLUME_THRESHOLD:
            play_audio('success.wav')
            return
        play_audio('da.wav')
        play_audio('decibel.wav')  # 미달 시 안내 재생 후 재측정
