import time
from nba_api.stats.endpoints import leaguestandings
from nba_api.library.http import NBAStatsHTTP
from requests.exceptions import ReadTimeout

# Monkey-patch NBAStatsHTTP to use friendlier headers
NBAStatsHTTP().session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
})

for attempt in range(5):
    try:
        ls_api = leaguestandings.LeagueStandings(season="2025-26", timeout=60)
        data = ls_api.get_dict()
        print(data)
        break
    except ReadTimeout:
        print(f"Timeout on attempt {attempt + 1}. Retrying in 10 seconds...")
        time.sleep(10)
else:
    raise Exception("Failed to fetch data after 5 attempts.")
