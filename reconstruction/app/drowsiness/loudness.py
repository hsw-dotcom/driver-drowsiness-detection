"""Rebuild of described decibel.py logic; value is raw PCM reference level.

The original described algorithm was 20*log10(RMS/1.0), threshold > 70.
This is neither calibrated dB SPL nor ordinary normalized dBFS.
"""
from array import array
from math import log10,sqrt
import sys


def rms_int16_bytes(data:bytes)->float:
    if len(data)%2:
        raise ValueError('16-bit PCM must contain even number of bytes')
    if not data:
        return 0.0
    samples=array('h')
    samples.frombytes(data)
    if sys.byteorder!='little': samples.byteswap()
    return sqrt(sum(sample*sample for sample in samples)/len(samples))


def raw_pcm_db(rms):
    return 20*log10(max(float(rms),1e-12)/1.0)


def measure_average_db(seconds=5.0,rate=44100,chunk=1024,stream_factory=None):
    # Pure-function stream factory injectable for tests, no PyAudio import until needed.
    if stream_factory is None:
        import pyaudio
        api=pyaudio.PyAudio()
        try:
            stream=api.open(format=pyaudio.paInt16,channels=1,rate=rate,
                            input=True,frames_per_buffer=chunk)
            values=_record_db_values(stream,seconds,rate,chunk)
        finally:
            try: stream.stop_stream(); stream.close()
            except (NameError,AttributeError): pass
            api.terminate()
    else:
        stream=stream_factory()
        try: values=_record_db_values(stream,seconds,rate,chunk)
        finally:
            close=getattr(stream,'close',None)
            if close: close()
    return sum(values)/len(values) if values else float('-inf')


def _record_db_values(stream,seconds,rate,chunk):
    count=max(1,round(seconds*rate/chunk))
    return [raw_pcm_db(rms_int16_bytes(stream.read(chunk,exception_on_overflow=False)))
            for _ in range(count)]


def wait_for_loud_reaction(audio,threshold=70.,seconds=5.,rate=44100,chunk=1024,
                           max_attempts=3,dry_run=False):
    if dry_run:
        print('[loudness simulation] No microphone read, expected threshold >',threshold)
        return False
    for n in range(1,max_attempts+1):
        try:
            level=measure_average_db(seconds,rate,chunk)
        except Exception as exc:
            print('[microphone error]',type(exc).__name__,str(exc))
            return False
        print(f'[loudness attempt {n}/{max_attempts}] average raw-PCM dB={level:.2f}')
        if level>threshold:
            audio.play('success.wav')
            return True
        if n<max_attempts: audio.play('da.wav')
    return False
