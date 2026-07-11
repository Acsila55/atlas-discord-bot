import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal

from cogs.base import BaseCog

@app_commands.default_permissions(administrator=True)
class AdminCog(commands.GroupCog, BaseCog, name="admin", description="Adminisztrátori parancsok a bot és a szerver kezeléséhez."):

    def cog_app_command_check(self, interaction: discord.Interaction) -> bool:
        """Checks if the user has administrator permissions

        Args:
            interaction (discord.Interaction): The interaction object context.

        Returns:
            bool: True if the user is an administrator, False otherwise.
        """
        return interaction.user.guild_permissions.administrator
    
    @app_commands.command(name="shutdown", description="Leállítja a botot.")
    async def shutdown(self, interaction: discord.Interaction):
        """Safely disconnects and shuts down the bot.

        Args:
            interaction (discord.Interaction): The interaction object.
        """
        await interaction.response.send_message("Atlas sikeresen leállt.", ephemeral=True)
        await self.bot.close()

    @app_commands.command(name="reload_module", description="Újratölt egy modult.") 
    async def reload_module(self, interaction: discord.Interaction, module: str):
        """Reloads a specific Cog extension.

        Args:
            interaction (discord.Interaction): The interaction object.
            module (str): The specific cog name to reload.
        """
        await interaction.response.defer(ephemeral=True)

        # Checks if module is already loaded into the bot.
        if f"cogs.{module}" not in getattr(self.bot, "cogs_list", self.bot.cogs_list if hasattr(self.bot, "cogs_list") else []):
            await interaction.followup.send(f"⚠️ ERROR: '{module}.py' nem létezik!")
            return

        # Reload the module and resyncs the commands.
        await self.bot.reload_extension(f"cogs.{module}")
        await self.bot.tree.sync() 
        
        await interaction.followup.send(f"✅ '{module}.py' sikeresen újratöltve!")

    @app_commands.command(name="change_status", description="Megváltoztatja a bot státuszát.")
    async def change_status(
        self, 
        interaction: discord.Interaction, 
        status: Literal["online", "idle", "dnd", "invisible"], 
        activity_type: Literal["playing", "watching", "listening", "custom"], 
        activity_text: str
    ):
        """Changes the bot's online status and activity.

        Args:
            interaction (discord.Interaction): The interaction object.
            status (str): The online status.
            activity_type (str): The type of activity.
            activity_text (str): The description of the activity.
        """
        await interaction.response.defer(ephemeral=True)

        # Convert status string to discord enum.
        discord_status = getattr(discord.Status, status)

        # Make the new activity.
        if activity_type == "custom":
            new_activity = discord.CustomActivity(name=activity_text)
        else:
            discord_activity_type = getattr(discord.ActivityType, activity_type)
            new_activity = discord.Activity(type=discord_activity_type, name=activity_text)

        # Apply the new status.
        await self.bot.change_presence(status=discord_status, activity=new_activity)
        
        await interaction.followup.send(
            f"✅ Státusz sikeresen megváltoztatva: **{status.upper()}** | {activity_type.capitalize()} **{activity_text}**!"
        )

    @app_commands.command(name="clear_messages", description="Kitörli az utolsó n db üzenetet.")
    async def clear_messages(self, interaction: discord.Interaction, n: int):
        """Bulk deletes a specified number of recent messages in the channel.

        Args:
            interaction (discord.Interaction): The interaction object.
            n (int): The number of messages to delete.
        """
        await interaction.response.defer(ephemeral=True)

        # Delete the specified number of messages.
        deleted_messages = await interaction.channel.purge(limit=n)
        await interaction.followup.send(f"✅ {len(deleted_messages)} db üzenet sikeresen törölve.")


async def setup(bot: commands.Bot):
    """Links the cog to the bot."""
    await bot.add_cog(AdminCog(bot))