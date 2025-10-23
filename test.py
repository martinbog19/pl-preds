
from nba_api.stats.endpoints.leaguestandings import LeagueStandings


ls_api = LeagueStandings(season="2025-26")

data = ls_api.get_dict()

print(data)