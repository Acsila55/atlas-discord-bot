import discord
from discord.ext import commands

from cogs.base import BaseCog


class LoggingCog(BaseCog, name="logging", description="A bot interakciójait logolja."):
    
    def make_log_embed(self, interaction: discord.Interaction) -> discord.Embed:
        """Creates an embed object with the logging details

        Args:
            interaction (discord.Interaction): The interaction object containing the commands context.

        Returns:
            discord.Embed: A formatted embed with the logging details.
        """
        embed = discord.Embed(
            title="💻 Command Executed",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(name="User", value=interaction.user.mention, inline=True)

        command_name = getattr(interaction.command, "name", "Unknown Command")
        embed.add_field(name="Command", value=f"`/{command_name}`", inline=True)
        
        channel_name = interaction.channel.mention if interaction.channel else "Private Message"
        embed.add_field(name="Channel", value=channel_name, inline=True)

        return embed

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction): 
        """Event listener triggered when a user interacts with the bot.

        Logs all interactions to the specified log channel.

        Args:
            interaction (discord.Interaction): The interaction object containing the commands context.
        """
        # Only listen for slash commands
        if interaction.type != discord.InteractionType.application_command:
            return
        
        log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID) 
            
        if log_channel is None:
            print("Logging channel has been deleted please restore it")
            return
        
        embed = self.make_log_embed(interaction)
        await log_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    """Links the cog to the bot."""
    await bot.add_cog(LoggingCog(bot))