"""Regression tests for 2023 conversation-backed logic (no hardware/API)."""
import math
import unittest
from array import array
from drowsiness.loudness import measure_average_db, raw_pcm_db, wait_for_loud_reaction
from drowsiness.quiz import feedback_clip, solve_question


class AlternatingStream:
    def __init__(self, levels):
        self.levels = iter(levels)
        self.closed = False

    def read(self, chunk, exception_on_overflow=False):
        return array('h', [next(self.levels)] * chunk).tobytes()

    def close(self):
        self.closed = True


class FakeAudio:
    def __init__(self):
        self.clips = []

    def play(self, name):
        self.clips.append(name)


class ConversationBackedTests(unittest.TestCase):
    def test_whole_recording_rms_not_average_of_log_chunks(self):
        # Two equally-sized chunks: one silent, one with PCM amplitude 6000.
        # Whole-recording RMS is 6000/sqrt(2), not the mean of dB(0) and dB(6000).
        stream = AlternatingStream([0, 6000])
        result = measure_average_db(seconds=2, rate=2, chunk=2,
                                    stream_factory=lambda: stream)
        self.assertAlmostEqual(result, raw_pcm_db(6000 / math.sqrt(2)))
        self.assertTrue(stream.closed)

    def test_success_wav_after_threshold(self):
        audio = FakeAudio()
        observations = iter([49.0, 71.0])
        self.assertTrue(wait_for_loud_reaction(
            audio, measure_fn=lambda seconds, rate, chunk: next(observations)))
        self.assertEqual(audio.clips, ['da.wav', 'decibel.wav', 'success.wav'])

    def test_feedback_wav_paths_match_original_quiz(self):
        self.assertEqual(feedback_clip('15', True), 'result1.wav')
        self.assertEqual(feedback_clip('12', False), 'result2.wav')
        self.assertEqual(feedback_clip('', False), 'result3.wav')
        self.assertEqual(feedback_clip('안 들려요', False), 'result3.wav')

    def test_unchanged_question_retry_with_feedback(self):
        answers = iter(['', '12', '15'])
        clips = []
        def on_response(transcript, correct):
            clips.append(feedback_clip(transcript, correct))
        result = solve_question('10+5?', 15, lambda _: next(answers), on_response)
        self.assertTrue(result.correct)
        self.assertEqual(clips, ['result3.wav', 'result2.wav', 'result1.wav'])


if __name__ == '__main__':
    unittest.main()
