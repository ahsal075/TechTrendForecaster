import os
import requests
import pandas as pd
from pytrends.request import TrendReq
import certifi
from time import sleep

# -----------------------------
# PART 1: Fetch real job postings from RemoteOK
# -----------------------------
print("📡 Collecting real tech job data from RemoteOK...")

url = "https://remoteok.com/api"
try:
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15,
        verify=certifi.where()
    )
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for job in data:
        if isinstance(job, dict) and "position" in job:
            jobs.append({
                "date": job.get("date"),
                "company": job.get("company"),
                "position": job.get("position"),
                "tags": ", ".join(job.get("tags", []) or [])
            })

    jobs_df = pd.DataFrame(jobs)
    jobs_df.to_csv("real_remoteok_jobs.csv", index=False)
    print(f"✅ {len(jobs_df)} job postings collected and saved as real_remoteok_jobs.csv")
except Exception as e:
    print(f"❌ Failed to fetch job data from RemoteOK: {e}")

# -----------------------------
# PART 2: Fetch Google Trends (real learning interest)
# -----------------------------
print("\n🌍 Collecting Google Trends data...")
try:
    pytrend = TrendReq(
        hl="en-US",
        tz=360,
        requests_args={"verify": certifi.where(), "headers": {"User-Agent": "Mozilla/5.0"}}
    )
    skills = ["python", "data science", "artificial intelligence", "cloud computing", "machine learning"]
    
    # Delay to prevent hitting rate limits (HTTP 429)
    sleep(10)
    
    pytrend.build_payload(kw_list=skills, timeframe="today 12-m")
    trend_data = pytrend.interest_over_time().reset_index()
    trend_data.to_csv("google_trends_data.csv", index=False)
    print("✅ Google Trends data collected and saved as google_trends_data.csv")

except Exception as e:
    print(f"❌ Failed to collect Google Trends data: {e}")

print("\n🎉 Real data collection complete! Files ready:")
print(" - real_remoteok_jobs.csv  (job market demand)")
print(" - google_trends_data.csv  (public learning interest)")
