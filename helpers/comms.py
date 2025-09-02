import pandas as pd
from .utils import int_to_rank


def format_rankings_msg(metrics: pd.DataFrame) -> str:

    arrows = {
        1: '🔺',
        0: '➖',
        -1: '🔻',
    }

    return '\t' + '\n\t'.join([
        f"{arrows.get(x['trend'], '➖')} {x['rank']}. {x['name']} ({x['total_diff']} diff.)"
        for _, x in metrics.sort_values('rank').iterrows()
    ])


def format_whatsapp_msg(x: pd.Series) -> str:

    medals = {
        1: '🥇',
        2: '🥈',
        3: '🥉'
    }

    perf_msg = ' (' + ', '.join([
        f'{tm} {int_to_rank(pos)}'
        for tm, pos
        in zip(str(x['perfect_tms']).split('_'), str(x['perfect_pos']).split('_'))
    ]) + ')' if x['total_perf'] > 0 else ''

    worst_msg = ', '.join(    
        [
            f'{tm} ({diff})'
            for tm, diff
            in zip(str(x['worst_tms']).split('_'), str(x['worst_bys']).split('_'))
        ]
    )

    return f"""
{medals.get(x['rank'], '')} {x['name']}, you're currently ranked {int_to_rank(x['rank'])}

Total difference: {x['total_diff']} positions
Perfect predictions: {x['total_perf']}{perf_msg}
Worst prediction{'s:' * (len(str(x['worst_bys']).split('_')) > 1) + ': ' * (len(str(x['worst_bys']).split('_')) <= 1)} {worst_msg}
    """