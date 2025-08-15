import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date






def scrape_standings() -> pd.DataFrame:

    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    table = soup.find('table')

    standings = pd.read_html(str(table))[0]
    standings = standings[['Rk', 'Squad']].rename(columns = {'Squad': 'Team'})
    standings['Date'] = date.today()

    return standings