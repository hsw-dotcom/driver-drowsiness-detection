# Driver Drowsiness Detection — 2023 Project Archive

> **Historical source archive.** 2023 Raspberry Pi camera-based eye-closure detection prototypes and separate voice-interaction experiments. **Not a ready-to-run safety device**, and there is no evidence in the uploaded files that the two modules were integrated in a single fully tested application. The original Raspberry Pi is no longer available, so current execution has not been verified.

## 개요

졸음운전을 감지하기 위한 카메라 프로토타입의 과거 개발 기록입니다. 라즈베리파이 카메라 프레임에서 dlib의 얼굴·68점 랜드마크 모델을 사용해 눈 위치 및 EAR(Eye Aspect Ratio)를 계산합니다. 별도 Windows 기반 음성 기능 실험에서는 수학 문제를 음성으로 읽고 Google Cloud Speech-to-Text로 음성 답변을 인식하는 코드를 작성했습니다.

## 코드 구성

- `src/eye_detection/test.py`: Picamera2, dlib, OpenCV, 평균 EAR 기준 및 연속 눈 감김 계산의 초기 버전
- `src/eye_detection/test_v2.py`: 초기 30초 평균 측정, EAR·눈 위치 임계값, `detected` 표시
- `src/eye_detection/test3.py`: Picamera2 캡처 화면 출력 및 카메라 로그 메모
- `src/voice_experiments/test1.py`: TTS 수학 문제 생성, 스트리밍 STT, 정답 판단과 안내 WAV 재생 시도
- `src/voice_experiments/111.py`, `222.py`, `333.py`, `app.py`, `test2.py`, `stt_test1.py`: 녹음/TTS/STT 단위 시험 코드. `stt_test1.py`는 Google의 예제 기반입니다.

## 기술 스택

Python, Raspberry Pi OS, Raspberry Pi Camera Module, Picamera2, OpenCV, dlib, SciPy, NumPy; Google Cloud Text-to-Speech/Speech-to-Text, PyAudio, gTTS, playsound(음성 모듈).

## 동작 상태·제약

- EAR은 눈 랜드마크의 수직 거리와 수평 거리의 비율로 계산합니다. `test_v2.py`에서는 30초간 평균을 구한 뒤 `EAR <= avg_EAR * 0.8`가 10프레임 이상 이어지거나 눈 위치 조건이 발생하면 `detected` 문구를 표시하도록 작성되어 있습니다.
- **현재 공개된 카메라 코드에는 WAV 경고음, SMS 전송 또는 음성 문제 모듈을 직접 호출하는 통합 코드가 없습니다.** 관련 기능이 전체 장치에서 정상 연동되었다고 주장하지 않습니다.
- 초기 카메라 코드에 `cap.release()` 관련 오류 가능성이 있습니다(`cap` 미정의). 과거 코드를 임의 수정하지 않고 보존했습니다.
- 음성 인식의 오인식, 루프 종료 조건, 자격증명 설정 등은 수정되지 않은 역사적 시험 상태입니다.
- 필요한 `shape_predictor_68_face_landmarks.dat`(약 99.7MB)는 권리·용량을 고려해 포함하지 않았습니다. 당시 백업에서 존재를 확인했습니다.
- Google Cloud 서비스 계정 JSON/개인 녹음·음성 및 시연 영상은 공개하지 않았습니다.

[구현 검증 및 한계](docs/implementation-notes.md) · [보안/출처](docs/security.md)
