# Raspberry Pi 실행 및 검증 가이드

## 환경 및 원본 구분
- 알려진 개발 환경: Raspberry Pi, Picamera2, Python, OpenCV, dlib, 68-point facial landmark 모델.
- `00_verified_originals` 는 원문 보존용입니다. **그대로 실행된다는 보장 없음**.
- `01_reference_refactor` 는 2026년에 분리 작성한 참고 예제이며, 2023년 실행 파일이 아닙니다.
- 컴퓨터 모의 경고만 제공하는 예제로, 실제 운전 중 안전을 이 시스템에 의존하지 마세요.

## 준비(라즈베리파이 OS)
라즈베리파이 OS Bookworm 계열의 경우 시스템 패키지로 Picamera2·dlib·OpenCV를 설치할 수 있습니다. 기기 및 OS 버전에 따라 명령/패키지가 다릅니다.

```bash
sudo apt update
sudo apt install python3-picamera2 python3-opencv python3-dlib python3-numpy
```

카메라 배선/권한을 확인하고, 합법적인 출처에서 `shape_predictor_68_face_landmarks.dat`를 구해 `02_missing_assets/model/`에 배치하세요. (이 ZIP에는 모델이 들어 있지 않습니다.)

## 원본 코드를 살펴보기
```bash
python3 -m py_compile 00_verified_originals/vision_detection/test_v2.py
```
컴파일 통과는 카메라·GPU·음성장치 작동 검증이 아닙니다.

## 참고 예제 실행
```bash
cd 01_reference_refactor
python3 -m unittest discover -s tests -v
python3 camera_demo.py --predictor ../02_missing_assets/model/shape_predictor_68_face_landmarks.dat
```

카메라 화면 없이 디버깅할 때:
```bash
python3 camera_demo.py --predictor ../02_missing_assets/model/shape_predictor_68_face_landmarks.dat --no-display
```

카메라에서 이미지가 비정상적으로 보이거나 변환 예외가 발생하면 RGB888/BGR 출력을 실제 이미지로 검사한 뒤 `--color-order BGR` 등을 변경해야 합니다. 예제 기본값은 실장 검증을 거치지 않았습니다.

## 기존 원본에서 주의할 부분
- `test_v2.py` 종료부의 `cap.release()`는 정의된 변수가 아니므로 실행 시 `NameError`가 발생할 수 있습니다. 원본 보존 때문에 수정하지 않았습니다.
- 30초 초기 측정은 얼굴이 충분히 검출되지 않은 경우 부정확할 수 있습니다.
- 각 클라우드 STT/TTS 코드는 별도 서비스 계정 인증과 마이크 입력, 네트워크가 필요하며 비용이 발생할 수 있습니다. 클라우드 코드는 테스트 목적일 때만 직접 실행하세요.
- 2023년 대화에 등장한 `warning.wav`/`danger.wav`의 재생, 3회 경고 후 문제 출제, 1초 감지 무시 등 통합 흐름은 현재 확보된 원본 4개만으로 검증할 수 없습니다.

## 검증 수준
- 원본 4개는 SHA-256 기록 후 원문 그대로 압축했습니다.
- Python 구문검사, 재구성 판단로직 단위 테스트, ZIP CRC 검사를 수행했습니다.
- Raspberry Pi 카메라, 사운드 디바이스, dlib 모델과 실차 조건은 별도 검증이 필요합니다.
