# PDF 파싱 & 이미지 OCR Streamlit 앱

FastAPI 서버와 Streamlit 프론트를 연동하여  
PDF 문서 텍스트 파싱과 이미지 OCR(문자 인식)을 수행하는 실습용 웹 애플리케이션입니다.


---

## 실행 환경
- Python 3.10 ~ 3.11 권장
- Streamlit
- FastAPI
- requests
- PyPDF2
- EasyOCR
- torch
- numpy
- pillow

---

## 설치 방법

필요한 패키지를 먼저 설치합니다.

```bash
pip install streamlit fastapi uvicorn requests pillow
pip install pypdf2 easyocr numpy
pip install torch sentencepiece transformers==4.48.0
```
---

## 실행 방법

아래 명령어로 앱 실행 가능합니다.
```bash
# 서버 실행
conda activate base
python faseapi_app.py

# streamlit 실행
python -m streamlit run streamlit_app.py
```
