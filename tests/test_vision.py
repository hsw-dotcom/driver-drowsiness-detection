import unittest
from drowsiness.vision import DrowsinessLogic,ear_for_eye

class TestVision(unittest.TestCase):
    def init_logic(self):
        d=DrowsinessLogic(calibration_seconds=3,closed_frames=10)
        for t in (0,1,2): self.assertEqual(d.update(t,.3,100).status,'calibrating')
        self.assertEqual(d.update(3,.3,100).status,'normal')
        return d
    def test_ear(self):
        p=[(0,0),(1,1),(3,1),(4,0),(3,-1),(1,-1)]
        self.assertAlmostEqual(ear_for_eye(p),.5)
    def test_wrong_landmarks(self):
        with self.assertRaises(ValueError):ear_for_eye([(0,0)])
    def test_calibrating_only(self):
        d=DrowsinessLogic()
        self.assertFalse(d.update(0,.3,100).trigger)
    def test_no_face_no_early_ready(self):
        d=DrowsinessLogic()
        self.assertEqual(d.update(9,None,None).status,'calibrating')
    def test_10_consecutive_eye_frames(self):
        d=self.init_logic()
        for i in range(9):self.assertFalse(d.update(3.1+i*.1,.1,100).trigger)
        self.assertTrue(d.update(4.0,.1,100).trigger)
    def test_eye_recovery_breaks_consecutive(self):
        d=self.init_logic()
        for i in range(8):d.update(4+i*.1,.1,100)
        d.update(5,.3,100)
        self.assertFalse(d.update(5.1,.1,100).trigger)
    def test_eye_level_20_px(self):
        d=self.init_logic()
        self.assertFalse(d.update(4,.3,120).trigger)
        self.assertTrue(d.update(4.1,.3,121).trigger)
    def test_immediate_head_drop_and_persistence_are_both_recorded(self):
        d=self.init_logic()
        for frame in range(1,11):
            state=d.update(3+frame*.1,.3,125)
            self.assertTrue(state.trigger)  # immediate drop remains effective
            self.assertEqual(state.head_down_frames,frame)  # 10-frame path tracked
        self.assertEqual(state.head_down_frames,10)
        d.finish_alert(4.05)
        self.assertEqual(d.head_down_count,0)
        normal=d.update(5.10,.3,100)
        self.assertEqual(normal.head_down_frames,0)

    def test_no_face_resets_head_down_counter(self):
        d=self.init_logic()
        self.assertEqual(d.update(4,.3,125).head_down_frames,1)
        self.assertEqual(d.update(4.2,None,None).head_down_frames,0)
        self.assertEqual(d.update(4.3,.3,125).head_down_frames,1)

    def test_no_face_reset(self):
        d=self.init_logic()
        for i in range(5):d.update(4+i*.1,.1,100)
        self.assertEqual(d.update(5,None,None).status,'no-face')
        self.assertEqual(d.update(5.1,.1,100).closed_frames,1)
    def test_unconfirmed_rearm_not_required(self):
        d=self.init_logic()
        self.assertTrue(d.update(4,.3,125).trigger)
        d.finish_alert(4.1)
        self.assertEqual(d.update(5.0,.3,125).status,'cooldown')
        # Original conversation specified 1-second ignore, not a separate
        # normal-frame rearm requirement.
        self.assertTrue(d.update(5.11,.3,125).trigger)
    def test_post_warning_cooldown(self):
        d=self.init_logic(); d.update(4,.3,125)
        d.finish_alert(5)
        self.assertEqual(d.update(5.9,.3,125).status,'cooldown')
        self.assertTrue(d.update(6,.3,125).trigger)
        d.finish_alert(6.05)
        self.assertEqual(d.update(6.1,.3,125).status,'cooldown')
        self.assertEqual(d.update(7.06,.3,100).status,'normal')
        self.assertTrue(d.update(7.1,.3,125).trigger)

if __name__=='__main__':unittest.main()
