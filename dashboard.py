import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from collections import Counter
import logging

# Disable verbose Stan logs (for Streamlit Cloud stability)
logging.getLogger("cmdstanpy").disabled = True

# ---------- Streamlit Page Config ----------
st.set_page_config(
    page_title="Tech Course Demand & Market Trend Forecaster",
    layout="wide"
)

st.title("📊 Tech Course Demand & Market Trend Forecaster")
st.write("Analyze real-world job trends and public learning interest for popular tech skills.")

# ---------- Load Data ----------
try:
    jobs = pd.read_csv("real_remoteok_jobs.csv")
    trends = pd.read_csv("google_trends_data.csv")
    trends["date"] = pd.to_datetime(trends["date"])
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ---------- Job Market Demand ----------
st.subheader("💼 Job Market Demand (From RemoteOK)")

cnt = Counter()
for tags in jobs["tags"].fillna(""):
    for t in [x.strip().lower() for x in tags.split(",") if x.strip()]:
        cnt[t] += 1

top_skills = pd.DataFrame(cnt.most_common(15), columns=["Skill", "Count"])

fig_jobs = px.bar(
    top_skills.sort_values("Count", ascending=True),
    x="Count",
    y="Skill",
    orientation="h",
    title="Top 15 In-demand Skills in Job Postings",
    color="Count",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_jobs, use_container_width=True)

# ---------- Google Trends ----------
st.subheader("🌍 Google Trends: Public Learning Interest")

skills = [c for c in trends.columns if c not in ["date", "isPartial"]]
selected_skill = st.selectbox("Select a skill to analyze:", skills)

fig_trend = px.line(
    trends,
    x="date",
    y=selected_skill,
    title=f"Google Trends Interest for '{selected_skill.title()}' (Past 12 Months)",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------- Forecasting (Prophet) ----------
st.subheader("🔮 Forecast (Next 6 Months)")

dfp = trends[["date", selected_skill]].rename(columns={"date": "ds", selected_skill: "y"})

try:
    from prophet import Prophet
    model = Prophet()
    model.fit(dfp)

    future = model.make_future_dataframe(periods=6, freq="M")
    fcst = model.predict(future)

    fig2 = model.plot(fcst, xlabel="Date", ylabel="Interest")
    plt.title(f"Forecast for '{selected_skill.title()}' Interest (Next 6 Months)")
    st.pyplot(fig2)

except Exception as e:
    st.error(f"⚠️ Forecasting failed due to a backend issue: {e}")
    st.info("Tip: Prophet may fail to initialize if the cmdstanpy backend is missing or misconfigured.")
    st.stop()

# ---------- Summary ----------
st.markdown("### 📈 Summary Insights")
st.write(f"- **'{selected_skill.title()}'** current average trend score: {dfp['y'].mean():.2f}")
st.write(f"- **Job skill diversity:** {len(top_skills)} top skills identified")
st.write("Data sourced from RemoteOK & Google Trends (collected in real-time).")

st.info("✅ Dashboard ready — you can update the CSVs anytime to refresh results!")

# ---------- Smart Recommendations ----------
st.subheader("🎓 Smart Course Recommendation")

if selected_skill.lower() in ["python", "data science"]:
    st.success("📘 Recommended Path: Learn 'Data Science with Python' and progress toward 'Machine Learning Foundations'.")
elif selected_skill.lower() in ["cloud computing"]:
    st.success("☁️ Recommended Path: Take 'AWS Cloud Practitioner' or 'Azure Fundamentals' certifications.")
elif selected_skill.lower() in ["artificial intelligence"]:
    st.success("🧠 Recommended Path: Try 'AI Fundamentals' or 'Deep Learning Specialization' courses.")
elif selected_skill.lower() in ["machine learning"]:
    st.success("🤖 Recommended Path: Explore 'ML with Scikit-Learn' and 'TensorFlow Developer' paths.")
else:
    st.info("🔍 Explore beginner-level courses on Coursera or Udemy to build expertise in this trending area.")
