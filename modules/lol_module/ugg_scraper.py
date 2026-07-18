from curl_cffi import requests
from bs4 import BeautifulSoup

def get_champion_url(champion_name: str):
    return f"https://u.gg/lol/champions/{champion_name.lower()}/build"

def fetch_html_bypass(url):
    # 'impersonate' makes this request look exactly like a real Chrome browser
    response = requests.get(url, impersonate="chrome120")
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

# Usage
soup = fetch_html_bypass(get_champion_url("Viego"))
print(soup.title.text)