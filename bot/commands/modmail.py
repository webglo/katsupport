import discord
from discord.ext import commands
from discord import app_commands
from config import CONFIG
from bot.database import is_blacklisted
from bot.views.modmail_views import ModMailButtonInside

class ModMailCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="modmail", description="Open/close a modmail channel")
    @app_commands.describe(
        action="Choose to open or close a modmail channel",
        member="The member to open a modmail for (only for 'open' action)",
        reason="Reason for opening/closing the modmail"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="open", value="open"),
        app_commands.Choice(name="close", value="close")
    ])
    @commands.has_role("‎♡‧₊˚staff")
    async def modmail(self, interaction: discord.Interaction, action: str, member: discord.Member = None, reason: str = None):
        if action == "open":
            await self.open_modmail(interaction, member, reason)
        elif action == "close":
            await self.close_modmail(interaction, reason)

    async def open_modmail(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not member:
            await interaction.response.send_message("❌ | You must specify a member to open a modmail for", ephemeral=True)
            return

        if await is_blacklisted(member.id, "modmail"):
            await interaction.response.send_message(f"❌ | {member.mention} is blacklisted from modmail", ephemeral=True)
            return

        category = interaction.guild.get_channel(CONFIG.MODMAIL_CATEGORY_ID)
        existing_modmail = discord.utils.get(category.text_channels, name=str(member.id))
        
        if existing_modmail:
            await interaction.response.send_message(f"❌ | A modmail channel already exists for {member.mention}: {existing_modmail.mention}", ephemeral=True)
            return

        try:
            await member.send(f"✅ | A staff member has opened a modmail channel for you.")
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ | Cannot open modmail for {member.mention}. Their DMs are closed.", ephemeral=True)
            return

        modmail_channel = await category.create_text_channel(name=str(member.id))
        view = ModMailButtonInside()
        message = await modmail_channel.send(f"✅ | Modmail opened for {member.mention} by {interaction.user.mention}\nReason: {reason}", view=view)
        await message.pin()

        await interaction.response.send_message(f"✅ | Modmail opened for {member.mention}: {modmail_channel.mention}", ephemeral=True)

    async def close_modmail(self, interaction: discord.Interaction, reason: str):
        if interaction.channel.category_id != CONFIG.MODMAIL_CATEGORY_ID:
            await interaction.response.send_message("❌ | This command can only be used in a modmail channel", ephemeral=True)
            return

        await interaction.response.send_message(f"🕛 | Closing modmail...", ephemeral=True)

        try:
            member_id = int(interaction.channel.name)
            member = interaction.guild.get_member(member_id)
            if member:
                await member.send(f"❗| Your modmail has been closed\nReason: {reason}")
        except:
            pass

        await interaction.channel.delete(reason=reason)

async def setup(bot):
    await bot.add_cog(ModMailCog(bot))