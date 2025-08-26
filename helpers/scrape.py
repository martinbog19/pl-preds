import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date






def scrape_standings() -> pd.DataFrame:

    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }

    page = requests.get(url, headers=headers)

    print(page.status_code, page.text)

    soup = BeautifulSoup(page.content, 'lxml')
    table = soup.find('table')

    standings = pd.read_html(str(table))[0]
    standings = standings[['Rk', 'Squad']].rename(columns = {'Squad': 'Team'})
    standings['Date'] = date.today()

    return standings