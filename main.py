import discord
from discord import Intents, app_commands
import asyncio
from discord.ext.commands import BucketType, Cog, BadArgument, command, cooldown, Bot, check
import random
import requests
import sqlite3
import re
import datetime
import json
import schedule
import aiohttp
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

from discord.ext import commands
import os

intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents)
client.help_command = None  # Menonaktifkan command bantuan bawaan

@client.event
async def on_ready():
  client.loop.create_task(change_activity())
  print('Logged in as ' + client.user.name + '!')
  log_channel_id = 1152922587140202516
  log_channel = client.get_channel(log_channel_id)
  embed = discord.Embed(title="Anime Update Bot is back online!", description=f"**Anime Update** Bot are back online!\nClient Ping : {round(client.latency * 1000)}ms", color=discord.Color.random())
  embed.set_footer(text='Watching Anime Update')
  await log_channel.send(embed=embed)
  try:
    synced = await client.tree.sync()
    print(f'Synced {len(synced)} Commands')
    guild_count = len(client.guilds)
    print(f"{guild_count} Discord Server(s).")
    client.loop.create_task(run_scheduled_tasks())
  except Exception as e:
    print(e)
    print('Worked')

# Fungsi untuk mengubah aktivitas bot
async def change_activity():
    while not client.is_closed():
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"Anime Update | Ping {round(client.latency * 1000)}ms")
        await client.change_presence(activity=activity)
        await asyncio.sleep(10)  # Tunggu selama 10 detik sebelum memperbarui lagi

try:
    with open('locked_commands.json', 'r') as file:
        command_locks = json.load(file)
except FileNotFoundError:
    command_locks = {}

def is_command_locked(command_name):
    def predicate(ctx):
        if command_name in command_locks and command_locks[command_name]:
            role = discord.utils.get(ctx.guild.roles, id=1153176392939352085)  # Replace with the actual role ID
            if role in ctx.author.roles:
                return True
            else:
                message = f'<:animeupdate:1154683499027116103> Command `{command_name}` is currently under development, try again later...'
                asyncio.create_task(ctx.send(message))
                return False
        return True
    return commands.check(predicate)

@client.command()
@commands.has_role(1153176392939352085)
async def lockcmd(ctx, command_name):
    command_locks[command_name] = True
    await ctx.send(f'<:animeupdate:1154683499027116103> Command `{command_name}` has been locked.')
    with open('locked_commands.json', 'w') as file:
        json.dump(command_locks, file, indent=4)

@client.command()
@commands.has_role(1153176392939352085)
async def unlockcmd(ctx, command_name):
    if command_name in command_locks:
        del command_locks[command_name]
        await ctx.send(f'<:animeupdate:1154683499027116103> Command `{command_name}` has been unlocked.')
        with open('locked_commands.json', 'w') as file:
            json.dump(command_locks, file, indent=4)
    else:
        await ctx.send(f'Command `{command_name}` already unlocked.')

def capitalize_title(text):
    words = text.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

