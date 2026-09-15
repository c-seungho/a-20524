# Update main.py content to add the fifth chart: Boxplot for genres with >= 10 movies
main_py_content_v5 = '''import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 메인 타이틀
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("KOBIS 박스오피스 데이터를 바탕으로 영화 시장의 분포와 다양한 변수 간의 관계를 시각화합니다.")
st.divider()

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre: 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 extraction
    if 'genre' in df.columns:
        df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if x and x != 'nan' else '기타')
    
    # openDt 날짜 형식 변환 (문자열 또는 숫자 8자리 -> datetime)
    if 'openDt' in df.columns:
        df['openDt'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
        
    return df

try:
    df = load_data()
    
    # 사이드바 데이터 요약 및 필터
    st.sidebar.header("🔍 데이터 정보")
    st.sidebar.metric("총 분석 영화 수", f"{len(df)} 편")
    
    # -------------------------------------------------------------------------
    # 첫 번째 그래프: 장르별 영화 편수 (도넛 차트)
    # -------------------------------------------------------------------------
    st.header("1. 장르별 영화 편수 분포")
    
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '영화 편수']
    
    fig_donut = px.pie(
        genre_counts,
        values='영화 편수',
        names='장르',
        hole=0.4,
        title="장르별 영화 비율 및 편수",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_donut.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )
    
    fig_donut.update_layout(
        legend_title_text="장르 목록",
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # 구역 구분 및 알 수 있는 것 안내
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("특정 주요 장르에 상업 영화 제작 및 개봉이 집중되어 있으며, 비주류 장르와의 편수 차이가 극명함을 확인할 수 있습니다.")
    st.divider()

    # -------------------------------------------------------------------------
    # 두 번째 그래프: 장르별 영화 트리맵 (총 관객수 기준)
    # -------------------------------------------------------------------------
    st.header("2. 장르별 영화 총 관객수 분포 (트리맵)")
    
    fig_treemap = px.treemap(
        df,
        path=[px.Constant("전체 영화"), 'genre', 'movieNm'],
        values='total_audi',
        color='genre',
        title="장르 및 영화별 총 관객수 비중",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_treemap.update_traces(
        hovertemplate="<b>영화명/구분: %{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
    )
    
    fig_treemap.update_layout(
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("흥행을 견인하는 주요 장르 내에서도 특정 메가 히트작(대형 관객 수 보유 영화)이 차지하는 비중이 매우 큼을 알 수 있습니다.")
    st.divider()

    # -------------------------------------------------------------------------
    # 세 번째 그래프: 총 관객수(total_audi) 히스토그램
    # -------------------------------------------------------------------------
    st.header("3. 총 관객수(total_audi) 분포 (히스토그램)")
    
    fig_hist = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        title="영화별 총 관객수 분포",
        labels={'total_audi': '총 관객수(명)'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig_hist.update_traces(
        hovertemplate="관객수 구간: %{x:,}명<br>영화 편수: %{y}편<extra></extra>"
    )
    
    fig_hist.update_layout(
        yaxis_title="영화 편수",
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # 관객 수가 가장 많은 영화 정보 분석
    top_movie = df.loc[df['total_audi'].idxmax()]
    top_movie_name = top_movie['movieNm']
    top_movie_audi = top_movie['total_audi']
    
    under_1m_count = (df['total_audi'] < 1000000).sum()
    under_1m_pct = (under_1m_count / len(df)) * 100
    
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info(
        f"대부분의 영화({under_1m_pct:.1f}%)가 관객수 100만 명 미만의 하위 구간에 집중되어 있는 롱테일(Long-tail) 분포 형태를 보이며, "
        f"가장 관객 수가 많은 영화는 총 {top_movie_audi:,}명을 동원한 '{top_movie_name}'입니다."
    )
    st.divider()

    # -------------------------------------------------------------------------
    # 네 번째 그래프: 개봉일 스크린수와 총 관객수 산점도 (Scatter Plot)
    # -------------------------------------------------------------------------
    st.header("4. 개봉일 스크린수(first_scrn)와 총 관객수(total_audi)의 관계")
    
    fig_scatter = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        labels={
            'first_scrn': '개봉일 스크린수(개)',
            'total_audi': '총 관객수(명)',
            'genre': '장르'
        },
        title="개봉일 스크린수 vs 총 관객수 산점도"
    )
    
    fig_scatter.update_traces(
        hovertemplate="<b>영화명: %{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>",
        marker=dict(size=9, opacity=0.8)
    )
    
    fig_scatter.update_layout(
        legend_title_text="장르",
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("개봉일 스크린수가 많이 확보될수록 총 관객수가 비례하여 증가하는 강한 양의 상관관계를 보이며, 초기 스크린 확보가 최종 흥행 실적에 핵심적인 요인임을 알 수 있습니다.")
    st.divider()

    # -------------------------------------------------------------------------
    # 다섯 번째 그래프: 주요 장르별 총 관객수 상자 그림 (Box Plot)
    # -------------------------------------------------------------------------
    st.header("5. 주요 장르별 총 관객수 분포 (상자 그림)")
    
    # 영화 편수가 10편 이상인 장르만 필터링
    genre_counts_series = df['genre'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
    df_major_genres = df[df['genre'].isin(major_genres)]
    
    fig_box = px.box(
        df_major_genres,
        x='genre',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        labels={
            'genre': '장르',
            'total_audi': '총 관객수(명)'
        },
        title="영화 편수 10편 이상 주요 장르별 총 관객수 분포 (이상치 표시)"
    )
    
    fig_box.update_traces(
        hovertemplate="<b>영화명: %{hovertext}</b><br>총 관객수: %{y:,}명<extra></extra>"
    )
    
    fig_box.update_layout(
        legend_title_text="장르",
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("영화 편수가 10편 이상인 주요 장르 대부분은 중간값(중앙값)이 낮게 형성되어 있으나, 일부 초대형 흥행작(상자 밖의 이상치)들이 해당 장르의 최고 흥행 실적을 이끌고 있음을 보여줍니다.")
    
except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다: {e}")
'''

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_py_content_v5)

print("Fifth graph added to main.py successfully.")
