# SETUP

import nextcord
import datetime
import sqlite3
import asyncio
import io
import os
from dotenv import load_dotenv

from nextcord.ext import commands, tasks
from nextcord.ui import View
from PIL import Image

# Load environment variables
load_dotenv()

# CONFIGURABLE VARIABLES

TOKEN = 'MTA3MTExMjQ0NzI1MzA0MTIxMw.G1tQ2h.Ljx2Bw2ZG7B3osrTYBQfUFORP8MVCvkqJvpaz8'
OWNER_ID = 577640362366205995
GUILD_ID = 1226286702428160001
DATABASE_NAME = 'katsupport.sqlite'
MODMAIL_CATEGORY_ID = 1230995301934829681
TICKET_CATEGORY_ID = 1231004154382782505
VOICE_CHANNEL_ID = 1230992899068661922
LOG_CHANNEL_ID = 1230992701776724219
ADMIN_ROLE_NAME = '+*:ꔫ:*administrator'
STAFF_ROLE_NAME = '‎♡‧₊˚staff'

# SQLITE3

CON = sqlite3.connect(DATABASE_NAME)
CUR = CON.cursor()

# BOT

INTENTS = nextcord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
BOT = commands.Bot(intents=INTENTS, owner_id=OWNER_ID)

# DEFINE

def table_exists(table_name):
    CUR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = CUR.fetchone()
    return result is not None

CON.commit()

if not table_exists('modmail_blacklist'):
    CUR.execute("CREATE TABLE modmail_blacklist(member_id INTEGER, reason TEXT)")

if not table_exists('ticket_blacklist'):
    CUR.execute("CREATE TABLE ticket_blacklist(member_id INTEGER, reason TEXT)")

# EVENTS

@BOT.event
async def on_ready():
    await BOT.wait_until_ready()

    activity = nextcord.Activity(name='my dms', type=nextcord.ActivityType.watching)
    await BOT.change_presence(activity=activity)
    print(f'logged into {BOT.user}')

    voice_channel = BOT.get_channel(VOICE_CHANNEL_ID)
    try:
        vc = await voice_channel.connect()
        await vc.guild.me.edit(mute=True)
        await vc.guild.me.edit(deafen=True)
    except Exception as e:
        print(f"Error connecting to voice channel: {e}")  # Logging the exception

    log_channel = BOT.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f'🟢 | started - <t:{int(datetime.datetime.now().timestamp())}:R>')

    for guilds in BOT.guilds:
        BOT.add_view(TicketButtonCreator(guilds.owner_id))
        BOT.add_view(TicketButtonInside(guilds.owner_id))
        BOT.add_view(ModMailButtonInside(guilds.owner_id))

@BOT.event
async def on_guild_join(guild: nextcord.Guild):
    if guild.id != GUILD_ID:
        default_channel = guild.system_channel
        if default_channel is not None:
            await default_channel.send("❌ | this bot isnt whitelisted on this server")
        await guild.leave()

