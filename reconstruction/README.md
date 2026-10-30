# 원본에 없는 부분만 최소 재구성

**원본 자체는 `../src/`에 있고, 이 폴더의 코드는 모두 2026년 추정 구현입니다.**

- `gaps/stage_flow.py`: 최종 발표의 경고 단계 전환 및 재시도 **구조만** 표시. 원본 눈 감지·TTS/STT를 재작성하지 않음.
- `gaps/decibel_formula.py`: 당시 대화에서 확인된 RMS → 프로그램 상대 음량 수식. 원본 차량 시험 `decibel.py`는 없음.
- `gaps/tests/`: 위 두 코드의 순수 로직 검증만 진행.

이 폴더에는 완전한 `main.py`가 없습니다. 원본만으로 2023년 최종 차량 시연 코드를 만들 수 있는 것처럼 보이게 하지 않기 위한 선택입니다. **인터페이스용 콜백은 실제 원본 실험 파일과 자동 연결되지 않습니다.**

근거별 판정은 [`../docs/ORIGINAL_VS_RECONSTRUCTED.md`](../docs/ORIGINAL_VS_RECONSTRUCTED.md)를 확인하세요.

### 코드만 검증

```bash
python3 -m unittest discover -s reconstruction/gaps/tests -v
```

안경/선글라스 경험, 약 10초 음성 답변, 문제·음량 무제한 재시도, 3단계 후 1단계 복귀는 사용자 설명에 근거합니다. 2023년 원본 10개는 단 한 줄도 수정하지 않았습니다.
