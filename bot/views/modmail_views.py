import discord
from discord.ui import View, Button, Modal, TextInput

class ModMailButtonInside(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close ModMail', style=discord.ButtonStyle.secondary, custom_id="modmail_closer")
    async def close_modmail(self, interaction: discord.Interaction, button: Button):
        if discord.utils.get(interaction.user.roles, name="‎♡‧₊˚staff"):
            await interaction.response.send_modal(ModMailClosureModal())
        else:
            await interaction.response.send_message("❌ | You don't have permission to close this modmail", ephemeral=True)

    @discord.ui.button(label='Blacklist User', style=discord.ButtonStyle.danger, custom_id="modmail_blacklist")
    async def blacklist_user(self, interaction: discord.Interaction, button: Button):
        if discord.utils.get(interaction.user.roles, name="+*:ꔫ:*administrator"):
            await interaction.response.send_modal(ModMailBlacklistModal(interaction.channel.name))
        else:
            await interaction.response.send_message("❌ | You don't have permission to blacklist users", ephemeral=True)

class ModMailClosureModal(Modal):
    def __init__(self):
        super().__init__(title="Close ModMail")
        self.reason = TextInput(label="Reason", style=discord.TextStyle.paragraph, placeholder="Why are you closing this modmail?", required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        from bot.commands.modmail import ModMailCog  # Avoid circular import
        await ModMailCog(interaction.client).close_modmail(interaction, self.reason.value)

class ModMailBlacklistModal(Modal):
    def __init__(self, user_id):
        super().__init__(title="Blacklist User")
        self.user_id = user_id
        self.reason = TextInput(label="Reason", style=discord.TextStyle.paragraph, placeholder="Why are you blacklisting this user?", required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        from bot.commands.blacklist import BlacklistCog  # Avoid circular import
        member = interaction.guild.get_member(int(self.user_id))
        if member:
            await BlacklistCog(interaction.client).blacklist(interaction, "modmail", "add", member, self.reason.value)
        else:
            await interaction.response.send_message("❌ | User not found", ephemeral=True)