from datetime import datetime
import pandas as pd
import os

from src.ref import PLAYERS
from src.scrape import get_scraper
from src.eval import get_evaluator


league = os.getenv("LEAGUE")


today = datetime.now().date()

names = PLAYERS[league]

scraper = get_scraper(league)
standings = scraper.scrape_standings()
standings.to_csv(f"data/{league}/standings.csv", index=False, header=False, mode="a")


evaluator = get_evaluator(league)

metrics = evaluator.evaluate(names)
metrics.insert(0, "date", today)

if league == "prem":
    metrics.drop(columns="spearmanr", inplace=True)

metrics.to_csv(f"data/{league}/metrics.csv", index=False, header=False, mode="a")