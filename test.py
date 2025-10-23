from bs4 import BeautifulSoup
import requests

url = "https://sports.yahoo.com/nba/standings/?selectedTab=CONFERENCE"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
tables = soup.find_all("table")
print(tables[-1])