# 한국어 감정 분석 Streamlit 앱

한국어 문장을 입력하면 감정을 분석하고,  
AI 텍스트 스트리밍 응답을 확인할 수 있는 Streamlit 기반 실습 프로젝트입니다.

---

## 실행 환경
- Python 3.10 ~ 3.11 권장
- Streamlit
- transformers
- sentencepiece
- torch

---

## 설치 방법

필요한 패키지를 먼저 설치합니다.

```bash
pip install sentencepiece transformers==4.48.0 torch streamlit

---

## 실행 방법

아래 명령어로 앱 실행 가능합니다.
```bash
python -m streamlit run app.py