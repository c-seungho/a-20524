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
    "분석할 영화를 선택하세요 (단일 영화 분석)", options=movie_order
)

# 선택한 영화에 대한 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]

# ==========================================
# [4 & 5] 그래프 구역 나누기 및 시각화
# ==========================================
st.subheader(f"📊 {selected_movie} - 관객수 변화 분석")

# 탭(Tab) 구역을 3개로 나눕니다.
tab1, tab2, tab3 = st.tabs(
    [
        "일별 관객수 변화 (선 그래프)",
        "누적 관객수 변화 (영역 차트)",
        "Top 5 영화 누적관객수 비교 (다중 선)",
    ]
)

# ------------------------------------------
# 첫 번째 탭: 개별 영화 일별 관객수 (선 그래프)
# ------------------------------------------
with tab1:
    fig_line = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 일자별 관객수 추이",
        markers=True,  # 각 데이터 지점에 점 표시
        labels={"기준일자": "날짜", "해당일관객수": "일별 관객수(명)"},
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie} 영화는 개봉 초기와 주말에 일별 관객수가 크게 증가하는 경향을 확인할 수 있습니다."
    )

# ------------------------------------------
# 두 번째 탭: 개별 영화 누적 관객수 (영역 차트)
# ------------------------------------------
with tab2:
    fig_area = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}'의 기준일자별 누적관객수 변화",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    st.plotly_chart(fig_area, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 {selected_movie} 영화의 전체 관객수가 폭발적으로 증가하는 구간과 완만해지는 흥행 정체 구간을 한눈에 파악할 수 있습니다."
    )

# ------------------------------------------
# 세 번째 탭: 누적관객수 Top 5 영화 비교 (다중 선 그래프)
# ------------------------------------------
with tab3:
    # 1. 누적관객수가 가장 높은 상위 5개 영화 선택
    top5_movies = movie_order[:5]

    # 2. 전체 데이터 중 Top 5 영화 데이터만 추출
    top5_df = df[df["영화명"].isin(top5_movies)]

    # 3. Plotly 다중 선 그래프 생성
    # color="영화명" 설정을 통해 영화별로 색상을 자동으로 다르게 적용하고 범례를 표시합니다.
    fig_multi_line = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",  # 영화별 색상 구분 및 범례 생성
        title="상위 5개 영화의 기준일자별 누적관객수 추이 비교",
        labels={
            "기준일자": "날짜",
            "누적관객수": "누적 관객수(명)",
            "영화명": "영화 제목",
        },
    )

    st.plotly_chart(fig_multi_line, use_container_width=True)

    # 상위 5개 영화 이름을 보기 쉽게 쉼표로 연결
    top5_names_str = ", ".join(top5_movies)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 역대 누적관객수 Top 5 영화({top5_names_str})의 흥행 속도를 한 화면에서 직접 비교하여, 특정 영화가 상대적으로 얼마나 가파르게 관객을 모았는지 알 수 있습니다."
    )
