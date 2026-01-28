import os
import streamlit as st
import requests
from openai import OpenAI
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

# FastAPI 서버 URL (환경변수로 설정 가능)
FASTAPI_URL = "http://localhost:8000"

# OpenAI 클라이언트 초기화
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다.")
        return None
    return OpenAI(api_key=api_key)

# 서버에 뉴스 검색 호출
def get_news_articles(query: str, display: int = 10):
    ################################################
    ######### 필수 과제 - 문제 2: fastapi를 호출한 검색결과 가져오기
    # query -- 어떤 뉴스 검색
    # display - 기사 개수
    reqBody = {
        "query": query,
        "display": display
    }
    response = requests.get(FASTAPI_URL + "/search", params=reqBody)
    
    print("status:", response.status_code)
    print("response text:", response.text)

    ## list 만 return
    data = response.json()
    return data["articles"]
    ################################################

### openAi로 분석 함수
def generate_with_openai(news_list, prompt):
    
    client = get_openai_client()
    if not client:
        return None
    
    # 뉴스 데이터를 JSON 문자열로 변환
    news_json = json.dumps(news_list, ensure_ascii=False, indent=2)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": news_json}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API 오류: {str(e)}")
        return None
    
### 오디오 파일 텍스트로 변환 STT
def transcribe_audio(audio_file):
    client = get_openai_client()
    if not client:
        return None
    
    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text
    except Exception as e:
        st.error(f"STT 오류: {str(e)}")
        return None


########################################################
# Streamlit UI
st.set_page_config(
    page_title="뉴스 검색 및 분석",
    page_icon="📰",
    layout="wide"
)

st.title("📰 네이버 뉴스 검색 및 AI 분석")

# 탭 생성
tab1, tab2 = st.tabs(["🔍 뉴스 검색 & 분석", "🎤 음성 입력 (STT)"])

with tab1:
    st.header("뉴스 검색")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("검색어를 입력하세요", placeholder="예: 주식, AI, 부동산")
    with col2:
        num_articles = st.number_input("기사 수", min_value=1, max_value=10, value=5)
    
    search_button = st.button("🔍 검색", type="primary", use_container_width=True)
    
    # 세션 스테이트에 뉴스 데이터 저장
    if "news_data" not in st.session_state:
        st.session_state.news_data = []
    
    if search_button and search_query:
        with st.spinner("FastAPI 서버를 통해 뉴스를 검색하고 있습니다..."):
            news_articles = get_news_articles(search_query, num_articles)
            st.session_state.news_data = news_articles
        
        if news_articles:
            st.success(f"✅ {len(news_articles)}개의 뉴스 기사를 찾았습니다!")
        else:
            st.warning("검색 결과가 없습니다.")
    
    # 검색 결과 표시
    if st.session_state.news_data:
        st.header("검색 결과")
        
        news_data = st.session_state.news_data

        ################################################
        ######### 필수 과제 - 문제 3: 검색결과 화면에 st.expander로 표시 및 LLM 프롬프팅 결과 출력
        # 뉴스 제목 (ex, 제목이모지 1.제목~)
        # 뉴스 링크 (ex, 링크: ~~)     
        # 뉴스 본문 (ex, 본문: text_area)   
        import html
        import re

        for index, article in enumerate(news_data, start=1):
            title_raw = article.get("title", "")
            link = article.get("link", "")
            body = article.get("body", "")
            
            title = html.unescape(title_raw)
            title = re.sub(r"<.*?>", "", title)

            with st.expander(f"📝 {index}. {title}"):
                st.markdown(f"**링크:** [{link}]({link})")
                st.text_area("본문", body, height=300)             
        
        ## AI 분석요청 및 분석 결과 
        st.header("AI 분석 요청")
        prompt = st.text_area(
            "프롬프트를 입력하세요.",
            height=100)

        analyze_btn = st.button("👾 AI 분석 실행", type="primary", use_container_width=True)

        if analyze_btn:
            with st.spinner("AI 분석 중..."):
                result = generate_with_openai(news_data, prompt)
                st.session_state.ai_result = result

        st.header("AI 분석 결과")

        if st.session_state.get("ai_result"):
            st.markdown(st.session_state.ai_result)
        else:
            st.info("아직 분석 결과가 없습니다.")
        ################################################
        
with tab2:
    st.header("음성 입력 및 STT (Speech to Text)")
    
    st.info("🎤 마이크 버튼을 눌러 음성을 녹음하세요. 녹음이 끝나면 자동으로 텍스트로 변환됩니다.")
    
    ##################################################
    ######### 도전 과제 - 문제 4: streamlit으로 오디오 입력 기능 구현
    
    # 1. audio 입력 UI (streamlit 사용)
    audio_file = st.audio_input("음성 메시지 녹음")

    if audio_file is None:
        st.warning("아직 녹음된 오디오가 없습니다.")
    else:
        # 2. 녹음된 음성 재생
        st.subheader("📢 녹음된 오디오")
        audio_bytes = audio_file.getvalue()

        ## 녹음버튼만 누르고 audio 안들어온 경우 예외처리
        if not audio_bytes or len(audio_bytes) == 0:
            st.warning("녹음된 음성이 없습니다. 다시 녹음해주세요.")
            st.stop

        st.audio(audio_bytes, format=audio_file.type)

        with st.spinner("음성을 텍스트로 변환 중입니다..."):
            stt_text = transcribe_audio(audio_file)
            st.session_state.stt_text = stt_text or ""
        st.subheader("📒 변환된 텍스트")
        st.text_area("STT 결과", value=st.session_state.get("stt_text", ""), height=120) 
    
        if st.button("🔎 이 텍스트로 뉴스 검색하기"):
            if not stt_text:
                st.warning("변환된 텍스트가 비어있습니다.")
            else:
                st.session_state.search_query = stt_text
                st.rerun()

    
    ##################################################