@client.event
async def on_guild_join(guild):
    # Dapatkan pengguna yang menambahkan bot
    inviter = await guild.invites()
    inviter = inviter[0].inviter
    link_invite = 'https://discord.gg/S9HbVjeaXA'
    embed = discord.Embed(title='Thank You!', description=f"<:animeupdate:1154683499027116103> Hello, thank you for inviting me to your discord server! If you wish, please join our official Discord Server!\n{link_invite}", color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/1121744755936739388/d955b4a6104d695be8ee466d558310a5.png?size=1024')
    # Kirim DM ke pengguna yang menambahkan bot
    await inviter.send(embed=embed)

    # Kirim pesan ke default channel server saat bot bergabung
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(title='Thank You!', description='<:animeupdate:1154683499027116103> Hello, thank you for inviting me to your discord server. To find out what commands and information I have, please use the command /help!', color=discord.Color.random())
            embed.set_footer(text='Watching Anime Update')
            embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/1121744755936739388/d955b4a6104d695be8ee466d558310a5.png?size=1024')
            await channel.send(embed=embed)


class Myselect(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label='List Commands', emoji='💬',description='To see the list of commands provided by this bot', value='listcommands'),
            discord.SelectOption(label='List Games Commands', emoji='🎮',description='See the list of games commands provided by this bot', value='listgamescommands'),
            discord.SelectOption(label="What's new?", emoji='❓',description='Show the latest bot updates', value='whatsnew'),
            discord.SelectOption(label='About Bot', emoji='👤',description='Information about this bot', value='aboutbot'),
            discord.SelectOption(label='Support Server', emoji='🔗',description='Join Anime Update discord server', value='supportserver')
        ]

        super().__init__(placeholder='Select an option', options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]

        if selected_option == 'listcommands':
            response = "**List Commands :**\n/help\nTo see bot info\n/topmanga\nTop 10 Manga with the most votes\n/topanime\nTop 10 Anime with the most votes\n/mangaprofiles\nCheck Manga Profile\n/animeprofiles\nCheck Anime Profile\n/animeschedule\nCheck Upcoming Anime Schecule\n/voteanime\nVote your favorite anime!\n/votemanga\nVote your favorite manga!\n/warnmember\nWarn someone using this command\n/checkwarnmember\nCheck the warnings of a member\n/removewarnmember\nRemove recent warnings from a member\n/kickmember\nKick someone using this command\n/removekickmember\nRemove a kick from a member\n/banmember\nBan someone using this command\n/removebanmember\nRemove a ban from a member\n/animememes\nRandom Anime Memes\n/readmanga\nRead all manga you want!\n/setwelcome\nSet Welcome Message for your discord server\n/setgoodbye\nSet Goodbye Message for your discord server\n\nMore will add to this Bot"
        elif selected_option == 'listgamescommands':
            response = "**List Games Commands :**\n/guessanime\nGuess the name of the anime and earn Points!\n/leaderboardpoints\nTop 20 People with the most Points\n/guesscharacter\nGuess the name of the anime character and get points!\n/trueorfalseanime\nPlay True or False Anime and earn points!\n\n\nMore will add to this Bot"
        elif selected_option == 'whatsnew':
            response = "1. We have reduced the issue with 'The Interaction Failed' in some commands.\n2. We have been improving this bot server little by little"
        elif selected_option == 'aboutbot':
            today = datetime.today()
            day = today.strftime("%A")
            month = today.strftime("%B")
            date = today.strftime("%d")
            time = today.strftime("%I:%M %p")
            response = f"**Always Update ~Anime Update Bot**\n**Developers Bot :** whyyou_hey, theotiwa\n**Moderator :** doya7414, Jameson#8661\n**Last Update :** Today\n**Time Zone :** {day}, {month} {date} [{time}]"
        elif selected_option == 'supportserver':
            response = "✓ **Join the Anime Update Discord Server!** 🌸\nhttps://discord.gg/PtykX6G9jQ\n\nAnime Update is a Discord server created for anime and manga fans to gather and discuss our common hobbies.\n\n✓ Not only that, on the Anime Update discord server, you can:\n🔔 Always updated about Anime or Manga\n💭 Chat and discuss with fellow Anime or Manga lovers\n📜 Share Anime or Manga recommendations with others\n🛡️ There are moderators ready at any time if needed\n🔰 There is an Anime Update bot which has various commands that are useful for you Anime or Manga lovers!\n\n✓ **And much more! For that, join the Anime Update discord server right now!** 🌸"
        else:
            response = "You chose an unknown option."

        embed = discord.Embed(title='Anime Update Discord Bot',description=response,color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/1121744755936739388/d955b4a6104d695be8ee466d558310a5.png?size=1024')

        await interaction.response.edit_message(embed=embed)

class Myview(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Myselect())
        self.timeout = None

@client.hybrid_command(description='Need help? Try this command')
@is_command_locked('help')
async def help(ctx):
    embed = discord.Embed(title='Anime Update Discord Bot',description='<:animeupdate:1154683499027116103> Hello, how can I help you?',color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/1121744755936739388/d955b4a6104d695be8ee466d558310a5.png?size=1024')
    await ctx.send(embed=embed, view=Myview())

@client.hybrid_command(description='Tells us the bot ping')
@is_command_locked('ping')
async def ping(ctx):
  await ctx.send(f'Ping **{round(client.latency *1000)}**ms')

@client.event
async def on_command(ctx):
    log_channel_id = 1153089972128186511
    if isinstance(ctx.command, commands.Command):
        log_channel = client.get_channel(log_channel_id)
        user = ctx.author
        command_name = ctx.command.name
        server_name = ctx.guild.name

        if command_name.lower() == "close":
            return

        if command_name.lower() == "animescheduleca":
            return

        if command_name.lower() == "reply":
            return

        if command_name.lower() == "checkvotemanga":
            return

        if command_name.lower() == "checkvoteanime":
            return

        if command_name.lower() == "lockcmd":
            return

        if command_name.lower() == "unlockcmd":
            return

        await log_channel.send(f"Command '{command_name}' used by {user.name}#{user.discriminator} on server '{server_name}'")

@client.hybrid_command(description='Kick Someone use this command')
@commands.has_permissions(kick_members=True)
@is_command_locked('kickmember')
async def kickmember(ctx, member: discord.Member, *, reason=None):
  if member == ctx.author:
      await ctx.send("<:animeupdate:1154683499027116103> You cannot kick yourself.")
      return

  if member.bot:
      await ctx.send("<:animeupdate:1154683499027116103> Bots cannot be kicked.")
      return

  if member == ctx.guild.me:
      await ctx.send("<:animeupdate:1154683499027116103> I cannot be kicked.")
      return

  if member.top_role >= ctx.author.top_role:
      await ctx.send("<:animeupdate:1154683499027116103> You cannot kick a member with a higher or equal role.")
      return

  if reason is None:
    reason = "No reason provided."

  await member.kick(reason=reason)
  await ctx.send(
    f'<:animeupdate:1154683499027116103> Kicked {member.mention} from this discord server\n**Reason** : {reason}'
  )

  server_name = ctx.guild.name
  mod_name = ctx.author.name

  # Send DM to the kicked member
  dm_message = (
    f"You have been kicked from {server_name} server by {mod_name} for:\n{reason}\n"
    f"**Please note that this is not a permanent ban.**")
  await member.send(dm_message)

@kickmember.error
async def kickmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to kick members.")

@client.hybrid_command(description='Ban Someone use this command')
@is_command_locked('banmember')
@commands.has_permissions(ban_members=True)
async def banmember(ctx, member: discord.Member, duration: str, *, reason=None):
  if member == ctx.author:
      await ctx.send("<:animeupdate:1154683499027116103> You cannot ban yourself.")
      return

  if member.bot:
      await ctx.send("<:animeupdate:1154683499027116103> Bots cannot be banned.")
      return

  if member == ctx.guild.me:
      await ctx.send("<:animeupdate:1154683499027116103> I cannot be banned.")
      return

  if member.top_role >= ctx.author.top_role:
      await ctx.send("<:animeupdate:1154683499027116103> You cannot ban a member with a higher or equal role.")
      return

  if reason is None:
    reason = "No reason provided."

  duration = duration.lower()

  time_units = {
    's': ('Second(s)', 1),
    'second': ('Second(s)', 1),
    'seconds': ('Second(s)', 1),
    'm': ('Minute(s)', 60),
    'minute': ('Minute(s)', 60),
    'minutes': ('Minute(s)', 60),
    'h': ('Hour(s)', 3600),
    'hour': ('Hour(s)', 3600),
    'hours': ('Hour(s)', 3600),
    'd': ('Day(s)', 86400),
    'day': ('Day(s)', 86400),
    'days': ('Day(s)', 86400)
  }

  pattern = re.compile(r'(\d+)\s*([a-z]+)')
  match = pattern.match(duration)

  if not match:
    await ctx.send("Invalid duration format. Try Again.")
    return

  amount = int(match.group(1))
  unit = match.group(2)

  if unit not in time_units:
    await ctx.send("Invalid time unit. Try Again.")
    return

  unit_name, seconds = time_units[unit]

  await member.ban(reason=reason)
  await ctx.send(
    f'<:animeupdate:1154683499027116103> Banned {member.mention} from this discord server for {amount} {unit_name}\n**Reason** : {reason}'
  )

  server_name = ctx.guild.name
  mod_name = ctx.author.name

  # Send DM to the banned member
  dm_message = (
    f"You have been banned {amount} {unit_name} from {server_name} server by {mod_name} for:\n{reason}\n"
    f"**If you have any concerns or wish to appeal, please contact the server moderators.**"
  )
  await member.send(dm_message)

  # Unban the member after the specified duration
  await asyncio.sleep(seconds)
  await member.unban(reason="Ban duration expired.")

@banmember.error
async def banmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to ban members.")

# Remove a ban from a member
@client.hybrid_command(description='Remove a ban from a member')
@is_command_locked('removebanmember')
@commands.has_permissions(ban_members=True)
async def removebanmember(ctx, member: discord.Member):
    bans = await ctx.guild.bans()

    for ban_entry in bans:
        if ban_entry.user.id == member.id:
            await ctx.guild.unban(ban_entry.user, reason="Ban removed.")
            await ctx.send(f'<:animeupdate:1154683499027116103> Removed ban from {member.mention}')
            return

    await ctx.send(f'<:animeupdate:1154683499027116103>{member.mention} is not banned.')

@removebanmember.error
async def removebanmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to remove ban members.")

# Connect to database and create warnings table
conn = sqlite3.connect('warnings.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS warnings
             (server_id INTEGER, member_id INTEGER, mod_name TEXT, reason TEXT, warning_time INTEGER)''')
conn.commit()

@client.hybrid_command(description='Warn someone using this command')
@is_command_locked('warnmember')
@commands.has_permissions(manage_messages=True)
async def warnmember(ctx, member: discord.Member, *, reason=None):
    # Get the server ID
    server_id = ctx.guild.id

    if member == ctx.author:
        await ctx.send("<:animeupdate:1154683499027116103> You cannot warn yourself.")
        return

    if member.bot:
        await ctx.send("<:animeupdate:1154683499027116103> Bots cannot be warned.")
        return

    if member == ctx.guild.me:
        await ctx.send("<:animeupdate:1154683499027116103> I cannot be warned.")
        return

    if member.top_role >= ctx.author.top_role:
        await ctx.send("<:animeupdate:1154683499027116103> You cannot warn a member with a higher or equal role.")
        return

    if reason is None:
        reason = "No reason provided."

    server_name = ctx.guild.name
    mod_name = ctx.author.name

    # Insert warning into the database with server ID
    c.execute("INSERT INTO warnings (server_id, member_id, mod_name, reason, warning_time) VALUES (?, ?, ?, ?, ?)", (server_id, member.id, mod_name, reason, int(datetime.now().timestamp())))
    conn.commit()

    # Kirim pesan peringatan melalui DM
    dm_message = (
        f"You have been warned on {server_name} server by {mod_name} for:\n{reason}\n"
        f"**Please read the rules!** <:rubymad:1128152167795142656>"
    )
    await member.send(dm_message)

    await ctx.send(
        f'<:animeupdate:1154683499027116103> {member.mention} has been warned.\n**Reason**: {reason}'
    )

@warnmember.error
async def warnmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to warn members.")

# Check the warnings of a member
@client.hybrid_command(description='Check the warnings of a member')
@is_command_locked('checkwarnmember')
@commands.has_permissions(manage_messages=True)
async def checkwarnmember(ctx, member: discord.Member):
    # Get the server ID
    server_id = ctx.guild.id

    c.execute("SELECT rowid, mod_name, reason, datetime(warning_time, 'unixepoch') as warn_date FROM warnings WHERE server_id=? AND member_id=?", (server_id, member.id))
    warnings = c.fetchall()

    if warnings:
        warning_list = "\n".join([f"**Warning #{rowid}**\n{mod_name} [{warn_date}]\nReason: {reason}\n" for rowid, mod_name, reason, warn_date in warnings])
        embed = discord.Embed(title=f'Warnings for {member.name}', description=warning_list, color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title=f'Warnings for {member.name}', description=f'{member.name} has no warnings.', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

@checkwarnmember.error
async def checkwarnmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to check warn members.")

# Remove the most recent warnings from a member
@client.hybrid_command(description='Remove recent warnings from a member')
@is_command_locked('removewarnmember')
@commands.has_permissions(manage_messages=True)
async def removewarnmember(ctx, member: discord.Member, amount: int):
    # Get the server ID
    server_id = ctx.guild.id

    c.execute("SELECT rowid, mod_name, reason FROM warnings WHERE server_id=? AND member_id=? ORDER BY rowid DESC", (server_id, member.id))
    warnings = c.fetchall()

    if not warnings:
        await ctx.send(f'<:animeupdate:1154683499027116103> {member.name} has no warnings to remove.')
        return

    if amount <= 0 or amount > len(warnings):
        await ctx.send("Invalid amount. Please provide a valid amount of warnings to remove.")
        return

    for i in range(amount):
        rowid, mod_name, reason = warnings[i]
        c.execute("DELETE FROM warnings WHERE rowid=?", (rowid,))
        conn.commit()

    await ctx.send(f'<:animeupdate:1154683499027116103> Removed {amount} warning from {member.mention}.')

@removewarnmember.error
async def removewarnmember_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to remove warn members.")

conn_welcome = sqlite3.connect('welcome_config.db')
cursor_welcome = conn_welcome.cursor()

# Membuat tabel jika belum ada
cursor_welcome.execute('''
    CREATE TABLE IF NOT EXISTS welcome_config (
        guild_id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        message TEXT
    )
''')
conn_welcome.commit()

class WelcomeModal(discord.ui.Modal):
  def __init__(self, client):
      super().__init__(title="Welcome Message Setup")
      self.client = client
      self.add_item(discord.ui.TextInput(label="Welcome Message", placeholder="Please type the Welcome Message that you want to use...", style=discord.TextStyle.paragraph))

  async def on_submit(self, interaction: discord.Interaction):
      welcome_msg = self.children[0].value

      guild_id = interaction.guild.id
      welcome_channel_id = interaction.channel.id

      # Memasukkan atau memperbarui konfigurasi ke database
      cursor_welcome.execute('''
          INSERT INTO welcome_config (guild_id, channel_id, message)
          VALUES (?, ?, ?)
          ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id, message=excluded.message
      ''', (guild_id, welcome_channel_id, welcome_msg))
      conn_welcome.commit()

      embed = discord.Embed(title='The Welcome Message that you created has been set on your Discord Server!', description=f"**Channel Name** :{interaction.channel.mention}\n**New Message** :```{welcome_msg}```",color=discord.Color.random())
      embed.set_footer(text='Watching Anime Update')
      await interaction.response.send_message(embed=embed)

class WelcomeModalButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
      # Make sure the interaction comes from the original user
      return interaction.user == self.ctx.author

    @discord.ui.button(label="Welcome Message", style=discord.ButtonStyle.primary, custom_id="welcome_button")
    async def welcome_button(self, interaction: discord.Interaction, button):
      modal = WelcomeModal(client)
      await interaction.response.send_modal(modal)

@client.hybrid_command(description='Set Welcome message for your Discord Server')
@is_command_locked('setwelcome')
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, channel: discord.TextChannel):
    # Check if the provided channel is valid
    if not channel:
        await ctx.send("The channel specified is invalid. Please try again with a valid channel.")
        return

    view = WelcomeModalButton(ctx)

    embed = discord.Embed(title='Welcome Message Setup', description = '`{tagmember}` : To mention people who have just joined your Discord Server.\n\n**Please press the button below to type the Welcome Message**', color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')

    await ctx.send(embed=embed, view=view)

@client.event
async def on_member_join(member):
    guild_id = member.guild.id

    # Mengambil konfigurasi dari database
    cursor_welcome.execute('SELECT channel_id, message FROM welcome_config WHERE guild_id = ?', (guild_id,))
    config = cursor_welcome.fetchone()
    if config is None:
        return

    welcome_channel_id, welcome_message = config

    welcome_channel = member.guild.get_channel(welcome_channel_id)
    if welcome_channel is None:
        # Send error message to the user who set up the configuration
        user = member  # Use the member who triggered the event
        if user:
            await user.send("Invalid welcome channel. Please check your configuration.")
        return

    member_tag = member.mention
    welcome_message_with_tag = welcome_message.replace("{tagmember}", member_tag)
    await welcome_channel.send(welcome_message_with_tag)

# Membuat atau terhubung ke database SQLite untuk konfigurasi perpisahan
conn_goodbye = sqlite3.connect('goodbye_config.db')
cursor_goodbye = conn_goodbye.cursor()

# Membuat tabel jika belum ada
cursor_goodbye.execute('''
    CREATE TABLE IF NOT EXISTS goodbye_config (
        guild_id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        message TEXT
    )
''')
conn_goodbye.commit()

class GoodbyeModal(discord.ui.Modal):
  def __init__(self, client):
      super().__init__(title="Goodbye Message Setup")
      self.client = client
      self.add_item(discord.ui.TextInput(label="Goodbye Message", placeholder="Please type the Goodbye Message that you want to use...", style=discord.TextStyle.paragraph))

  async def on_submit(self, interaction: discord.Interaction):
      goodbye_msg = self.children[0].value

      guild_id = interaction.guild.id
      goodbye_channel_id = interaction.channel.id

      # Memasukkan atau memperbarui konfigurasi ke database
      cursor_goodbye.execute('''
          INSERT INTO goodbye_config (guild_id, channel_id, message)
          VALUES (?, ?, ?)
          ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id, message=excluded.message
      ''', (guild_id, goodbye_channel_id, goodbye_msg))
      conn_goodbye.commit()

      embed = discord.Embed(title='The Goodbye Message that you created has been set on your Discord Server!', description=f"**Channel Name** :{interaction.channel.mention}\n**New Message** :```{goodbye_msg}```",color=discord.Color.random())
      embed.set_footer(text='Watching Anime Update')
      await interaction.response.send_message(embed=embed)

class GoodbyeModalButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
      # Make sure the interaction comes from the original user
      return interaction.user == self.ctx.author

    @discord.ui.button(label="Goodbye Message", style=discord.ButtonStyle.primary, custom_id="goodbye_button")
    async def goodbye_button(self, interaction: discord.Interaction, button):
      modal = GoodbyeModal(client)
      await interaction.response.send_modal(modal)

@client.hybrid_command(description='Set Goodbye message for your Discord Server')
@commands.has_permissions(administrator=True)
@is_command_locked('setgoodbye')
async def setgoodbye(ctx, channel: discord.TextChannel):
    # Check if the provided channel is valid
    if not channel:
        await ctx.send("The channel specified is invalid. Please try again with a valid channel.")
        return

    view = GoodbyeModalButton(ctx)

    embed = discord.Embed(title='Goodbye Message Setup', description = '`{tagmember}` : To mention people who have just leave your Discord Server.\n\n**Please press the button below to type the Goodbye Message**', color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')

    await ctx.send(embed=embed, view=view)

@client.event
async def on_member_remove(member):
    guild_id = member.guild.id

    # Mengambil konfigurasi dari database
    cursor_goodbye.execute('SELECT channel_id, message FROM goodbye_config WHERE guild_id = ?', (guild_id,))
    config = cursor_goodbye.fetchone()
    if config is None:
        return

    goodbye_channel_id, goodbye_message = config

    goodbye_channel = member.guild.get_channel(goodbye_channel_id)
    if goodbye_channel is None:
        # Send error message to the user who set up the configuration
        user = member  # Use the member who triggered the event
        if user:
            await user.send("Invalid goodbye channel. Please check your configuration.")
        return

    member_tag = member.mention
    goodbye_message_with_tag = goodbye_message.replace("{tagmember}", member_tag)
    await goodbye_channel.send(goodbye_message_with_tag)

@client.command(name='hello')
async def hello(ctx):
  await ctx.send("Hello!")

@client.hybrid_command(description='Check Anime Schedule')
@is_command_locked('animeschedule')
async def animeschedule(ctx):
    await ctx.defer()
    url = "https://animecountdown.com/soon"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    anime_elements = soup.find_all(class_="countdown-content-trending-item")

    today = datetime.today()
    day = today.strftime("%A").lower()  # Change to lowercase
    month = today.strftime("%B")
    date = today.strftime("%d")

    anime_list = []

    for index, anime in enumerate(anime_elements, start=1):
        anime_name = anime.find("countdown-content-trending-item-title").text
        genre_anime = anime.find("countdown-content-trending-item-desc").text

        countdown_time = anime.find("countdown-content-trending-item-countdown")["data-time"]
        countdown_days = int(countdown_time) // (3600 * 24)
        countdown_hours = (int(countdown_time) // 3600) % 24
        countdown_minutes = (int(countdown_time) // 60) % 60

        if countdown_days == 0:
            if countdown_hours == 0:
              countdown_text = f"[{countdown_minutes} Minutes]"
            elif countdown_hours > 2:
              countdown_text = f"[{countdown_hours} Hours]"
            else:
              countdown_text = f"[{countdown_hours}h {countdown_minutes}m]"

            message = f"{index}. **{countdown_text}** {anime_name} ({genre_anime})"
            anime_list.append(message)

    if anime_list:
        thumbnail_url = "https:" + anime_elements[0]["data-poster"]

        anime_message = "\n".join(anime_list)
        embed = discord.Embed(
            title=f"Anime Schedule [{day.capitalize()}, {month} {date}]",
            description=f"{anime_message}\n\n**Always update every time you use this command.**",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text="Watching Anime Update")

        await ctx.send(embed=embed)
    else:
        await ctx.send("No anime schedules for today.")

manga_voting_options = {}
manga_voted_members = {}

# Load data from JSON files if they exist
try:
    with open('manga_voting_options.json', 'r') as f:
        manga_voting_options = json.load(f)
except FileNotFoundError:
    manga_voting_options = {}

try:
    with open('manga_voted_members.json', 'r') as f:
        manga_voted_members = json.load(f)
except FileNotFoundError:
    manga_voted_members = {}

class BotVoteButtonView(discord.ui.View):
    def __init__(self, manga_title, member_id):
        super().__init__()
        self.manga_title = manga_title
        self.member_id = member_id
        self.timeout = None
        self.add_item(discord.ui.Button(label="Vote Anime Update Bot", url="https://top.gg/bot/1121744755936739388/vote"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.member_id

    @discord.ui.button(label="Cancel Vote", style=discord.ButtonStyle.danger)
    async def cancel_vote(self, interaction: discord.Interaction, manga_title: str):
        manga_title = self.manga_title
        member_id = self.member_id

        if str(member_id) in manga_voted_members and manga_title in manga_voted_members[str(member_id)]['voted_manga']:
            manga_voting_options[manga_title] -= 1
            manga_voted_members[str(member_id)]['voted_manga'].remove(manga_title)
            manga_voted_members[str(member_id)]['last_vote_time'] = None

            if manga_voting_options[manga_title] <= 0:
                del manga_voting_options[manga_title]

            with open('manga_voting_options.json', 'w') as f:
                json.dump(manga_voting_options, f, indent=4)

            with open('manga_voted_members.json', 'w') as f:
                json.dump(manga_voted_members, f, indent=4)

            await interaction.response.send_message(f"You have successfully canceled your vote for **{manga_title}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You have not voted for **{manga_title}** yet.", ephemeral=True)

@client.hybrid_command(description='Vote your favorite manga!')
@is_command_locked('votemanga')
async def votemanga(ctx, *, manga_name):
    if str(ctx.author.id) in manga_voted_members:
        last_vote_time = manga_voted_members[str(ctx.author.id)]['last_vote_time']
        if last_vote_time and isinstance(last_vote_time, str):
            last_vote_datetime = datetime.strptime(last_vote_time, '%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.now()

            if current_datetime < last_vote_datetime:
                cooldown = last_vote_datetime - current_datetime
                cooldown_seconds = cooldown.total_seconds()

                if cooldown_seconds > 0:
                    remaining_time = ""
                    if cooldown_seconds >= 86400:
                        remaining_days = int(cooldown_seconds // 86400)
                        remaining_time = f"{remaining_days} days"
                    elif cooldown_seconds >= 3600:
                        remaining_hours = int(cooldown_seconds // 3600)
                        remaining_time = f"{remaining_hours} hours"
                    elif cooldown_seconds >= 60:
                        remaining_minutes = int(cooldown_seconds // 60)
                        remaining_time = f"{remaining_minutes} minutes"
                    else:
                        remaining_time = f"{int(cooldown_seconds)} seconds"

                    embed = discord.Embed(
                        title='Something went wrong',
                        description=f'You have already voted this week.\nCooldown remaining: **{remaining_time}**',
                        color=discord.Color.random()
                    )
                    embed.set_footer(text='Watching Anime Update')
                    await ctx.send(embed=embed)
                    return

    url = f'https://myanimelist.net/search/prefix.json?type=manga&keyword={manga_name}&v=1'
    response = requests.get(url).json()
    manga_results = response['categories'][0]['items']

    if manga_results:
        manga_info = manga_results[0]
        manga_title = manga_info['name']
        manga_image_url = manga_info['image_url']

        if manga_title in manga_voting_options:
            manga_voting_options[manga_title] += 1
        else:
            manga_voting_options[manga_title] = 1

        member_id = str(ctx.author.id)

        if member_id in manga_voted_members:
            manga_voted_members[member_id]['voted_manga'].append(manga_title)
        else:
            manga_voted_members[member_id] = {'voted_manga': [manga_title],}

        manga_voted_members[member_id]['last_vote_time'] = (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')

        embed = discord.Embed(title='Thank you for voting this manga!', description=f'You have voted for a Manga named **{manga_title}**, you have to wait another week for you to get a chance to vote again!', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        embed.set_thumbnail(url=manga_image_url) 
        view = BotVoteButtonView(manga_title, ctx.author.id)
        await ctx.send(embed=embed, view=view)

        with open('manga_voting_options.json', 'w') as f:
            json.dump(manga_voting_options, f, indent=4)

        with open('manga_voted_members.json', 'w') as f:
            json.dump(manga_voted_members, f, indent=4)
    else:
        embed = discord.Embed(title='Something went wrong', description='No manga found with that name.', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        await ctx.send(embed=embed, view=BotVoteButtonView())

@client.hybrid_command(description='Top 10 Manga with the most votes')
@is_command_locked('topmanga')
async def topmanga(ctx):
    if not manga_voting_options:
        await ctx.send("No votes have been cast yet.")
        return

    sorted_options = sorted(manga_voting_options.items(), key=lambda x: x[1], reverse=True)
    top_10_options = sorted_options[:10]
    results_text = '\n'.join([f"{index + 1}. {manga} : {votes} {'votes' if votes > 1 else 'vote'}" for index, (manga, votes) in enumerate(top_10_options)])

    embed = discord.Embed(title='Top 10 Manga with the most votes', description=f"{results_text}\n\nYou haven't voted for your favorite manga yet? Vote now using the command `/votemanga`", color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    await ctx.send(embed=embed)

@client.command(description='Check the list of manga voted by a specific member')
@is_command_locked('checkvotemanga')
async def checkvotemanga(ctx, member_name):
    member_found = None
    for guild in client.guilds:
        for member in guild.members:
            if member.name.lower() == member_name.lower():
                member_found = member
                break

    if not member_found:
        await ctx.send(f"Member '{member_name}' not found.")
        return

    member_id = str(member_found.id)

    if member_id not in manga_voted_members:
        await ctx.send(f"{member_found.display_name} hasn't voted for any manga yet.")
        return

    voted_manga = manga_voted_members[member_id]['voted_manga']
    if not voted_manga:
        await ctx.send(f"{member_found.display_name} hasn't voted for any manga yet.")
    else:
        manga_votes = {manga: voted_manga.count(manga) for manga in set(voted_manga)}
        voted_manga_text = "\n".join([f"{index + 1}. {manga} [{votes}x]" for index, (manga, votes) in enumerate(manga_votes.items())])
        embed = discord.Embed(
            title=f'Manga voted by {member_found.display_name}',
            description=f"{voted_manga_text}\n\n**Total Votes**: {len(voted_manga)}",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=member_found.avatar.url)
        embed.set_footer(text='Watching Anime Update')
        await ctx.send(embed=embed)

anime_voting_options = {}
anime_voted_members = {}

# Load data from JSON files if they exist
try:
    with open('anime_voting_options.json', 'r') as f:
        anime_voting_options = json.load(f)
except FileNotFoundError:
    anime_voting_options = {}

try:
    with open('anime_voted_members.json', 'r') as f:
        anime_voted_members = json.load(f)
except FileNotFoundError:
    anime_voted_members = {}

class BotVoteButtonViews(discord.ui.View):
    def __init__(self, anime_title, member_id):
        super().__init__()
        self.anime_title = anime_title
        self.member_id = member_id
        self.timeout = None
        self.add_item(discord.ui.Button(label="Vote Anime Update Bot", url="https://top.gg/bot/1121744755936739388/vote"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.member_id

    @discord.ui.button(label="Cancel Vote", style=discord.ButtonStyle.danger)
    async def cancel_vote(self, interaction: discord.Interaction, anime_title: str):
        anime_title = self.anime_title
        member_id = self.member_id

        if str(member_id) in anime_voted_members and anime_title in anime_voted_members[str(member_id)]['voted_anime']:
            anime_voting_options[anime_title] -= 1
            anime_voted_members[str(member_id)]['voted_anime'].remove(anime_title)
            anime_voted_members[str(member_id)]['last_vote_time'] = None

            if anime_voting_options[anime_title] <= 0:
                del anime_voting_options[anime_title]

            with open('anime_voting_options.json', 'w') as f:
                json.dump(anime_voting_options, f, indent=4)

            with open('anime_voted_members.json', 'w') as f:
                json.dump(anime_voted_members, f, indent=4)

            await interaction.response.send_message(f"You have successfully canceled your vote for **{anime_title}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You have not voted for **{anime_title}** yet.", ephemeral=True)

@client.hybrid_command(description='Vote your favorite anime!')
async def voteanime(ctx, *, anime_name):
    if str(ctx.author.id) in anime_voted_members:
      last_vote_time = anime_voted_members[str(ctx.author.id)]['last_vote_time']
      if last_vote_time and isinstance(last_vote_time, str):
          last_vote_datetime = datetime.strptime(last_vote_time, '%Y-%m-%d %H:%M:%S')
          current_datetime = datetime.now()

          if current_datetime < last_vote_datetime:
              cooldown = last_vote_datetime - current_datetime
              cooldown_seconds = cooldown.total_seconds()

              if cooldown_seconds > 0:
                  remaining_time = ""
                  if cooldown_seconds >= 86400:
                      remaining_days = int(cooldown_seconds // 86400)
                      remaining_time = f"{remaining_days} days"
                  elif cooldown_seconds >= 3600:
                      remaining_hours = int(cooldown_seconds // 3600)
                      remaining_time = f"{remaining_hours} hours"
                  elif cooldown_seconds >= 60:
                      remaining_minutes = int(cooldown_seconds // 60)
                      remaining_time = f"{remaining_minutes} minutes"
                  else:
                      remaining_time = f"{int(cooldown_seconds)} seconds"

                  embed = discord.Embed(
                      title='Something went wrong',
                      description=f'You have already voted this week.\nCooldown remaining : **{remaining_time}**',
                      color=discord.Color.random()
                  )
                  embed.set_footer(text='Watching Anime Update')
                  await ctx.send(embed=embed)
                  return

    url = f'https://myanimelist.net/search/prefix.json?type=anime&keyword={anime_name}&v=1'
    response = requests.get(url).json()
    anime_results = response['categories'][0]['items']

    if anime_results:
        anime_info = anime_results[0]
        anime_title = anime_info['name']
        anime_image_url = anime_info['image_url']

        if anime_title in anime_voting_options:
            anime_voting_options[anime_title] += 1
        else:
            anime_voting_options[anime_title] = 1

        member_id = str(ctx.author.id)

        if member_id in anime_voted_members:
            anime_voted_members[member_id]['voted_anime'].append(anime_title)
        else:
            anime_voted_members[member_id] = {'voted_anime': [anime_title],}

        anime_voted_members[member_id]['last_vote_time'] = (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')

        embed = discord.Embed(title='Thank you for voting this anime!', description=f'You have voted for an Anime named **{anime_title}**, you have to wait another week for you to get a chance to vote again!', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        embed.set_thumbnail(url=anime_image_url)
        view = BotVoteButtonViews(anime_title, ctx.author.id)
        await ctx.send(embed=embed, view=view)

        with open('anime_voting_options.json', 'w') as f:
            json.dump(anime_voting_options, f, indent=4)

        with open('anime_voted_members.json', 'w') as f:
            json.dump(anime_voted_members, f, indent=4)
    else:
        embed = discord.Embed(title='Something went wrong', description='No anime found with that name.', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        await ctx.send(embed=embed, view=BotVoteButtonViews())

@client.hybrid_command(description='Top 10 Anime with the most votes')
async def topanime(ctx):
    if not anime_voting_options:
        await ctx.send("No votes have been cast yet.")
        return

    sorted_options = sorted(anime_voting_options.items(), key=lambda x: x[1], reverse=True)
    top_10_options = sorted_options[:10]
    results_text = '\n'.join([f"{index + 1}. {anime} : {votes} {'votes' if votes > 1 else 'vote'}" for index, (anime, votes) in enumerate(top_10_options)])

    embed = discord.Embed(title='Top 10 Anime with the most votes', description=f"{results_text}\n\nYou haven't voted for your favorite anime yet? Vote now using the command `/voteanime`", color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    await ctx.send(embed=embed)

@client.command(description='Check the list of anime voted by a specific member')
async def checkvoteanime(ctx, *, member_name):
    member_found = None
    for guild in client.guilds:
        for member in guild.members:
            if member.name.lower() == member_name.lower():
                member_found = member
                break

    if not member_found:
        await ctx.send(f"Member '{member_name}' not found.")
        return

    member_id = str(member_found.id)

    if member_id not in anime_voted_members:
        await ctx.send(f"{member_found.display_name} hasn't voted for any anime yet.")
        return

    voted_anime = anime_voted_members[member_id]['voted_anime']
    if not voted_anime:
        await ctx.send(f"{member_found.display_name} hasn't voted for any anime yet.")
    else:
        anime_votes = {anime: voted_anime.count(anime) for anime in set(voted_anime)}
        voted_anime_text = "\n".join([f"{index + 1}. {anime} [{votes}x]" for index, (anime, votes) in enumerate(anime_votes.items())])
        embed = discord.Embed(
            title=f'Anime voted by {member_found.display_name}',
            description=f"{voted_anime_text}\n\n**Total Votes**: {len(voted_anime)}",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=member_found.avatar.url)
        embed.set_footer(text='Watching Anime Update')
        await ctx.send(embed=embed)

@commands.cooldown(1, 10, commands.BucketType.user)
@is_command_locked('animememes')
@client.hybrid_command(description="Random Anime Memes")
async def animememes(ctx):
    await ctx.defer()

    total_pages = 145  # Set the total number of pages to scrape
    base_url = 'https://www.memedroid.com/memes/tag/anime'

    # Generate a random page number between 1 and 145
    random_page = random.randint(1, total_pages)

    meme_images = []
    page_url = f'{base_url}?page={random_page}'

    # Fetching the website content
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting meme images from the current random page
    meme_images = soup.find_all('img', class_='img-responsive grey-background')

    if meme_images:
        # Selecting a random meme image from the current random page
        random_meme = random.choice(meme_images).get('src')

        # Creating an embed
        embed = discord.Embed(title="Random Anime Meme", color=discord.Color.random())
        embed.set_image(url=random_meme)
        embed.set_footer(text='Watching Anime Update')

        # Sending the embed to the Discord channel
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Something went wrong',description='No anime memes found.')
        embed.set_footer(text='Watching Anime Update')
        await ctx.send(embed=embed)

@animememes.error
async def animememes_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

POINTS_FILE = "points.json"
ANIME_DATA_FILE = "anime_data.json"
player_in_game = {}

def load_anime_data():
    try:
        with open(ANIME_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_anime_data(anime_data):
    with open(ANIME_DATA_FILE, 'w') as f:
        json.dump(anime_data, f, indent=4)

def load_user_points():
    try:
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_points(points_data):
    with open(POINTS_FILE, 'w') as f:
        json.dump(points_data, f, indent=4)

def is_answer_unique(answer):
    anime_data = load_anime_data()
    for entry in anime_data:
        if entry["answer"].lower() == answer.lower():
            return False
    return True

@commands.cooldown(1, 180, commands.BucketType.user)
@client.hybrid_command(description='Guess the name of the anime and earn points!')
@is_command_locked('guessanime')
@app_commands.describe(member = "Use this if you want to play with other members!")
async def guessanime(ctx, member: discord.Member = None):
  if member is not None:
      # Check if the member is not the command invoker and the bot is not trying to play with itself
      if member == ctx.author or member == client.user:
          await ctx.send("You can't play with yourself or the bot.")
          return

      # Check if both players have at least 3 points
      user_points = load_user_points()
      invoker_points = user_points.get(str(ctx.author.id), 0)
      invitee_points = user_points.get(str(member.id), 0)
      if invoker_points < 3 or invitee_points < 3:
          if invoker_points < 3 and invitee_points < 3:
              await ctx.send(f"{ctx.author.mention}, You and the player you invite need to have at least 3 points to play in `/guessanime`.")
          elif invoker_points < 3:
              await ctx.send(f"{ctx.author.mention}, you need to have at least 3 points to play in `/guessanime`.")
          else:
              await ctx.send(f"The player you invite to play needs to have at least 3 points to play in `/guessanime`.")
          return

      if ctx.author.id in player_in_game:
          await ctx.send(f"{ctx.author.mention}, you are already in a game. Please finish your current game first.")
          return

      # Check if the invitee is already in a game
      if member.id in player_in_game:
          await ctx.send(f"{member.mention} is already in a game. Please wait for them to finish their current game.")
          return

      # Check if both players reacted with a checkmark
      def check_reaction(reaction, user):
          return user == member and str(reaction.emoji) == '✅' and reaction.message.author == ctx.author

      try:
          # Send the invitation message and wait for the invitee to react
          invite_msg = await ctx.send(f"{member.mention}, {ctx.author.mention} has invited you to play Guess Anime Multiplayer!\n"
                                      f"React with ✅ to accept the invitation and start the game.")
          await invite_msg.add_reaction('✅')

          def check_invitation(reaction, user):
              return user == member and str(reaction.emoji) == '✅' and reaction.message.id == invite_msg.id

          await client.wait_for('reaction_add', timeout=30.0, check=check_invitation)

          # Set the status of both players to be in a game
          player_in_game[ctx.author.id] = True
          player_in_game[member.id] = True

          # Load anime data and pick a random question
          anime_data = load_anime_data()
          question_data = random.choice(anime_data)
          question = question_data['question']
          clues = question_data['clues']

          # Create an embed with the initial question and clue 1 in the description
          embed = discord.Embed(title='Guess the anime!', description=f'```{question}```\n**You have 40 seconds to answer, every 10 seconds the bot will give the second and third clues**\n\nClue 1: {clues[0]}', color=discord.Color.random())
          embed.set_footer(text='Watching Anime Update')

          question_message = await ctx.send(embed=embed)

          async def send_clues(embed):
              # Update the embed with additional clues one by one with a 10-second delay
              for i in range(1, len(clues)):
                  await asyncio.sleep(10)
                  embed.description += f'\nClue {i + 1}: {clues[i]}'
                  await question_message.edit(embed=embed)

          # Create a task to send the clues while waiting for the user's response
          clue_task = asyncio.create_task(send_clues(embed))

          def check_answer(message):
              return message.author in (ctx.author, member) and message.channel == ctx.channel

          # Wait for one of the players to answer correctly or until time is up
          user_points = load_user_points()
          points_earned = 0
          correct_answer = question_data['answer'].lower()
          winner = None
          loser = None

          while True:
              try:
                  user_response = await client.wait_for('message', timeout=40, check=check_answer)
                  user_answer = user_response.content.lower()

                  if user_answer == correct_answer:
                      # Determine the points the user earns based on the clue they answered
                      if len(embed.description.split('\n')) == 4:
                          points_earned = 9
                      elif len(embed.description.split('\n')) == 5:
                          points_earned = 4
                      elif len(embed.description.split('\n')) == 6:
                          points_earned = 3

                      # Determine the winner
                      if user_response.author == ctx.author:
                          winner = ctx.author
                          loser = member
                      else:
                          winner = member
                          loser = ctx.author

                      # Update the user's points and save it to the JSON file
                      winner_username = str(winner.id)
                      loser_username = str(loser.id)

                      user_points[winner_username] = user_points.get(winner_username, 0) + points_earned
                      user_points[loser_username] = max(user_points.get(loser_username, 0) - points_earned, 0)

                      save_user_points(user_points)

                      sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

                      # Find the winner's position in the leaderboard
                      winner_position = None
                      for index, (username, points) in enumerate(sorted_points, start=1):
                          if username == winner_username:
                              winner_position = index
                              break

                      # Cancel the clue task if the user answered correctly
                      clue_task.cancel()
                      if winner_position <= 20 and points_earned > 0:
                          embed.description = "The game has ended."
                          await question_message.edit(embed=embed)
                          await ctx.send(f'Congratulations {winner.mention}! Your answer is correct. You earned {points_earned} points.\n**Status** : {winner.mention} are in {winner_position} position on the /leaderboardpoints.\n{loser.mention}, you lost {points_earned} points.')
                      else:
                          if points_earned > 0:
                              embed.description = "The game has ended."
                              await question_message.edit(embed=embed)
                              await ctx.send(f'Congratulations {winner.mention}! Your answer is correct. You earned {points_earned} points.\n{loser.mention}, you lost {points_earned} points.')
                      break
                  else:
                      await ctx.send("Sorry, your answer is incorrect. Try again.")
              except asyncio.TimeoutError:
                  embed.description = "The game has ended."
                  await question_message.edit(embed=embed)
                  await ctx.send("Time is up! No one managed to answer.")
                  break
      except asyncio.TimeoutError:
          await ctx.send(f"{ctx.author.mention}, The player you invited did not accept the invitation on time.")

      # Game is over, reset the status of both players
      player_in_game.pop(ctx.author.id, None)
      player_in_game.pop(member.id, None)
  else:
      # Single-player mode logic here (Same as the original /guessanime command)
      with open('anime_data.json', 'r') as f:
          anime_data = json.load(f)

      # Get a random question from anime data
      question_data = random.choice(anime_data)
      question = question_data['question']
      clues = question_data['clues']

      # Create an embed with the initial question and clue 1 in the description
      embed = discord.Embed(title='Guess the anime!', description=f'```{question}```\n**You have 40 seconds to answer, every 10 seconds the bot will give the second and third clues**\n\nClue 1: {clues[0]}', color=discord.Color.random())
      embed.set_footer(text='Watching Anime Update')
      question_message = await ctx.send(embed=embed)

      async def send_clues(embed):
          # Update the embed with additional clues one by one with a 10-second delay
          for i in range(1, len(clues)):
              await asyncio.sleep(10)
              embed.description += f'\nClue {i + 1}: {clues[i]}'
              await question_message.edit(embed=embed)

      # Create a task to send the clues while waiting for the user's response
      clue_task = asyncio.create_task(send_clues(embed))

      def check(message):
          return message.author == ctx.author and message.channel == ctx.channel

      user_points = load_user_points()
      points_earned = 0

      try:
          user_response = await client.wait_for('message', timeout=40, check=check)

          if user_response.content.lower() == question_data['answer'].lower():
              # Determine the points the user earns based on the clue they answered
              if len(embed.description.split('\n')) == 4:
                  points_earned = 9
              elif len(embed.description.split('\n')) == 5:
                  points_earned = 4
              elif len(embed.description.split('\n')) == 6:
                  points_earned = 3

              # Update the user's points and save it to the JSON file
              username = str(ctx.author.id)  # Get the username
              user_points[username] = user_points.get(username, 0) + points_earned
              save_user_points(user_points)

              sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

              # Find the user's position in the leaderboard
              user_position = None
              for index, (username, points) in enumerate(sorted_points, start=1):
                  if username == str(ctx.author.id):
                      user_position = index
                      break

              # Cancel the clue task if the user answered correctly
              clue_task.cancel()
              if user_position <= 20:
                  embed.description = "The game has ended."
                  await question_message.edit(embed=embed)
                  await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned {points_earned} points.\n**Status** : You are in {user_position} position on the /leaderboardpoints.')
              else:
                  embed.description = "The game has ended."
                  await question_message.edit(embed=embed)
                  await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned {points_earned} points.')
          else:
              clue_task.cancel()
              embed.description = "The game has ended."
              await question_message.edit(embed=embed)
              await ctx.send(f'Sorry {ctx.author.mention}, your answer is incorrect. Try again after 3 minutes cooldown.')
      except asyncio.TimeoutError:
          embed.description = "The game has ended."
          await question_message.edit(embed=embed)
          await ctx.send(f'{ctx.author.mention}, time is up! Try again after 3 minutes cooldown.')

@guessanime.error
async def guessanime_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

@client.hybrid_command(description='Added questions and answers for /guessanime')
@is_command_locked('addguessanime')
@commands.has_role(1170897207059284079)
async def addguessanime(ctx, question: str, answer: str, clue1: str, clue2: str, clue3: str):
    if not is_answer_unique(answer):
        await ctx.send(f"The answer '{answer}' already exists in the database. Please provide a unique answer.")
        return
    # Create the new question data
    new_question_data = {
        "question": question,
        "answer": answer,
        "clues": [clue1, clue2, clue3]
    }

    # Load the existing anime data
    anime_data = load_anime_data()

    # Add the new question data to the list
    anime_data.append(new_question_data)

    # Save the updated anime data
    save_anime_data(anime_data)

    await ctx.send("New anime question added successfully!")

@addguessanime.error
async def addguessanime_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Only Admins who have special access can run this command")

player_in_game_character = {}
CHARACTER_DATA_FILE = "anime_data2.json"

def load_character_data():
    try:
        with open(CHARACTER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_character_data(character_data):
    with open(CHARACTER_DATA_FILE, 'w') as f:
        json.dump(character_data, f, indent=4)

def is_character_answer_unique(answer):
    character_data = load_character_data()
    for entry in character_data:
        for ans in entry["answer"]:
            if ans.lower() == answer.lower():
                return False
    return True

@commands.cooldown(1, 180, commands.BucketType.user)
@client.hybrid_command(description='Guess the name of the anime character and get points!')
@app_commands.describe(member = "Use this if you want to play with other members!")
@is_command_locked('guesscharacter')
async def guesscharacter(ctx, member: discord.Member = None):
    if member is not None:
        if member == ctx.author or member == client.user:
            await ctx.send("You can't play with yourself or the bot.")
            return

        user_points = load_user_points()
        invoker_points = user_points.get(str(ctx.author.id), 0)
        invitee_points = user_points.get(str(member.id), 0)

        if invoker_points < 3 or invitee_points < 3:
            if invoker_points < 3 and invitee_points < 3:
                await ctx.send(f"{ctx.author.mention}, You and the player you invite need to have at least 3 points to play in `/guesscharacter`.")
            elif invoker_points < 3:
                await ctx.send(f"{ctx.author.mention}, you need to have at least 3 points to play in `/guesscharacter`.")
            else:
                await ctx.send(f"The player you invite to play needs to have at least 3 points to play in `/guesscharacter`.")
            return

        if ctx.author.id in player_in_game_character:
            await ctx.send(f"{ctx.author.mention}, you are already in a game. Please finish your current game first.")
            return

        if member.id in player_in_game_character:
            await ctx.send(f"{member.mention} is already in a game. Please wait for them to finish their current game.")
            return

        def check_reaction(reaction, user):
            return user == member and str(reaction.emoji) == '✅' and reaction.message.author == ctx.author

        try:
            invite_msg = await ctx.send(f"{member.mention}, {ctx.author.mention} has invited you to play Guess Anime Character Multiplayer!\n"
                                        f"React with ✅ to accept the invitation and start the game.")
            await invite_msg.add_reaction('✅')

            def check_invitation(reaction, user):
                return user == member and str(reaction.emoji) == '✅' and reaction.message.id == invite_msg.id

            await client.wait_for('reaction_add', timeout=30.0, check=check_invitation)

            player_in_game_character[ctx.author.id] = True
            player_in_game_character[member.id] = True

            character_data = load_character_data()
            question_data = random.choice(character_data)
            question = question_data['question']
            image_url = question_data['image']
            clues = question_data['clues']

            embed = discord.Embed(title='Guess the Anime Character!', description=f'```{question}```\n**You have 40 seconds to answer, every 10 seconds the bot will give the second and third clues**\n\nClue 1: {clues[0]}', color=discord.Color.random())
            embed.set_image(url=image_url)
            embed.set_footer(text='Watching Anime Update')

            question_message = await ctx.send(embed=embed)

            async def send_clues(embed):
                for i in range(1, len(clues)):
                    await asyncio.sleep(10)
                    embed.description += f'\nClue {i + 1}: {clues[i]}'
                    await question_message.edit(embed=embed)

            clue_task = asyncio.create_task(send_clues(embed))

            def check_answer(message):
                return message.author in (ctx.author, member) and message.channel == ctx.channel

            user_points = load_user_points()
            points_earned = 0

            while True:
                try:
                    user_response = await client.wait_for('message', timeout=40, check=check_answer)
                    user_answer = user_response.content.lower()

                    if user_answer in [ans.lower() for ans in question_data['answer']]:
                        if len(embed.description.split('\n')) == 4:
                            points_earned = 9
                        elif len(embed.description.split('\n')) == 5:
                            points_earned = 4
                        elif len(embed.description.split('\n')) == 6:
                            points_earned = 3

                        winner = ctx.author if user_response.author == ctx.author else member
                        loser = member if user_response.author == ctx.author else ctx.author

                        winner_username = str(winner.id)
                        loser_username = str(loser.id)

                        user_points[winner_username] = user_points.get(winner_username, 0) + points_earned
                        user_points[loser_username] = max(user_points.get(loser_username, 0) - points_earned, 0)

                        save_user_points(user_points)

                        sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

                        winner_position = None
                        for index, (username, points) in enumerate(sorted_points, start=1):
                            if username == winner_username:
                                winner_position = index
                                break

                        clue_task.cancel()
                        if winner_position <= 20 and points_earned > 0:
                            embed.description = "The game has ended."
                            embed.set_image(url=None)
                            await question_message.edit(embed=embed)
                            await ctx.send(f'Congratulations {winner.mention}! Your answer is correct. You earned {points_earned} points.\n**Status** : {winner.mention} are in {winner_position} position on the /leaderboardpoints.\n{loser.mention}, you lost {points_earned} points.')
                        else:
                            if points_earned > 0:
                                embed.description = "The game has ended."
                                embed.set_image(url=None)
                                await question_message.edit(embed=embed)
                                await ctx.send(f'Congratulations {winner.mention}! Your answer is correct. You earned {points_earned} points.\n{loser.mention}, you lost {points_earned} points.')
                        break
                    else:
                        await ctx.send("Sorry, your answer is incorrect. Try again.")
                except asyncio.TimeoutError:
                    embed.description = "The game has ended."
                    embed.set_image(url=None)
                    await question_message.edit(embed=embed)
                    await ctx.send("Time is up! No one managed to answer.")
                    break
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, The player you invited did not accept the invitation on time.")

        player_in_game_character.pop(ctx.author.id, None)
        player_in_game_character.pop(member.id, None)
    else:
        with open(CHARACTER_DATA_FILE, 'r') as f:
            character_data = json.load(f)

        question_data = random.choice(character_data)
        question = question_data['question']
        image_url = question_data['image']
        clues = question_data['clues']

        embed = discord.Embed(title='Guess the Anime Character!', description=f'```{question}```\n**You have 40 seconds to answer, every 10 seconds the bot will give the second and third clues**\n\nClue 1: {clues[0]}', color=discord.Color.random())
        embed.set_image(url=image_url)
        embed.set_footer(text='Watching Anime Update')
        question_message = await ctx.send(embed=embed)

        async def send_clues(embed):
            for i in range(1, len(clues)):
                await asyncio.sleep(10)
                embed.description += f'\nClue {i + 1}: {clues[i]}'
                await question_message.edit(embed=embed)

        clue_task = asyncio.create_task(send_clues(embed))

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        user_points = load_user_points()
        points_earned = 0

        try:
            user_response = await client.wait_for('message', timeout=40, check=check)

            user_response_lower = user_response.content.lower()

            if user_response_lower in [ans.lower() for ans in question_data['answer']]:
                if len(embed.description.split('\n')) == 4:
                    points_earned = 9
                elif len(embed.description.split('\n')) == 5:
                    points_earned = 4
                elif len(embed.description.split('\n')) == 6:
                    points_earned = 3

                username = str(ctx.author.id)
                user_points[username] = user_points.get(username, 0) + points_earned
                save_user_points(user_points)

                sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

                user_position = None
                for index, (username, points) in enumerate(sorted_points, start=1):
                    if username == str(ctx.author.id):
                        user_position = index
                        break

                clue_task.cancel()
                if user_position <= 20:
                    embed.description = "The game has ended."
                    embed.set_image(url=None)
                    await question_message.edit(embed=embed)
                    await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned {points_earned} points.\n'
                                   f'**Status**: You are in {user_position} position on the /leaderboardpoints.')
                else:
                    embed.description = "The game has ended."
                    embed.set_image(url=None)
                    await question_message.edit(embed=embed)
                    await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned {points_earned} points.')
            else:
                clue_task.cancel()
                embed.description = "The game has ended."
                embed.set_image(url=None)
                await question_message.edit(embed=embed)
                await ctx.send(f'Sorry {ctx.author.mention}, your answer is incorrect. Try again after 3 minutes cooldown.')
        except asyncio.TimeoutError:
            embed.description = "The game has ended."
            embed.set_image(url=None)
            await question_message.edit(embed=embed)
            await ctx.send(f'{ctx.author.mention}, time is up! Try again after 3 minutes cooldown.')

@guesscharacter.error
async def guesscharacter_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # If the command is not found, reset the status of the player
        player_in_game.pop(ctx.author.id, None)
        player_in_game_character.pop(ctx.author.id, None)
    else:
        # Handle other errors here
        print(error)

@client.hybrid_command(description='Added questions and answers for /guesscharacter')
@is_command_locked('addguesscharacter')
@commands.has_role(1170897207059284079)
async def addguesscharacter(ctx, question: str, image_url: str, answer: str, clue1: str, clue2: str, clue3: str):
    answer_list = answer.split(", ")  # Memisahkan jawaban berdasarkan koma dan spasi
    if not is_character_answer_unique(answer):
        await ctx.send(f"The answer '{answer}' already exists in the database. Please provide a unique answer.")
        return
    # Create the new character data
    new_character_data = {
        "question": question,
        "image": image_url,
        "answer": answer_list,
        "clues": [clue1, clue2, clue3]
    }

    # Load the existing character data
    character_data = load_character_data()

    # Add the new character data to the list
    character_data.append(new_character_data)

    # Save the updated character data
    save_character_data(character_data)

    await ctx.send("New anime character question added successfully!")

@addguesscharacter.error
async def addguesscharacter_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Only Admins who have special access can run this command")

with open('trueorfalseanime.json', 'r') as json_file:
    questions_data = json.load(json_file)

@commands.cooldown(1, 180, commands.BucketType.user)
@client.hybrid_command(description='Play True or False Anime and earn points!')
@is_command_locked('trueorfalseanime')
async def trueorfalseanime(ctx):
    # Choose a random question
    question = random.choice(questions_data['questions'])
    question_text = question['question']
    answer = question['answer']

    # Create an embed for the question
    embed = discord.Embed(title='True or False Anime', description=f'{question_text}\n\n**You have 10 seconds to answer!**\n**Be careful with trick questions!**', color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    question_message = await ctx.send(embed=embed)

    # Add checkmark and X reactions to the question message
    await question_message.add_reaction('✅')  # Checkmark
    await question_message.add_reaction('❌')  # X

    def check(reaction, user):
        return user == ctx.author and reaction.message == question_message and str(reaction.emoji) in ['✅', '❌']

    try:
        reaction, user = await client.wait_for('reaction_add', check=check, timeout=10)

        user_answer = '✅' if str(reaction.emoji) == '✅' else '❌'

        if user_answer == answer:
            # Check and update user points
            user_points = load_user_points()
            if str(ctx.author.id) not in user_points:
                user_points[str(ctx.author.id)] = 3
            else:
                user_points[str(ctx.author.id)] += 3

            save_user_points(user_points)

            sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

            # Find the user's position in the leaderboard
            user_position = None
            for index, (username, points) in enumerate(sorted_points, start=1):
                if username == str(ctx.author.id):
                    user_position = index
                    break

            if user_position <= 20:
                embed.description = "The game has ended."
                await question_message.edit(embed=embed)
                await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned 3 points.\n**Status**: You are in {user_position} position on the /leaderboardpoints.')
            else:
                embed.description = "The game has ended."
                await question_message.edit(embed=embed)
                await ctx.send(f'Congratulations {ctx.author.mention}! Your answer is correct. You earned 3 points.')
        else:
            embed.description = "The game has ended."
            await question_message.edit(embed=embed)
            await ctx.send(f'Sorry {ctx.author.mention}, your answer is incorrect. Try again after 3 minutes cooldown.')
    except asyncio.TimeoutError:
        embed.description = "The game has ended."
        await question_message.edit(embed=embed)
        await ctx.send(f'{ctx.author.mention}, time is up! Try again after 3 minutes cooldown.')
        return

@trueorfalseanime.error
async def trueorfalseanime_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

@client.command(description='Add points to a member')
@commands.has_role(1153176392939352085)
@is_command_locked('addpoints')
async def addpoints(ctx, member_name: str, amount: int):
    user_points = load_user_points()

    if member_name.isnumeric():
        member = discord.utils.get(client.users, id=int(member_name))
        member_name = member.name
    else:
        member = discord.utils.get(client.users, name=member_name)

    if not member:
        await ctx.send(f"<:animeupdate:1154683499027116103> User '{member_name}' not found.")
        return

    user_id = str(member.id)
    points = user_points.get(user_id, 0)
    user_points[user_id] = points + amount
    save_user_points(user_points)
    await ctx.send(f'<:animeupdate:1154683499027116103> {amount} points added to {member_name}. New total: {points + amount} points.')

@client.command(description='Remove points from a member')
@commands.has_role(1153176392939352085)
@is_command_locked('removepoints')
async def removepoints(ctx, member_name: str, amount: int):
    user_points = load_user_points()

    # Find the member by name in any server the bot is part of
    if member_name.isnumeric():
        member = discord.utils.get(client.users, id=int(member_name))
        member_name = member.name
    else:
        member = discord.utils.get(client.users, name=member_name)

    if not member:
        await ctx.send(f"<:animeupdate:1154683499027116103> User '{member_name}' not found.")
        return

    user_id = str(member.id)
    points = user_points.get(user_id, 0)
    if points >= amount:
        user_points[user_id] = points - amount
        save_user_points(user_points)
        await ctx.send(f'<:animeupdate:1154683499027116103>{amount} points removed from {member_name}. New total: {points - amount} points.')
    else:
        await ctx.send(f"<:animeupdate:1154683499027116103> Sorry, {member_name} doesn't have {amount} points.")

class HelpPoints(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None

    @discord.ui.button(label='How to Get Points?', style=discord.ButtonStyle.green, custom_id='help_points')
    async def help_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('**How to Get Points?**\n\nYou can get and collect as many points as possible by using commands that use a points system such as `/guessanime`, `/guesscharacter` and `/trueorfalseanime`. Good Luck!', ephemeral=True)

@client.hybrid_command(description='Top 20 People with the highest points')
@is_command_locked('leaderboardpoints')
async def leaderboardpoints(ctx):
    view = HelpPoints()
    user_points = load_user_points()

    if not user_points:
        await ctx.send("No points data available.")
        return

    sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

    await ctx.defer()

    leaderboard_text = ""
    for index, (user_id, points) in enumerate(sorted_points[:20], start=1):
        try:
          user = await client.fetch_user(int(user_id))
          username = user.name
        except discord.NotFound:
          username = "Unknown User"

        leaderboard_text += f"{index}. **{username} :** {points} points\n"

    embed = discord.Embed(title='Top 20 Users with the Highest Points', description=leaderboard_text, color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')

    await ctx.send(embed=embed, view=view)

@client.hybrid_command(description='See member information here!')
async def userinfo(ctx, member: discord.Member):
    member = member or ctx.author
    user_points = load_user_points()

    embed = discord.Embed(title=member.name, color=member.color)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text='Watching Anime Update')
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    points = user_points.get(str(member.id), 0)
    embed.add_field(name="Points", value=points, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Discord", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

    await ctx.send(embed=embed)

@commands.cooldown(1, 10, commands.BucketType.user)
@client.hybrid_command(
    name="mangaprofiles",
    description="Check Manga Profile Here!",
        )
@is_command_locked('mangaprofiles')
async def mangaprofiles(ctx, name: str):
    await ctx.defer()

    if name.isdigit():  # If the query is a number, treat it as the manga ID
        manga_id = name
    else:  # Otherwise, treat it as the manga title
        # Send a GET request to the search API to find the manga ID by title
        search_url = f"https://myanimelist.net/search/prefix.json?type=manga&keyword={name}&v=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                manga_data = await response.json()

        # Retrieve the manga ID from the search results
        if manga_data and 'categories' in manga_data and manga_data['categories']:
            manga_id = manga_data['categories'][0]['items'][0]['id']
        else:
            embed = discord.Embed(title='No manga found with that title.', color=discord.Color.random())
            embed.set_footer(text='Watching Anime Update')
            await ctx.send(embed=embed)
            return

    # Construct the manga URL using the ID
    url = f"https://myanimelist.net/manga/{manga_id}"

    # Send a GET request to the manga URL and retrieve the HTML content
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')

    # Find the manga information on the page
    manga_title_element = soup.find('span', itemprop='name')
    manga_title = manga_title_element.contents[0].strip() if manga_title_element and manga_title_element.contents else "Title not found."

    manga_image_element = soup.find('img', itemprop='image')
    manga_image_url = manga_image_element['data-src'] if manga_image_element else "Image not found."

    manga_synopsis_element = soup.find('span', itemprop='description')
    manga_synopsis = manga_synopsis_element.text.strip() if manga_synopsis_element else "Synopsis not found."

    manga_type_element = soup.find('span', string='Type:')
    manga_type = manga_type_element.find_next('a').text.strip() if manga_type_element else "Type not found."

    manga_volumes_element = soup.find('span', string='Volumes:')
    manga_volumes = manga_volumes_element.next_sibling.strip() if manga_volumes_element else "Volumes not found."

    manga_chapters_element = soup.find('span', string='Chapters:')
    manga_chapters = manga_chapters_element.next_sibling.strip() if manga_chapters_element else "Chapters not found."

    manga_status_element = soup.find('span', string='Status:')
    manga_status = manga_status_element.next_sibling.strip() if manga_status_element else "Status not found."

    manga_published_element = soup.find('span', string='Published:')
    manga_published = manga_published_element.next_sibling.strip() if manga_published_element else "Published not found."

    manga_genres_element = soup.find('span', itemprop='genre')
    manga_genres = []
    if manga_genres_element:
        genres_elements = manga_genres_element.find_next_siblings('a')
        for genres_element in genres_elements:
            genre = genres_element.text.strip()
            manga_genres.append(genre)
    if not manga_genres:
        manga_genres = ["Genres not found."]

    manga_themes_element = soup.find('span', string='Themes:')
    manga_themes = []
    if manga_themes_element:
        themes_elements = manga_themes_element.find_next_siblings('a')
        for themes_element in themes_elements:
            themes = themes_element.text.strip()
            manga_themes.append(themes)
    else:
        manga_themes = ["Themes not found."]

    manga_demographic_element = soup.find('span', string='Demographic:')
    manga_demographic = []
    if manga_demographic_element:
        demographic_elements = manga_demographic_element.find_next_siblings('a')
        for demographic_element in demographic_elements:
            demographic = demographic_element.text.strip()
            manga_demographic.append(demographic)
    else:
        manga_demographic = ["Demographic not found."]

    manga_serialization_element = soup.find('span', string='Serialization:')
    manga_serialization = manga_serialization_element.find_next('a').text.strip() if manga_serialization_element else "Serialization not found."

    manga_authors_element = soup.find('span', string='Authors:')
    manga_authors = manga_authors_element.find_next('a').text.strip() if manga_authors_element else "Authors not found."

    # Prepare the manga information as a response
    embed = discord.Embed(title=manga_title,description=f"**Synopsis**\n{manga_synopsis}\n\n**Information**\nType: {manga_type}\nVolumes: {manga_volumes}\nChapters: {manga_chapters}\nStatus: {manga_status}\nPublished: {manga_published}\nGenres: {', '.join(manga_genres)}\nThemes: {', '.join(manga_themes)}\nDemographic: {', '.join(manga_demographic)}\nSerialization: {manga_serialization}\nAuthors: {manga_authors}",color=discord.Color.random())
    embed.set_thumbnail(url=manga_image_url)
    embed.set_footer(text="Watching Anime Update")
    await ctx.send(embed=embed)

@mangaprofiles.error
async def mangaprofiles_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

@commands.cooldown(1, 10, commands.BucketType.user)
@client.hybrid_command(
    name="animeprofiles",
    description="Check Anime Profile Here!",
        )
@is_command_locked('animeprofiles')
async def animeprofiles(ctx, name: str):
    if name:
      await ctx.defer()

      if name.isdigit():
          anime_id = name
      else:
          search_url = f"https://myanimelist.net/search/prefix.json?type=anime&keyword={name}&v=1"
          async with aiohttp.ClientSession() as session:
              async with session.get(search_url) as response:
                  if response.status == 200:
                      anime_data = await response.json()
                      if anime_data and 'categories' in anime_data and anime_data['categories']:
                          anime_id = anime_data['categories'][0]['items'][0]['id']
                      else:
                          embed = discord.Embed(title='No anime found with that title.', color=discord.Color.random())
                          embed.set_footer(text='Watching Anime Update')
                          await ctx.send(embed=embed)
                          return
                  else:
                      embed = discord.Embed(title='No anime found with that title.', color=discord.Color.random())
                      embed.set_footer(text='Watching Anime Update')
                      await ctx.send(embed=embed)
                      return

    # Construct the anime URL using the ID
    url = f"https://myanimelist.net/anime/{anime_id}"

    # Send a GET request to the anime URL and retrieve the HTML content
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers={'User-Agent': 'DiscordBot (https://github.com/Rapptz/discord.py 2.3.1) Python/3.10 aiohttp/3.8.3'}) as response:
          response.raise_for_status()
          soup = BeautifulSoup(await response.text(), 'html.parser')

    # Find the manga information on the page
    anime_title_element = soup.find('h1', class_='title-name h1_bold_none')
    anime_title = anime_title_element.text.strip() if anime_title_element else "Title not found."

    anime_synopsis_element = soup.find('p', itemprop='description')
    anime_synopsis = anime_synopsis_element.text.strip() if anime_synopsis_element else "Synopsis not found."

    anime_image_element = soup.find('img', itemprop='image')
    anime_image_url = anime_image_element['data-src'] if anime_image_element else "Image not found."

    anime_type_element = soup.find('span', string='Type:')
    anime_type = anime_type_element.find_next('a').text.strip() if anime_type_element else "Type not found."

    anime_episodes_element = soup.find('span', string='Episodes:')
    anime_episodes = anime_episodes_element.next_sibling.strip() if anime_episodes_element else "Volumes not found."

    anime_status_element = soup.find('span', string='Status:')
    anime_status = anime_status_element.next_sibling.strip() if anime_status_element else "Status not found."

    anime_aired_element = soup.find('span', string='Aired:')
    anime_aired = anime_aired_element.next_sibling.strip() if anime_aired_element else "Aired not found."

    anime_premiered_element = soup.find('span', string='Premiered:')
    anime_premiered = anime_premiered_element.find_next('a').text.strip() if anime_premiered_element else "Premiered not found."

    anime_broadcast_element = soup.find('span', string='Broadcast:')
    anime_broadcast = anime_broadcast_element.next_sibling.strip() if anime_broadcast_element else "Broadcast not found."

    anime_producers_element = soup.find('span', string='Producers:')
    anime_producers = []
    if anime_producers_element:
        producers_elements = anime_producers_element.find_next_siblings('a')
        for producers_element in producers_elements:
            producers = producers_element.text.strip()
            anime_producers.append(producers)
    if not anime_producers:
        anime_producers = ["Producers not found."]

    anime_licensors_element = soup.find('span', string='Licensors:')
    anime_licensors = []
    if anime_licensors_element:
        licensors_elements = anime_licensors_element.find_next_siblings('a')
        for licensors_element in licensors_elements:
            licensors = licensors_element.text.strip()
            anime_licensors.append(licensors)
    if not anime_licensors:
        anime_licensors = ["Licensors not found."]

    anime_studios_element = soup.find('span', string='Studios:')
    anime_studios = []
    if anime_studios_element:
        studios_elements = anime_studios_element.find_next_siblings('a')
        for studios_element in studios_elements:
            studios = studios_element.text.strip()
            anime_studios.append(studios)
    if not anime_studios:
        anime_studios = ["Studios not found."]

    anime_source_element = soup.find('span', string='Source:')
    anime_source = anime_source_element.next_sibling.strip() if anime_source_element else "Source not found."

    anime_genres_element = soup.find('span', itemprop='genre')
    anime_genres = []
    if anime_genres_element:
        genres_elements = anime_genres_element.find_next_siblings('a')
        for genres_element in genres_elements:
            genre = genres_element.text.strip()
            anime_genres.append(genre)
    if not anime_genres:
        anime_genres = ["Genres not found."]

    anime_themes_element = soup.find('span', string='Themes:')
    anime_themes = []
    if anime_themes_element:
        themes_elements = anime_themes_element.find_next_siblings('a')
        for themes_element in themes_elements:
            themes = themes_element.text.strip()
            anime_themes.append(themes)
    else:
        anime_themes = ["Themes not found."]

    anime_demographic_element = soup.find('span', string='Demographic:')
    anime_demographic = []
    if anime_demographic_element:
        demographic_elements = anime_demographic_element.find_next_siblings('a')
        for demographic_element in demographic_elements:
            demographic = demographic_element.text.strip()
            anime_demographic.append(demographic)
    else:
        anime_demographic = ["Demographic not found."]

    anime_duration_element = soup.find('span', class_='dark_text', string='Duration:')
    anime_duration = anime_duration_element.next_sibling.strip() if anime_duration_element else "Duration not found."


    anime_rating_element = soup.find('span', class_='dark_text', string='Rating:')
    anime_rating = anime_rating_element.next_sibling.strip() if anime_rating_element else "Rating not found."

    # Prepare the manga information as a response
    embed = discord.Embed(title=anime_title,description=f"**Synopsis**\n{anime_synopsis}\n\n**Information**\nType: {anime_type}\nEpisodes: {anime_episodes}\nStatus: {anime_status}\nAired: {anime_aired}\nPremiered: {anime_premiered}\nBroadcast: {anime_broadcast}\nProducers: {', '.join(anime_producers)}\nLicensors: {', '.join(anime_licensors)}\nStudios: {', '.join(anime_studios)}\nSource: {anime_source}\nGenres: {', '.join(anime_genres)}\nThemes: {', '.join(anime_themes)}\nDemographic: {', '.join(anime_demographic)}\nDuration: {anime_duration}\nRating: {anime_rating}",color=discord.Color.random())
    embed.set_thumbnail(url=anime_image_url)
    embed.set_footer(text="Watching Anime Update")
    await ctx.send(embed=embed)

@animeprofiles.error
async def animeprofiles_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

class MyModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title='Skip Page')
        self.view = view
        self.add_item(discord.ui.TextInput(label='Page Number', placeholder='Enter the page number you want to skip to...', required=True, min_length=1, max_length=5))

    async def on_submit(self, interaction: discord.Interaction):
        # Get the page number from the input
        page_number = int(self.children[0].value)
        embed = discord.Embed(title='Loading...', description='Trying to skip to the next manga page...', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        await interaction.response.edit_message(embed=embed)
        await self.view.send_manga_page(page_number)

# MangaView for check /readmanga command (404 error code = 30%)
class MangaView(discord.ui.View):
    def __init__(self, ctx, manga_name, chapter, page):
        super().__init__()
        self.ctx = ctx
        self.manga_name = manga_name.lower()
        self.chapter = chapter
        self.page = page
        self.editable_message = None
        self.manga_found = False  # Initialize the flag

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Make sure the interaction comes from the original user
        return interaction.user == self.ctx.author

    @discord.ui.button(label='Skip Page', style=discord.ButtonStyle.danger, custom_id='skip_page_button')
    async def skip_page_button(self, interaction: discord.Interaction, button):
        # Add the modal to the response
        await interaction.response.send_modal(MyModal(self))

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.primary, custom_id='previous_button')
    async def previous_button(self, interaction: discord.Interaction, button):
        # Calculate the previous page number
        previous_page = self.page - 1
        embed = discord.Embed(title='Loading...', description='Trying to go back to the previous manga page...', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        await interaction.response.edit_message(embed=embed)
        await self.send_manga_page(previous_page)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary, custom_id='next_button')
    async def next_button(self, interaction: discord.Interaction, button):
        # Calculate the next page number
        next_page = self.page + 1
        embed = discord.Embed(title='Loading...', description='Trying to go to the next manga page...', color=discord.Color.random())
        embed.set_footer(text='Watching Anime Update')
        await interaction.response.edit_message(embed=embed)
        await self.send_manga_page(next_page)

    async def search_manga(self):
        if self.manga_found:
          return

        # Get the first character of the manga name
        first_char = self.manga_name[0].lower()

        # Construct the directory URL for the first character
        directory_url = f'https://rmanga.app/directory/{first_char}'

        async with aiohttp.ClientSession() as session:
          async with session.get(directory_url) as response:
            if response.status != 200:
                embed = discord.Embed(title='Something went wrong', description='Failed to find the manga you were looking for. Try again', color=discord.Color.random())
                embed.set_footer(text='Watching Anime Update')
                await self.editable_message.edit(embed=embed)
                return

            soup = BeautifulSoup(await response.text(), 'html.parser')
            manga_links = soup.find_all('li')

            for manga_link in manga_links:
                manga_name_elem = manga_link.find('a')
                if manga_name_elem:
                    manga_name = manga_name_elem.text.strip().lower()

                    if manga_name == self.manga_name:
                        manga_url = manga_name_elem['href']
                        manga_names = manga_url.split('/')[-1]

                        self.manga_found = True
                        self.manga_name = manga_names
                        return

    async def send_manga_page(self, page):
        # Find the manga directory if not already found
        await self.search_manga()

        if not self.manga_found:
            # If manga is not found, display a message and return
            embed = discord.Embed(title='Something went wrong', description="It looks like the manga you are looking for can't be found. If you are trying to find the name of the manga in Japanese, now try looking for the name of the manga in English", color=discord.Color.random())
            embed.set_footer(text='Watching Anime Update')
            await self.editable_message.edit(embed=embed)
            return

        # Now you have the manga ID, you can proceed to fetch and display the manga pages.
        manga_url = f'https://rmanga.app/{self.manga_name}/chapter-{self.chapter}/{page}'

        async with aiohttp.ClientSession() as session:
          async with session.get(manga_url) as response:
              if response.status != 200:
                  embed = discord.Embed(title='Something went wrong', description='Failed to find the page manga you were looking for. Try again', color=discord.Color.random())
                  embed.set_footer(text='Watching Anime Update')
                  await self.editable_message.edit(embed=embed)
                  return

              soup = BeautifulSoup(await response.text(), 'html.parser')
              img_tags = soup.find_all('img')

              image_url = None
              for img_tag in img_tags:
                  if 'src' in img_tag.attrs:
                      image_url = img_tag['src']
                      if image_url.startswith('https://readm.org/uploads/chapter_files'):
                          break

              self.page = page

              if image_url:
                  embed = discord.Embed(title='Read Manga', description=f'Chapter {self.chapter} - Page {self.page}', color=discord.Color.random())
                  embed.set_footer(text='Watching Anime Update')
                  embed.set_image(url=image_url)
                  await self.editable_message.edit(embed=embed, view=self)
              else:
                  embed = discord.Embed(title='Something went wrong', description='It seems that the manga page you are looking for cannot be found. Try again', color=discord.Color.random())
                  embed.set_footer(text='Watching Anime Update')
                  await self.editable_message.edit(embed=embed)

@client.hybrid_command(description='Read all manga you want!')
@is_command_locked('readmanga')
@commands.cooldown(1, 180, commands.BucketType.user)
async def readmanga(ctx, manga_name, chapter, page):
    # Convert 'page' to an integer
    page = int(page)

    manga_view = MangaView(ctx, manga_name, chapter, page)
    embed = discord.Embed(title='Loading...', description='Looking for a manga you want to read...', color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    manga_view.editable_message = await ctx.send(embed=embed)
    await manga_view.send_manga_page(page)

@readmanga.error
async def readmanga_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Handle cooldown error
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

# Nama file database SQLite
DATABASE_NAME = "webhook_messages.db"

# ID thread yang diizinkan untuk /newsupdate (ganti dengan ID thread yang sesuai)
allowed_threads = [1153090748435136563, 1153090815858573463]

# Fungsi untuk membuat tabel jika belum ada
def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS webhook_messages
                 (message_id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan pesan ke database
def add_news_to_db(message_id, content, timestamp):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO webhook_messages (message_id, content, timestamp) VALUES (?, ?, ?)", (message_id, content, timestamp))
    conn.commit()
    conn.close()

def get_news_embed():
    today = datetime.today()
    day = today.strftime("%A")
    month = today.strftime("%B")
    date = today.strftime("%d")
    embed = discord.Embed(title=f"News Anime & Manga Update [{day}, {month} {date}]", color=discord.Color.random())
    embed.set_footer(text='Watching Anime Update')
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM webhook_messages ORDER BY message_id DESC LIMIT 5")  # Ambil 5 pesan terakhir
    news_list = c.fetchall()
    conn.close()

    if news_list:
        for idx, news_content in enumerate(news_list, start=1):
            embed.add_field(name=f"{idx}. {news_content[0]}", value="\u200b", inline=False)
    else:
        embed.add_field(name="There is no latest news today.", value="\u200b", inline=False)

    return embed

# Command untuk menampilkan /newsupdate
@client.command()
@is_command_locked('newsupdate')
async def newsupdate(ctx):
    embed = get_news_embed()
    await ctx.send(embed=embed)

# Function to reset news update status
def reset_news_update():
    # Clear the news data from the database or perform any other necessary reset actions
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM webhook_messages")
    conn.commit()
    conn.close()

# Schedule the reset to happen daily at 00:00
schedule.every().day.at("00:00").do(reset_news_update)

# Function to run the scheduled tasks (e.g., check if any tasks are due and execute them)
async def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# Ketika bot dijalankan, buat tabel jika belum ada
create_table()

# Menyimpan pesan dalam format JSON
def save_to_json(message_content):
    data = {"content": message_content}
    with open('saved_messages.json', 'a') as file:
        json.dump(data, file)
        file.write('\n')

# Menyimpan pesan dalam format JSON
def save_to_jsons(message_content):
    data = {"content": message_content}
    with open('project_saved_messages.json', 'a') as file:
        json.dump(data, file)
        file.write('\n')

mail_support_file = "mail_support.json"

# Load existing mail support data from the file
try:
    with open(mail_support_file, "r") as file:
        mail_support_data = json.load(file)
except FileNotFoundError:
    mail_support_data = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    target_thread_name = "🎁・daily-rewards-logs"

    if message.guild is not None and message.channel.name == target_thread_name:
        save_to_json(message.content)

        if "[" in message.content and "]" in message.content:
            username = message.content.split("[")[1].split("]")[0]

            user_points = load_user_points()

            if username in user_points:
                user_points[username] += 2
            else:
                user_points[username] = 2

            save_user_points(user_points)

    project_thread_name = "🎁・theotiwa-project"

    if message.guild is not None and message.channel.name == project_thread_name:
        save_to_jsons(message.content)

        if "[" in message.content and "]" in message.content:
            username = message.content.split("[")[1].split("]")[0]
            if "(" in message.content and ")" in message.content:
                points_to_add = message.content.split("(")[1].split(")")[0]
                user_points = load_user_points()

                if username in user_points:
                    user_points[username] += int(points_to_add)
                else:
                    user_points[username] = int(points_to_add)

                save_user_points(user_points)

    if message.webhook_id and message.channel.id in allowed_threads:
        add_news_to_db(message.id, message.clean_content, str(message.created_at))

    user_id = str(message.author.id)
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:

      if user_id in cooldowns and time.time() - cooldowns[user_id] < 60:
          remaining_cooldown = round(60 - (time.time() - cooldowns[user_id]))
          await message.author.send(f"<:animeupdate:1154683499027116103> You are still on cooldown. Please wait {remaining_cooldown} seconds before opening the mail support again.")
          return

      if user_id in mail_support_data and mail_support_data[user_id].get("rules_accepted", False):

        await send_user_message_to_support_channel(message)
        await message.author.send("<:animeupdate:1154683499027116103> Waiting for a reply from Moderator...")
      else:
        await send_rules(message)

    await client.process_commands(message)

async def send_rules(message):
  user_id = str(message.author.id)
  embed = discord.Embed(
    title='Rules Anime Update Mail Support',
    description=
    "1. Be respectful and patient.\n2. Spam messages are prohibited.\n3. Ask your questions and Don't just say hi or something similar\n4. Don't cause drama or problems with moderators.\n5. Do not edit messages that have been sent because we cannot see edited messages\n\nIf you violate the rules during Mail Support. Your Mail Support will be closed or you could be blacklisted from Mail Support\n\n**React with ✅ if you agree to these rules or ❌ if you disagree. You have 1 minute to react.**",
    color=discord.Color.random())
  embed.set_footer(text='Watching Anime Update')
  rules_message = await message.author.send(embed=embed)

  await rules_message.add_reaction("✅")
  await rules_message.add_reaction("❌")

  try:
    reaction, _ = await client.wait_for('reaction_add',
                                        timeout=60.0,
                                        check=lambda r, u: u == message.author
                                        and r.message.id == rules_message.id)
    if str(reaction.emoji) == "✅":
        await message.author.send("<:animeupdate:1154683499027116103> Waiting for a reply from Moderator...")

        # If the user is in mail_support_data, update rules_accepted to True
        if user_id in mail_support_data:
            mail_support_data[user_id]["rules_accepted"] = True
        else:
            # If not, add the user ID to mail_support_data with rules_accepted set to True
            mail_support_data[user_id] = {"rules_accepted": True}

        # Save the updated mail support data back to the file
        with open(mail_support_file, "w") as file:
            json.dump(mail_support_data, file)

        # Proceed with mail support
        await send_user_message_to_support_channel(message)
    else:
        await message.author.send(
            "<:animeupdate:1154683499027116103> You have disagreed to the rules. You are not allowed to open mail support until you agree to the rules."
        )
  except asyncio.TimeoutError:
    await message.author.send(
        "<:animeupdate:1154683499027116103> You took too long to react. You are not allowed to open mail support until you agree to the rules."
    )

async def send_user_message_to_support_channel(message):
  user_id = str(message.author.id)
  embed = discord.Embed(
    title=f"Message from {message.author.name} **(Bot User)**",
    description=f"{message.content}\n\n",
    color=discord.Color.random())
  embed.add_field(name="How to Reply and Close this Mail Support?", value="Use `!reply <username> <message>` to reply message from this user and `!close <username>` to close this user's mail support", inline=False)
  embed.set_footer(text='Watching Anime Update')

  # Check for image attachments and add them to the embed
  for attachment in message.attachments:
    if attachment.content_type.startswith('image'):
      embed.set_image(url=attachment.url)

  if user_id in mail_support_data:
    mod_channel = client.get_channel(1153091737569468416)

    if mod_channel is not None:
        await mod_channel.send('<@&1153176876571955240> <@&1154021489494995024>', embed=embed)
    else:
        await message.author.send("<:animeupdate:1154683499027116103> Apologies, but sending messages to Moderators is currently unavailable.")
  else:
    await message.author.send(
        "<:animeupdate:1154683499027116103> Apologies, but sending messages to Moderators is currently unavailable."
    )

@client.event
async def on_message_edit(before, after):
  user_id = str(after.author.id)

  if isinstance(after.channel, discord.DMChannel) and not after.author.bot and user_id in mail_support_data:
    mod_channel = client.get_channel(1153091737569468416)

    if mod_channel is not None and mail_support_data[user_id].get("rules_accepted", False):
        async for message in mod_channel.history(limit=100):
            if message.embeds and message.embeds[0].title.startswith(f"Message from {after.author.name} **(Bot User)**"):
                await after.author.send(
                    "<:animeupdate:1154683499027116103> Please do not edit the message you sent because we cannot see edited messages."
                )
                break
    else:
        await after.author.send(
            "<:animeupdate:1154683499027116103> Apologies, but sending messages to Moderators is currently unavailable."
        )

@client.command()
@is_command_locked('reply')
@commands.has_any_role(1153176392939352085, 1153176876571955240, 1154021489494995024, 1153177560335781898)
async def reply(ctx, username: str, *, response: str):
  user = discord.utils.get(client.users, name=username)
  user_id = str(user.id)

  if user is not None and user_id in mail_support_data:
      mod_channel = client.get_channel(1153091737569468416)
      if mod_channel is not None:
          await user.send(f"<:animeupdate:1154683499027116103> {ctx.author.name} **(Moderator)**: {response}")
          await ctx.send("<:animeupdate:1154683499027116103> Response sent successfully. Waiting for a reply from Bot User...")
      else:
          await ctx.send("<:animeupdate:1154683499027116103> Mail Support channel not found.")
  else:
      await ctx.send("<:animeupdate:1154683499027116103> User not opening Mail Support")

cooldowns = {}

@client.command()
@is_command_locked('close')
@commands.has_any_role(1153176392939352085, 1153176876571955240, 1154021489494995024, 1153177560335781898)
async def close(ctx, username: str):
  user = discord.utils.get(client.users, name=username)
  user_id = str(user.id)

  if user is not None and user_id in mail_support_data:
      mod_channel = client.get_channel(1153091737569468416)
      if mod_channel is not None:
          embed = discord.Embed(
              title='Thank You for using Mail Support',
              description='Your Mail Support has been closed. Please wait 1 minute cooldown before opening another support mail',
              color=discord.Color.random()
          )
          embed.set_footer(text='Watching Anime Update')
          await user.send(embed=embed)
          await ctx.send(f"<:animeupdate:1154683499027116103> Mail Support from {user.name} has been closed.")
          cooldowns[user_id] = time.time()
          del mail_support_data[user_id]

          # Save the updated mail support data back to the file
          with open(mail_support_file, "w") as file:
              json.dump(mail_support_data, file)
      else:
          await ctx.send("<:animeupdate:1154683499027116103> Mail Support channel not found.")
  else:
      await ctx.send("<:animeupdate:1154683499027116103> User not opening Mail Support")

from keep_alive import keep_alive
keep_alive()

discord_token = os.getenv("DISCORD_TOKEN")
client.run(discord_token)