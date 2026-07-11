import aiohttp

from os import getenv
from dotenv import load_dotenv

load_dotenv()
api_key = getenv("RIOT_API_KEY")
routing = "europe"

session = None
    
async def get_session():
    global session
    if session is None:
        headers = {"X-Riot-Token": api_key} if api_key else {}
        session = aiohttp.ClientSession(headers=headers)
    return session

async def call_api(url: str, params: dict = None):
    client = await get_session()

    async with client.get(f"https://{url}", params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            error_msg = f"Riot API Error {response.status} on endpoint: {url}"
            raise ConnectionError(error_msg)
    
# Account-v1
async def account_by_riot_id(name: str, tag: str):
    return await call_api(f"{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}")

async def account_by_puuid(puuid: str):
    return await call_api(f"{routing}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}")

# Champion-Mastery-v4
async def champion_masteries_by_puuid(region: str, puuid: str, count: int = 3):
    queries = {"count": count}
    return await call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top", params=queries)

async def champion_mastery_by_puuid(region: str, puuid: str, champion_id: int):
    return await call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}")

async def mastery_score_by_puuid(region: str, puuid: str):
    return await call_api(f"{region}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}")

# League-v4 (ranked stats)
async def ranks_by_puuid(region: str, puuid: str):
    return await call_api(f"{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")

# Match-v5
async def matches_by_puuid(puuid: str, count: int = 20):
    queries = {
        "type": "ranked",
        "start": 0,
        "count": count
    }
    return await call_api(f"{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids", params=queries)

async def match_by_puuid(match_id: str):
    return await call_api(f"{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}")

# Spectator-v5
async def live_match_by_puuid(region: str, puuid: str):
    return await call_api(f"{region}.api.riotgames.com/lol/spectator/v5/active-games/by-puuid/{puuid}")

# Summoner-v4
async def summoner_by_puuid(region: str, puuid: str):
    return await call_api(f"{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}")

