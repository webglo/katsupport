import discord
from discord.ext import commands
from config import CONFIG

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, owner_id=CONFIG.OWNER_ID)

    async def setup_hook(self):
        await self.load_extension("bot.events")
        await self.load_extension("bot.commands.ticket")
        await self.load_extension("bot.commands.modmail")
        await self.load_extension("bot.commands.blacklist")

bot = Bot()