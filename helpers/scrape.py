import requests
import pandas as pd
from datetime import date
import json


from nba_api.stats.endpoints.leaguestandings import LeagueStandings


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

    def __init__(self, season="2025-26"):

        self.ls_api = LeagueStandings(season=season)

        with open("utils/abbr_nba.json", "r") as f:
            abbr_dict = json.load(f)
        self.abbr_map = {v: k for k, v in abbr_dict.items()}

    def scrape_standings(self) -> pd.DataFrame:

        data = self.ls_api.get_dict()

        columns = data["resultSets"][0]["headers"]
        rows = data["resultSets"][0]["rowSet"]

        standings = pd.DataFrame(rows, columns=columns)
        standings["Team"] = standings.apply(
            lambda row: " ".join([row["TeamCity"], row["TeamName"]]),
            axis=1
        ).map(self.abbr_map)

        standings = (
            standings.rename(columns={"PlayoffRank": "Rk"})
            [["Conference", "Rk", "Team"]]
        )

        standings['Date'] = date.today()

        return standings.sort_values(["Conference", "Rk"]).reset_index(drop=True)
    

def get_scraper(league: str):

    league = league.lower()
    if league == "prem":
        return PremScraper()
    elif league == "nba":
        return NBAScraper()
    else:
        raise ValueError(f"Unsupported league: {league}")