import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from cogs.base import BaseCog

class GeneralCog(BaseCog, name="general", description="Random parancsok gyűjteménye."):  

    @app_commands.command(name="edge", description="Cibálj meg egy embert. (Ne abuseold mert szétbaszlak)")
    @app_commands.default_permissions(move_members=True)
    async def edge(self, interaction: discord.Interaction, member: discord.Member, n: int):
        """Moves a user repeatedly between public voice channels.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The target member to move.
            n (int): The number of times to move the user.
        """
        # Check if the command can be started.
        if not await self.check_edge_conditions(interaction, member, n):
            return
        
        await interaction.response.defer(ephemeral=True)

        # Get all public voice channels excluding the current one to avoid sound.
        voice_channels = [
            vc for vc in interaction.guild.voice_channels 
            if vc.id != member.voice.channel.id 
            and vc.permissions_for(interaction.guild.default_role).connect
        ]

        # Check if there are enough public channels.
        if not voice_channels:
            await interaction.followup.send("⚠️ Nincs elég elérhető publikus hangcsatorna!", ephemeral=True)
            return

        # Edge the target repeatedly.
        for index in range(n):
            target_index = index % len(voice_channels)
            try:
                await member.move_to(voice_channels[target_index])
                await asyncio.sleep(1.5)
            except Exception:
                await interaction.followup.send("⚠️ A cibálás a vége előtt megszakadt.", ephemeral=True)
                return 
                
        await interaction.followup.send(f"✅ **{member.display_name}** meg lett cibálva.", ephemeral=True)

    async def check_edge_conditions(self, interaction: discord.Interaction, member: discord.Member, n: int) -> bool:
        """Validates the conditions before executing the edge command.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The target member.
            n (int): The number of moves.

        Returns:
            bool: True if all conditions are met, False otherwise.
        """
        # Check if called on a server.
        if interaction.guild is None:
            await interaction.response.send_message("⚠️ Ezt a parancsot csak szerveren használhatod!", ephemeral=True)
            return False
        
        # Check if n is valid.
        if n <= 0:
            await interaction.response.send_message("⚠️ Hogy a faszba cibáljam negatívszor, te agyhalott", ephemeral=True)
            return False
            
        # Check if member is in a voice channel.
        if member.voice is None or member.voice.channel is None:
            await interaction.response.send_message(f"⚠️ **{member.display_name}** jelenleg nincs hangcsatornában!", ephemeral=True)
            return False
        
        return True


async def setup(bot: commands.Bot):
    """Links the cog to the bot."""
    await bot.add_cog(GeneralCog(bot))