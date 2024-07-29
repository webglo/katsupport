import discord
from discord.ext import commands
from discord import app_commands
from config import CONFIG
from bot.database import is_blacklisted
from bot.views.ticket_views import TicketButtonCreator, TicketButtonInside

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Create/delete a ticket")
    @app_commands.describe(
        action="Choose to create or delete a ticket",
        reason="Reason for creating/deleting the ticket"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="create", value="create"),
        app_commands.Choice(name="delete", value="delete")
    ])
    async def ticket(self, interaction: discord.Interaction, action: str, reason: str):
        if action == "create":
            await self.create_ticket(interaction, reason)
        elif action == "delete":
            await self.delete_ticket(interaction, reason)

    async def create_ticket(self, interaction: discord.Interaction, reason: str):
        if await is_blacklisted(interaction.user.id, "ticket"):
            await interaction.response.send_message("❌ | You are blacklisted from creating tickets", ephemeral=True)
            return

        category = interaction.guild.get_channel(CONFIG.TICKET_CATEGORY_ID)
        existing_ticket = discord.utils.get(category.text_channels, name=f'ticket-{interaction.user.id}')
        
        if existing_ticket:
            await interaction.response.send_message(f"❌ | You already have an open ticket: {existing_ticket.mention}", ephemeral=True)
            return

        support_role = discord.utils.get(interaction.guild.roles, name="‎♡‧₊˚staff")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await category.create_text_channel(f'ticket-{interaction.user.id}', overwrites=overwrites)
        view = TicketButtonInside()
        message = await ticket_channel.send(f"❗| Welcome to your ticket, {interaction.user.mention}! {support_role.mention} will be here shortly.\nReason: {reason}", view=view)
        await message.pin()

        await interaction.response.send_message(f"✅ | Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

    async def delete_ticket(self, interaction: discord.Interaction, reason: str):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ | This command can only be used in a ticket channel", ephemeral=True)
            return

        support_role = discord.utils.get(interaction.guild.roles, name="‎♡‧₊˚staff")
        if support_role not in interaction.user.roles:
            await interaction.response.send_message("❌ | You don't have permission to delete tickets", ephemeral=True)
            return

        await interaction.response.send_message(f"🕛 | Deleting ticket...", ephemeral=True)

        try:
            ticket_owner_id = int(interaction.channel.name.split('-')[1])
            ticket_owner = interaction.guild.get_member(ticket_owner_id)
            if ticket_owner:
                await ticket_owner.send(f"❗| Your ticket was deleted\nTicket: {interaction.channel.name}\nReason: {reason}")
        except:
            pass

        await interaction.channel.delete(reason=reason)

    @app_commands.command(name="ticketbuttoncreator", description="Create interaction buttons for ticket creation")
    @commands.has_role("+*:ꔫ:*administrator")
    async def ticketbuttoncreator(self, interaction: discord.Interaction):
        view = TicketButtonCreator()
        await interaction.channel.send("Click the button below to create a ticket:", view=view)
        await interaction.response.send_message("✅ | Ticket creation button has been added", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))