import pandas as pd
import numpy as np
import os
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



class PremEvaluator:

    def __init__(self, standings):
        
        self.standings = standings
        self.prediction_folder = "predictions/prem"

    def ev(self, names):

        res_list = []
        for name in names:

            prediction_path = os.path.join(self.prediction_folder, f"{name.lower().txt}")
            with open(prediction_path, "r") as f:
                preds = f.read().splitlines()

            res_list.append(
                eval_preds(self.standings, preds)
            )

        metrics = pd.concat(res_list)
        metrics.insert(0, "name", names)

        metrics = metrics.sort_values(
            ["spearmanr", "total_perf", "total_diff", "worst_by", "name"],
            ascending=[True, True, False, True, True],
        ).reset_index(drop=True)
        metrics["rank"] = metrics.index + 1

        return metrics



class NBAEvaluator:

    def __init__(self, standings):
        
        self.standings = standings
        self.prediction_folder = "predictions/nba"

    def ev(self, names):
        
        metrics_list = []
        for conf in ["East", "West"]:

            conf_standings = self.standings.copy()
            conf_standings = conf_standings[
                conf_standings["Conference"] == conf
            ]
        
            res_list = []
            for name in names:

                prediction_path = os.path.join(self.prediction_folder, conf.lower(), f"{name.lower()}.txt")
                with open(prediction_path, "r") as f:
                    preds = f.read().splitlines()

                res_list.append(
                    eval_preds(conf_standings, preds)
                )

            conf_metrics = pd.concat(res_list)
            conf_metrics.insert(0, "name", names)
            conf_metrics["conference"] = conf
            metrics_list.append(conf_metrics)

            # metrics = metrics.sort_values(
            #     ["spearmanr", "total_perf", "total_diff", "worst_by", "name"],
            #     ascending=[True, True, False, True, True],
            # ).reset_index(drop=True)

        tmp = pd.concat(metrics_list)
        worsts = tmp[tmp["worst_by"] == tmp["worst_by"].max()]

        metrics = pd.DataFrame(
            {
                "spearmanr": [tmp["spearmanr"].mean()],
                "total_diff": [tmp["total_diff"].sum()],
                "total_perf": [tmp["total_perf"].sum()],
                "worst_tms": ["_".join(worsts["worst_tms"])],
                "worst_by": [tmp["worst_by"].max()],
                "worst_bys": ["_".join(worsts["worst_bys"])],
                "perfect_tms": ["_".join(tmp["perfect_tms"]).strip("_")],
                "perfect_pos": ["_".join(tmp["perfect_pos"]).strip("_")],
            }
        )

        return metrics