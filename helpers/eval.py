import pandas as pd
import numpy as np



def eval_preds(
        standings: pd.DataFrame,
        preds: list[str],
) -> pd.DataFrame:
    
    standings = standings.sort_values('Rk').copy()

    standings['pred'] = preds
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
            'total_diff': [total_diff],
            'total_perf': [total_perf],
            'worst_tms': [worst_tms],
            'worst_by': [worst_by],
            'worst_bys': [worst_bys],
            'perfect_tms': [perfect_tms],
            'perfect_pos': [perfect_pos],
        }
    )