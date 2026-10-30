import unittest
from array import array
from drowsiness.loudness import rms_int16_bytes,raw_pcm_db,measure_average_db

class FakeStream:
    def __init__(self,value): self.value=value;self.closed=False
    def read(self,chunk,exception_on_overflow=False):return array('h',[self.value]*chunk).tobytes()
    def close(self):self.closed=True

class TestLoudness(unittest.TestCase):
    def test_rms_pcm(self):
        self.assertAlmostEqual(rms_int16_bytes(array('h',[3000,-3000]*4).tobytes()),3000)
    def test_70_threshold_is_raw_pcm_not_spl(self):
        self.assertLess(raw_pcm_db(3000),70)
        self.assertGreater(raw_pcm_db(4000),70)
    def test_empty_quiet(self):
        self.assertEqual(rms_int16_bytes(b''),0)
        self.assertLess(raw_pcm_db(0),0)
    def test_malformed_pcm(self):
        with self.assertRaises(ValueError):rms_int16_bytes(b'1')
    def test_fake_microphone(self):
        self.assertAlmostEqual(measure_average_db(seconds=.01,rate=100,chunk=1,stream_factory=lambda:FakeStream(4000)),raw_pcm_db(4000))

if __name__=='__main__':unittest.main()
