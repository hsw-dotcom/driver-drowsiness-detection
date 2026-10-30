"""Original test1.py / 222.py-based Korean math quiz reconstruction.

A problem is generated ONCE. Its voice prompt and approximately 10 seconds of
speech input repeat without an attempt limit until the correct answer arrives.
Google Cloud is the historical TTS/STT provider. Network-call timeout is NOT
speech recognition duration; an invented 10-second RPC timeout is not used.
"""
from dataclasses import dataclass
from pathlib import Path
import random
import tempfile


@dataclass(frozen=True)
class QuizResult:
    question: str
    answer: int
    transcript: str
    correct: bool
    error: str = ''


def generate_question(rng=None):
    rng = rng or random
    if rng.choice([0, 1]) == 0:
        a, b = rng.randint(10, 99), rng.randint(10, 99)
        return f'두 자릿수 덧셈 문제: {a} 더하기 {b} 은 무엇입니까?', a + b
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    return f'한 자릿수 곱셈 문제: {a} 곱하기 {b} 은 무엇입니까?', a * b


def normalize_answer(s):
    # 2023's prototype accepted numeric speech text; no speculative NLP.
    s = str(s).strip().replace(' ', '').replace(',', '').replace('.', '')
    try:
        return int(s)
    except ValueError:
        return None


def solve_question(question, answer, recognize_once, on_response=None):
    """Repeat the SAME problem; injectable recognizer enables hardware-free tests.

    recognize_once(question) should play/speak the question and obtain ONE reply.
    Exceptions (e.g. unavailable Google Cloud) propagate and are not conflated
    with wrong answers; ordinary incorrect/unrecognized speech repeats forever.
    """
    while True:
        transcript = str(recognize_once(question) or '')
        correct = normalize_answer(transcript) == answer
        if on_response is not None:
            on_response(transcript, correct)
        if correct:
            return QuizResult(question, answer, transcript, True)


def run_quiz(record_seconds=10.0, backend='google', dry_run=False):
    question, answer = generate_question()
    if dry_run or backend == 'disabled':
        print(f'[quiz simulation] {question} (simulated answer {answer})')
        return QuizResult(question, answer, str(answer), True, 'simulation-only')
    if backend != 'google':
        raise ValueError('Unknown quiz backend')

    # 2023 prototypes used Google Cloud TTS and Google STT, with recorded input
    # or experimental streaming STT. A 10-second finite recording implements
    # the user-confirmed response window; streaming-vs-batch final code is lost.
    import numpy as np
    import sounddevice as sd
    from google.cloud import texttospeech, speech
    from scipy.io import wavfile
    from .audio import Audio

    tts = texttospeech.TextToSpeechClient()
    response = tts.synthesize_speech(
        input=texttospeech.SynthesisInput(text=question),
        voice=texttospeech.VoiceSelectionParams(
            language_code='ko-KR', name='ko-KR-Wavenet-D'),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16))
    stt = speech.SpeechClient()

    with tempfile.TemporaryDirectory(prefix='drowsiness_quiz_') as directory:
        folder = Path(directory)
        (folder / 'question.wav').write_bytes(response.audio_content)
        audio = Audio(folder, backend='playsound')

        def recognize_once(_question):
            audio.play('question.wav')
            print(f'[quiz] recording {record_seconds:g} seconds of speech')
            rate = 44100  # 222.py prototype rate
            samples_float = sd.rec(
                int(rate * record_seconds), samplerate=rate,
                channels=1, dtype='float32')
            sd.wait()
            samples = (np.clip(samples_float, -1, 1) * 32767).astype(np.int16)
            response_file = folder / 'user_response.wav'
            wavfile.write(str(response_file), rate, samples)
            recognized = stt.recognize(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=rate, language_code='ko-KR'),
                audio=speech.RecognitionAudio(content=response_file.read_bytes()))
            return (recognized.results[0].alternatives[0].transcript
                    if recognized.results else '')

        def on_response(transcript, correct):
            # The original quiz replays the question after wrong/non-numeric
            # responses. Original result1/2/3 WAVs are not in the repository.
            print('[quiz]', repr(transcript), 'correct' if correct else 'repeat')

        return solve_question(question, answer, recognize_once, on_response)
