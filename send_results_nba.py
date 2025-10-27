import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import time
import os
import sys
import json
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.ref import EMAILS, VARS
from src.utils import int_to_rank


league = "nba"

REF_DATE = VARS[league]["ref_date"]
EMAIL_FREQUENCY = VARS[league]["email_frequency"]

today = datetime.now().date()
yesterday = today - timedelta(days=1)

if (today - REF_DATE).days % EMAIL_FREQUENCY != 0:
    print("No email to send today.")
    sys.exit()


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
# USERNAME = os.getenv('NBA_GMAIL_USERNAME')
# PASSWORD = os.getenv('NBA_GMAIL_APP_PASSWORD')

USERNAME = "nba.predictions.reports@gmail.com"
PASSWORD = "olmc ignq zrbp hebi"


metrics = pd.read_csv(f'data/{league}/metrics.csv')
metrics = metrics[metrics["conference"] == "Overall"].copy()

metrics_yesterday = metrics[metrics['date'].astype(str) == datetime.strftime(yesterday, '%Y-%m-%d')][['name', 'rank']]
metrics = metrics[metrics['date'].astype(str) == datetime.strftime(today, '%Y-%m-%d')]

metrics = metrics.merge(
    metrics_yesterday,
    on='name',
    how='left',
    suffixes=('', '_past')
)
metrics['trend'] = (metrics['rank_past'] - metrics['rank']).fillna(0)

metrics["Rank"] = metrics.apply(lambda row: f"{int_to_rank(row['rank'])}", axis=1)
metrics["Score"] = metrics['spearmanr'].apply(lambda x: f"{100 * (x + 1) / 2:.1f}%")


rankings_html = metrics[["rank", "Rank", "name", "Score", "total_perf"]].rename(
    columns={
        "name": "Name",
        "Rank": "",
        "total_perf": "Perfect",
    }
).sort_values("rank").drop(columns="rank").to_html(index=False, classes="dataframe", border=0)

subject = f'{league.upper()} Predictions Update  -  {today.strftime("%d %b %Y")}'

with open("template.html") as f:
    template = Template(f.read())


with open("utils/abbr_nba.json", "r") as f:
    abbr_nba = json.load(f)


for _, row in metrics.sort_values('name').iterrows():

    name = row['name']
    rank = row['rank']
    medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, '')
    position = int_to_rank(rank)

    to_email = EMAILS.get(name)

    perf_msg = ", ".join(
        [
            f"{abbr_nba[tm]} ({int_to_rank(pos)})"
            for tm, pos in zip(
                row['perfect_tms'].split("_"),
                row['perfect_pos'].split("_"),
            )
        ]
    ) if row['perfect_tms'] != "" else "None..."

    worst_msg = ", ".join(
        [
            f"{abbr_nba[tm]} ({pos})"
            for tm, pos in zip(
                row['worst_tms'].split("_"),
                row['worst_bys'].split("_"),
            )
        ]
    )

    report_html = template.render(
        medal=medal,
        name=name,
        report_date=today.strftime("%d %B %Y"),
        rankings_table=rankings_html,
        score=row["Score"],
        abs_diff=row['total_diff'],
        perf_msg=perf_msg,
        worst_msg=worst_msg,
        position=position,
    )

    email = MIMEMultipart()
    email['From'] = USERNAME
    email['To'] = to_email
    email['Subject'] = subject

    email.attach(MIMEText(report_html, 'html'))

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(email)
        print(f'Email sent successfully to {to_email}!')
    except Exception as e:
        print(f"Failed to send email to {to_email} because of '{e}'")
    finally:
        server.quit()
        time.sleep(1)
