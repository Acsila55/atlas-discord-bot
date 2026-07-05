from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

import modules.lol_module.riot_api as riot_api


@dataclass
class LolAccount:
    name: str
    tag: str
    region: str = "eun1"

    puuid: Optional[str] = None
    
    summoner_level: Optional[int] = None
    summoner_icon: Optional[int] = None
    revision_date: Optional[float] = None
    
    ranks: Optional[List[dict]] = None
    
    mastery_score: Optional[int] = None
    champion_mastery: Optional[List[dict]] = None

    def json(self):
        return asdict(self) 

    def update(self):
        account = riot_api.account_by_riot_id(self.name, self.tag)
            
        if account:
            self.puuid = account.get("puuid")
            
            summoner = riot_api.summoner_by_puuid(self.region, self.puuid)
            if summoner:
                self.summoner_level = summoner.get("summonerLevel")
                self.summoner_icon = summoner.get("profileIconId")
                self.revision_date = summoner.get("revisionDate")
            
            self.ranks = riot_api.ranks_by_puuid(self.region, self.puuid)

            self.mastery_score = riot_api.mastery_score_by_puuid(self.region, self.puuid)
            self.champion_mastery = riot_api.champion_masteries_by_puuid(self.region, self.puuid, 5)

        else:
            print(f"Failed to find {self.name}#{self.tag}.")


class DataDragon:
    def __init__(self):
        self.versions = riot_api.call_api("ddragon.leagueoflegends.com/api/versions.json")
        self.champions = self.get_champions()

    def get_champions(self):
        champion_data = riot_api.call_api(f"ddragon.leagueoflegends.com/cdn/{self.versions[0]}/data/en_US/champion.json")
        return champion_data["data"] if champion_data else {}

    def get_champion_icon_url(self, champion_name: str):
        for champ_id, champ_info in self.champions.items():
            if champ_info["name"].lower() == champion_name.lower():
                return f"https://ddragon.leagueoflegends.com/cdn/{self.versions[0]}/img/champion/{champ_info['image']['full']}"
        return None

    def get_profile_icon_url(self, icon_id: int):
        return f"https://ddragon.leagueoflegends.com/cdn/{self.versions[0]}/img/profileicon/{icon_id}.png"








