# collect_remote_jobs.py
import requests
import pandas as pd
import os

# Try 1: fetch a stable GitHub-hosted mirror of remote jobs
GITHUB_URL = "https://raw.githubusercontent.com/remoteintech/remote-jobs/master/remote-jobs.json"
OUTFILE = "real_remoteok_jobs.csv"

def fetch_from_github(url):
    print("➡️ Fetching jobs JSON from GitHub mirror...")
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    return r.json()

def normalize_and_save(data, outpath):
    jobs = []
    for item in data:
        # Ensure keys exist and coerce to strings
        company = item.get("company") or item.get("company_name") or ""
        position = item.get("position") or item.get("title") or ""
        tags = item.get("tags") or item.get("job_types") or []
        if isinstance(tags, list):
            tags_str = ", ".join(tags)
        else:
            tags_str = str(tags)
        url = item.get("url") or item.get("apply_url") or ""
        date = item.get("date") or item.get("created_at") or ""
        jobs.append({
            "date": date,
            "company": company,
            "position": position,
            "tags": tags_str,
            "url": url
        })
    df = pd.DataFrame(jobs)
    df.to_csv(outpath, index=False)
    print(f"✅ Saved {len(df)} rows to {outpath}")

def main():
    outpath = os.path.join(os.getcwd(), OUTFILE)
    try:
        data = fetch_from_github(GITHUB_URL)
        normalize_and_save(data, outpath)
    except Exception as e:
        print("⚠️ GitHub fetch failed:", type(e).__name__, e)
        # Fallback: try remoteok.com (may need verify=False in restricted environments)
        try:
            print("➡️ Trying RemoteOK (fallback)...")
            r = requests.get("https://remoteok.com/api", headers={"User-Agent":"Mozilla/5.0"}, timeout=20, verify=False)
            r.raise_for_status()
            data = r.json()
            normalize_and_save(data, outpath)
        except Exception as e2:
            print("❌ Fallback also failed:", type(e2).__name__, e2)
            print("Please check network / proxy or run the script where internet is allowed.")

if __name__ == "__main__":
    main()
