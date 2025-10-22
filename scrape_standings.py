from datetime import datetime
import os

from src.ref import VARS
from src.scrape import get_scraper
from src.eval import get_evaluator


league = os.getenv("LEAGUE")
assert league, f"Please specify league to scrape!"


today = datetime.now().date()

names = VARS[league]["players"]

scraper = get_scraper(league)
standings = scraper.scrape_standings()
standings.to_csv(f"data/{league}/standings.csv", index=False, header=False, mode="a")


evaluator = get_evaluator(league, standings)

metrics = evaluator.evaluate(names)
metrics.insert(0, "date", today)

if league == "prem":
    metrics.drop(columns="spearmanr", inplace=True)

metrics.to_csv(f"data/{league}/metrics.csv", index=False, header=False, mode="a")