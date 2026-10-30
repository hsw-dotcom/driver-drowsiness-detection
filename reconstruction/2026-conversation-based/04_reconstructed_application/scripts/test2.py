"""RECONSTRUCTED adapter for historical test2.py (original unavailable)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from drowsiness.quiz import run_quiz
if __name__=='__main__':
    result=run_quiz()
    print(result)
    raise SystemExit(0 if result.correct else 1)
