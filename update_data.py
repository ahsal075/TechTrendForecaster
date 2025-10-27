import pandas as pd
from datetime import datetime

# Example: create or update a CSV file with a timestamp
def update_data():
    data = {
        "timestamp": [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
        "message": ["Data updated successfully!"]
    }
    df = pd.DataFrame(data)
    df.to_csv("update_log.csv", index=False)
    print("✅ update_log.csv updated successfully!")

if __name__ == "__main__":
    update_data()
