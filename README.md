How to run the Bot: 
py main.py

Required packages:
discord.py
python-

TODO:
GENERAL:
edgelo 
atrako
lenemito
spam pinger (lehet nem jo otlet)
rank megvaltoztato +rang generalo
nev megvaltoztato

GEMINI kerdezo(ha lehet ingyen)

LOL:
api:
    profile checker
    live game checker
    history checker
    
op.gg scraper:
    champ counters
    champ build
    champ runes

discord related:
    discord to riot accoutnt linker
    5v5 team randomizer

KOMPLEX
media player
soundboard palayer

 def make_leaderboard_embed(self, entries, message: discord.Message):
        """Makes the leaderboard embed"""
        embed = discord.Embed(
            title="🏆 LoL Leaderboard",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        
        table = f"{'Lol Leaderboard':^84}\n"
        table += "=" * 84 + "\n"
        table += f"{'#':<3} | {'Discord':<15} | {'Lol':<18} | {'Solo Rank':<18} | {'Flex Rank':<18}\n"
        table += "=" * 84 + "\n"

        for index, entry in enumerate(entries[:20], start=1):
            member = message.guild.get_member(int(entry.discord_id)) if message.guild else None
            discord_name = member.display_name if member else "Unknown"

            discord_name = (discord_name[:12] + '...') if len(discord_name) > 15 else discord_name
            riot_name = (entry.riot_id[:15] + '...') if len(entry.riot_id) > 18 else entry.riot_id
            solo_rank = (entry.solo_display[:15] + '...') if len(entry.solo_display) > 18 else entry.solo_display
            flex_rank = (entry.flex_display[:15] + '...') if len(entry.flex_display) > 18 else entry.flex_display

            table += f"{index:<3} | {discord_name:<15} | {riot_name:<18} | {solo_rank:<18} | {flex_rank:<18}\n"

        embed.description = f"```text\n{table}\n```"

        return embed



