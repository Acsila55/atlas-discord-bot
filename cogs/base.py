import os
import json
import discord
from discord.ext import commands
from discord import app_commands

class BaseCog(commands.Cog):
    """A base template for other cogs to inherit from."""

    LOG_CHANNEL_ID = 1512863571229409300   # The channel where the user issued commands are logged 
    ERROR_CHANNEL_ID = 1524165829321691348 # The channel where the bot errors are logged

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Cog Handling ---

    async def cog_load(self):
        """Triggers automatically when the cog is successfully loaded."""
        print(f"✅ Cog loaded: {self.__cog_name__}")

    async def cog_unload(self):
        """Triggers automatically when the cog is unloaded."""
        print(f"🛑 Cog unloaded: {self.__cog_name__}")
    
    # --- Error Handling ---

    async def log_bot_error(self, action_name: str, error: Exception):
        """Logs an error to the error channel"""
        error_channel = self.bot.get_channel(self.ERROR_CHANNEL_ID)
        if not error_channel:
            return
        
        embed = discord.Embed(
            title="⚠️ Error Occurred",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(name="Action", value=action_name, inline=False)
        embed.add_field(name="Error", value=str(error), inline=False)
        
        await error_channel.send(embed=embed)
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Cathes slash command errors, logs them and notifies the user."""
        command_name = getattr(interaction.command, "name", "Unknown Command")
        
        await self.log_bot_error(f"Command: `/{command_name}`", error)

        error_message = "❌ Egy váratlan hiba történt a parancs futtatása közben."
        if interaction.response.is_done():
            await interaction.followup.send(error_message, ephemeral=True)
        else:
            await interaction.response.send_message(error_message, ephemeral=True)

    # ---  JSON Handling ---

    def load_json(self, filepath: str) -> dict:
        """Universal JSON loader."""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_json(self, filepath: str, data: dict):
        """Universal JSON saver."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)