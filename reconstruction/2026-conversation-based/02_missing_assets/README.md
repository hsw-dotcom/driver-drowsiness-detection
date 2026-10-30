# 원본에서 참조하지만 확보하지 못한 자료

다음 항목은 원본 파일이 확보되지 않았으므로 가짜 파일로 대체하거나 원본으로 표시하지 않았습니다.

## Python 원본 (추가 발견 시 원문 그대로 복사할 것)
- `test.py`: 초기/통합 졸음 감지 실행 프로그램으로 2023년 대화에 등장
- `test1.py`: TTS/STT 문제·정답 판정 기능으로 2023년 대화에 등장
- `test2.py`, `decibel.py`: 경고 반응 단계 관련 2023년 대화에 등장
- `app.py`, `stt_test1.py`: 2026년 10월 30일 `py.zip` 분류 기록상 존재
- `py.zip`의 `test1.py`, `test2.py` 등과 `backup.zip` 추가 코드: 과거 검토 기록은 있으나 이 정리 세션에서 원본 데이터에 접근 불가

## 모델·사운드 (빈 디렉터리만 포함)
- `model/shape_predictor_68_face_landmarks.dat`: dlib 68점 특징점 모델
- `audio/warning.wav`, `audio/danger.wav` 또는 `wa.wav`, `da.wav`: 과거 대화에 등장한 경고음 명칭
- 그 외 2023년 `py.zip`에 포함된 것으로 기록된 WAV/MP3 10개: 원본 파일 미확보

## 자격 증명
- Google Cloud 서비스 계정 JSON: 개인 인증정보 포함 가능. 공유 ZIP/Git 저장소에서 **제외**. 실행 환경에만 별도로 안전하게 배치.

## 추후 보강
1. 원본 ZIP에서 소스만 선별해 이 문서의 이름별로 `00_verified_originals/` 내 해당 폴더에 보관
2. SHA-256 및 파일 출처/변경 여부를 `03_documentation/CODE_INVENTORY.csv`에 추가
3. 실제 경고·3단계 반응을 작동시키기 전 원본 `test.py`와 단계별 호출 순서를 직접 대조
4. 완성형 통합 코드로 단정하지 않기
