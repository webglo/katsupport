import discord

def has_staff_role(member: discord.Member) -> bool:
    return discord.utils.get(member.roles, name="‎♡‧₊˚staff") is not None

def has_admin_role(member: discord.Member) -> bool:
    return discord.utils.get(member.roles, name="+*:ꔫ:*administrator") is not None

async def send_to_user(user: discord.User, content: str) -> bool:
    try:
        await user.send(content)
        return True
    except discord.Forbidden:
        return False

def format_timestamp(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"

# Add more utility functions as needed