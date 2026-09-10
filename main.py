import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
st.subheader("📊 박스오피스 다각도 데이터 분석")

# 탭(Tab) 구역을 4개로 나눕니다.
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "일별 관객수 변화 (선 그래프)",
        "누적 관객수 변화 (영역 차트)",
        "20일 이상 장기 흥행 Top 5 비교 (다중 선)",
        "전체 박스오피스 7일 이동평균선",
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
# 세 번째 탭: TOP10 20일 이상 등재 영화 중 누적관객수 Top 5
# ------------------------------------------
with tab3:
    # 1. 영화별 등장 일수(행 수) 및 최대 누적관객수 집계
    movie_stats = (
        df.groupby("영화명")
        .agg(
            days_in_top10=("기준일자", "count"),  # TOP10 차트 등재 일수
            max_audience=("누적관객수", "max"),  # 최대 누적관객수
        )
        .reset_index()
    )

    # 2. TOP10에 20일 미만으로 등장한 영화 제외 (20일 이상만 남김)
    long_running_movies = movie_stats[movie_stats["days_in_top10"] >= 20]

    # 3. 20일 이상 장기 흥행한 영화 중 누적관객수 기준 상위 5개 추출
    top5_long_running = long_running_movies.sort_values(
        by="max_audience", ascending=False
    ).head(5)["영화명"].tolist()

    # 4. 전체 데이터에서 해당 Top 5 영화 데이터만 필터링
    top5_df = df[df["영화명"].isin(top5_long_running)]

    # 5. Plotly 다중 선 그래프 생성
    fig_multi_line = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",  # 영화별 색상 구분 및 범례 생성
        title="TOP 10 20일 이상 장기 흥행 영화 중 누적관객수 Top 5 비교",
        labels={
            "기준일자": "날짜",
            "누적관객수": "누적 관객수(명)",
            "영화명": "영화 제목",
        },
    )

    st.plotly_chart(fig_multi_line, use_container_width=True)

    top5_names_str = ", ".join(top5_long_running)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 단기 반짝 흥행을 제외하고, TOP 10에 20일 이상 장기 등재된 검증된 흥행작({top5_names_str})들의 누적관객수 증가 속도와 흥행 유지력을 비교할 수 있습니다."
    )

# ------------------------------------------
# 네 번째 탭: TOP10 합계 일별 관객수 및 7일 이동평균선 (신규)
# ------------------------------------------
with tab4:
    # 1. 기준일자별로 TOP10 영화 전체의 해당일관객수를 합산합니다.
    daily_total = (
        df.groupby("기준일자")["해당일관객수"]
        .sum()
        .reset_index()
        .sort_values("기준일자")
    )

    # 2. 7일 이동평균(Moving Average) 계산
    # window=7: 7일간의 평균, min_periods=1: 초반 1~6일차 데이터도 누락 없이 표시
    daily_total["7일이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
    )

    # 3. Plotly graph_objects를 이용해 원본 선과 이동평균 선을 하나의 그래프에 중첩
    fig_ma = go.Figure()

    # (1) 원본 일별 총 관객수 (연하게 표현)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (일간 합계)",
            line=dict(color="rgba(150, 180, 220, 0.4)", width=1.5),  # 연한 파란색
        )
    )

    # (2) 7일 이동평균선 (진하게 표현)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일이동평균"],
            mode="lines",
            name="7일 이동평균선",
            line=dict(color="#1f77b4", width=3),  # 진한 파란색 및 두꺼운 선
        )
    )

    # 그래프 레이아웃 설정
    fig_ma.update_layout(
        title="전체 박스오피스(TOP 10) 일별 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="관객수(명)",
        hovermode="x unified",  # 마우스 커서 위치의 X축 값 통합 표시
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_ma, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 주말과 평일의 심한 변동성(연한 선)을 제거하고, 7일 이동평균선(진한 선)을 통해 연중 전체 극장가 관객 수의 전반적인 상승·하락 흐름과 성수기/비성수기 추세를 명확하게 확인할 수 있습니다."
    )
