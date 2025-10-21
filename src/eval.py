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

    def evaluate(self, names):

        res_list = []
        for name in names:

            prediction_path = os.path.join(self.prediction_folder, f"{name.lower()}.txt")
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


    def compute_overall_metrics(self, metrics: pd.DataFrame) -> pd.DataFrame:
        
        worsts = metrics[metrics["worst_by"] == metrics["worst_by"].max()].copy()
        return pd.DataFrame(
            {
                "spearmanr": [metrics["spearmanr"].mean()],
                "total_diff": [metrics["total_diff"].sum()],
                "total_perf": [metrics["total_perf"].sum()],
                "worst_tms": ["_".join(worsts["worst_tms"])],
                "worst_by": [metrics["worst_by"].max()],
                "worst_bys": ["_".join(worsts["worst_bys"])],
                "perfect_tms": ["_".join(metrics["perfect_tms"]).strip("_")],
                "perfect_pos": ["_".join(metrics["perfect_pos"]).strip("_")],
            }
        )

    def evaluate(self, names: list[str]) -> pd.DataFrame:
        
        metrics_list = []
        names = ["Martin", "Lucas"]
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

            all_metrics = pd.concat(metrics_list)
            metrics = all_metrics.groupby("name").apply(self.compute_overall_metrics, include_groups=False).droplevel(1).reset_index()
            metrics["conference"] = "Overall"
            metrics = pd.concat([all_metrics, metrics], ignore_index=True)

        return metrics
    

def get_evaluator(league: str, standings: pd.DataFrame):

    league = league.lower()
    if league == "prem":
        return PremEvaluator(standings)
    elif league == "nba":
        return NBAEvaluator(standings)
    else:
        raise ValueError(f"Unsupported league: {league}")