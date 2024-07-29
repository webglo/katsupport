import discord
from discord.ext import commands
import logging
from config import CONFIG
from bot.database import init_db

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('bot')

    @commands.Cog.listener()
    async def on_ready(self):
        await init_db()
        self.logger.info(f'Logged in as {self.bot.user}')
        
        activity = discord.Activity(name='my DMs', type=discord.ActivityType.watching)
        await self.bot.change_presence(activity=activity)

        voice_channel = self.bot.get_channel(CONFIG.VOICE_CHANNEL_ID)
        try:
            vc = await voice_channel.connect()
            await vc.guild.me.edit(mute=True, deafen=True)
        except Exception as e:
            self.logger.error(f"Error connecting to voice channel: {e}")

        log_channel = self.bot.get_channel(CONFIG.LOG_CHANNEL_ID)
        await log_channel.send(f'🟢 | Bot started')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if guild.id != CONFIG.GUILD_ID:
            default_channel = guild.system_channel
            if default_channel:
                await default_channel.send("❌ | This bot isn't whitelisted on this server")
            await guild.leave()

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("❌ | Missing required arguments", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await interaction.response.send_message("❌ | Bad arguments provided", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(f"❌ | Command is on cooldown. Try again in {error.retry_after:.2f} seconds", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            await interaction.response.send_message("❌ | You don't have permission to execute this command", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ | An error occurred while processing the command: {error}", ephemeral=True)
            self.logger.error(f"Command error: {error}", exc_info=True)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))