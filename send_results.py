import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from twilio.rest import Client

from helpers.ref import NAMES, EMAILS, PHONES
from helpers.comms import format_rankings_msg, format_whatsapp_msg, send_email, send_whatsapp




# ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
ACCOUNT_SID = 'ACa7f0f17d7d08787859bb5db69b6f098a'
# AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
AUTH_TOKEN = '227ff92c6483229c934ea967e772b1c0'


today = datetime.now().date()
last_week = today - timedelta(days=7)

metrics = pd.read_csv('metrics.csv')
metrics_last_week = metrics[metrics['date'].astype(str) == datetime.strftime(last_week, '%Y-%m-%d')][['name', 'rank']]
metrics = metrics[metrics['date'].astype(str) == datetime.strftime(today, '%Y-%m-%d')]

metrics = metrics.merge(
    metrics_last_week,
    on='name',
    suffixes=('', '_past')
)
metrics['rank_past'] = metrics['rank_past'].combine_first(metrics['rank'])

metrics['trend'] = np.sign(metrics['rank_past'] - metrics['rank'])

    
ranking_msg = format_rankings_msg(metrics)

for _, x in metrics.iterrows():

    name = x['name']
    phone_to = PHONES.get(name, '')

    whatsapp_msg = format_whatsapp_msg(x)

    msg = whatsapp_msg + '\n' + ranking_msg

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=msg,
        from_="whatsapp:+14155238886",
        to=f"whatsapp:{phone_to}",
    )