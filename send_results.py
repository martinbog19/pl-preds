import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from helpers.comms import format_rankings_msg, format_whatsapp_msg
from helpers.ref import EMAILS



SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'martinbog19@gmail.com'
PASSWORD = os.getenv('GMAIL_APP_PASSWORD')


today = datetime.now().date()
last_week = today - timedelta(days=7)

metrics = pd.read_csv('metrics.csv')

metrics_last_week = metrics[metrics['date'].astype(str) == datetime.strftime(last_week, '%Y-%m-%d')][['name', 'rank']]
metrics = metrics[metrics['date'].astype(str) == datetime.strftime(today, '%Y-%m-%d')]

metrics = metrics.merge(
    metrics_last_week,
    on='name',
    how='left',
    suffixes=('', '_past')
)
metrics['trend'] = np.sign(metrics['rank_past'] - metrics['rank'])

rankings_msg = format_rankings_msg(metrics)
subject = f'PL Predictions Weekly Update  -  {today.strftime("%d %b %Y")}'

for _, row in metrics.sort_values('name').iterrows():

    body = format_whatsapp_msg(row) + '\n\nCurrent rankings:\n' + rankings_msg

    name = row['name']
    to_email = EMAILS.get(name)
    assert to_email, f'Email for {name} not found in dictionary!'

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
        print(f'Email sent successfully to {to_email}!')
    except Exception as e:
        print(f"Failed to send email base of '{e}'")
    finally:
        server.quit()
        time.sleep(.1)