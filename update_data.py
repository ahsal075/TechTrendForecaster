import os
import pandas as pd
from datetime import datetime
import subprocess

def update_data():
    print("🚀 Starting data update process...")

    # Step 1: Run your data collection scripts
    scripts = ["collect_jobs.py", "collect_real_data.py", "collect_remote_jobs.py"]
    for script in scripts:
        if os.path.exists(script):
            print(f"▶ Running {script}...")
            subprocess.run(["python", script], check=True)
        else:
            print(f"⚠️ {script} not found, skipping.")

    # Step 2: Optionally run analysis/forecast script
    if os.path.exists("analyze_and_forecast.py"):
        print("📈 Running data analysis and forecasting...")
        subprocess.run(["python", "analyze_and_forecast.py"], check=True)
    else:
        print("⚠️ analyze_and_forecast.py not found, skipping.")

    # Step 3: Log update timestamp
    log_data = {
        "timestamp": [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
        "message": ["Data pipeline executed successfully!"]
    }
    pd.DataFrame(log_data).to_csv("update_log.csv", index=False)
    print("✅ update_log.csv updated successfully!")

if __name__ == "__main__":
    update_data()
