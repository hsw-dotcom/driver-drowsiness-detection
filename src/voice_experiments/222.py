import random
from google.cloud import texttospeech
from playsound import playsound
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
import sounddevice as sd
import scipy.io.wavfile as wav
from google.cloud import speech
import io
import numpy as np

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient()

    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,  # 44.1 kHz 샘플링 레이트로 설정
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)

    # API로부터 받은 텍스트 결과를 반환
    if len(response.results) > 0:
        return response.results[0].alternatives[0].transcript
    else:
        return ""  # 인식된 음성이 없을 경우 빈 문자열 반환

# Google Cloud Text-to-Speech 클라이언트 생성
client = texttospeech.TextToSpeechClient()

# 녹음할 시간 (초)
duration = 1

# 샘플 속도
sample_rate = 44100



# 문제 유형을 랜덤하게 선택 (0: 덧셈, 1: 한자릿수 곱셈)
problem_type = random.choice([0, 1])

if problem_type == 0:
    # 두 자릿수 덧셈 문제 생성
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    question = f"두 자릿수 덧셈 문제: {num1}    더하기    {num2}     은 무엇입니까?"
    answer = num1 + num2
else:
    # 한 자릿수 곱셈 문제 생성
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    question = f"한 자릿수 곱셈 문제: {num1}    곱하기    {num2}     은 무엇입니까?"
    answer = num1 * num2

# TTS로 문제 음성 생성
synthesis_input = texttospeech.SynthesisInput(text=question)
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR", name="ko-KR-Wavenet-D", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# 음성 파일을 저장 (question.wav로 저장)
with open("question.wav", "wb") as out:
    out.write(response.audio_content)

while True:
    # 음성 파일을 재생
    playsound("question.wav")

# 오디오 녹음
    print("1초간 음성을 녹음합니다...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()

# WAV 파일로 저장
    wav.write("user_response.wav", sample_rate, audio_data)
    print("녹음이 완료되었습니다.")
# 스테레오 WAV 파일을 읽고 모노로 변환
    sample_rate, stereo_audio_data = wav.read("user_response.wav")
    mono_audio_data = stereo_audio_data.mean(axis=1)  # 스테레오를 모노로 변환

# 모노 오디오를 새로운 WAV 파일로 저장
    wav.write("user_response_mono.wav", sample_rate, mono_audio_data.astype(np.int16))

# 음성을 텍스트로 변환
    user_answer = transcribe_audio("user_response_mono.wav")

    # 정답과 사용자 입력 비교
    if user_answer:
        try:
            user_answer = int(user_answer)
            if user_answer == answer:
                print("정답입니다!")
            else:
                print("틀렸습니다.")
        except ValueError:
            print("올바른 숫자를 말해주세요.")
    else:
        print("음성이 인식되지 않았습니다.")