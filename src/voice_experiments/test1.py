from __future__ import division
import random
import os
import time
import re
import sys
from google.cloud import texttospeech
from google.cloud import speech_v1 as speech
import pyaudio
from playsound import playsound
from six.moves import queue


# Google Cloud Text-to-Speech 클라이언트 생성
client = texttospeech.TextToSpeechClient()
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True

        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):

        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:

            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0

def recognize_speech():
    client = speech.SpeechClient()
    language_code = 'ko-KR'  # a BCP-47 language tag

    RATE = 16000
    CHUNK = int(RATE / 200)  # 200ms

    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code
        ),
        interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        recognized_text = ""
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            recognized_text += transcript

            if result.is_final:
                break

        recognized_text = recognized_text[-len(str(answer)):].strip()
        numeric_text = ''.join(filter(str.isdigit, recognized_text))
        return recognized_text

def get_user_answer():
    while True:
        user_answer = recognize_speech()
        print(user_answer)
        if user_answer.isdigit():
            return int(user_answer)
        else:
            playsound("result3.wav")
            playsound("question.wav")

def main():
    global streaming_config
    language_code = 'ko-KR'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        listen_print_loop(responses)

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
print(answer)
while True:
    # 음성 파일을 재생
    playsound("question.wav")

    # 사용자 입력 받기
    user_answer = get_user_answer()

    # 정답과 사용자 입력 비교
    if int(user_answer) == answer:
        # 음성 파일을 재생
        playsound("result1.wav")
        # 정답을 맞추면 루프 탈출
        sys.exit()
    else:
        # 음성 파일을 재생
        playsound("result2.wav")

if __name__ == '__main__':
    main()  # main 함수 호출
    recognized_text = recognize_speech()