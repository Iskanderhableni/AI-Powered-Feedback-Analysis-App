from pandas import pd
from scraper.agoda_scraper import scrape_agoda_reviews

df = pd.DataFrame(all_reviews, columns=["review"])
df.to_csv("agoda_reviews.csv", index=False, encoding="utf-8-sig")