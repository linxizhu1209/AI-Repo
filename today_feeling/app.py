import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime

# 버튼 css 선언
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    background-color: #ff4b4b;
    color: white;
    font-weight: bold;
    height: 3em;
    border-radius: 6px;
}
</style>     
""", unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(page_title="한국어 감정 분석", layout="wide")

# 모델 및 토크나이저 로드 (캐싱)
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained("rkdaldus/ko-sent5-classification")
    return tokenizer, model

# 감정 분석 함수
def analyze_sentiment(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    
    # 감정 레이블 정의 (이모티콘 제외)
    emotion_labels = {
        0: "Angry",
        1: "Fear",
        2: "Happy",
        3: "Tender",
        4: "Sad"
    }
    
    return emotion_labels[predicted_label]

# 세션 스테이트 초기화
if 'history' not in st.session_state:
    st.session_state.history = []

# 모델 로드
with st.spinner('모델을 로딩중입니다...'):
    tokenizer, model = load_model()

# 제목
st.title("한국어 감정 분석 앱")
st.markdown("---")

# 레이아웃: 왼쪽과 오른쪽 컬럼
left_col, right_col = st.columns([2, 1])

# 왼쪽 컬럼: 입력 및 출력
with left_col:
    st.subheader("감정 입력")
    
    ########################################
    #### 필수과제 - 문제1) 감정 입력 및 모델 출력 화면 구성
    
    description = st.text_area("감정을 표현하는 문장을 입력해주세요:", height=100)
 
    if st.button("감정 분석하기"):
        with st.spinner("감정 분석중입니다 .."):
            feeling_result = analyze_sentiment(description, tokenizer, model)

            # 분석 기록 추가 코드
            st.session_state.history.insert(0, {
                "text": description,
                "feeling": feeling_result,
                "time": datetime.now()
            })

            st.subheader("분석 결과")
            st.success(f"감정: {feeling_result}")
            st.caption(datetime.today())   


    ########################################

# 오른쪽 컬럼: 과거 기록
with right_col:
    st.subheader("분석 기록")

    if st.button("기록 초기화"):
        st.session_state.history.clear()
        st.success("기록 초기화 완료")
        st.rerun()

    ########################################
    #### 필수과제 - 문제2) 분석 기록 컬럼 화면 제작

    if not st.session_state.history:
        st.info("아직 분석 기록이 없습니다.")
    else:
        sorted_history = sorted(
        st.session_state.history,
        key=lambda x: x["time"],
        reverse=True
        )

        for i, item in enumerate(sorted_history, start=1):
            st.markdown(f"### #{i}")
            st.markdown(f"**입력:** {item['text']}")
            st.markdown(f"**감정:** {item['feeling']}")
            st.caption(f"**시간:** {item['time']}")    
            st.markdown("---")

    ########################################

# 구분선
st.markdown("---")

# 텍스트 스트리밍 섹션
st.title("텍스트 생성 스트리밍")

# 텍스트 생성 generator 함수
import time

def text_generator():
    """텍스트를 한 단어씩 생성하는 generator 함수"""
    sample_text = """
다시 시작되는 월요일에게 붙이는 짧은 시

커피가 먼저 부팅되고, 내가 뒤늦게 로그인한다.
알람은 세 번의 재시도를 거쳐 나를 인증한다.
거울 속 내 얼굴은 “쿠키 허용?”을 묻는다.

현관 앞 양말은 좌우가 다르다—A/B 테스트 중이라서.
엘리베이터는 1층에서만 고집 세고,
나는 계단에서 숨이 차 “업데이트 나중에”를 누른다.

회사 앞 자판기는 잔액을 모른 척하고,
내 지갑은 오류 메시지 없이 비었다.
점심 메뉴는 회의록보다 길고, 결정은 더 느리다.

그래도 퇴근길 하늘이 파랗게 컴파일되면
나는 하루를 저장하고—이불 속에서
어제에 Ctrl+Z, 내일에 Ctrl+S를 누른다.
"""
    
    # 단어 단위로 분리
    words = sample_text.split()
    
    for word in words:
        yield word + " "
        time.sleep(0.05)  # 0.05초 딜레이로 스트리밍 효과



########################################
#### 도전과제 - 문제3) 텍스트 생성 스트리밍 기능 제작

question = st.text_input("질문을 입력하세요:")

# generator - 값을 한번에 만들지 않고, 필요할 때마다 하나씩 만들어 내보내는 함수
# -> yield 사용
if st.button("AI 응답 생성"):
    if not question.strip():
        st.warning("질문을 입력해주세요!")
    else:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            st.write_stream(text_generator()) # generator 또는 iterator가 내보내는 조각들 실시간으로 화면에 이어서 출력해주는 함수
        
        st.success("응답 완료")









########################################