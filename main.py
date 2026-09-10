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

# 탭(Tab) 구역을 6개로 나눕니다.
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "일별 관객수 변화 (선 그래프)",
        "누적 관객수 변화 (영역 차트)",
        "20일 이상 장기 흥행 Top 5 비교 (다중 선)",
        "전체 박스오피스 7일 이동평균선",
        "월별 전체 관객수 합계 (막대그래프)",
        "월×요일별 관객수 캘린더 히트맵",
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
# 네 번째 탭 & 다섯 번째 탭 & 여섯 번째 탭 공통 데이터 계산
# ------------------------------------------
daily_total = (
    df.groupby("기준일자")["해당일관객수"]
    .sum()
    .reset_index()
    .sort_values("기준일자")
)

# ------------------------------------------
# 네 번째 탭: TOP10 합계 일별 관객수 및 7일 이동평균선
# ------------------------------------------
with tab4:
    daily_total["7일이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
    )

    fig_ma = go.Figure()

    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (일간 합계)",
            line=dict(color="rgba(150, 180, 220, 0.4)", width=1.5),
        )
    )

    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일이동평균"],
            mode="lines",
            name="7일 이동평균선",
            line=dict(color="#1f77b4", width=3),
        )
    )

    fig_ma.update_layout(
        title="전체 박스오피스(TOP 10) 일별 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="관객수(명)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_ma, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 주말과 평일의 심한 변동성(연한 선)을 제거하고, 7일 이동평균선(진한 선)을 통해 연중 전체 극장가 관객 수의 전반적인 상승·하락 흐름과 성수기/비성수기 추세를 명확하게 확인할 수 있습니다."
    )

# ------------------------------------------
# 다섯 번째 탭: 월별 전체 관객수 합계 (막대그래프)
# ------------------------------------------
with tab5:
    daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

    monthly_total = (
        daily_total.groupby("연월")["해당일관객수"]
        .sum()
        .reset_index()
        .sort_values("연월")
    )

    fig_bar = px.bar(
        monthly_total,
        x="연월",
        y="해당일관객수",
        title="월별 전체 박스오피스(TOP 10) 총 관객수 합계",
        labels={"연월": "연-월", "해당일관객수": "월간 총 관객수(명)"},
        text_auto=".2s",
    )

    fig_bar.update_traces(marker_color="#2b5c8f", textposition="outside")
    fig_bar.update_layout(xaxis_type="category")

    st.plotly_chart(fig_bar, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 일별/주별 변동을 넘어 월별 총 관객 규모를 한눈에 파악할 수 있으며, 연중 극장가가 가장 붐비는 대목(성수기 월)과 상대적으로 관객이 적은 비성수기 월의 차이를 명확하게 알 수 있습니다."
    )

# ------------------------------------------
# 여섯 번째 탭: 월×요일별 관객수 캘린더 히트맵 (신규)
# ------------------------------------------
with tab6:
    # 1. 히트맵 작성을 위한 날짜 파생 컬럼 준비
    heatmap_df = daily_total.copy()
    heatmap_df["연월"] = heatmap_df["기준일자"].dt.strftime("%Y-%m")
    heatmap_df["날짜문자열"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

    # 요일 한글명 및 순서 정렬 (월요일 ~ 일요일)
    weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
    heatmap_df["요일_num"] = heatmap_df["기준일자"].dt.dayofweek
    heatmap_df["요일"] = heatmap_df["요일_num"].map(weekday_map)

    days_order = ["월", "화", "수", "목", "금", "토", "일"]

    # 2. 피벗 테이블 생성 (행: 연월, 열: 요일)
    # 관객수(z 값)와 호버에 표시할 YYYY-MM-DD(customdata)를 각각 생성합니다.
    pivot_audience = heatmap_df.pivot_table(
        index="연월", columns="요일", values="해당일관객수", aggfunc="sum"
    ).reindex(columns=days_order)

    pivot_date = heatmap_df.pivot_table(
        index="연월", columns="요일", values="날짜문자열", aggfunc="first"
    ).reindex(columns=days_order)

    # 3. Plotly Heatmap 생성
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot_audience.values,  # 관객수 (색상 매핑)
            x=days_order,  # X축: 월~일
            y=pivot_audience.index,  # Y축: 연-월
            customdata=pivot_date.values,  # 호버용 날짜 문자열(yyyy-mm-dd)
            colorscale="Viridis",  # 진할수록(값이 클수록) 선명한 색상
            hoverongaps=False,
            hovertemplate="<b>날짜: %{customdata}</b><br>요일: %{x}요일<br>연-월: %{y}<br>일 관객 합계: %{z:,.0f}명<extra></extra>",
        )
    )

    fig_heatmap.update_layout(
        title="월(연-월) × 요일별 전체 박스오피스 일관객 합계 히트맵",
        xaxis_title="요일",
        yaxis_title="월 (연-월)",
        yaxis=dict(autorange="reversed"),  # 최신 월 또는 과거 월 순서대로 보기 좋게 정렬
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 월별 및 요일별(월~일) 관객 수 분포를 시각적으로 한눈에 비교할 수 있으며, 토/일요일 주말 집중 현상 및 특정 달의 특정 요일(공휴일 등)에 관객 수가 폭발적으로 증가한 날을 손쉽게 포착할 수 있습니다."
    )
