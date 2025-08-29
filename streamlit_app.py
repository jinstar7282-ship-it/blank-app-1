#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Titanic Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
    color: white; /* ✅ 텍스트 색상을 흰색으로 변경 */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white; /* ✅ Label 텍스트도 흰색으로 */
}

[data-testid="stMetricValue"] {
  color: white; /* ✅ 값(숫자) 흰색 */
  font-weight: bold;
}

[data-testid="stMetricDelta"] {
  color: white !important; /* ✅ Delta(증감률)도 흰색 */
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv')

#######################
# Sidebar
with st.sidebar:
    st.title("⚙️ 분석 조건 선택")

    # Pclass (객실 등급)
    pclass_options = df_reshaped["Pclass"].unique()
    selected_pclass = st.multiselect(
        "객실 등급 (Pclass) 선택", 
        options=sorted(pclass_options),
        default=sorted(pclass_options)
    )

    # Sex (성별)
    sex_options = df_reshaped["Sex"].unique()
    selected_sex = st.multiselect(
        "성별 선택", 
        options=sex_options,
        default=sex_options
    )

    # Embarked (출항지)
    embarked_options = df_reshaped["Embarked"].dropna().unique()
    selected_embarked = st.multiselect(
        "출항지 (Embarked) 선택", 
        options=embarked_options,
        default=embarked_options
    )

    # 분석 지표 선택
    analysis_metric = st.selectbox(
        "분석 지표 선택",
        ["생존율 분석", "요금(Fare) 분석", "나이(Age) 분포 분석"]
    )

# 필터링된 데이터 만들기
filtered_df = df_reshaped[
    (df_reshaped["Pclass"].isin(selected_pclass)) &
    (df_reshaped["Sex"].isin(selected_sex)) &
    (df_reshaped["Embarked"].isin(selected_embarked))
]

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown("### 📊 요약 정보")

    # 총 탑승객 수
    total_passengers = len(filtered_df)
    st.metric("총 탑승객 수", f"{total_passengers} 명")

    # 생존자 수 & 비율
    survived_count = filtered_df["Survived"].sum()
    survival_rate = (survived_count / total_passengers * 100) if total_passengers > 0 else 0
    st.metric("생존자 수", f"{survived_count} 명", f"{survival_rate:.1f}%")

    # 평균 나이
    avg_age = filtered_df["Age"].mean()
    st.metric("평균 나이", f"{avg_age:.1f} 세" if pd.notnull(avg_age) else "데이터 없음")

    # 평균 요금(Fare)
    avg_fare = filtered_df["Fare"].mean()
    st.metric("평균 요금", f"${avg_fare:.2f}" if pd.notnull(avg_fare) else "데이터 없음")

with col[1]:
    st.markdown("### 📈 시각화")

    # 1. 생존율 비교 (Pclass × Sex)
    st.subheader("생존율 비교")
    survival_rate_df = (
        filtered_df.groupby(["Pclass", "Sex"])["Survived"]
        .mean()
        .reset_index()
    )
    survival_rate_df["Survived"] *= 100

    bar_chart = alt.Chart(survival_rate_df).mark_bar().encode(
        x=alt.X("Pclass:N", title="객실 등급"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Sex:N",
        column="Sex:N",
        tooltip=["Pclass", "Sex", alt.Tooltip("Survived:Q", format=".1f")]
    ).properties(width=120, height=300)

    st.altair_chart(bar_chart, use_container_width=True)

    # 2. 나이 분포
    st.subheader("나이 분포")
    age_hist = px.histogram(
        filtered_df,
        x="Age",
        nbins=20,
        color="Sex",
        title="연령 분포 (성별 기준)"
    )
    st.plotly_chart(age_hist, use_container_width=True)

    # 3. 요금 분포
    st.subheader("요금 분포")
    fare_box = px.box(
        filtered_df,
        x="Pclass",
        y="Fare",
        color="Sex",
        title="요금 분포 (등급 & 성별 기준)"
    )
    st.plotly_chart(fare_box, use_container_width=True)

with col[2]:
    st.markdown("### 🔎 상세 분석 & 설명")

    # 생존율 상위 그룹
    st.subheader("생존율 상위 그룹")
    group_survival = (
        filtered_df.groupby(["Pclass", "Sex"])["Survived"]
        .mean()
        .reset_index()
    )
    group_survival["Survived"] *= 100
    top_groups = group_survival.sort_values("Survived", ascending=False).head(3)

    for _, row in top_groups.iterrows():
        st.write(
            f"➡️ **{row['Sex']} / {row['Pclass']}등급** : 생존율 {row['Survived']:.1f}%"
        )

    # 생존율 하위 그룹
    st.subheader("생존율 하위 그룹")
    bottom_groups = group_survival.sort_values("Survived", ascending=True).head(3)

    for _, row in bottom_groups.iterrows():
        st.write(
            f"❌ **{row['Sex']} / {row['Pclass']}등급** : 생존율 {row['Survived']:.1f}%"
        )

    # About
    st.subheader("ℹ️ About")
    st.markdown("""
    - **데이터 출처**: [Kaggle Titanic Dataset](https://www.kaggle.com/c/titanic)
    - **변수 설명**  
      - `Pclass`: 객실 등급 (1=1등석, 2=2등석, 3=3등석)  
      - `Sex`: 성별 (male, female)  
      - `Age`: 나이  
      - `Fare`: 운임 요금  
      - `Embarked`: 탑승 항구 (C=프랑스 셰르부르, Q=아일랜드 퀸스타운, S=영국 사우샘프턴)  
      - `Survived`: 생존 여부 (0=사망, 1=생존)  
    """)
