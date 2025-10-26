import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from collections import Counter
import os
# Enable inline plotting for VS Code interactive window (only if running in IPython)
ip = globals().get("get_ipython")
if callable(ip):
    try:
        ip().run_line_magic('matplotlib', 'inline')
    except Exception:
        pass


# --------- Part 1: Job data analysis ---------
jobs_path = "real_remoteok_jobs.csv"
if not os.path.exists(jobs_path):
    raise SystemExit("❌ Missing real_remoteok_jobs.csv — run collect_remote_jobs.py first.")

jobs = pd.read_csv(jobs_path)
print(f"✅ Loaded {len(jobs)} job records.")

jobs["tags"] = jobs["tags"].fillna("").astype(str)

cnt = Counter()
for tags in jobs["tags"]:
    for t in [x.strip().lower() for x in tags.split(",") if x.strip()]:
        cnt[t] += 1

top = pd.DataFrame(cnt.most_common(15), columns=["Skill", "Count"])
print("\n🔥 Top 15 in-demand skills from job data:")
print(top)

plt.figure(figsize=(10,5))
plt.barh(top["Skill"].head(10)[::-1], top["Count"].head(10)[::-1], color="skyblue")
plt.title("Top 10 Skills in Job Listings")
plt.tight_layout()
plt.show()

# --------- Part 2: Google Trends analysis ---------
trends_path = "google_trends_data.csv"
if not os.path.exists(trends_path):
    raise SystemExit("❌ Missing google_trends_data.csv.")

tr = pd.read_csv(trends_path)
tr["date"] = pd.to_datetime(tr["date"])
skills = [c for c in tr.columns if c not in ["date", "isPartial"]]

print("\n📈 Google Trends columns:", skills)
tr.set_index("date")[skills].plot(figsize=(12,6), marker="o")
plt.title("Google Trends (Last 12 Months)")
plt.ylabel("Interest (0–100)")
plt.show()

# --------- Part 3: Forecast with Prophet ---------
skill = "python"  # choose which skill to forecast
dfp = tr[["date", skill]].rename(columns={"date": "ds", skill: "y"})

model = Prophet()
model.fit(dfp)
future = model.make_future_dataframe(periods=6, freq="M")
fcst = model.predict(future)

model.plot(fcst)
plt.title(f"Forecast for '{skill.title()}' Interest (Next 6 Months)")
plt.show()

top.to_csv("top_skills_from_jobs.csv", index=False)
fcst[["ds","yhat","yhat_lower","yhat_upper"]].tail(6).to_csv("forecast_sample_python.csv", index=False)
print("\n✅ Saved: top_skills_from_jobs.csv and forecast_sample_python.csv")
