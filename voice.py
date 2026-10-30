"""당시 구글 TTS/STT 실험을 바탕으로 만든 수학 문제·음성 응답."""
import random
import tempfile
from pathlib import Path

from config import QUIZ_SECONDS


def make_question():
    if random.choice((0, 1)) == 0:
        a, b = random.randint(10, 99), random.randint(10, 99)
        return f'{a} 더하기 {b} 은 무엇입니까?', a + b
    a, b = random.randint(1, 9), random.randint(1, 9)
    return f'{a} 곱하기 {b} 은 무엇입니까?', a * b


def answer_as_number(transcript):
    try:
        return int(str(transcript).strip().replace(' ', '').replace(',', '').replace('.', ''))
    except ValueError:
        return None


def ask_until_correct(play_audio, *, recognize=None, question=None):
    """동일 문제와 음성 안내를 정답이 나올 때까지 반복한다.

    recognize 함수는 코드 검증용 대체 입력이다. 실제 동작은 10초 녹음 후 STT.
    """
    text, answer = question or make_question()
    if recognize is None:
        recognize = _make_google_recognizer(text)
    try:
        while True:
            transcript = recognize() or ''
            value = answer_as_number(transcript)
            if value == answer:
                play_audio('result1.wav')
                return
            play_audio('result3.wav' if value is None else 'result2.wav')
    finally:
        close = getattr(recognize, 'close', None)
        if close is not None:
            close()


def _make_google_recognizer(question):
    """2023년 11월 녹음→Google STT 방식. 마이크 장치는 실행 시에만 사용."""
    import numpy as np
    import sounddevice as sd
    from scipy.io import wavfile
    from google.cloud import texttospeech, speech
    from playsound import playsound

    tts = texttospeech.TextToSpeechClient()
    result = tts.synthesize_speech(
        input=texttospeech.SynthesisInput(text=question),
        voice=texttospeech.VoiceSelectionParams(language_code='ko-KR', name='ko-KR-Wavenet-D'),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16),
    )
    stt = speech.SpeechClient()
    folder = tempfile.TemporaryDirectory(prefix='drowsiness_')
    prompt = Path(folder.name) / 'question.wav'
    prompt.write_bytes(result.audio_content)

    class Recognizer:
        def __call__(self):
            playsound(str(prompt))
            sample_rate = 44100
            samples = sd.rec(int(sample_rate * QUIZ_SECONDS), samplerate=sample_rate,
                             channels=1, dtype='float32')
            sd.wait()
            pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
            output = Path(folder.name) / 'answer.wav'
            wavfile.write(str(output), sample_rate, pcm)
            response = stt.recognize(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=sample_rate, language_code='ko-KR'),
                audio=speech.RecognitionAudio(content=output.read_bytes()),
            )
            return response.results[0].alternatives[0].transcript if response.results else ''

        def close(self):
            folder.cleanup()

    return Recognizer()
