import requests
import pandas as pd
from datetime import date
import json
from bs4 import BeautifulSoup
from io import StringIO
import os



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

        self.base_url = "http://site.api.espn.com/apis/site/v2/"

        with open("utils/abbr_nba.json", "r") as f:
            abbr_dict = json.load(f)
        self.abbr_map = {v: k for k, v in abbr_dict.items()}

    def _get_conference(self, standing_summary: str) -> str:
        if (
            "southwest" in standing_summary.lower()
            or "northwest" in standing_summary.lower()
            or "pacific" in standing_summary.lower()
        ):
            return "West"
        else:
            return "East"

    def scrape_standings(self) -> pd.DataFrame:

        query_url = os.path.join(self.base_url, "sports/basketball/nba/teams")
        response = requests.get(query_url)
        response.raise_for_status()

        teams = response.json()["sports"][0]["leagues"][0]["teams"]
        data = []
        for team in teams:

            team_id = team["team"]["id"]
            team_abbr = team["team"]["abbreviation"]
            team_name = team["team"]["displayName"]

            query_url = os.path.join(self.base_url, f"sports/basketball/nba/teams/{team_id}")
            tm_response = requests.get(query_url)

            overall_record_stats = tm_response.json()["team"]["record"]["items"][0]["stats"]
            playoff_seed = [x["value"] for x in overall_record_stats if x["name"] == "playoffSeed"][0]

            standingSummary = tm_response.json()["team"]["standingSummary"]
            conference = self._get_conference(standingSummary)

            data.append(
                {
                    "Conference": conference,
                    "Rk": int(playoff_seed),
                    "Team": self.abbr_map[team_abbr],
                    "TeamName": team_name,
                    "Date": date.today(),
                }
            )

        standings = pd.DataFrame(data)

        return standings.sort_values(["Conference", "Rk"]).reset_index(drop=True)
    

def get_scraper(league: str):

    league = league.lower()
    if league == "prem":
        return PremScraper()
    elif league == "nba":
        return NBAScraper()
    else:
        raise ValueError(f"Unsupported league: {league}")