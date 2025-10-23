import requests
import pandas as pd
from datetime import date
import json
from bs4 import BeautifulSoup
from io import StringIO



class PremScraper:

    def __init__(self):
        
        self.url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings"

    def scrape_standings(self) -> pd.DataFrame:

        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()
        stgs = data['children'][0]['standings']['entries']
        standings = [x['team']['abbreviation'] for x in stgs]

        standings = pd.DataFrame(
            {
                "Rk": range(1, 21),
                "Team": standings
            }
        )

        standings['Date'] = date.today()

        return standings
    


class NBAScraper:

    def __init__(self):

        self.url = "https://sports.yahoo.com/nba/standings/?selectedTab=CONFERENCE"

        with open("utils/abbr_nba.json", "r") as f:
            abbr_dict = json.load(f)
        self.abbr_map = {v: k for k, v in abbr_dict.items()}

    def scrape_standings(self) -> pd.DataFrame:

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all("table")

        conf_standings = []
        for table in tables[-2:]:

            df = pd.read_html(StringIO(str(table)))[0]
            conf = df.columns[0]

            cf_st = df[[conf]].rename(columns={conf: "Team"})
            cf_st["Team"] = cf_st["Team"].map(self.abbr_map)
            cf_st["Conference"] = conf.removesuffix("ern")
            cf_st["Rk"] = range(1, 16)
            cf_st["Date"] = date.today()
            conf_standings.append(
                cf_st[["Conference", "Rk", "Team", "Date"]]
            )

        standings = pd.concat(conf_standings, ignore_index=True)

        return standings.sort_values(["Conference", "Rk"]).reset_index(drop=True)
    

def get_scraper(league: str):

    league = league.lower()
    if league == "prem":
        return PremScraper()
    elif league == "nba":
        return NBAScraper()
    else:
        raise ValueError(f"Unsupported league: {league}")