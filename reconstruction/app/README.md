# 졸음운전 방지 카메라 — 통합 코드 복원본 (2026)

2023년 질문·답변과 현재 확보한 원본 자료에 근거해 작성한 **단일 통합 구현**입니다. **2023년 최종 시연 원문이 아니며**, 실제 하드웨어 실행을 목표로 하지 않습니다. 코드의 구조와 판단 흐름을 재현하는 것이 목적입니다.

## 가장 먼저 볼 파일

- `main.py`: 단계별 호출 순서와 데모 모드. **통합 진입점은 하나입니다.**
- `drowsiness/vision.py`: 초기 기준값, EAR, 눈 위치 변화, 연속 감김 및 재감지 제한
- `drowsiness/stages.py`: 1·2·3단계 경고 진행, 퀴즈·음량 판정 연결
- `drowsiness/quiz.py`: 수학 문제 생성, 선택적 TTS/STT 정답 판정
- `drowsiness/loudness.py`: RMS 기반 상대 음량 점수 및 반응 확인
- `drowsiness/audio.py`: WAV 재생만 전담 (경고 순서 중복 구현 제거)
- `drowsiness/camera.py`: Picamera2 입력과 색상 변환
- `drowsiness/config.py`, `config.ini`: 확정 설정과 추정 설정의 기본값
- `tests/`: 하드웨어·클라우드 없이 로직 검증

2023년 원본은 **`../../src/`** 에만 보관합니다. `src/`의 여러 `test*.py`, `111.py`, `222.py`, `333.py`는 시기·기능이 다른 *원본 실험 이력*이며 이 디렉터리의 진입점이 아닙니다. 단지 같은 기능의 실험 파일이라는 이유만으로 원본을 삭제하지 않았습니다.

## 하드웨어 없이 확인

```bash
cd reconstruction/app
python3 -m unittest discover -s tests -v
python3 main.py --demo
```

`--demo`는 사람 영상·음성 입력 없이 3단계 경고 상태 전이를 재현합니다. 경고 음성, TTS/STT, 마이크, 카메라는 **모의 처리**하며 실제 검출률과 음성 인식 성공을 의미하지 않습니다. 이 코드 복원 작업에는 물리 장치, 모델 파일, 클라우드 자격 증명이 필요하지 않습니다.

## 핵심 기본값 (대화에서 복원한 2023년 11월 22일 설정)

- 초기 보정 3초 (기존 `src/eye_detection/test_v2.py` 버전은 30초)
- EAR 기준 = 초기 평균 × 0.8 / 연속 10프레임
- 눈 위치 = 초기 평균보다 +20픽셀
- 경고 다음 1초 무시
- 1단계: `wa.wav` → `warning.wav`
- 2단계: `da.wav` → `danger.wav` → 산수 문제 TTS/STT
- 3단계: `da.wav` → `decibel.wav` → 음량 반응 평가
- 음량 판정: PCM RMS 기반 `20 log10(RMS/1)` 평균값이 70 초과 (교정된 SPL 데시벨이 **아님**)

원본이 없는 상세값(유효 프레임 수, 재무장 조건, 음량 재시도 횟수, 음성 대기 시간 등)은 2026년 재구성 추정이며 `docs/TRACEABILITY.md`에 표시했습니다.

## 코드 정리 원칙

기존 정리본의 `00_verified_originals/`(원본 중복 복사), `01_reference_refactor/`(감지 기능 중복), `02_missing_assets/` 및 `03_documentation/`(구형 구조 문서), `scripts/test2.py`·`scripts/decibel.py`(기능 중복 래퍼), `systemd/`(하드웨어 자동 실행), WAV·모델 빈 폴더는 정리했습니다. 단일 구현에서는 경고 순서가 `stages.py`에만 있고, 실제 판정 알고리즘은 각 전담 모듈에만 있습니다.

외부 파일 `shape_predictor_68_face_landmarks.dat`, WAV 및 Google Cloud 인증은 저장소에 포함되지 않으며, 코드 검증에는 필요하지 않습니다. 실장 동작·주행 안전성을 주장하지 않습니다.

[기능별 근거/추정표](docs/TRACEABILITY.md) · [기능과 원본 대응](../README.md)
