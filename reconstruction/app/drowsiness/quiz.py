"""Rebuilt 222.py-style math question, Korean Google TTS/STT, separate from loudness.

This is new integration code; STT success rates in a vehicle are not verified.
"""
from dataclasses import dataclass
from pathlib import Path
import random
import tempfile

@dataclass(frozen=True)
class QuizResult:
    question:str
    answer:int
    transcript:str
    correct:bool
    error:str=''

def generate_question(rng=None):
    rng=rng or random
    if rng.choice([0,1])==0:
        a,b=rng.randint(10,99),rng.randint(10,99)
        return f'두 자릿수 덧셈 문제: {a} 더하기 {b} 은 무엇입니까?',a+b
    a,b=rng.randint(1,9),rng.randint(1,9)
    return f'한 자릿수 곱셈 문제: {a} 곱하기 {b} 은 무엇입니까?',a*b

def normalize_answer(s):
    s=str(s).strip().replace(' ','').replace(',','').replace('.','')
    try: return int(s)
    except ValueError: return None

def run_quiz(record_seconds=5.0,backend='google',dry_run=False):
    question,answer=generate_question()
    if dry_run or backend=='disabled':
        print('[quiz simulation] '+question+' (expected: '+str(answer)+')')
        return QuizResult(question,answer,'',False,'simulation')
    try:
        import numpy as np
        import sounddevice as sd
        from google.cloud import texttospeech,speech
        from scipy.io import wavfile
        tts=texttospeech.TextToSpeechClient()
        response=tts.synthesize_speech(
            input=texttospeech.SynthesisInput(text=question),
            voice=texttospeech.VoiceSelectionParams(language_code='ko-KR',name='ko-KR-Wavenet-D'),
            audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16),
            timeout=10.0)
        # Use a temporary path; never store Google credentials or raw responses in ZIP.
        with tempfile.TemporaryDirectory(prefix='drowsiness_quiz_') as directory:
            prompt=Path(directory)/'question.wav'
            prompt.write_bytes(response.audio_content)
            from .audio import Audio
            Audio(Path(directory)).play('question.wav')
            rate=44100  # match 222.py capture experiment
            print(f'[quiz] Listening for {record_seconds:.1f}s')
            recording=sd.rec(int(rate*record_seconds),samplerate=rate,channels=1,dtype='float32')
            sd.wait()
            samples=(np.clip(recording,-1,1)*32767).astype(np.int16)
            answer_file=Path(directory)/'response.wav'
            wavfile.write(str(answer_file),rate,samples)
            stt=speech.SpeechClient()
            recognized=stt.recognize(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=rate,language_code='ko-KR'),
                audio=speech.RecognitionAudio(content=answer_file.read_bytes()),
                timeout=10.0)
            transcript=(recognized.results[0].alternatives[0].transcript if recognized.results else '')
            return QuizResult(question,answer,transcript,normalize_answer(transcript)==answer)
    except Exception as exc:
        # Google credentials, mic or API can fail; never loop forever blocking vision.
        print(f'[quiz unavailable] {type(exc).__name__}: {exc}')
        return QuizResult(question,answer,'',False,type(exc).__name__)
