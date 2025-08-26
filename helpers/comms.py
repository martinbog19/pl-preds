import pandas as pd
from datetime import datetime, timedelta
import os
from twilio.rest import Client

from .utils import int_to_rank


def format_rankings_msg(metrics: pd.DataFrame) -> str:

    arrows = {
        1: '🔺',
        0: '➖',
        -1: '🔻',
    }

    return '\n'.join([
        f"{arrows.get(x['trend'])} {x['rank']}. {x['name']} ({x['total_diff']} diff.)"
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

    Total difference:    {x['total_diff']}
    Perfect predictions: {x['total_perf']}{perf_msg}
    Worst prediction{'s:' * (len(str(x['worst_bys']).split('_')) > 1) + ': ' * (len(str(x['worst_bys']).split('_')) <= 1)}   {worst_msg}
    """


def send_email(
    results: pd.DataFrame,
    EMAILS: list,
    img_path: str,
) -> None: #TODO
    
    pass
    
    # MY_EMAIL = os.getenv('MY_EMAIL')
    # GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
        
    # today = datetime.now().date()

    # # Create a MIMEMultipart object
    # msg = MIMEMultipart()

    # subject = f'PREMIER LEAGUE PREDICTIONS UPDATE {datetime.strftime(today, "%d%b%y")}
    # msg['Subject'] = subject

    # leaders = [] #TODO
    # mult = len(leaders) > 1

    # prog = 0 #TODO

    # html = f"""
    # <html>
    # <body>
    # <p>{" & ".join(leaders)} {mult*"are"}{(1-mult) * "is"} leading the way!</p>
    # <p>Leaderboard after completion of {prog}% of the 2025-26 Premier League season:</p>
    # <p style="margin-left: 20px;">1. {}:  {} pts<br>
    # <p style="margin-left: 20px;">2. {}:  {} pts<br>
    # <p style="margin-left: 20px;">3. {}:  {} pts</p>
    # <p><img src="cid:image1" alt="Image"></p>
    # </body>
    # </html>
    # """
    # msg.attach(MIMEText(html, 'html'))

    # # Read and attach the image
    # with open(path, 'rb') as img_file:
    #     img = MIMEImage(img_file.read())
    #     img.add_header('Content-ID', '<image1>')
    #     msg.attach(img)

    # # Set up the SMTP server and send the email
    # try:
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(MY_EMAIL, GMAIL_PASSWORD)
    #     server.sendmail(MY_EMAIL, EMAILS, msg.as_string())
    #     print('Email sent successfully!')
    # except Exception as e:
    #     print('Error sending email: ', str(e))
    # finally:
    #     server.quit()

