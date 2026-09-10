import pandas as pd
import plotly.express as px
import streamlit as st


# ==========================================
# [1] 데이터 불러오기 (캐싱 적용)
# ==========================================
# @st.cache_data 데코레이터를 사용하여 매번 파일 전체를 다시 불러오지 않고
# 한 번 로드한 데이터를 메모리에 저장(캐싱)하여 앱의 실행 속도를 높입니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # ------------------------------------------
    # [2] 데이터 전처리
    # ------------------------------------------
    # 1. 결측치(빈값)가 포함된 모든 행 삭제
    df = df.dropna()

    # 2. '기준일자' 컬럼을 datetime(날짜) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 3. 전체 데이터를 '기준일자' 기준으로 오름차순 정렬
    df = df.sort_values("기준일자")

    return df


# 데이터 로드
df = load_data()

# Page 설정
st.set_page_config(page_title="영화 박스오피스 분석 앱", layout="wide")
st.title("🎬 영화 박스오피스 데이터 분석 앱")

# ==========================================
# [3] 영화 선택 기능 (사이드바)
# ==========================================
st.sidebar.header("🔍 검색 및 선택")

# 각 영화의 최대 누적관객수를 구해 누적관객수가 많은 순서대로 정렬합니다.
movie_order = (
    df.groupby("영화명")["누적관객수"].max().sort_values(ascending=False).index
)

# 사용자로부터 영화 이름을 선택받습니다.
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요", options=movie_order
)

# 선택한 영화에 대한 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]

# ==========================================
# [4 & 5] 그래프 구역 나누기 및 시각화
# ==========================================
st.subheader(f"📊 {selected_movie} - 관객수 변화 분석")

# 추후 다른 그래프를 추가하기 용이하도록 탭(Tab) 구역을 나눕니다.
tab1, tab2 = st.tabs(["일별 관객수 변화 (Plotly)", "추후 추가 예정 구역"])

with tab1:
    # Plotly 라인 차트 생성
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 일자별 관객수 추이",
        markers=True,  # 각 데이터 지점에 점 표시
        labels={"기준일자": "날짜", "해당일관객수": "일별 관객수(명)"},
    )

    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 하단 설명 문구 들어갈 자리
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie} 영화는 개봉 초기와 주말에 관객수가 크게 증가하는 경향을 확인할 수 있습니다."
    )

with tab2:
    st.write("📌 이 구역에는 향후 추가할 새로운 그래프(예: 누적관객수 추이, 스크린수 대비 관객수 등)를 배치할 수 있습니다.")
