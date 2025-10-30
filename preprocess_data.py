import pandas as pd

# Load datasets
print("Loading data...")
trends = pd.read_csv('google_trends_data.csv')
jobs = pd.read_csv('real_jobs_data.csv')

print("Cleaning and merging data...")

# Basic cleaning
trends.columns = trends.columns.str.strip()
jobs.columns = jobs.columns.str.strip()

# Drop duplicates
trends.drop_duplicates(inplace=True)
jobs.drop_duplicates(inplace=True)

# Merge on the date column if available
if 'date' in trends.columns and 'date' in jobs.columns:
    merged = pd.merge(trends, jobs, on='date', how='outer')
else:
    print("No common 'date' column found. Saving separately.")
    merged = pd.concat([trends, jobs], axis=1)

# Save the cleaned data
merged.to_csv('cleaned_data.csv', index=False)
print("✅ Data preprocessing complete! Saved as 'cleaned_data.csv'")
