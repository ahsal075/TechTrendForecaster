import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="Tech Course Demand & Market Trend Forecaster", layout="wide")

st.title("📊 Tech Course Demand & Market Trend Forecaster")
st.write("Analyze real-world job trends and public learning interest for popular tech skills.")

# -------- Load datasets --------
@st.cache_data
def load_data():
    jobs = pd.read_csv("real_remoteok_jobs.csv")
    trends = pd.read_csv("google_trends_data.csv")
    trends["date"] = pd.to_datetime(trends["date"])
    return jobs, trends

jobs, trends = load_data()

# -------- Job demand visualization --------
st.subheader("💼 Job Market Demand (From RemoteOK)")

cnt = Counter()
for tags in jobs["tags"].fillna(""):
    for t in [x.strip().lower() for x in tags.split(",") if x.strip()]:
        cnt[t] += 1

top_skills = pd.DataFrame(cnt.most_common(15), columns=["Skill", "Count"])
fig_jobs = px.bar(
    top_skills.sort_values("Count", ascending=True),
    x="Count", y="Skill", orientation="h",
    title="Top 15 In-demand Skills in Job Postings",
    color="Count", color_continuous_scale="Blues"
)
st.plotly_chart(fig_jobs, use_container_width=True)

# -------- Google Trends visualization --------
st.subheader("🌍 Google Trends: Public Learning Interest")

skills = [c for c in trends.columns if c not in ["date", "isPartial"]]
selected_skill = st.selectbox("Select a skill to analyze:", skills)

fig_trend = px.line(
    trends, x="date", y=selected_skill,
    title=f"Google Trends Interest for '{selected_skill.title()}' (Past 12 Months)",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

# -------- Forecast with Prophet (Safe version) --------
st.subheader("🔮 Forecast (Next 6 Months)")

try:
    from prophet import Prophet
    import cmdstanpy
    try:
        cmdstanpy.set_cmdstan_path("/home/adminuser/.cmdstanpy")
    except Exception:
        pass

    dfp = trends[["date", selected_skill]].rename(columns={"date": "ds", selected_skill: "y"})
    model = Prophet()
    model.fit(dfp)
    future = model.make_future_dataframe(periods=6, freq="M")
    fcst = model.predict(future)

    fig2 = model.plot(fcst, xlabel="Date", ylabel="Interest")
    plt.title(f"Forecast for '{selected_skill.title()}' Interest (Next 6 Months)")
    st.pyplot(fig2)

except Exception as e:
    st.error("⚠️ Forecasting failed due to environment limits or backend errors.")
    st.info("Prophet model can take time to compile. Try reloading after a few minutes.")
    st.caption(f"Error details: {e}")

# -------- Summary --------
st.markdown("### 📈 Summary Insights")
st.write(f"- **'{selected_skill.title()}'** current average trend score: {trends[selected_skill].mean():.2f}")
st.write(f"- **Job skill diversity:** {len(top_skills)} top skills identified")
st.write("Data sourced from RemoteOK & Google Trends (collected in real-time).")

st.info("✅ Dashboard ready — update the CSVs anytime to refresh results!")

# -------- Smart Recommendation System --------
st.subheader("🎓 Smart Course Recommendation")

skill_lower = selected_skill.lower()

if skill_lower in ["python", "data science"]:
    st.success("📘 Recommended Path: Learn 'Data Science with Python' and progress toward 'Machine Learning Foundations'.")
elif skill_lower in ["cloud computing"]:
    st.success("☁️ Recommended Path: Take 'AWS Cloud Practitioner' or 'Azure Fundamentals' certifications.")
elif skill_lower in ["artificial intelligence"]:
    st.success("🧠 Recommended Path: Try 'AI Fundamentals' or 'Deep Learning Specialization' courses.")
elif skill_lower in ["machine learning"]:
    st.success("🤖 Recommended Path: Explore 'ML with Scikit-Learn' and 'TensorFlow Developer' paths.")
else:
    st.info("🔍 Explore beginner-level courses on Coursera or Udemy to build expertise in this trending area.")
