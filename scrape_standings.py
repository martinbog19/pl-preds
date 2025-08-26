from datetime import datetime
import pandas as pd

from helpers.ref import NAMES
from helpers.scrape import scrape_standings
from helpers.eval import eval_preds



today = datetime.now().date()


standings = scrape_standings()
standings.to_csv('standings.csv', index=False, header=False, mode='a')


res_list = []
for name in NAMES:

    with open(f'predictions/{name}.txt', 'r') as f:
        preds = f.read().splitlines()

    res_list.append(eval_preds(standings, preds))

metrics = pd.concat(res_list)
metrics.insert(0, 'name', NAMES)

metrics['rank'] = metrics.sort_values(
    ["total_diff", "total_perf", "worst_by", "name"],
    ascending=[True, False, True, True]
).reset_index(drop=True).index + 1

metrics.insert(0, 'date', today)

metrics.to_csv('metrics.csv', index=False, header=False, mode='a')