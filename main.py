import streamlit as st
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
    
    # genre: 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 추출
    if 'genre' in df.columns:
        df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if x and x != 'nan' else '기타')
        
    return df

try:
    df = load_data()
    
    # 사이드바 데이터 정보
    st.sidebar.header("🔍 데이터 정보")
    st.sidebar.metric("분석 영화 총 편수", f"{len(df)} 편")
    
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
    
    # 이 그래프로 알 수 있는 것 구역
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("특정 주요 장르에 상업 영화 개봉이 집중되어 있으며, 비주류 장르와의 편수 차이가 극명함을 확인할 수 있습니다.")
    st.divider()

    # -------------------------------------------------------------------------
    # 두 번째 그래프: 개봉일 스크린수와 관객수의 관계 (산점도)
    # -------------------------------------------------------------------------
    st.header("2. 개봉일 스크린수와 총 관객수의 관계")
    
    fig_scatter = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        size='first_show',
        labels={
            'first_scrn': '개봉일 스크린수',
            'total_audi': '총 관객수',
            'genre': '장르',
            'first_show': '개봉일 상영횟수'
        },
        title="개봉일 스크린수 vs 총 관객수 (점 크기: 개봉일 상영횟수)"
    )
    fig_scatter.update_traces(hovertemplate="<b>%{hovertext}</b><br>스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.info("개봉일 스크린수와 상영횟수가 많이 확보될수록 총 누적 관객수가 증가하는 강한 양의 상관관계가 나타납니다.")
    st.divider()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
