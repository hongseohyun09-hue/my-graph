import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("365일간의 일별 박스오피스 데이터를 시간의 흐름에 따라 살펴봅니다.")

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜: 하이픈 없는 8자리 숫자를 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d", errors="coerce")

    # 숫자형 열 변환
    numeric_cols = ["순위", "영화코드", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["날짜", "영화명"]).sort_values(["날짜", "순위"])


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.info(f"오류 내용: {e}")
    st.stop()


# ============================================================
# 그래프 1
# ============================================================
st.header("1. 영화별 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique().tolist())

if not movie_list:
    st.warning("영화 데이터가 없습니다.")
    st.stop()

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list,
    key="movie_selector",
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    height=500,
    margin=dict(l=20, r=20, t=60, b=20),
    yaxis=dict(tickformat=","),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("선택한 영화의 일별 관객 수가 시간에 따라 어떻게 증가하거나 감소했는지 확인할 수 있습니다.")


# ============================================================
# 그래프 2
# ============================================================
st.divider()
st.header("2. 일관객 합계가 가장 큰 영화 5편")

# 전체 기간 동안 영화별 일관객을 합산하여 상위 5편 선정
top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = df[df["영화명"].isin(top5_movies)].copy()

# 날짜 × 영화 형태로 만들어 한 그래프에 5개 선을 표시
top5_daily = (
    top5_df.groupby(["날짜", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values(["날짜", "영화명"])
)

fig2 = px.line(
    top5_daily,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "영화명": True,
        "일관객": ":,",
    },
)

fig2.update_traces(
    hovertemplate="영화: %{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    height=600,
    margin=dict(l=20, r=20, t=60, b=20),
    yaxis=dict(tickformat=","),
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    ),
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("이 기간 동안 일관객 합계가 가장 큰 5편의 관객 수가 날짜에 따라 어떻게 변했는지 비교할 수 있습니다.")


# ============================================================
# 앞으로 추가할 그래프 영역
# ============================================================
st.divider()
st.header("3. 다음 그래프")
st.caption("앞으로 시간에 따른 다른 영화 데이터 그래프를 이 구역에 추가할 수 있습니다.")

# 그래프를 추가할 때 아래와 같은 형식으로 구역을 계속 확장하면 됩니다.
# st.subheader("3-1. 그래프 제목")
# st.plotly_chart(...)
# st.markdown("**이 그래프로 알 수 있는 것:**")
# st.info("그래프에서 알 수 있는 내용을 한 문장으로 적습니다.")

st.divider()
st.caption("데이터 출처: KOBIS 일별 박스오피스 데이터")
