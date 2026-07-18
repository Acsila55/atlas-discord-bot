import random
import asyncio

import discord
from discord.ext import commands, tasks
from discord import app_commands

from cogs.base import BaseCog
from modules.lol_module.lol_data import LolAccount, DataDragon, LolLeaderboard

class LolCog(commands.GroupCog, BaseCog, name="lol", description="League of Legends profilok, rangok és statisztikák lekérdezése."):
    """A Discord cog handling League of Legends commands and background tasks."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ddragon = DataDragon() 
        self.database_path = "modules/lol_module/lol_database.json"
        self.database = self.load_json(self.database_path)
        self.leaderboard = LolLeaderboard()
        
    async def cog_load(self):
        """Loads the cog, loads all necessary data and starts the tasks"""
        await super().cog_load() 
        await self.ddragon.update_data() 
        self.background_rank_updater.start()
        self.background_leaderboard_updater.start()

    async def cog_unload(self):
        """Cleanly cancels the task and unloads the cog."""
        self.background_rank_updater.cancel()
        await super().cog_unload()

    # --- Background Tasks ---

    @tasks.loop(minutes=5)
    async def background_rank_updater(self):
        """Background task that updates player profiles."""
        print("Várakozás a Riot API-ra: profilok frissítése a háttérben...")

        for discord_id, db_data in self.database.items():
            try:
                account = LolAccount(name=db_data.get("name"), tag=db_data.get("tag"))
                await account.update_all()
                
                if account.puuid:
                    self.database[discord_id] = account.json()

            except Exception as e:
                await self.log_bot_error(f"Lol Task Update Failed (ID: {discord_id})", e)

        self.save_json(self.database_path, self.database)
        print("Frissítés kész.")

    @background_rank_updater.before_loop
    async def wait_rank_updater(self):
        """Forces the task to wait until the bot is fully logged in and cached."""
        await self.bot.wait_until_ready()

    @background_rank_updater.error
    async def background_rank_updater_error(self, error: Exception):
        """Catches critical errors if the entire background task crashes."""
        await self.log_bot_error("Task: background_lol_rank_updater", error)


    @tasks.loop(minutes=5)
    async def background_leaderboard_updater(self):
        """Background task that updates the leaderboard."""
        new_leaderboard = LolLeaderboard()

        for discord_id, db_data in self.database.items():
            try:
                account = LolAccount(
                    name=db_data.get("name"),
                    tag=db_data.get("tag"),
                    region=db_data.get("region", "eun1"),
                    puuid=db_data.get("puuid"),
                    summoner_level=db_data.get("summoner_level"),
                    summoner_icon=db_data.get("summoner_icon"),
                    ranks=db_data.get("ranks"),
                    mastery_score=db_data.get("mastery_score"),
                    champion_mastery=db_data.get("champion_mastery")
                )
                new_leaderboard.add_user(discord_id, account)

            except Exception as e:
                await self.log_bot_error(f"Leaderboard Update Failed (ID: {discord_id})", e)
                continue

        self.leaderboard = new_leaderboard
        await self.display_leaderboard()

    @background_leaderboard_updater.before_loop
    async def wait_leaderboard_updater(self):
        """Forces the task to wait until the bot is fully logged in and cached."""
        await self.bot.wait_until_ready()


    @background_leaderboard_updater.error
    async def background_leaderboard_updater_error(self, error: Exception):
        """Catches critical errors if the entire background task crashes."""
        await self.log_bot_error("Task: background_lol_leaderboard_updater", error)


    # --- Leaderboard ---

    async def display_leaderboard(self):
        """Displays the updated leaderboard"""
        channel_id = 1525259803096514560
        message_id = 1525298879321346201

        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Hiba: A csatorna ({channel_id}) nem található.")
            return
        
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            print("Hiba: Az üzenet nem található (lehet, hogy törölték).")
            return
        except discord.Forbidden:
            print("Hiba: Nincs jogom olvasni ezt a csatornát.")
            return
        
        embed = self.make_leaderboard_embed(message)

        await message.edit(embed=embed, content=None)

    def make_leaderboard_embed(self, entries):
        """Creates a cleaner, larger, and better-formatted leaderboard."""
        embed = discord.Embed(
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )

        embed.description = "### 🏆 League of Legends Leaderboard"

        solo_entries = self.leaderboard.order_solo()
        flex_entries = self.leaderboard.order_flex()
        fivestack_entries = self.leaderboard.order_fivestack()

        # Helper to format rows with more spacing
        def format_list(entries, attr_name):
            text = ""
            for i, entry in enumerate(entries[:15], start=1):
                name = entry.riot_id.split('#')[0]
                val = getattr(entry, attr_name)
                text += f"**{i}. {name}**`{val}`\n\n"
            return text

        embed.add_field(name="**Solo / Duo**", value=format_list(solo_entries, "solo_display") or "No data", inline=True)
        embed.add_field(name="**Flex**", value=format_list(flex_entries, "flex_display") or "No data", inline=True)
        embed.add_field(name="**5v5**", value=format_list(fivestack_entries, "fivestack_display") or "No data", inline=True)

        return embed
    
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
        
        embed = discord.Embed(title=champ_info["name"].upper(), color=discord.Color.dark_grey())
        embed.set_image(url= self.ddragon.get_champion_icon_url(champ_info["name"]))

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="link_account", description="Linkeli a megadott lol fiókot a discord fiókodhoz")
    async def link_account(self, interaction: discord.Interaction, username: str, tag: str):
        await interaction.response.defer(ephemeral=True)
         
        account = LolAccount(name=username, tag=tag)
        await asyncio.to_thread(account.update)
        
        if not account.puuid:
            await interaction.followup.send("⚠️ Nem találtam ilyen fiókot!")
            return

        self.database[str(interaction.user.id)] = account.json()
        self.save_json(self.database_path, self.database)
        
        await interaction.followup.send(f"✅ Sikeresen linkelted a fiókod: **{username}#{tag}**!")

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="admin_link_account", description="Linkeli a megadott lol fiókot a discord fiókhoz")
    async def admin_link_account(self, interaction: discord.Interaction, member: discord.Member, username: str, tag: str):
        await interaction.response.defer(ephemeral=True)
         
        account = LolAccount(name=username, tag=tag)
        await account.update_all()
        
        if not account.puuid:
            await interaction.followup.send("⚠️ Nem találtam ilyen fiókot!")
            return

        self.database[member.id] = account.json()
        self.save_json(self.database_path, self.database)
        
        await interaction.followup.send(f"✅ Sikeresen linkelted a fiókod: **{username}#{tag}**!")

    @app_commands.command(name="my_account", description="Visszaadja a te lol accountodat")
    async def my_account(self, interaction: discord.Interaction):
        await interaction.response.defer()
   
        discord_id = str(interaction.user.id)
        
        if discord_id not in self.database:
            await interaction.followup.send("⚠️ Még nem linkelted a fiókodat!")
            return

        db_data = self.database[discord_id]
        account = LolAccount(name=db_data.get("name"), tag=db_data.get("tag"))
        
        await account.update_all()
        self.database[discord_id] = account.json()
        self.save_json(self.database_path, self.database)

        solo_string = self.__format_queue_rank(account.ranks, "RANKED_SOLO_5x5")
        flex_string = self.__format_queue_rank(account.ranks, "RANKED_FLEX_SR")
        
        embed = self.__make_account_embed(interaction.user, account, solo_string, flex_string)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="get_account", description="Visszaadja a egy discord felhasznaló lol fiókját")
    async def get_account(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
 
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

    # --- Helper Functions ---

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
        
        embed.add_field(name="Level", value=str(account.summoner_level or 'Unknown'), inline=False)
        embed.add_field(name="🏆 Solo/Duo", value=solo_str, inline=True)
        embed.add_field(name="🏆 Flex", value=flex_str, inline=True)

        if account.champion_mastery:
            mastery_text = ""
            for entry in account.champion_mastery:
                champ_name = next((c['name'] for c in self.ddragon.champions.values() if int(c['key']) == entry['championId']), "Ismeretlen")
                mastery_text += f"**{champ_name}**: Lvl {entry.get('championLevel')} ({entry.get('championPoints', 0):,} pts)\n"
            embed.add_field(name="🔥 Top Champions", value=mastery_text, inline=False)
        
        return embed
    

async def setup(bot: commands.Bot):
    await bot.add_cog(LolCog(bot))