import feedparser
import pandas as pd

skills = ["python developer", "data scientist", "ai engineer",
          "cloud engineer", "machine learning"]

all_jobs = []

for skill in skills:
    print(f"🔍 Collecting jobs for: {skill}")
    url = f"https://www.careerjet.in/search/rss?s={skill.replace(' ', '+')}&l=india"
    feed = feedparser.parse(url)

    for entry in feed.entries:
        all_jobs.append({
            "skill": skill,
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })

df = pd.DataFrame(all_jobs)
print(f"\n✅ Total jobs collected: {len(df)}")
df.to_csv("real_jobs_data.csv", index=False)
print("💾 Saved as real_jobs_data.csv")
