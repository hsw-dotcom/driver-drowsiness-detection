"""RECONSTRUCTED adapter for historical decibel.py (original unavailable)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from drowsiness.audio import Audio
from drowsiness.loudness import wait_for_loud_reaction
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    answered=wait_for_loud_reaction(Audio(root/'assets'/'audio'))
    print('volume response confirmed' if answered else 'no confirmed response')
    raise SystemExit(0 if answered else 1)
