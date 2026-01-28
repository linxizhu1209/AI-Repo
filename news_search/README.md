# 네이버 뉴스 검색 & AI 분석 Streamlit 앱

네이버 뉴스 Open API를 이용해 뉴스를 검색하고,
검색된 뉴스 본문을 AI(Open AI, GPT)로 요약·분석할 수 있는 Streamlit 기반 실습 프로젝트입니다.

---

## 실행 환경
- Python 3.10 ~ 3.11 권장
- Streamlit
- FastAPI
- requests
- beautifulsoup4
- python-dotenv
- openai 
- torch
- transformers
- sentencepiece

---

## 설치 방법

필요한 패키지를 먼저 설치합니다.

```bash
pip install streamlit fastapi uvicorn requests beautifulsoup4 python-dotenv openai
pip install sentencepiece transformers==4.48.0 torch
```
---

## 실행 방법

아래 명령어로 앱 실행 가능합니다.
```bash
# 서버 실행
conda activate base
python main.py

# streamlit 실행
python -m streamlit run app.py
```
