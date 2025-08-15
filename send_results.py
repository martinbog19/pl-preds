import pandas as pd

from helpers.ref import NAMES, EMAILS, PHONES
from helpers.comms import send_email, send_whatsapp



results = pd.read_csv('results.csv')


send_email(
    results,
    EMAILS,
)

for name in NAMES:

    phone_to = PHONES[name]

    send_whatsapp(
        results,
        name,
        phone_to,
    )