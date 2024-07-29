import asyncio
from bot.bot import Bot
from config import CONFIG
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    bot = Bot()
    if bot is None:
        logger.error("Failed to create Bot instance")
        return

    logger.info("Bot instance created successfully")
    
    try:
        await bot.load_cogs()
        logger.info("All cogs loaded successfully")
        
        await bot.start(CONFIG.TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        await bot.close()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)