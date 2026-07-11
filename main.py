import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


class AtlasBot(commands.Bot):
    """The main bot class, inherits from commands.Bot.
    
    This class handles the intial bot setup and event listeners.
    """
    def __init__(self):
        """Initializes the bot with default intents, status, activity.

        Also defines the list of cogs to be loaded during startup.
        """
        super().__init__(
            command_prefix="!",  
            intents=discord.Intents.all(), 
            case_insensitive=True,  
            activity=discord.CustomActivity(name="Just Gooning"),  
            status=discord.Status.online  
        )

        self.cogs_list = [
            "cogs.logging",
            "cogs.admin",
            "cogs.lol",
            "cogs.general",
        ]
    
    async def setup_hook(self): 
        """Setup function that initialises the bot behaviour.

        Loads extensions (cogs) and slash commands.
        """
        print("Loading Bot Commands...")
        
        for cog in self.cogs_list:
            await self.load_extension(cog)
        
        await self.tree.sync() 

        print("Bot Commands Loaded & Synced!")

    async def on_ready(self):
        """Event listener triggered when the bot is ready."""
        print("Atlas is online!")


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN not found.")

    bot = AtlasBot()
    bot.run(TOKEN)