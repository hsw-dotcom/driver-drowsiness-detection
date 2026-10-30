import unittest
from dataclasses import dataclass
from drowsiness.stages import WarningStages
from drowsiness.quiz import QuizResult,normalize_answer
from drowsiness.config import Config

class FakeAudio:
    def __init__(self):self.clips=[]
    def play(self,name):self.clips.append(name)

class StageTests(unittest.TestCase):
    def test_cycle_and_exact_file_sequence(self):
        sound=FakeAudio(); sleeps=[]; quiz=[]; loud=[]
        def check_quiz():quiz.append(True);return QuizResult('q',3,'3',True)
        def check_volume():loud.append(True);return True
        ctrl=WarningStages(sound,Config(),check_quiz,check_volume,sleep_fn=sleeps.append)
        self.assertEqual(ctrl.on_alert().outcome,'warning-audio')
        self.assertEqual(ctrl.on_alert().outcome,'quiz-correct')
        self.assertEqual(ctrl.on_alert().outcome,'volume-response')
        self.assertEqual(ctrl.warning_count,3)
        self.assertEqual(ctrl.on_alert().stage,1)
        self.assertEqual(sound.clips,['wa.wav','warning.wav','da.wav','danger.wav',
                                      'da.wav','decibel.wav','wa.wav','warning.wav'])
        self.assertEqual(len(quiz),1);self.assertEqual(len(loud),1)
        self.assertEqual(sleeps,[4,4,4,4,4,4])
    def test_busy_reset_on_error(self):
        def fail():raise RuntimeError('STT timeout')
        ctrl=WarningStages(FakeAudio(),Config(),fail,lambda:False,sleep_fn=lambda _:None)
        ctrl.on_alert()
        self.assertEqual(ctrl.on_alert().outcome,'error')
        self.assertFalse(ctrl.busy)
        self.assertEqual(ctrl.on_alert().stage,3)
    def test_busy_reentrance(self):
        ctrl=WarningStages(FakeAudio(),Config(),lambda:None,lambda:False)
        ctrl.busy=True
        self.assertEqual(ctrl.on_alert().outcome,'busy')
        self.assertEqual(ctrl.warning_count,0)
    def test_answer_not_loudness(self):
        self.assertEqual(normalize_answer(' 54. '),54)
        self.assertIsNone(normalize_answer('크게 말함'))

if __name__=='__main__':unittest.main()
