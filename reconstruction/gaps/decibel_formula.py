"""MISSING-ORIGINAL GAP: the described numerical RMS/dB conversion only.

This is not the missing original 2023 ``decibel.py``. Audio recording,
device setup and original retry UI are deliberately NOT recreated here.
The output is relative to raw integer PCM sample amplitude, not dB SPL.
"""
from math import log10, sqrt


def program_relative_db(samples):
    """Calculate 20*log10(RMS/1) for a sequence of signed PCM samples.

    None is returned for empty input. Nonzero input containing only zeros
    yields negative infinity (avoid treating silence as a valid threshold).
    """
    values = list(samples)
    if not values:
        return None
    rms = sqrt(sum(float(s) * float(s) for s in values) / len(values))
    if rms == 0:
        return float('-inf')
    return 20 * log10(rms / 1.0)
