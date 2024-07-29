import asyncio
from bot.bot import bot
from config import CONFIG

async def main():
    async with bot:
        await bot.start(CONFIG.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())