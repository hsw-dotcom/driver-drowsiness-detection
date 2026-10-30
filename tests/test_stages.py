import unittest
from drowsiness.stages import WarningStages
from drowsiness.quiz import QuizResult, normalize_answer, solve_question
from drowsiness.config import Config


class FakeAudio:
    def __init__(self):
        self.clips = []

    def play(self, name):
        self.clips.append(name)


class StageTests(unittest.TestCase):
    def test_cycle_and_exact_file_sequence(self):
        sound = FakeAudio()
        sleeps = []
        quiz = []
        loud = []

        def check_quiz():
            quiz.append(True)
            return QuizResult('q', 3, '3', True)

        def check_volume():
            loud.append(True)
            return True

        ctrl = WarningStages(sound, Config(), check_quiz, check_volume,
                             sleep_fn=sleeps.append)
        self.assertEqual(ctrl.on_alert().outcome, 'warning-audio')
        self.assertEqual(ctrl.on_alert().outcome, 'quiz-correct')
        self.assertEqual(ctrl.on_alert().outcome, 'volume-response')
        self.assertEqual(ctrl.warning_count, 3)
        self.assertEqual(ctrl.on_alert().stage, 1)
        self.assertEqual(sound.clips, ['detect.wav', 'wa.wav', 'warning.wav',
                                      'detect.wav', 'da.wav', 'danger.wav',
                                      'detect.wav', 'da.wav', 'decibel.wav',
                                      'detect.wav', 'wa.wav', 'warning.wav'])
        self.assertEqual(len(quiz), 1)
        self.assertEqual(len(loud), 1)
        self.assertEqual(sleeps, [4, 4, 4, 4, 4, 4])

    def test_unlimited_quiz_retries_same_stage(self):
        tries = []

        def quiz():
            tries.append('try')
            correct = len(tries) >= 9  # more than any invented max=3
            return QuizResult('same question', 10, '10' if correct else '9', correct)

        ctrl = WarningStages(FakeAudio(), Config(), quiz, lambda: True,
                             sleep_fn=lambda _: None)
        ctrl.on_alert()
        result = ctrl.on_alert()
        self.assertEqual(result.outcome, 'quiz-correct')
        self.assertEqual(len(tries), 9)
        self.assertEqual(ctrl.warning_count, 2)

    def test_quiz_same_question_kept_until_solved(self):
        prompts = []
        answers = iter(['12', '', '13', 'not a number', '15'])
        result = solve_question('same math problem', 15,
                                lambda q: (prompts.append(q), next(answers))[1])
        self.assertTrue(result.correct)
        self.assertEqual(prompts, ['same math problem'] * 5)

    def test_unlimited_loudness_retries_same_stage(self):
        count = []
        def read_volume():
            count.append(True)
            return len(count) >= 8

        ctrl = WarningStages(FakeAudio(), Config(),
                             lambda: QuizResult('q', 3, '3', True),
                             read_volume, sleep_fn=lambda _: None)
        ctrl.on_alert()
        ctrl.on_alert()
        result = ctrl.on_alert()
        self.assertEqual(result.stage, 3)
        self.assertEqual(result.outcome, 'volume-response')
        self.assertEqual(len(count), 8)
        self.assertEqual(ctrl.on_alert().stage, 1)

    def test_stage_remains_pending_when_cloud_error(self):
        def fail():
            raise RuntimeError('Cloud unavailable')

        ctrl = WarningStages(FakeAudio(), Config(), fail, lambda: True,
                             sleep_fn=lambda _: None)
        ctrl.on_alert()
        self.assertEqual(ctrl.on_alert().outcome, 'error')
        self.assertFalse(ctrl.busy)
        self.assertEqual(ctrl.warning_count, 1)
        self.assertEqual(ctrl.on_alert().stage, 2)

    def test_common_detect_alarm_precedes_each_stage(self):
        sound=FakeAudio()
        ctrl=WarningStages(sound,Config(),
                           lambda:QuizResult('q',2,'2',True),lambda:True,
                           sleep_fn=lambda _:None)
        for stage in (1,2,3,1):
            old_len=len(sound.clips)
            self.assertEqual(ctrl.on_alert().stage,stage)
            self.assertEqual(sound.clips[old_len],'detect.wav')

    def test_quiz_voice_prompt_repeated_after_wrong_answer(self):
        seen=[]
        answers=iter(['4','', '5'])
        def recognize(question):
            seen.append(question)
            return next(answers)
        self.assertTrue(solve_question('2 + 3',5,recognize).correct)
        self.assertEqual(seen,['2 + 3']*3)

    def test_busy_reentrance(self):
        ctrl = WarningStages(FakeAudio(), Config(), lambda: None, lambda: False)
        ctrl.busy = True
        self.assertEqual(ctrl.on_alert().outcome, 'busy')
        self.assertEqual(ctrl.warning_count, 0)

    def test_answer_not_loudness(self):
        self.assertEqual(normalize_answer(' 54. '), 54)
        self.assertIsNone(normalize_answer('크게 말함'))


if __name__ == '__main__':
    unittest.main()
