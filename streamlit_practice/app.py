import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import date, timedelta
import time

st.set_page_config(page_title="My App", page_icon="🚀")

st.sidebar.title("Navigation")
st.title("Main Content")

user_input = st.text_input("Enter something:")

if user_input:
    st.write(f"You entered: {user_input}")


# 기본 패턴 
user_name = st.text_input("이름을 입력해주세요:")

if user_name:
    st.write(f"안녕하세요, {user_name}님!")

# 폼 패턴
with st.form("my_form"):
    name = st.text_input("이름")
    age = st.number_input("나이", min_value=0, max_value=120)
    submitted = st.form_submit_button("제출")

    if submitted:
        st.write(f"{name}님의 나이는 {age}세입니다.")


# 컬럼 레이아웃 패턴
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("첫 번째 열")

with col2:
    st.header("Column 2")
    st.write("두 번째 열")

with col3:
    st.header("Column 3")
    st.write("세 번째 열")

# 사이드바 패턴
st.sidebar.title("설정")
option = st.sidebar.selectbox("옵션 선택", ["A","B","C"])
value = st.sidebar.slider("값 선택", 0, 100, 50)

st.title("메인 콘텐츠")
st.write(f"선택된 옵션: {option}")
st.write(f"선택된 값: {value}")


# 짧은 텍스트
name = st.text_input("이름")

# 긴 텍스트
description = st.text_area("설명", height=100)

# 비밀번호
password = st.text_input("비밀번호", type="password")

# 정확한 값
age = st.number_input("나이", min_value=0, max_value=120, value=25)

# 범위 선택
price_range = st.slider("가격 범위", 0, 1000, (200, 800))

# 단일 값 선택
rating = st.select_slider("평점", options=[1, 2, 3, 4, 5])

# 단일 선택
category = st.selectbox("카테고리", ["A", "B", "C"])
option = st.radio("옵션", ["Option 1", "Option 2"])

# 다중 선택
features = st.multiselect("기능 선택", ["기능1", "기능2", "기능3"])

# 체크박스
agree = st.checkbox("동의합니다")


# 제목과 헤더
st.title("메인 제목")
st.header("섹션 헤더")
st.subheader("서브 헤더")

# 일반 텍스트
st.write("일반 텍스트")
st.markdown("**굵은 글씨**")

# 코드
st.code("print('Hello World')", language="python")

# 테이블
# st.dataframe(df)  # 인터랙티브
# st.table(df)      # 정적

# 메트릭
st.metric("매출", "1,000,000원", "10%")

# JSON
st.json({"key": "value"})

# -------------
# 차트 등 예시
# -------------
st.title("차트 예시")

st.header("기본 차트")

data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["A","B","C"]
)

st.subheader("Line Chart")
st.line_chart(data)

st.subheader("Bar Chart")
st.bar_chart(data)

# ---------------------

st.header("Plotly 차트")
df_plotly = pd.DataFrame({
    "x": range(10),
    "y": np.random.randint(1, 100, 10)
})

fig_plotly = px.line(
    df_plotly,
    x="x",
    y="y",
    title="Plotly Line Chart"
)

st.plotly_chart(fig_plotly, use_container_width=True)

# ------------------- 

st.header("Matplotlib 차트")

fig_mpl, ax = plt.subplots()
ax.plot(df_plotly["x"], df_plotly["y"], marker="o")
ax.set_title("Matplotlib Line Chart")
ax.set_xlabel("x")
ax.set_ylabel("y")

st.pyplot(fig_mpl)

# -----------------
st.header("지도 (Map)")

location_data = pd.DataFrame({
    "lat": [37.5665, 35.1796, 35.8714],
    "lon": [126.9780, 129.0756, 128.6014]
})

st.map(location_data)
# ----------------------


# 균등 분할
col1, col2, col3 = st.columns(3)

# 비율 분할
col1, col2 = st.columns([2, 1])  # 2:1 비율

# 사용 예시
with col1:
    st.header("메인 콘텐츠")
    st.write("주요 내용")

with col2:
    st.header("사이드 정보")
    st.write("부가 정보")

# 일반 컨테이너
with st.container():
    st.write("그룹화된 콘텐츠")
    st.button("버튼")


np.random.seed(0)
data = pd.DataFrame({
    "category": np.random.choice(["A", "B", "C"], size=30),
    "value": np.random.randint(10, 100, size=30),
    "date": [date.today() - timedelta(days=i) for i in range(30)]
})

detailed_data = data.sort_values("value", ascending=False)

# 확장 가능한 컨테이너
with st.expander("자세히 보기"):
    st.write("상세 데이터 (값 기준 내림차순)")
    st.dataframe(detailed_data)    

# 사이드바에 컨트롤 배치
with st.sidebar:
    st.header("설정")

    options = ["전체", "A","B","C"]
    filter_option = st.selectbox("카테고리 필터", options)
    date_range = st.date_input("날짜 범위", value=(date.today() - timedelta(days=7), date.today()))

# 메인 영역은 결과 표시용

def apply_filter(df, category, date_range):
    filtered = df.copy()

    if category != "전체":
        filtered = filtered[filtered["category"] == category]

    start_date, end_date = date_range
    filtered = filtered[
        (filtered["date"] >= start_date) &
        (filtered["date"] <= end_date)
        ]
    return filtered
    
st.header("결과")
filtered_data = apply_filter(data, filter_option, date_range)
st.dataframe(filtered_data)



# -----사용자 경험 개선 ------

st.header("spinner 로딩 상태 표시")

def expensive_computation():
    time.sleep(2)
    return pd.DataFrame(
        np.random.randn(5, 3),
        columns=["A", "B", "C"]
    )

if st.button("데이터 처리 시작"):
    with st.spinner("데이터를 처리하는 중..."):
        result = expensive_computation()

    st.success("처리 완료")
    st.dataframe(result)   


st.header("progress Bar 진행률 표시")

if st.button("진행률 테스트"):
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"진행 중... {i + 1}%")
        time.sleep(0.03)

    status_text.text("완료")
    st.success("모든 작업이 완료되었습니다.")    


#------------------#

st.header("피드백 제공")

data = pd.DataFrame({
    "id": range(1, 6),
    "value": np.random.randint(10, 100, 5)
})

st.subheader("현재 데이터")
st.dataframe(data)


def save_data(df: pd.DataFrame):
    save_dir = Path("output")
    save_dir.mkdir(exist_ok=True)

    file_path = save_dir / "data.csv"

    # raise RuntimeError("강제 에러 테스트")

    df.to_csv(file_path, index=false)


if st.button("데이터 저장"):
    try:
        st.success("데이터가 성공적으로 저장되었습니다!")
        st.info("output/data.csv 파일로 저장됨")
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {e}")


#------------#
if st.sidebar.checkbox("모바일 뷰"):
    st.write("차트")
    st.line_chart(data)
    st.write("테이블")
    st.dataframe(data)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(data)
    with col2:
        st.dataframe(data)