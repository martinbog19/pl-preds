from datetime import datetime
import pandas as pd
import json

from helpers.ref import NAMES
from helpers.scrape import scrape_standings
from helpers.eval import eval_preds

with open('helpers/abbr.json') as f:
    abbr_map = json.load(f)

today = datetime.now().date()

standings = scrape_standings(abbr_map)
standings.to_csv('standings.csv', index=False, header=False, mode='a')


res_list = []
for name in NAMES:

    with open(f'predictions/{name.lower()}.txt', 'r') as f:
        preds = f.read().splitlines()

    res_list.append(eval_preds(standings, preds))

metrics = pd.concat(res_list)
metrics.insert(0, 'name', NAMES)

metrics = pd.concat(res_list)
metrics.insert(0, 'name', NAMES)
metrics = metrics.sort_values(
    ["total_diff", "total_perf", "worst_by", "name"],
    ascending=[True, False, True, True],
).reset_index(drop=True)
metrics['rank'] = metrics.index + 1

metrics.insert(0, 'date', today)

metrics.to_csv('metrics.csv', index=False, header=False, mode='a')