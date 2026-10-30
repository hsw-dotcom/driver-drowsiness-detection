# 대화 근거 기반 졸음운전 방지 카메라 통합 재구성 (2026)

**중요:** 2023년 최종 시연 코드의 원문이 아닙니다. 사용자가 당시 ChatGPT와 나눈 질문·수정·오류 해결 기록 및 확보된 원본 `test_v2.py`, `111.py`, `222.py`, `333.py`를 토대로 기능을 **재구성한 참고·학습용 구현**입니다. 차량 안전장치로 인증된 소프트웨어가 아닙니다.

## 빠른 실행

```bash
cd 04_reconstructed_application
python3 -m unittest discover -s tests -v
python3 main.py --demo
# 모델·WAV·Raspberry Pi 전용 라이브러리 확보 후:
python3 main.py --no-display
# 모니터 연결 시:
python3 main.py
```

## 2023년 11월 22일 대화의 설정(이 통합본의 기본값)

- Raspberry Pi Picamera2 640×480, 요청 60fps, 색상 프레임 XBGR8888; dlib 68점과 EAR 측정
- 초기 평균 측정 **3초** (이전 `test_v2.py` 원본 **30초**와 다름), 평균 EAR×0.8 이하 상태 연속 10프레임 또는 눈 y위치 평균+20픽셀 초과
- 재검출 1초 무시 및 중복 경고 방지. 단, 경고 단계를 마친 뒤 정상 상태 재관측 시에만 다음 트리거 허용(추가 안정화)
- 첫 감지 `wa.wav → warning.wav`, 둘째 `da.wav → danger.wav → 수학문제/Google STT`, 셋째 `da.wav → decibel.wav → PyAudio 음량 반응` → 1회로 순환
- 단계별 오디오 사이 4초 및 반응 전 4초는 대화 후기의 설정을 반영. 시스템이 경고·반응 처리 중에는 **프레임 인식을 추가 실행하지 않음**
- 음량 검사 44,100Hz, 1,024샘플 청크, 5초, `20*log10(원시 PCM RMS / 1)` 평균값이 **70 초과**하면 성공. **실제 SPL dB 수치가 아니므로 음향계 측정으로 오인하지 마세요.**
- 정답 STT와 큰소리 RMS는 서로 다른 판정이며, 하나가 다른 하나를 대체하지 않습니다.

## 보완·추정 사항

- 미확보 원본 `test2.py`/`decibel.py`는 `scripts/`에 **새로 만든 동일 역할 어댑터**를 두었습니다. 원본이라고 표시하지 않습니다.
- dlib 모델/실제 WAV/Cloud 인증은 포함하지 않았습니다. `assets/README.md`를 확인하세요.
- STT 입력시간 5초, 음량 3회 시도 제한, 초기 유효 프레임 최소 3개, 얼굴 유실 시 카운트 리셋, 쿨다운 후 정상 관측해야 재무장, 최대면적 얼굴 선정, 예외 처리 및 `aplay`은 **합리적 추정/안정화 보완**이지 확인된 옛 코드가 아닙니다.
- 2023년 `test_v2.py`의 `cap.release()` 오류는 원본을 변경하지 않았고, 새 통합본에서는 `Picamera2.stop()/close()`로 종료합니다.
- 과거 YUV420을 `cv2.COLOR_BGR2GRAY`로 변환하던 문제를 방지하도록 프레임 형식별 변환을 분리했습니다. RGB/BGR 실제 배열은 현장 카메라에서 검증이 필요합니다.
- `subprocess.run()`과 Google STT 스트리밍 무음 타임아웃으로 인식과 영상이 멈췄던 문제는 새 코드에서 유한 시간의 Google `recognize()` 호출과 단발 단계 처리로 완화했습니다. 네트워크/API 타임아웃 자체는 환경에 따라 여전히 발생할 수 있습니다.

## 실제 하드웨어 준비

Raspberry Pi OS에서 Picamera2, dlib, OpenCV 및 마이크 장치 드라이버를 준비하세요. 가급적 OS 패키지 (`sudo apt install python3-picamera2 python3-opencv python3-dlib python3-pyaudio alsa-utils`)를 사용하고, 필요한 Python 모듈(Cloud TTS/STT, sounddevice 등)을 프로젝트 환경에 맞게 설치합니다. Google Cloud 인증은 로컬 환경변수 `GOOGLE_APPLICATION_CREDENTIALS`로 설정하며 공개 저장소에 업로드하지 않습니다. 헤드리스 자동실행 예시는 `systemd/driver-drowsiness.service.example`에 있으며, 2023년 당시 service 파일의 원본은 아닙니다.

## 구조

```text
04_reconstructed_application/
  main.py                   # 카메라와 경고 통합 루프
  config.ini                # 과거 최종 문답 기반 기본값
  drowsiness/vision.py      # EAR/눈높이/초기 평균/래치
  drowsiness/camera.py      # Picamera2 형식별 프레임
  drowsiness/stages.py      # 1·2·3회차 경고
  drowsiness/audio.py       # 오디오 파일 재생
  drowsiness/quiz.py        # TTS/STT 수학 문제
  drowsiness/loudness.py    # 5초 RMS/임계값 70
  scripts/test2.py          # *추정 재구성* 퀴즈 어댑터
  scripts/decibel.py        # *추정 재구성* 음량 어댑터
  assets/                   # 모델/WAV 자리, 원본 미확보
  systemd/                  # 부팅 자동실행 예시
  tests/                    # 하드웨어 비의존 로직 테스트
```

루트 `00_verified_originals`의 원본 파일은 수정하지 않았습니다. 구버전 `01_reference_refactor`는 유지하고, `04_reconstructed_application`가 새 통합본입니다.
