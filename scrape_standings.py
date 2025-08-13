import numpy as np
from datetime import date

from ref import NAMES
from helpers.scrape import scrape_standings



today = date.today()
RESULTS_PATH = 'results.csv'


standings = scrape_standings()


for name in NAMES:

    with open(f'predictions/{name.lower()}.txt', 'r') as f:
        preds = [line.strip() for line in f.readlines()]

    standings[f'pred_{name.lower()}'] = preds

    standings[f'diff_{name.lower()}'] = [np.abs(np.where(standings[f'pred_{name.lower()}'] == tm)[0][0] - idx) for tm, idx in zip(standings.actual, standings.index)]
    standings[f'perf_{name.lower()}'] = (standings[f'diff_{name.lower()}'] == 0).astype(int)

standings.to_csv(RESULTS_PATH, index=False, header=False, mode='a')