@BOT.event
async def on_message(message: nextcord.Message):
    guild = BOT.get_guild(GUILD_ID)
    perm_role = nextcord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
    staff_role = nextcord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

    if message.author != BOT.user and message.content != None and message.author.bot == False:
        guild = BOT.get_guild(GUILD_ID)
        category = nextcord.utils.get(guild.categories, id=MODMAIL_CATEGORY_ID)
        dm_existing_channel = nextcord.utils.get(category.channels, name=f'{message.author.id}')
        server_existing_channel = BOT.get_channel(message.channel.id)
        CUR.execute("SELECT * FROM modmail_blacklist WHERE member_id=?", (message.author.id,))
        if_blacklisted = CUR.fetchone()

        if isinstance(message.channel, nextcord.DMChannel):
            if not if_blacklisted:
                if not dm_existing_channel:
                    await asyncio.sleep(0.1)
                    if message.attachments:
                        if not len(message.attachments) > 1:
                            for attachment in message.attachments:
                                image_bytes = await attachment.read()
                                image = Image.open(io.BytesIO(image_bytes))
                                converted_image = image.convert("RGBA")
                                converted_image.save("attachment_image.png", "PNG")
                        else:
                            await message.author.send(f'❌ | you can only send 1 attachment at a time')
                            return
                        if not len(message.attachments) > 1:
                            with open('attachment_image.png', "rb") as file:
                                discord_file = nextcord.File(file)
                                modmail_channel = await category.create_text_channel(name=f"{message.author.id}")
                                for guilds in BOT.guilds:
                                    view = ModMailButtonInside(guilds.owner_id)
                                send = await modmail_channel.send(f"❗| {staff_role.mention}\nnew modmail from {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}", file=discord_file, view=view)
                                await send.pin()
                                await message.author.send(f'✅ | sent, you are now connected to modmail - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}')
                                await message.add_reaction('✅')
                    else:
                        modmail_channel = await category.create_text_channel(name=f"{message.author.id}")
                        for guilds in BOT.guilds:
                            view = ModMailButtonInside(guilds.owner_id)
                        send = await modmail_channel.send(f"❗| {staff_role.mention}\nnew modmail from {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}", view=view)
                        await send.pin()
                        await message.author.send(f'✅ | sent, you are now connected to modmail - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}')
                        await message.add_reaction('✅')
                        return

                await asyncio.sleep(0.1)
                if message.attachments:
                    if not len(message.attachments) > 1:
                        for attachment in message.attachments:
                            image_bytes = await attachment.read()
                            image = Image.open(io.BytesIO(image_bytes))
                            converted_image = image.convert("RGBA")
                            converted_image.save("attachment_image.png", "PNG")
                    else:
                        await message.author.send(f'❌ | you can only send 1 attachment at a time')
                        return
                    if not len(message.attachments) > 1:
                        with open('attachment_image.png', "rb") as file:
                            discord_file = nextcord.File(file)
                            await dm_existing_channel.send(f"❗| {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}", file=discord_file)
                            await message.add_reaction('✅')
                else:
                    await dm_existing_channel.send(f"❗| {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}")
                    await message.add_reaction('✅')
            else:
                await message.author.send(f'❌ | could not connect to modmail\nreason: {if_blacklisted[1]}')
        else:
            if server_existing_channel.category == category:
                await asyncio.sleep(0.1)
                if message.attachments:
                    if not len(message.attachments) > 1:
                        for attachment in message.attachments:
                            image_bytes = await attachment.read()
                            image = Image.open(io.BytesIO(image_bytes))
                            converted_image = image.convert("RGBA")
                            converted_image.save("attachment_image.png", "PNG")
                    else:
                        await message.author.send(f'❌ | you can only send 1 attachment at a time')
                        return
                    if not len(message.attachments) > 1:
                        with open('attachment_image.png', "rb") as file:
                            discord_file = nextcord.File(file)
                            try:
                                await guild.get_member(int(message.channel.name)).send(f"❗| {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}", file=discord_file)
                                await message.add_reaction('✅')
                            except:
                                await message.add_reaction('❌')
                else:
                    try:
                        await guild.get_member(int(message.channel.name)).send(f"❗| {message.author.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>\n{message.content}")
                        await message.add_reaction('✅')
                    except:
                        await message.add_reaction('❌')

