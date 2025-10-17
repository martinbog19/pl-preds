import pandas as pd
import numpy as np
from scipy.stats import spearmanr



def eval_preds(
    standings: pd.DataFrame,
    preds: list[str],
) -> pd.DataFrame:
    
    standings = standings.sort_values('Rk').reset_index(drop=True).copy()
    standings['pred'] = preds

    teams = standings["Team"].tolist()
    actuals = {tm: rk for tm, rk in zip(standings["Team"], standings["Rk"])}
    predicted = {tm: rk for tm, rk in zip(standings["pred"], standings["Rk"])}

    actual_ranks = [actuals[tm] for tm in teams]
    predicted_ranks = [predicted[tm] for tm in teams]

    rho = spearmanr(actual_ranks, predicted_ranks)

    standings['diff'] = [idx - np.where(standings['pred'] == tm)[0][0] for tm, idx in zip(standings['Team'], standings.index)]
    standings['asb_diff'] = standings['diff'].abs()
    standings['perf'] = (standings['diff'] == 0).astype(int)

    total_diff = standings['asb_diff'].sum()
    total_perf = standings['perf'].sum()

    worst_by = standings['asb_diff'].max()
    worsts = standings[
        standings['asb_diff'] == worst_by
    ]
    worst_tms = '_'.join(worsts['Team'].tolist())
    worst_bys = '_'.join(worsts['diff'].astype(str).tolist())

    perfects = standings[
        standings['diff'] == 0
    ]
    perfect_tms = '_'.join(perfects['Team'].tolist())
    perfect_pos = '_'.join(perfects['Rk'].astype(str).tolist())

    return pd.DataFrame(
        {
            "spearmanr": [rho.statistic],
            'total_diff': [total_diff],
            'total_perf': [total_perf],
            'worst_tms': [worst_tms],
            'worst_by': [worst_by],
            'worst_bys': [worst_bys],
            'perfect_tms': [perfect_tms],
            'perfect_pos': [perfect_pos],
        }
    )