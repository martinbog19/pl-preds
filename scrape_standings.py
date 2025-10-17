from datetime import datetime
import pandas as pd

from src.ref import NAMES
from src.scrape import get_scraper
from src.eval import eval_preds


today = datetime.now().date()

league = "prem"

scraper = get_scraper(league)
standings = scraper.scrape_standings()
standings.to_csv("data/standings.csv", index=False, header=False, mode="a")


evaluator = get_evaluator(league)

metrics = evaluator.compute_metrics(
    NAMES
)


for conf, conf_standings in standings.groupby("Conference"):

    res_list = []
    for name in NAMES:

        with open(f"predictions/{league}/{conf}/{name.lower()}.txt", "r") as f:
            preds = f.read().splitlines()

        res_list.append(
            eval_preds(conf_standings, preds)
        )

    metrics = pd.concat(res_list)
    metrics.insert(0, "name", NAMES)

    metrics = metrics.sort_values(
        ["total_diff", "total_perf", "worst_by", "name"],
        ascending=[True, False, True, True],
    ).reset_index(drop=True)
    metrics["rank"] = metrics.index + 1

    metrics.insert(0, "Conference", conf)
    metrics.insert(0, "date", today)

    metrics.to_csv(f"data/{league}/metrics.csv", index=False, header=False, mode="a")