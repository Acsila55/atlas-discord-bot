from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple

import modules.lol_module.riot_api as riot_api


@dataclass
class LolAccount:
    """Dataclass that stores all necessary information of a lol account"""

    name: str
    tag: str
    region: str = "eun1"

    puuid: Optional[str] = None
    
    summoner_level: Optional[int] = None
    summoner_icon: Optional[int] = None
    
    ranks: Optional[List[dict]] = None
    
    mastery_score: Optional[int] = None
    champion_mastery: Optional[List[dict]] = None

    def json(self):
        """Returns a json of the class"""
        return asdict(self) 

    async def update_puuid(self):
        """Fetches the PUUID from the Riot API."""
        if not self.puuid:
            account = await riot_api.account_by_riot_id(self.name, self.tag)
            if account:
                self.puuid = account.get("puuid")

    async def update_summoner_data(self):
        if not self.puuid:
            await self.update_puuid()
            
        if self.puuid:
            summoner = await riot_api.summoner_by_puuid(self.region, self.puuid)
            if summoner:
                self.summoner_level = summoner.get("summonerLevel")
                self.summoner_icon = summoner.get("profileIconId")

    async def update_ranks(self):
        """Updates only the Solo/Duo and Flex ranked data."""
        if not self.puuid:
            await self.update_puuid()
            
        if not self.puuid:
            return

        raw_ranks = await riot_api.ranks_by_puuid(self.region, self.puuid)
        if raw_ranks:
            self.ranks = [
                {
                    "queueType": r.get("queueType"),
                    "tier": r.get("tier"),
                    "rank": r.get("rank"),
                    "leaguePoints": r.get("leaguePoints", 0),
                    "rankscore": self.get_rankscore(r.get("tier"), r.get("rank"), r.get("leaguePoints", 0)),
                    "wins": r.get("wins"),
                    "losses": r.get("losses"),
                }
                for r in raw_ranks
            ]
        else:
            self.ranks = []

    async def update_mastery(self):
        """Updates only the total mastery score and top 5 champions."""
        if not self.puuid:
            await self.update_puuid()
            
        if not self.puuid:
            return

        self.mastery_score = await riot_api.mastery_score_by_puuid(self.region, self.puuid)
        
        raw_mastery = await riot_api.champion_masteries_by_puuid(self.region, self.puuid, 5)
        if raw_mastery:
            self.champion_mastery = [
                {
                    "championId": m.get("championId"),
                    "championLevel": m.get("championLevel"),
                    "championPoints": m.get("championPoints")
                }
                for m in raw_mastery
            ]
        else:
            self.champion_mastery = []

    async def update_all(self):
        """Updates all account data at once."""
        await self.update_puuid()
        if self.puuid:
            await self.update_summoner_data()
            await self.update_ranks()
            await self.update_mastery()

    def get_rankscore(self, tier: str, rank: str, lp: int) -> int:
        """Calculates the overall lp from the rank"""

        tier = tier.upper()
        rank = rank.upper()

        tier_lps = {
            "IRON": 400, "BRONZE": 800, "SILVER": 1200, "GOLD": 1600, 
            "PLATINUM": 2000, "EMERALD": 2400, "DIAMOND": 2800, 
            "MASTER": 3200, "GRANDMASTER": 3600, "CHALLENGER": 5000 
        }
        rank_lps = {"I": 300, "II": 200, "III": 100, "IV": 0}

        return tier_lps.get(tier, 0) + rank_lps.get(rank, 0) + lp


class DataDragon:
    def __init__(self):
        self.versions = []
        self.champions = {}

    async def update_data(self):
        """fetches the list of champions asyncronously."""
        self.versions = await riot_api.call_api("ddragon.leagueoflegends.com/api/versions.json")
        if self.versions:
            champion_data = await riot_api.call_api(f"ddragon.leagueoflegends.com/cdn/{self.versions[0]}/data/en_US/champion.json")
            self.champions = champion_data["data"] if champion_data else {}

    def get_champion_icon_url(self, champion_name: str):
        """Returns the url of a champion icon."""
        for champ_id, champ_info in self.champions.items():
            if champ_info["name"].lower() == champion_name.lower():
                return f"https://ddragon.leagueoflegends.com/cdn/{self.versions[0]}/img/champion/{champ_info['image']['full']}"
        return None

    def get_profile_icon_url(self, icon_id: int):
        """Returns the url of a profile icon."""
        return f"https://ddragon.leagueoflegends.com/cdn/{self.versions[0]}/img/profileicon/{icon_id}.png"
    
@dataclass
class LeaderboardEntry:
    """A class for storing an entry in the leaderboard."""
    discord_id: str
    riot_id: str
    
    solo_score: int
    solo_display: str
    
    flex_score: int
    flex_display: str

    fivestack_score: int
    fivestack_display: str

class LolLeaderboard:
    """A class for storing the lol leaderboard."""
    def __init__(self):
        self.entries: List[LeaderboardEntry] = []

    def add_user(self, discord_id: str, account: LolAccount):
        """Adds a user to the leaderboard."""

        solo_score, solo_display = self._extract_rank_info(account.ranks, "RANKED_SOLO_5x5")
        flex_score, flex_display = self._extract_rank_info(account.ranks, "RANKED_FLEX_SR")
        fivestack_score, fivestack_display = self._extract_rank_info(account.ranks, "RANKED_PREMADE_5x5")
    
        entry = LeaderboardEntry(
            discord_id=discord_id,
            riot_id=f"{account.name}#{account.tag}",
            solo_score=int(solo_score),
            solo_display=solo_display,
            flex_score=int(flex_score),
            flex_display=flex_display,
            fivestack_score=int(fivestack_score),
            fivestack_display=fivestack_display
        )
        self.entries.append(entry)

    def order_solo(self):
        """Orders the entries based on the solo rankscores"""
        entries = sorted(self.entries, key=lambda x: x.solo_score, reverse=True)
        return entries
    
    def order_flex(self):
        """Orders the entries based on the flex rankscores"""
        entries = sorted(self.entries, key=lambda x: x.flex_score, reverse=True)
        return entries
    
    def order_fivestack(self):
        """Orders the entries based on the ranked 5s rankscores"""
        entries = sorted(self.entries, key=lambda x: x.fivestack_score, reverse=True)
        return entries

    def _extract_rank_info(self, ranks: List[dict], queue_type: str) -> Tuple[int, str]:
        """Helper to convert the rank from the database to the rankscore and a rank string"""
        if not ranks:
            return 0, "Unranked"
            
        for r in ranks:
            if r.get("queueType") == queue_type:
                score = r.get("rankscore", 0)
                tier = r.get("tier", "").capitalize()
                rank = r.get("rank", "")
                lp = r.get("leaguePoints", 0)
                
                return score, f"{tier} {rank} ({lp} LP)"
                
        return 0, "Unranked"








