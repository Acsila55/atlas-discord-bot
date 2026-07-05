import random
import asyncio
import json
import os

import discord
from discord.ext import commands, tasks
from discord import app_commands

from modules.lol_module.lol_data import LolAccount, DataDragon


class LolCog(commands.GroupCog, name="lol", description="League of Legends profilok, rangok és statisztikák lekérdezése."):
    """A Discord cog handling League of Legends commands and background tasks."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ddragon = DataDragon() 
        self.database_path = "lol_database.json"
        self.database = self._load_database()
        self.background_rank_updater.start()
    
    def cog_unload(self):
        self.background_rank_updater.cancel()

    # --- Database Functions ---
    def _load_database(self):
        """Loads the JSON database from disk."""
        if os.path.exists(self.database_path):
            with open(self.database_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_database(self):
        """Saves the current database state to disk."""
        with open(self.database_path, "w", encoding="utf-8") as f:
            json.dump(self.database, f, indent=4)

    @tasks.loop(minutes=5)
    async def background_rank_updater(self):
        """Background task that updates player profiles."""
        print("Várakozás a Riot API-ra: profilok frissítése a háttérben...")

        for discord_id, db_data in self.database.items():
            try:
                account = LolAccount(name=db_data.get("name"), tag=db_data.get("tag"))
                await asyncio.to_thread(account.update)
                
                if account.puuid:
                    self.database[discord_id] = account.json()

            except Exception as e:
                print(f"Error updating ranks for {discord_id}:\n```\n{e}\n```")

        self._save_database()
        print("Frissítés kész.")

    # --- Commands ---
    @app_commands.command(name="random_champion", description="Megad egy random lol championt.")
    async def random_champion(self, interaction: discord.Interaction):
        await interaction.response.defer()

        champ_names = list(self.ddragon.champions.keys())
        if not champ_names:
            await interaction.followup.send("⚠️ Nem sikerült betölteni a championöket.")
            return
            
        random_champ_id = random.choice(champ_names)
        champ_info = self.ddragon.champions[random_champ_id]
        
        embed = discord.Embed(title=champ_info["name"].upper(), color=discord.Color.blue())
        embed.set_image(self.ddragon.get_champion_icon_url(champ_info["name"]))

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="link_account", description="Linkeli a megadott lol fiókot a discord fiókodhoz")
    async def link_account(self, interaction: discord.Interaction, username: str, tag: str):
        await interaction.response.defer(ephemeral=True)

        try:            
            account = LolAccount(name=username, tag=tag)
            await asyncio.to_thread(account.update)
            
            if not account.puuid:
                await interaction.followup.send("⚠️ Nem találtam ilyen fiókot!")
                return

            self.database[str(interaction.user.id)] = account.json()
            self._save_database()
            
            await interaction.followup.send(f"✅ Sikeresen linkelted a fiókod: **{username}#{tag}**!")
        
        except Exception as e:
            print(f"Error linking account: {e}")
            await interaction.followup.send("⚠️ Hiba történt a fiók linkelése közben.")

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="admin_link_account", description="Linkeli a megadott lol fiókot a discord fiókhoz")
    async def link_account(self, interaction: discord.Interaction, member: discord.Member, username: str, tag: str):
        await interaction.response.defer(ephemeral=True)

        try:            
            account = LolAccount(name=username, tag=tag)
            await asyncio.to_thread(account.update)
            
            if not account.puuid:
                await interaction.followup.send("⚠️ Nem találtam ilyen fiókot!")
                return

            self.database[member.id] = account.json()
            self._save_database()
            
            await interaction.followup.send(f"✅ Sikeresen linkelted a fiókod: **{username}#{tag}**!")
        
        except Exception as e:
            print(f"Error linking account: {e}")
            await interaction.followup.send("⚠️ Hiba történt a fiók linkelése közben.")

    @app_commands.command(name="my_account", description="Visszaadja a te lol accountodat")
    async def my_account(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:     
            discord_id = str(interaction.user.id)
            
            if discord_id not in self.database:
                await interaction.followup.send("⚠️ Még nem linkelted a fiókodat!")
                return

            db_data = self.database[discord_id]
            account = LolAccount(name=db_data.get("name"), tag=db_data.get("tag"))
            
            await asyncio.to_thread(account.update)
            self.database[discord_id] = account.json()
            self._save_database()

            solo_string = self.__format_queue_rank(account.ranks, "RANKED_SOLO_5x5")
            flex_string = self.__format_queue_rank(account.ranks, "RANKED_FLEX_SR")
            
            embed = self.__make_account_embed(interaction.user, account, solo_string, flex_string)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error in my_account: {e}")
            await interaction.followup.send("⚠️ Hiba történt az adatok lekérésekor.")

    @app_commands.command(name="get_account", description="Visszaadja a egy discord felhasznaló lol fiókját")
    async def my_account(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()

        try:     
            discord_id = str(member.id)
            
            if discord_id not in self.database:
                await interaction.followup.send("⚠️ Még nem linkelted a fiókodat!")
                return

            db_data = self.database[discord_id]
            account = LolAccount(name=db_data.get("name"), tag=db_data.get("tag"))
            
            await asyncio.to_thread(account.update)
            self.database[discord_id] = account.json()
            self._save_database()

            solo_string = self.__format_queue_rank(account.ranks, "RANKED_SOLO_5x5")
            flex_string = self.__format_queue_rank(account.ranks, "RANKED_FLEX_SR")
            
            embed = self.__make_account_embed(interaction.user, account, solo_string, flex_string)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error in my_account: {e}")
            await interaction.followup.send("⚠️ Hiba történt az adatok lekérésekor.")

    def __format_queue_rank(self, ranks_list: list, queue_type: str) -> str:
        if not ranks_list: return "Unranked"
        for queue in ranks_list:
            if queue.get("queueType") == queue_type:
                return f"{queue.get('tier', '').capitalize()} {queue.get('rank', '')} ({queue.get('leaguePoints', 0)} LP)"
        return "Unranked"
    
    def __make_account_embed(self, member, account, solo_str, flex_str) -> discord.Embed:
        icon_url = self.ddragon.get_profile_icon_url(account.summoner_icon or 1)
        embed = discord.Embed(title=f"{account.name}#{account.tag}", color=discord.Color.blue())
        
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=icon_url)
        
        embed.add_field(name="Szint", value=str(account.summoner_level or 'Ismeretlen'), inline=False)
        embed.add_field(name="🏆 Solo/Duo", value=solo_str, inline=True)
        embed.add_field(name="🏆 Flex", value=flex_str, inline=True)

        if account.champion_mastery:
            mastery_text = ""
            for entry in account.champion_mastery:
                champ_name = next((c['name'] for c in self.ddragon.champions.values() if int(c['key']) == entry['championId']), "Ismeretlen")
                mastery_text += f"**{champ_name}**: Lvl {entry.get('championLevel')} ({entry.get('championPoints', 0):,} pts)\n"
            embed.add_field(name="🔥 Top Championök", value=mastery_text, inline=False)
        
        return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(LolCog(bot))