from pathlib import Path
import unittest
from drowsiness.config import Config

class TestConfig(unittest.TestCase):
    def test_history_defaults(self):
        c=Config.load(Path(__file__).resolve().parents[1]/'config.ini')
        self.assertEqual(c.calibration_seconds,3)
        self.assertEqual(c.closed_frames,10)
        self.assertEqual(c.pixel_format,'XBGR8888')
        self.assertEqual(c.loudness_threshold,70)
        self.assertEqual(c.quiz_record_seconds,10)
        self.assertEqual(c.sound_backend,'playsound')
        self.assertFalse(hasattr(c,'loudness_max_attempts'))
    def test_missing(self):
        with self.assertRaises(FileNotFoundError):Config.load(Path('/never_here_abc.ini'))
if __name__=='__main__':unittest.main()
