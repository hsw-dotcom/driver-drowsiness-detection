import pyaudio
import wave
import time

# 음성 녹음을 위한 설정
FORMAT = pyaudio.paInt16 # 16비트 PCM 포맷
CHANNELS = 1 # 모노 사운드
RATE = 44100 # 초당 샘플 수
CHUNK = 1024 # 데이터를 한 번에 몇 바이트씩 읽을 것인지
RECORD_SECONDS = 3 # 녹음할 시간 (초)

# 녹음할 파일 이름
output_filename = "user_response.wav"

# PyAudio 객체 생성
audio = pyaudio.PyAudio()

# 음성 녹음을 위한 스트림 열기
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("말하세요...")

frames = [] # 녹음한 데이터를 저장할 리스트

# 3초간 녹음
start_time = time.time()
while time.time() - start_time < RECORD_SECONDS:
    # CHUNK만큼의 데이터를 읽어 frames에 추가
    data = stream.read(CHUNK)
    frames.append(data)

print("녹음이 완료되었습니다.")

# 스트림과 PyAudio 객체 닫기
stream.stop_stream()
stream.close()
audio.terminate()

# 녹음 데이터를 파일로 저장
with wave.open(output_filename, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))

print(f"음성 녹음이 완료되었습니다. 파일은 {output_filename}에 저장되었습니다.")
