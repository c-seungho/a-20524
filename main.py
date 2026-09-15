# -------------------------------------------------------------------------
# 여섯 번째 그래프: 버블 차트 (개봉 첫 주 관객수 크기 반영)
# -------------------------------------------------------------------------
st.header("6. 스크린수·총 관객수 및 첫 주 관객수 관계 (버블 차트)")

fig_bubble = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='genre',
    hover_name='movieNm',
    size_max=40,
    labels={
        'first_scrn': '개봉일 스크린수(개)',
        'total_audi': '총 관객수(명)',
        'first_week_audi': '개봉 첫 주 관객수(명)',
        'genre': '장르'
    },
    title="개봉일 스크린수 vs 총 관객수 (버블 크기: 개봉 첫 주 관객수)"
)

fig_bubble.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{marker.size:,}명<extra></extra>"
)

fig_bubble.update_layout(
    legend_title_text="장르",
    font=dict(size=14)
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.info("초기 스크린수 확보가 개봉 첫 주 관객수(버블 크기) 폭발로 이어지며, 이 첫 주 흥행 성공이 최종 관객수 도달에 절대적인 동력이 됨을 알 수 있습니다.")