@BOT.event
async def on_application_command_error(interaction: nextcord.Interaction, error: Exception):
    try:
        if isinstance(error, nextcord.errors.ApplicationInvokeError):
            if isinstance(error, nextcord.ext.commands.errors.MissingRequiredArgument):
                await interaction.response.send_message("❌ | missing required arguments", ephemeral=True)
            elif isinstance(error, nextcord.ext.commands.errors.BadArgument):
                await interaction.response.send_message("❌ | bad arguments provided", ephemeral=True)
            elif isinstance(error, nextcord.ext.commands.errors.CommandOnCooldown):
                await interaction.response.send_message(f"❌ | command is on cooldown try again in {error.retry_after:.2f} seconds", ephemeral=True)
            elif isinstance(error, nextcord.ext.commands.errors.CheckFailure):
                await interaction.response.send_message("❌ | you dont have permission to execute this command", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ | an error occurred while processing the command\n{error}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ | an error occurred while processing the command\n{error}", ephemeral=True)
    except:
        pass

# TASKS

@tasks.loop(seconds=1)
async def check_guilds():
    for guild in BOT.guilds:
        if guild.id != GUILD_ID:
            default_channel = guild.system_channel
            if default_channel is not None:
                await default_channel.send("❌ | this bot isnt whitelisted on this server")
            await guild.leave()
            break
        
# SLASH COMMANDS

@BOT.slash_command(guild_ids=[GUILD_ID], description="latency")
async def ping(interaction: nextcord.Interaction):
    response = await interaction.response.send_message(f"🕛 | pinging...", ephemeral=True)
    await response.edit(f"✅ | pong\nraw: {BOT.latency * 1000}ms\nactual: {int(BOT.latency * 1000)}ms")

@BOT.slash_command(guild_ids=[GUILD_ID], description='create/delete a ticket')
async def ticket(interaction: nextcord.Interaction, action: str = nextcord.SlashOption(required=True, choices=['create', 'delete']), reason: str = nextcord.SlashOption(required=True)):
    support_role = nextcord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
    category = BOT.get_channel(TICKET_CATEGORY_ID)
    CUR.execute("SELECT * FROM ticket_blacklist WHERE member_id=?", (interaction.user.id,))
    if_blacklisted = CUR.fetchone()
    if isinstance(category, nextcord.CategoryChannel):
        if action == 'create':
            response = await interaction.response.send_message(f'🕛 | creating...', ephemeral=True)
            if not if_blacklisted:
                try:
                    for channel in interaction.guild.channels:
                        if channel.name.startswith(f'ticket-{interaction.user.id}'):
                            await response.edit(f'❌ | a ticket already exists for you\nticket: {channel.mention}')
                            return
                    overwrites = {
                        support_role: nextcord.PermissionOverwrite(read_messages=True),
                        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                        interaction.user: nextcord.PermissionOverwrite(read_messages=True, embed_links=True, attach_files=True)
                    }
                    ticket_channel = await interaction.guild.create_text_channel(f'ticket-{interaction.user.id}', category=category, overwrites=overwrites)
                    for guild in BOT.guilds:
                        view = TicketButtonInside(guild.owner_id)
                    send = await ticket_channel.send(f"❗| welcome to your ticket, {interaction.user.mention}! {support_role.mention} will be here shortly.\nreason: {reason}", view=view)
                    await send.pin()
                    await response.edit(f'✅ | your ticket has been created\n{ticket_channel.mention}')
                except Exception as e:
                    await response.edit(f'❌ | your ticket couldnt be created {e}')
            else:
                await response.edit(f'❌ | your ticket couldnt be created\nreason: {if_blacklisted[1]}')
        elif action == 'delete':
            member_highest_role = interaction.user.top_role
            if not member_highest_role >= support_role:
                await interaction.response.send_message(f'❌ | you dont have permissions (‎♡‧₊˚staff role or higher)', ephemeral=True)
                return
            try:
                if interaction.channel.name.startswith("ticket-"):
                    response = await interaction.response.send_message(f'🕛 | deleting...', ephemeral=True)
                    try:
                        substring = interaction.channel.name[len("ticket-"):]
                        await interaction.guild.get_member(int(substring)).send(f'❗| your ticket was deleted\nticket: {interaction.channel.name}\nreason: {reason}')
                    except:
                        pass
                    await interaction.channel.delete(reason=reason)
            except:
                await response.edit(f'❌ | couldnt delete the ticket')

@BOT.slash_command(guild_ids=[GUILD_ID], description='create interaction buttons for ticket creation')
async def ticketbuttoncreator(interaction: nextcord.Interaction):
    perm_role = nextcord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
    member_highest_role = interaction.user.top_role
    if not member_highest_role >= perm_role:
        await interaction.response.send_message(f'❌ | you dont have permissions ({ADMIN_ROLE_NAME} role or higher)', ephemeral=True)
        return
    
    for guilds in BOT.guilds:
        view = TicketButtonCreator(guilds.owner_id)
    send = BOT.get_channel(interaction.channel_id)
    await interaction.response.send_message('sent', ephemeral=True)
    await send.send(view=view)

@BOT.slash_command(guild_ids=[GUILD_ID], description='open/close a modmail channel')
async def modmail(interaction: nextcord.Interaction, action: str = nextcord.SlashOption(required=True, choices=['open', 'close']), member: nextcord.Member = nextcord.SlashOption(required=False), reason: str = nextcord.SlashOption(required=False)):
    perm_role = nextcord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
    member_highest_role = interaction.user.top_role
    if not member_highest_role >= perm_role:
        await interaction.response.send_message(f'❌ | you dont have permissions ({STAFF_ROLE_NAME} role or higher)', ephemeral=True)
        return
    
    category = BOT.get_channel(MODMAIL_CATEGORY_ID)

    if isinstance(category, nextcord.CategoryChannel):
        if action == 'open':
            response = await interaction.response.send_message(f'🕛 | opening... (if hasnt changed then something went wrong)', ephemeral=True)
            dm_existing_channel = nextcord.utils.get(category.channels, name=f'{member.id}')
            if not dm_existing_channel:
                if not member:
                    await response.edit(f'❌ | cannot force a connection to modmail with no one')
                try:
                    try:
                        await member.send(f'✅ | you have been forced a connection to modmail with {interaction.user.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>')
                    except:
                        await response.edit(f'❌ | cannot force a connection to modmail with their dms closed')
                        return
                    modmail_channel = await category.create_text_channel(name=f"{member.id}")
                    await modmail_channel.send(f"✅ | you have forced a connection to modmail with {member.mention} - <t:{int(datetime.datetime.now().timestamp())}:R>")
                    await response.edit(f'✅ | modmail opened\n{modmail_channel.mention}')
                except:
                    await interaction.response.send_message(f'❌ | couldnt force modmail connection', ephemeral=True)
            else:
                await interaction.response.send_message(f'❌ | this modmail connection already exists', ephemeral=True)
        elif action == 'close':
            response = await interaction.response.send_message(f'🕛 | closing...', ephemeral=True)
            try:
                if interaction.channel.category == category:
                    if not reason:
                        reason = 'closed'
                    try:
                        await interaction.guild.get_member(int(interaction.channel.name)).send(f'❗| your modmail was closed\nmodmail: {interaction.channel.name}\nreason: {reason}')
                    except:
                        pass
                    await interaction.channel.delete(reason=reason)
                else:
                    await response.edit(f'❌ | this isnt the modmail category')
            except:
                await response.edit(f'❌ | couldnt close the modmail')

@BOT.slash_command(guild_ids=[GUILD_ID], description='blacklist a member from modmail/tickets')
async def blacklist(interaction: nextcord.Interaction, type: str = nextcord.SlashOption(required=True, choices=['ticket', 'modmail']), action: str = nextcord.SlashOption(required=True, choices=['add', 'remove', 'check']), member: nextcord.Member = nextcord.SlashOption(required=True), reason: str = nextcord.SlashOption(required=False)):
    perm_role = nextcord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
    member_highest_role = interaction.user.top_role
    if not member_highest_role >= perm_role:
        await interaction.response.send_message(f'❌ | you dont have permissions ({ADMIN_ROLE_NAME} role or higher)', ephemeral=True)
        return
    
    staff_role = nextcord.utils.get(member.guild.roles, name=STAFF_ROLE_NAME)
    
    if staff_role in member.roles or member.id == interaction.user.id:
        await interaction.response.send_message("❌ | you cannot blacklist a staff member or yourself", ephemeral=True)
        return
    
    if type == 'ticket':
        if action == 'add':
            if not reason:
                await interaction.response.send_message(f'❌ | provide a reason to blacklist', ephemeral=True)
                return
            
            response = await interaction.response.send_message(f"🕛 | adding...", ephemeral=True)

            CUR.execute("SELECT * FROM ticket_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if not if_blacklisted:
                CUR.execute(
                    "INSERT INTO ticket_blacklist VALUES (?, ?)",
                    (member.id, reason)
                )
                CON.commit()
                await response.edit(f'✅ | blacklisted {member.mention}')
            else:
                await response.edit(f'❌ | {member.mention} is already blacklisted')
        elif action == 'remove':
            response = await interaction.response.send_message(f"🕛 | removing...", ephemeral=True)
            CUR.execute("SELECT * FROM ticket_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if if_blacklisted:
                CUR.execute("DELETE FROM ticket_blacklist WHERE member_id=?", (member.id,))
                CON.commit()
                await response.edit(f'✅ | unblacklisted {member.mention}')
            else:
                await response.edit(f'❌ | {member.mention} is not blacklisted')
        elif action == 'check':
            response = await interaction.response.send_message(f"🕛 | checking...", ephemeral=True)
            CUR.execute("SELECT * FROM ticket_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if if_blacklisted:
                await response.edit(f'✅ | checked {member.mention}\nreason: {if_blacklisted[1]}')
            else:
                await response.edit(f'❌ | {member.mention} is not blacklisted')
    elif type == 'modmail':
        if action == 'add':
            if not reason:
                await interaction.response.send_message(f'❌ | provide a reason to blacklist', ephemeral=True)
                return
            
            response = await interaction.response.send_message(f"🕛 | adding...", ephemeral=True)

            CUR.execute("SELECT * FROM modmail_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if not if_blacklisted:
                CUR.execute(
                    "INSERT INTO modmail_blacklist VALUES (?, ?)",
                    (member.id, reason)
                )
                CON.commit()
                await response.edit(f'✅ | blacklisted {member.mention}')
            else:
                await response.edit(f'❌ | {member.mention} is already blacklisted')
        elif action == 'remove':
            response = await interaction.response.send_message(f"🕛 | removing...", ephemeral=True)

            CUR.execute("SELECT * FROM modmail_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if if_blacklisted:
                CUR.execute("DELETE FROM modmail_blacklist WHERE member_id=?", (member.id,))
                CON.commit()
                await response.edit(f'✅ | unblacklisted {member.mention}')
            else:
                await response.edit(f'❌ | {member.mention} is not blacklisted')
        elif action == 'check':
            response = await interaction.response.send_message(f"🕛 | checking...", ephemeral=True)
            
            CUR.execute("SELECT * FROM modmail_blacklist WHERE member_id=?", (member.id,))
            if_blacklisted = CUR.fetchone()

            if if_blacklisted:
                await response.edit(f'✅ | checked {member.mention}\nreason: {if_blacklisted[1]}')
            else:
                await response.edit(f'❌ | {member.mention} is not blacklisted')

# INTERACTION CREATORS

# TICKET

# TICKET

class TicketButtonInside(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @nextcord.ui.button(label='delete ticket', style=nextcord.ButtonStyle.secondary, custom_id="ticketbuttondeleter")
    async def button_callback(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if button.custom_id == "ticketbuttondeleter":
            support_role = nextcord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
            member_highest_role = interaction.user.top_role
            if not member_highest_role >= support_role:
                await interaction.response.send_message(f'❌ | you dont have permission', ephemeral=True)
                return
            for guilds in BOT.guilds:
                modal = TicketDeletionTextInput(guilds.owner_id)
            await interaction.response.send_modal(modal)

    @nextcord.ui.button(label='blacklist user', style=nextcord.ButtonStyle.danger, custom_id="ticketbuttonblacklist")
    async def button_callback2(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if button.custom_id == "ticketbuttonblacklist":
            perm_role = nextcord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
            member_highest_role = interaction.user.top_role
            if not member_highest_role >= perm_role:
                await interaction.response.send_message(f'❌ | you dont have permission', ephemeral=True)
                return
            try:
                substring = interaction.channel.name[len("ticket-"):]
                getmember = interaction.guild.get_member(int(substring))
            except:
                pass
            modal = TicketBlackListTextInput(getmember)
            await interaction.response.send_modal(modal)

class TicketDeletionTextInput(nextcord.ui.Modal):
    def __init__(self, user_id):
        super().__init__("delete ticket", timeout=1 * 60)
        self.user_id = user_id

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.short,
            placeholder="information or reason why youre deleting this ticket",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        callbackresponse = self.description.value
        if not callbackresponse:
            callbackresponse += ('ticket deleted with no reason')
        await ticket(interaction, action='delete', reason=f'{callbackresponse}')

class TicketBlackListTextInput(nextcord.ui.Modal):
    def __init__(self, getmember):
        super().__init__("ticket blacklist", timeout=1 * 60)
        self.getmember = getmember

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.short,
            placeholder="information or reason why youre blacklisting this user",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        callbackresponse = self.description.value
        if not callbackresponse:
            callbackresponse += ('blacklisted from tickets')
        await blacklist(interaction, type='ticket', action='add', member=self.getmember, reason=f'{callbackresponse}')

class TicketButtonCreator(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @nextcord.ui.button(label='create ticket', style=nextcord.ButtonStyle.green, custom_id="ticketbuttoncreator")
    async def button_callback(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if button.custom_id == "ticketbuttoncreator":
            for guilds in BOT.guilds:
                modal = TicketCreationTextInput(guilds.owner_id)
            await interaction.response.send_modal(modal)

class TicketCreationTextInput(nextcord.ui.Modal):
    def __init__(self, user_id):
        super().__init__("create ticket", timeout=1 * 60)
        self.user_id = user_id

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.short,
            placeholder="information or reason why youre creating your ticket",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        callbackresponse = self.description.value
        if not callbackresponse:
            callbackresponse += ('ticket created with no reason')
        await ticket(interaction, action='create', reason=f'{callbackresponse}')

# MODMAIL

class ModMailButtonInside(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @nextcord.ui.button(label='delete modmail', style=nextcord.ButtonStyle.secondary, custom_id="modmailbuttondeleter")
    async def button_callback(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if button.custom_id == "modmailbuttondeleter":
            support_role = nextcord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
            member_highest_role = interaction.user.top_role
            if not member_highest_role >= support_role:
                await interaction.response.send_message(f'❌ | you dont have permission', ephemeral=True)
                return
            for guilds in BOT.guilds:
                modal = ModMailDeletionTextInput(guilds.owner_id)
            await interaction.response.send_modal(modal)

    @nextcord.ui.button(label='blacklist user', style=nextcord.ButtonStyle.danger, custom_id="modmailbuttonblacklist")
    async def button_callback2(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if button.custom_id == "modmailbuttonblacklist":
            perm_role = nextcord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
            member_highest_role = interaction.user.top_role
            if not member_highest_role >= perm_role:
                await interaction.response.send_message(f'❌ | you dont have permission', ephemeral=True)
                return
            try:
                getmember = interaction.guild.get_member(int(interaction.channel.name))
            except:
                pass
            modal = ModMailBlackListTextInput(getmember)
            await interaction.response.send_modal(modal)

class ModMailDeletionTextInput(nextcord.ui.Modal):
    def __init__(self, user_id):
        super().__init__("modmail close", timeout=1 * 60)
        self.user_id = user_id

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.short,
            placeholder="information or reason why youre deleting this modmail",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        callbackresponse = self.description.value
        if not callbackresponse:
            callbackresponse += ('modmail deleted with no reason')
        await modmail(interaction, action='close', reason=f'{callbackresponse}')

class ModMailBlackListTextInput(nextcord.ui.Modal):
    def __init__(self, getmember):
        super().__init__("modmail blacklist", timeout=1 * 60)
        self.getmember = getmember

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.short,
            placeholder="information or reason why youre blacklisting this user",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        callbackresponse = self.description.value
        if not callbackresponse:
            callbackresponse += ('blacklisted from modmail')
        await blacklist(interaction, type='modmail', action='add', member=self.getmember, reason=f'{callbackresponse}')

BOT.run(TOKEN)
CON.close()