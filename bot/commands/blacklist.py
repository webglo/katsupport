import discord
from discord.ext import commands
from discord import app_commands
from bot.database import add_to_blacklist, remove_from_blacklist, is_blacklisted, get_blacklist_reason

class BlacklistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blacklist", description="Manage blacklist for modmail/tickets")
    @app_commands.describe(
        type="Choose modmail or ticket blacklist",
        action="Choose to add, remove, or check blacklist status",
        member="The member to blacklist/unblacklist/check",
        reason="Reason for blacklisting (required for 'add' action)"
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="ticket", value="ticket"),
            app_commands.Choice(name="modmail", value="modmail")
        ],
        action=[
            app_commands.Choice(name="add", value="add"),
            app_commands.Choice(name="remove", value="remove"),
            app_commands.Choice(name="check", value="check")
        ]
    )
    @commands.has_role("+*:ꔫ:*administrator")
    async def blacklist(self, interaction: discord.Interaction, type: str, action: str, member: discord.Member, reason: str = None):
        staff_role = discord.utils.get(interaction.guild.roles, name="‎♡‧₊˚staff")
        
        if staff_role in member.roles or member.id == interaction.user.id:
            await interaction.response.send_message("❌ | You cannot blacklist a staff member or yourself", ephemeral=True)
            return

        if action == "add":
            if not reason:
                await interaction.response.send_message("❌ | You must provide a reason when blacklisting a member", ephemeral=True)
                return
            await add_to_blacklist(member.id, reason, type)
            await interaction.response.send_message(f"✅ | {member.mention} has been blacklisted from {type}s\nReason: {reason}", ephemeral=True)

        elif action == "remove":
            await remove_from_blacklist(member.id, type)
            await interaction.response.send_message(f"✅ | {member.mention} has been removed from the {type} blacklist", ephemeral=True)

        elif action == "check":
            is_blocked = await is_blacklisted(member.id, type)
            if is_blocked:
                reason = await get_blacklist_reason(member.id, type)
                await interaction.response.send_message(f"✅ | {member.mention} is blacklisted from {type}s\nReason: {reason}", ephemeral=True)
            else:
                await interaction.response.send_message(f"✅ | {member.mention} is not blacklisted from {type}s", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BlacklistCog(bot))