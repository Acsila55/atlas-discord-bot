import requests

from os import getenv
from dotenv import load_dotenv

load_dotenv()

api_key = getenv("RIOT_API_KEY")
routing = "europe"
    
session = requests.Session()
if api_key:
    session.headers.update({"X-Riot-Token": api_key})
else:
    print("Error: RIOT_API_KEY not found.")

def call_api(url: str, params: dict = None):
    response = session.get(f"https://{url}", params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error calling {url} api. Respone code: {response.status_code}")
        return None
    
# Account-v1
def account_by_riot_id(name: str, tag: str):
    return call_api(f"{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}")

def account_by_puuid(puuid: str):
    return call_api(f"{routing}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}")

# Champion-Mastery-v4
def champion_masteries_by_puuid(region: str, puuid: str, count: int = 3):
    queries = {"count": count}
    return call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top", params=queries)

def champion_mastery_by_puuid(region: str, puuid: str, champion_id: int):
    return call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}")

def mastery_score_by_puuid(region: str, puuid: str):
    return call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}")

# League-v4 (ranked stats)
def ranks_by_puuid(region: str, puuid: str):
    return call_api(f"{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")

# Match-v5
def matches_by_puuid(puuid: str, count: int = 20):
    queries = {
        "type": "ranked",
        "start": 0,
        "count": count
    }
    return call_api(f"{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids", params=queries)

def match_by_puuid(match_id: str):
    return call_api(f"{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}")

# Spectator-v5
def live_match_by_puuid(region: str, puuid: str):
    return call_api(f"{region}.api.riotgames.com/lol/spectator/v5/active-games/by-puuid/{puuid}")

# Summoner-v4
def summoner_by_puuid(region: str, puuid: str):
    return call_api(f"{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}")

