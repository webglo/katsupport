import discord
from discord.ui import View, Button, Modal, TextInput

class TicketButtonCreator(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Create Ticket', style=discord.ButtonStyle.green, custom_id="ticket_creator")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TicketCreationModal())

class TicketButtonInside(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.secondary, custom_id="ticket_closer")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        if discord.utils.get(interaction.user.roles, name="‎♡‧₊˚staff"):
            await interaction.response.send_modal(TicketClosureModal())
        else:
            await interaction.response.send_message("❌ | You don't have permission to close this ticket", ephemeral=True)

    @discord.ui.button(label='Blacklist User', style=discord.ButtonStyle.danger, custom_id="ticket_blacklist")
    async def blacklist_user(self, interaction: discord.Interaction, button: Button):
        if discord.utils.get(interaction.user.roles, name="+*:ꔫ:*administrator"):
            await interaction.response.send_modal(TicketBlacklistModal(interaction.channel.name[7:]))  # Removes 'ticket-' prefix
        else:
            await interaction.response.send_message("❌ | You don't have permission to blacklist users", ephemeral=True)

class TicketCreationModal(Modal):
    def __init__(self):
        super().__init__(title="Create Ticket")
        self.reason = TextInput(label="Reason", style=discord.TextStyle.paragraph, placeholder="Why are you creating this ticket?", required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        from bot.commands.ticket import TicketCog  # Avoid circular import
        await TicketCog(interaction.client).create_ticket(interaction, self.reason.value)

class TicketClosureModal(Modal):
    def __init__(self):
        super().__init__(title="Close Ticket")
        self.reason = TextInput(label="Reason", style=discord.TextStyle.paragraph, placeholder="Why are you closing this ticket?", required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        from bot.commands.ticket import TicketCog  # Avoid circular import
        await TicketCog(interaction.client).delete_ticket(interaction, self.reason.value)

class TicketBlacklistModal(Modal):
    def __init__(self, user_id):
        super().__init__(title="Blacklist User")
        self.user_id = user_id
        self.reason = TextInput(label="Reason", style=discord.TextStyle.paragraph, placeholder="Why are you blacklisting this user?", required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        from bot.commands.blacklist import BlacklistCog  # Avoid circular import
        member = interaction.guild.get_member(int(self.user_id))
        if member:
            await BlacklistCog(interaction.client).blacklist(interaction, "ticket", "add", member, self.reason.value)
        else:
            await interaction.response.send_message("❌ | User not found", ephemeral=True)