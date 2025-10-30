import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# Random User-Agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

ROLES = [
    "python developer",
    "data scientist",
    "ai engineer",
    "cloud engineer",
    "machine learning engineer"
]

print("🔍 Collecting real job listings from Google Jobs...")

all_jobs = []

for role in ROLES:
    print(f"\nFetching jobs for: {role}")
    query = role.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}+jobs"

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        job_elements = soup.select("div.BjJfJf.PUpOsf")
        if not job_elements:
            print(f"⚠️  No job elements found for {role}.")
        else:
            for job in job_elements:
                title = job.select_one("div.BjJfJf.PUpOsf")
                company = job.select_one("div.vNEEBe")
                location = job.select_one("div.Qk80Jf")
                if title and company:
                    all_jobs.append({
                        "role": role,
                        "title": title.text.strip(),
                        "company": company.text.strip(),
                        "location": location.text.strip() if location else ""
                    })
            print(f"✅ Found {len(job_elements)} listings for {role}")

        # Sleep between requests to avoid IP blocking
        time.sleep(random.uniform(3, 6))

    except Exception as e:
        print(f"❌ Error fetching {role}: {e}")

# If no jobs found, fallback to RemoteOK
if not all_jobs:
    print("\n⚠️ No jobs collected from Google. Trying RemoteOK as fallback...")
    try:
        r = requests.get("https://remoteok.com/api", headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=15, verify=False)
        data = r.json()
        for job in data:
            if isinstance(job, dict) and "position" in job:
                all_jobs.append({
                    "role": "remote job",
                    "title": job.get("position"),
                    "company": job.get("company"),
                    "location": job.get("location", ""),
                })
        print(f"✅ Fallback successful. Collected {len(all_jobs)} jobs from RemoteOK.")
    except Exception as e:
        print(f"❌ Fallback failed: {e}")

# Save results
if all_jobs:
    df = pd.DataFrame(all_jobs)
    df.to_csv("real_jobs_data.csv", index=False)
    print(f"\n💾 Saved {len(df)} jobs to real_jobs_data.csv")
else:
    print("\n⚠️ Still no jobs found. Try using a VPN or different IP.")
