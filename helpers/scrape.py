import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
from selenium import webdriver



def scrape_standings(abbr_map: dict) -> pd.DataFrame:

    url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    stgs = data['children'][0]['standings']['entries']
    standings = [x['team']['abbreviation'] for x in stgs]

    standings = pd.DataFrame(
        {
            "Rk": range(1, 21),
            "Tm": standings
        }
    )
    standings["Team"] = standings["Tm"].map(abbr_map)
    standings['Date'] = date.today()

    return standings