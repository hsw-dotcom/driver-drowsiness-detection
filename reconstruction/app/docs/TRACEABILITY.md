# 기능별 출처·추정 경계

| 기능 | 근거 | 통합 복원 구현 |
|---|---|---|
| 640×480, Picamera2, XBGR8888, 요청 60fps | 2023년 카메라 설정·변환 오류 대화와 원본 | `camera.py`, `config.ini` |
| dlib 68점 얼굴/눈 특징점 및 EAR | `src/eye_detection/test.py`, `test_v2.py` | `vision.py` |
| 초기 평균: 원본 30초와 후기 3초 | 초기 `test_v2.py`; 2023-11-22 후기 대화 | `vision.py`, 기본 3초 |
| EAR ≤ 평균×0.8, 연속 10프레임 | 확보된 원본 및 개발 대화 | `vision.py` |
| 눈높이 평균+20픽셀 | 확보된 원본 및 개발 대화 | `vision.py` |
| 감지 이후 1초 무시 | 당시 경고 중복 방지 대화 | `vision.py` |
| 3단계 경고와 WAV 순서 | 2023-11-22 대화 | `stages.py` |
| 수학 문제 및 한국어 TTS/STT | `src/voice_experiments/test1.py`, `222.py` 및 대화 | `quiz.py` |
| 음량 측정 5초·44.1kHz·청크 1024·RMS 기반 값 70 초과 | 당시 `decibel.py` 관련 대화. **후기 통합 decibel.py 원본은 확인되지 않음** | `loudness.py` |
| 카메라 인식과 경고 처리를 순차 연결 | 당시 회고와 테스트 영상의 동작 흐름 | `main.py` |
| 유효 보정 프레임 최소 3, 얼굴 선택 방식, 재무장 상태, 최대 3회 음량 시도 | 원본 수치·정확한 선택 방식 미확인 | **2026년 추정 안정화** |
| Google STT 제한시간 5초 및 Audio `aplay` | 기존 실험 버전과 처리 지연 회피 목적 | **2026년 추정 구현** |

## 동일 기능 파일의 처리 방식

- **역사적 원본** `src/eye_detection/test.py`, `test_v2.py`, `test3.py`: 각각 당시 시도·수정 단계이므로 삭제하지 않고 원본 영역에서만 보관합니다. 통합 판단 구현은 오직 `reconstruction/app/drowsiness/vision.py`입니다.
- **역사적 음성 실험** `src/voice_experiments/`의 `test1.py`, `111.py`, `222.py`, `333.py`, `app.py`, `stt_test1.py`, `test2.py`: 파일명과 작성 목적을 유지한 실험 이력이며 복원 앱의 실행 파일이 아닙니다. `src/voice_experiments/test2.py`는 결과 안내 TTS WAV 생성 코드입니다. 후기에 호출된 다른 `test2.py`와 동일하다고 확인되지 않습니다.
- **제거한 2026 중복본**: `00_verified_originals/`(원본 복사), `01_reference_refactor/`(중복 감지 엔진), `scripts/test2.py`·`scripts/decibel.py`(전담 모듈 호출만 하던 단독 래퍼), `Audio.sequence()`(단계 순서 중복).
- 파일이나 실행 흐름에서 원본 실험이 사용되었다는 사실과 2026 재구성본의 단위 테스트 성공은 구분합니다.

## 검증 수준

모듈 단위 테스트 및 `main.py --demo`는 카메라·마이크·클라우드 없이 수행 가능한 로직 검사입니다. 실제 Raspberry Pi 실행, 음성 입출력, 모델 검출 성능, 안전성은 검증 대상이 아닙니다.
