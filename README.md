# 졸음운전 예방 카메라 — 원본 우선 코드 보존

**최종 발표자료를 기능/흐름의 최상위 기준으로, 2023년 확보한 소스 파일을 구현 근거로 사용합니다.** 2026년 추정 재구성은 원본이 없는 부분에만 최소한으로 둡니다. 하드웨어를 이용한 재현이나 실제 차량 안전성을 검증하는 작업이 아닙니다.

## 무엇이 실제 원본인가?

**`src/` 디렉터리의 Python 파일 10개만 2023년 보존 원본**입니다. 2023년 실험의 여러 시점과 목적을 반영하기 때문에 이름과 기능이 유사한 파일도 그대로 보존합니다. 기존 파일 내용은 수정하지 않았습니다.

- `src/eye_detection/test.py`, `test_v2.py`, `test3.py`: Picamera2/OpenCV/dlib 기반 얼굴·눈 랜드마크, EAR/눈 위치 계산, 카메라 시험.
- `src/voice_experiments/test1.py`, `111.py`, `222.py`, `333.py`, `app.py`, `stt_test1.py`, `test2.py`: 녹음, 수학 문제, Google TTS/STT 등 음성 기능 실험.

**원본이 해결하는 역할은 다시 작성하지 않았습니다.** 이전 `reconstruction/app/`의 비전, 음성, 카메라, 오디오 재구현 및 종합 `main.py`는 기본 브랜치에서 제외했습니다.

## 원본만으로 완성 가능한가?

- **눈 기반 졸음 감지 실험** 및 **독립된 음성 문제/TTS/STT 실험**: 원본 소스가 존재합니다.
- **최종 발표의 통합 3단계 프로그램**: **원본만으로는 불가능**합니다. 차량 시연 당시 통합 `/home/pi/project/test.py`와 `decibel.py`가 확보되지 않았습니다.
- `reconstruction/gaps/`: 누락된 3단계 상태 전환과 음량 수식의 **별도 추정 참고 코드**만 보유합니다. 원본을 대체하거나 통합 구동을 보장하지 않습니다.

## 확정한 동작 이해

눈의 EAR와 위치로 판단하며 얼굴형 분류는 하지 않았습니다. 사용자는 안경·선글라스 착용 상태에서 작동함을 관찰했습니다. 음성 답변은 약 10초 동안 인식했고, 2단계 문제/3단계 음량 미충족은 해결할 때까지 반복하며 경고 흐름은 1→2→3→1로 순환했습니다. **이 경험 사실을 보편적인 인식 성능 검증으로 확대하지 않습니다.**

## 문서

- [`docs/ORIGINAL_VS_RECONSTRUCTED.md`](docs/ORIGINAL_VS_RECONSTRUCTED.md): **파일별 원본/재구성 경계와 증거 등급**
- [`docs/vehicle-test-evidence-2023.md`](docs/vehicle-test-evidence-2023.md): 영상에서 확인된 실제 시험과 미확인 사항
- [`docs/implementation-notes.md`](docs/implementation-notes.md): 코드 감사 기록
- [`docs/security.md`](docs/security.md): 비공개 제외 자료
- [`reconstruction/README.md`](reconstruction/README.md): 원본에 없는 최소 참고 코드

## 로컬에서 하드웨어 없이 확인

```bash
python3 -m unittest discover -s reconstruction/gaps/tests -v
```

위 7개 테스트는 **추정 흐름·수식만** 검사합니다. 2023년 원본의 실기 작동, Google Cloud 계정, 마이크·카메라 및 최종 발표 전체 통합 작동은 검증한 것이 아닙니다.
