"""Dependency-free tests for the 2026 reference-only pure threshold logic."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.drowsiness_core import DrowsinessDetector, calculate_ear

class DetectorTests(unittest.TestCase):
    def test_wait_for_calibration(self):
        d=DrowsinessDetector(calibration_seconds=30)
        s=d.update(.3,100,0)
        self.assertFalse(s['ready'])
        self.assertFalse(s['alert'])
    def test_closed_eyes_after_ten_frames(self):
        d=DrowsinessDetector()
        d.update(.3,100,0)
        for i in range(9):
            self.assertFalse(d.update(.1,100,31+i)['alert'])
        self.assertEqual(d.update(.1,100,40)['reason'],'eyes-closed')
    def test_eye_level(self):
        d=DrowsinessDetector()
        d.update(.3,100,0)
        self.assertEqual(d.update(.3,121,31)['reason'],'eye-level')
    def test_no_face_resets_counter(self):
        d=DrowsinessDetector(closed_frame_threshold=2)
        d.update(.3,100,0)
        d.update(.1,100,31)
        self.assertFalse(d.update(None,None,32)['alert'])
        self.assertFalse(d.update(.1,100,33)['alert'])
    def test_ear(self):
        points = [(0,0),(1,1),(3,1),(4,0),(3,-1),(1,-1)]
        self.assertAlmostEqual(calculate_ear(points),.5)

if __name__=='__main__':
    unittest.main()
