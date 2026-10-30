"""Restore the final presentation's unlimited loudness retry branch.

The scalar is 20*log10(raw PCM RMS/1), NOT calibrated physical dB SPL.
Historical decibel.py concatenated 5s of 44.1kHz mono PCM (1024-sample
chunks), calculated one overall RMS, and used threshold >70.
"""
from array import array
from math import log10, sqrt
import sys


def rms_int16_bytes(data: bytes) -> float:
    if len(data) % 2:
        raise ValueError('16-bit PCM must contain even number of bytes')
    if not data:
        return 0.0
    samples = array('h')
    samples.frombytes(data)
    if sys.byteorder != 'little':
        samples.byteswap()
    return sqrt(sum(sample * sample for sample in samples) / len(samples))


def raw_pcm_db(rms):
    return 20 * log10(max(float(rms), 1e-12) / 1.0)


def _record_whole_interval_db(stream, seconds, rate, chunk):
    """2023-11-22 decibel.py: concatenate all PCM chunks, then calculate ONE RMS.

    Averaging individual chunk dB levels is not equivalent to measuring the
    RMS of the entire five-second recording. This mirrors the pasted original.
    """
    count = int(rate / chunk * seconds)
    frames = [stream.read(chunk, exception_on_overflow=False)
              for _ in range(count)]
    return raw_pcm_db(rms_int16_bytes(b''.join(frames)))


def measure_average_db(seconds=5.0, rate=44100, chunk=1024,
                       stream_factory=None):
    if stream_factory is None:
        import pyaudio
        api = pyaudio.PyAudio()
        stream = None
        try:
            stream = api.open(format=pyaudio.paInt16, channels=1, rate=rate,
                              input=True, frames_per_buffer=chunk)
            level = _record_whole_interval_db(stream, seconds, rate, chunk)
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            api.terminate()
    else:
        stream = stream_factory()
        try:
            level = _record_whole_interval_db(stream, seconds, rate, chunk)
        finally:
            close = getattr(stream, 'close', None)
            if close:
                close()
    return level


def wait_for_loud_reaction(audio, threshold=70., seconds=5., rate=44100,
                           chunk=1024, dry_run=False, measure_fn=None):
    """Repeat until a sufficient response; no historical attempt cap.

    Device failures propagate to the caller rather than masquerading as a
    solved level. A dry run makes ONLY a simulated passing response.
    """
    if dry_run:
        print('[loudness simulation] simulated response above threshold', threshold)
        return True
    measure_fn = measure_fn or measure_average_db
    attempt = 0
    while True:
        attempt += 1
        level = measure_fn(seconds, rate, chunk)
        print(f'[loudness attempt {attempt}] raw-PCM score={level:.2f}')
        if level > threshold:
            audio.play('success.wav')  # observed in the 2023-11-22 decibel.py
            return True
        # Repeat BOTH the warning cue and the explanatory guidance.
        # The user confirmed that guidance repeats after each insufficient read.
        audio.play('da.wav')
        audio.play('decibel.wav')
