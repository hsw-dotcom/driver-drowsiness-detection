import math
import unittest
from reconstruction.gaps.decibel_formula import program_relative_db
from reconstruction.gaps.stage_flow import StageFlow


class GapTests(unittest.TestCase):
    def make_stage_flow(self, responses=(True,), volumes=(100,)):
        clips, questions, answer_checks, volume_checks = [], [], [], []
        answers, values = iter(responses), iter(volumes)

        def create_question():
            q = {'text': '2+3?', 'answer': 5}
            questions.append(q)
            return q

        def answer(q, seconds):
            answer_checks.append((q, seconds))
            return next(answers)

        def volume():
            v = next(values)
            volume_checks.append(v)
            return v

        return StageFlow(clips.append, create_question, answer, volume), (clips, questions, answer_checks, volume_checks)

    def test_1_2_3_1(self):
        flow, history = self.make_stage_flow()
        self.assertEqual([flow.trigger().stage for _ in range(4)], [1, 2, 3, 1])
        self.assertEqual(flow.stage, 2)
        self.assertEqual(history[0], ['wa.wav','warning.wav','da.wav','danger.wav','da.wav','decibel.wav','wa.wav','warning.wav'])

    def test_same_question_retries_unbounded_by_code(self):
        flow, history = self.make_stage_flow(responses=[False]*7+[True])
        flow.trigger()
        result=flow.trigger()
        self.assertEqual(result.result, 'question-solved')
        self.assertEqual(len(history[1]), 1)
        self.assertEqual(len(history[2]), 8)
        self.assertTrue(all(pair[0] is history[1][0] for pair in history[2]))
        self.assertTrue(all(pair[1] == 10 for pair in history[2]))

    def test_volume_retries_past_three_attempts(self):
        flow, history = self.make_stage_flow(volumes=[12,33,67,70,70.01])
        flow.trigger(); flow.trigger()
        self.assertEqual(flow.trigger().result, 'volume-confirmed')
        self.assertEqual(history[3], [12,33,67,70,70.01])
        self.assertEqual(flow.stage, 1)

    def test_silence_returns_negative_infinity(self):
        self.assertEqual(program_relative_db([0,0,0]), -math.inf)

    def test_zero_samples_returns_none(self):
        self.assertIsNone(program_relative_db([]))

    def test_pcm_threshold(self):
        self.assertLess(program_relative_db([3000,-3000]), 70)
        self.assertGreater(program_relative_db([4000,-4000]), 70)

    def test_stage_one_does_not_ask_question(self):
        flow, history=self.make_stage_flow()
        flow.trigger()
        self.assertFalse(history[1] or history[2] or history[3])


if __name__=='__main__':
    unittest.main()
