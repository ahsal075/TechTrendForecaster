import os
import requests
import pandas as pd
from pytrends.request import TrendReq
import certifi

# --- proxy & CA handling ---
# Optionally set CORPORATE_CA to path of your proxy CA cert (PEM). Example:
# $env:CORPORATE_CA = "C:\path\corp_proxy_ca.pem"  (PowerShell)
corp_ca = os.environ.get("CORPORATE_CA")  # path to corporate CA (optional)
base_cert = certifi.where()
verify_path = base_cert

if corp_ca and os.path.exists(corp_ca):
    combined = os.path.expanduser(os.path.join("~", ".certs", "combined_certs.pem"))
    os.makedirs(os.path.dirname(combined), exist_ok=True)
    # create combined bundle (certifi + corporate CA)
    with open(base_cert, "rb") as bf, open(corp_ca, "rb") as cf, open(combined, "wb") as out:
        out.write(bf.read())
        out.write(b"\n")
        out.write(cf.read())
    verify_path = combined
    os.environ["REQUESTS_CA_BUNDLE"] = combined
    os.environ["SSL_CERT_FILE"] = combined

# Read proxy from environment (set in PowerShell for current session):
# $env:HTTPS_PROXY='http://user:pass@proxy:port'
# $env:HTTP_PROXY='http://user:pass@proxy:port'
https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
proxies = None
if https_proxy or http_proxy:
    proxies = {}
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy

# If you want to bypass the proxy specifically for remoteok:
no_proxy = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
# Add remoteok.com to NO_PROXY for this process only
os.environ.setdefault("NO_PROXY", (no_proxy + ",remoteok.com") if no_proxy else "remoteok.com")

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
        verify=verify_path,
        proxies=proxies
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
except requests.exceptions.SSLError as ssl_err:
    print(f"⚠️ SSL verification failed: {ssl_err}.")
    print(" - If you are behind a corporate proxy, set CORPORATE_CA to your proxy CA PEM and retry.")
    print(" - For testing you can set verify=False (insecure) but corporate proxies often return 403 blocking pages.")
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
        requests_args={"verify": verify_path, "proxies": proxies, "headers": {"User-Agent": "Mozilla/5.0"}}
    )
    skills = ["python", "data science", "artificial intelligence", "cloud computing", "machine learning"]
    pytrend.build_payload(kw_list=skills, timeframe="today 12-m")
    trend_data = pytrend.interest_over_time().reset_index()
    trend_data.to_csv("google_trends_data.csv", index=False)
    print("✅ Google Trends data collected and saved as google_trends_data.csv")
except Exception as e:
    print(f"❌ Failed to collect Google Trends data: {e}")

print("\n🎉 Real data collection complete! Files ready:")
print(" - real_remoteok_jobs.csv  (job market demand)")
print(" - google_trends_data.csv  (public learning interest)")

# Additional test request to RemoteOK API
try:
    r = requests.get("https://remoteok.com/api",
                     headers={"User-Agent":"Mozilla/5.0"},
                     verify=r"C:\temp\corp_proxy_ca.pem",
                     timeout=15)
    print("status:", r.status_code)
    print(r.text[:200])
except Exception as e:
    print("error:", type(e).__name__, e)