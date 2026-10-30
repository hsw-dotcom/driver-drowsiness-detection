"""Restore the final presentation's unlimited loudness retry branch.

The scalar is 20*log10(raw PCM RMS/1), NOT calibrated physical dB SPL.
Historical single-measurement parameters were 44.1kHz, 1024 sample chunks,
about 5 seconds per measurement, threshold > 70 (development discussion).
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


def _record_db_values(stream, seconds, rate, chunk):
    count = max(1, round(seconds * rate / chunk))
    return [raw_pcm_db(rms_int16_bytes(
        stream.read(chunk, exception_on_overflow=False))) for _ in range(count)]


def measure_average_db(seconds=5.0, rate=44100, chunk=1024,
                       stream_factory=None):
    if stream_factory is None:
        import pyaudio
        api = pyaudio.PyAudio()
        stream = None
        try:
            stream = api.open(format=pyaudio.paInt16, channels=1, rate=rate,
                              input=True, frames_per_buffer=chunk)
            values = _record_db_values(stream, seconds, rate, chunk)
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            api.terminate()
    else:
        stream = stream_factory()
        try:
            values = _record_db_values(stream, seconds, rate, chunk)
        finally:
            close = getattr(stream, 'close', None)
            if close:
                close()
    return sum(values) / len(values) if values else float('-inf')


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
            return True
        audio.play('da.wav')  # repeat prompt on insufficient volume
