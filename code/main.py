import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import has_permissions
import sqlite3
import os
import emoji as emji
from colorama import Fore, Back
import random

os.chdir(os.path.join(__file__, ".."))

creatorUsername = "tomatodealer23" # Replace with yours if you want
botToken = "Y0UR.B0T.T0K3N"

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def CreateServerConifgRecordIfNotExists(serverId):
    query = f"INSERT INTO serversData ( serverId, LolBannerActive ) VALUES ({serverId}, 0)"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    dbconn.commit()
    dbconn.close()


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="men"))

    await tree.sync()
    print(f"{Back.BLUE}{Fore.WHITE}Bot is logged in as > {Back.MAGENTA}{Fore.WHITE}{client.user.name}{Fore.RESET}{Back.RESET}")
    if banlol.get_task() == None:
        banlol.start()


@tree.command(name="bruh", description="Bruhs, dramatically")  # REMOVE IN PROD
async def slash_command(interaction: discord.Interaction):
    await interaction.response.send_message("**Bruh.**")
    

@tree.command(name="clear_channel", description="Clears the channel the command is executed in [ADMIN ONLY]")
async def slash_command(interaction: discord.Interaction):
    if interaction.permissions.administrator:
        await interaction.channel.purge()
        await interaction.response.send_message("Channel cleared")
    else:
        await interaction.response.send_message("You don't have the administrator privileges needed to run this command")


@tasks.loop(minutes=2.5)
async def banlol():
    for guild in client.guilds:
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()

        query = f"SELECT * FROM serversData WHERE serverId = {guild.id} AND LolBannerActive = 1"
        dbcursor.execute(query)
        if dbcursor.fetchone() == None:
            continue
        else:
            for member in guild.members:
                if member.bot:
                    continue
                if member.activity and member.activity.type == discord.ActivityType.playing:
                    if "league of legends" in member.activity.name.lower() and member.activity.timestamps:
                        elapsedtime = (discord.utils.utcnow(
                        ) - member.activity.timestamps.start).total_seconds()
                        if elapsedtime >= 900:
                            await member.send(f"You were banned from {guild.name} for playing league for more than 15 minutes")
                            await member.ban(reason="Playing league for more than 15 minutes")
                        elif elapsedtime >= 600:
                            await member.send(f"**LAST WARNING**: Stop playing league, consequences WILL follow.\n**Server**: {guild.name}")
                        elif elapsedtime >= 300:
                            await member.send(f"**WARNING**: Stop playing league, consequences WILL follow.\n**Server**: {guild.name}")


@tree.command(name="toggle_lol_player_banner", description="Toggles the LoL player banner [1st Warning: 5min. | 2nd Warning: 10min. | Ban: 15min.]")
@has_permissions(administrator=True)
async def slash_command(interaction: discord.Interaction):
    query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        dbconn.close()
        await CreateServerConifgRecordIfNotExists(interaction.guild.id)
        query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        row = dbcursor.fetchone()
        if row is None:
            await interaction.response.send_message(f"No SQL record found for this server. This is a rare error, please contact **{creatorUsername}** and send him your server id so he can debug my crappy data processing. ಥ_ಥ")
            return
    lolBan = not bool(row[1])
    query = f"UPDATE serversData SET LolBannerActive = {int(lolBan)} WHERE serverId = {interaction.guild.id}"
    dbcursor.execute(query)
    dbconn.commit()
    dbconn.close()
    if lolBan:
        await interaction.response.send_message(f"The LoL player banner is now active")
    elif not lolBan:
        await interaction.response.send_message(f"The LoL player banner is now inactive")


@tree.command(name="toggle_currency_system", description="Toggles the bot's currency system")
@has_permissions(administrator=True)
async def slash_command(interaction: discord.Interaction):
    query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        dbconn.close()
        await CreateServerConifgRecordIfNotExists(interaction.guild.id)
        query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        row = dbcursor.fetchone()
        if row is None:
            await interaction.response.send_message(f"No SQL record found for this server. This is a rare error, please contact **{creatorUsername}** and send him your server id so he can debug my crappy data processing. ಥ_ಥ")
            return
    currencyEnabled = not bool(row[2])
    query = f"UPDATE serversData SET currencySystemEnabled = {int(currencyEnabled)} WHERE serverId = {interaction.guild.id}"
    dbcursor.execute(query)
    dbconn.commit()
    dbconn.close()
    if currencyEnabled:
        await interaction.response.send_message(f"The currency system is now enabled")
    elif not currencyEnabled:
        await interaction.response.send_message(f"The currency system is now disabled")


@tree.command(name="set_currency", description="Changes the emoji of the bot's currency for this server")
@has_permissions(administrator=True)
async def slash_command(interaction: discord.Interaction, emoji: str):
    query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        dbconn.close()
        await CreateServerConifgRecordIfNotExists(interaction.guild.id)
        query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        row = dbcursor.fetchone()
        if row is None:
            await interaction.response.send_message(f"No SQL record found for this server. This is a rare error, please contact **{creatorUsername}** and send him your server id so he can debug my crappy data processing. ಥ_ಥ")
            return
    try:
        if emoji is not None:
            if not is_valid_emoji(emoji, interaction):
                await interaction.response.send_message("Error: The provided emoji is not valid :|")
                return
            query = "UPDATE serversData SET currencyEmoji = ? WHERE serverId = ?"
            await interaction.response.send_message(
                f"This server's currency is now set to: {emoji}")
            dbcursor.execute(query, (emoji, interaction.guild.id))
            dbconn.commit()
            dbconn.close()
        else:
            interaction.response.send_message(
                "Error: The provided emoji is not valid :|")

    except ValueError:
        interaction.response.send_message(
            f"This command is in late BETA and has ran into a ValueError, contact **{creatorUsername}** with the command you tried to execute and the server id")


def is_valid_emoji(emoji: str, interaction: discord.Interaction) -> bool:
    # Check if the input is a standard Unicode emoji
    if emoji in emji.EMOJI_DATA:
        return True
    # Check if the input is a custom emoji
    if emoji.startswith('<:') and emoji.endswith('>'):
        if interaction.guild.get_emoji(int(emoji.removeprefix('<:').removesuffix('>').split(":")[1])) is not None:
            return True
    return False


# ECONOMY STUFF WITH CURRENCY [ NOT CONFIG LIKE PREVIOUS ]

def CreateServerEconomyTableIfNotExists(serverId: int):
    dbconn = sqlite3.connect("serversEconomy.db")
    dbcursor = dbconn.cursor()

    query1 = f"SELECT name FROM sqlite_master WHERE type='table' AND name='server_{serverId}'"
    dbcursor.execute(query1)
    if dbcursor.fetchone() is not None:
        return
    else:
        query2 = f"""
        CREATE TABLE server_{serverId} (
            userId INTEGER UNIQUE,
            currencyAmount INTEGER
        )"""

        dbcursor.execute(query2)
        dbconn.commit()
        dbconn.close()


def CreateServerEconomyRecordIfNotExists(serverId, userId):
    CreateServerEconomyTableIfNotExists(serverId)

    dbconn = sqlite3.connect("serversEconomy.db")
    dbcursor = dbconn.cursor()

    query1 = f"SELECT * FROM server_{serverId} WHERE userId = {userId}"
    dbcursor.execute(query1)
    if dbcursor.fetchone() is not None:
        return
    else:
        query2 = f"INSERT INTO server_{serverId} ( userId, currencyAmount ) VALUES ({userId}, 0)"
        dbcursor.execute(query2)
        dbconn.commit()
        dbconn.close()


def getBalance(serverId, userId):
    CreateServerEconomyRecordIfNotExists(serverId, userId)
    dbconn = sqlite3.connect("serversEconomy.db")
    dbcursor = dbconn.cursor()

    query1 = f"SELECT currencyAmount FROM server_{serverId} WHERE userId = {userId}"
    dbcursor.execute(query1)
    row = dbcursor.fetchone()
    balance = row[0]
    dbconn.close()
    return balance


def getCurrencyEmoji(serverId):
    query = f"SELECT * FROM serversData WHERE serverId = {serverId}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    emoji = dbcursor.fetchone()
    if emoji is None:
        dbconn.close()
        CreateServerConifgRecordIfNotExists(serverId)
        query = f"SELECT * FROM serversData WHERE serverId = {serverId}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        emoji = dbcursor.fetchone()
    return emoji[3]


def getCurrencyEnabled(serverId):
    query = f"SELECT * FROM serversData WHERE serverId = {serverId}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        dbconn.close()
        CreateServerConifgRecordIfNotExists(serverId)
        query = f"SELECT * FROM serversData WHERE serverId = {serverId}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        enabled = bool(dbcursor.fetchone()[2])
        return enabled


def addCurrency(serverId, userId, amount):
    CreateServerEconomyRecordIfNotExists(serverId, userId)
    dbconn = sqlite3.connect("serversEconomy.db")
    dbcursor = dbconn.cursor()
    userPrevAmount = getBalance(serverId, userId)
    userNextAmount = userPrevAmount + amount

    query2 = f"UPDATE server_{serverId} SET currencyAmount = {userNextAmount} WHERE userId = {userId}"
    dbcursor.execute(query2)
    dbconn.commit()
    dbconn.close()


# THE ARRAYS CONTAIN THE MESSAGE + THE MULTIPLIER OF THE RANDOM .25 to .75 AMOUNT YOU WILL GET
# TODO: ADD RARE CASES WHERE YOU LOSE MONEY
workMessages = [
    ["You slaved away as a McDonald's cashier for the day and earned %d%s", 30],
    ["You delivered some pizzas and earned %d%s in tips", 40],
    ["You helped a grandma with her Amazon package return and earned %d%s", 50],
    ["You sang in the rain and got %d%s for some reason", 55],
    ["You dressed up as shrek at the local park and you earned %d%s", 90],
    ["You sold 90 grams of columbian to the local highschool and got %d%s", 90],
    ["You spent 9 depressing hours in an office, only to earn %d%s", 40],
    ["You didn't work but %d%s fell from the sky, it's your lucky day! 👈(ﾟヮﾟ👈)", 65],
    ["You earned %d%s by making a cringy mukbang video *.__.*", 65],
    ["You spent 20 hours on writing a discord bot only to earn %d%s", 10],
    ["You spent 90 hours to write a script that automates a 2-minute task just for you to earn %d%s 👁️👄👁️", 25],
    ["You performed at the worst concert of all time but that was enough for a bunch of white women to give you %d%s", 80],
    ["You made an evil AI that will take over the world and got paid %d%s for it", 75],
    ["You fulfilled your childhood dream of becoming a YouTuber and earned %d%s in ad revenue", 70],
    ["You made a cool meme and got %d%s", 25],
    ["You spent the day fixing some bugs in your crappy discord bot and earned %d%s in donations", 25],
    ["You published a VHS horror game to itch.io and got %d%s in donations", 30],
    ["You worked as a dog walker and earned %d%s for taking the happy pups on a walk <3", 35],
    ["You became a part-time DJ at a local club and earned %d%s for playing sick beats", 60],
    ["You worked as a tech support agent and earned %d%s for dealing with endless tech issues", 45],
    ["You participated in a focus group for a new flavor of potato chips and earned %d%s", 20],
    ["You spent the day as a mystery shopper and earned %d%s for evaluating customer service", 30],
    ["You worked as a barista and earned %d%s for crafting the perfect latte art", 25],
    ["You babysat for a neighbor's hyperactive kids and earned %d%s", 35],
    ["You became a street performer and earned %d%s from impressed passersby", 50],
    ["You worked as a freelance graphic designer and earned %d%s for a unique logo design", 55],
    ["You tutored a struggling student in math and earned %d%s", 40],
    ["You spent the day as a tour guide and earned %d%s showcasing the local attractions", 50],
    ["You volunteered at a charity event and received %d%s as a token of appreciation", 15],
    ["You worked as a virtual assistant and earned %d%s for efficiently managing tasks", 45],
    ["You participated in a research study and earned %d%s for sharing your opinions", 30],
    ["You organized a community cleanup and received %d%s for your environmental efforts", 20],


    # LOSE CASES
    ["You tripped while falling from the construction site,  you should've died but for some reason you only lost %d%s", -40],
    ["You felt like losing coins today and lost %d%s", -25],
    ["Instead of working, you went partying and spent %d%s on beer ( ﾉ ﾟｰﾟ)ﾉ", -45],
]


@tree.command(name="work", description="Work for some money")
async def slash_command(interaction: discord.Interaction):
    query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
    dbconn = sqlite3.connect("serversConfig.db")
    dbcursor = dbconn.cursor()
    dbcursor.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        dbconn.close()
        await CreateServerConifgRecordIfNotExists(interaction.guild.id)
        query = f"SELECT * FROM serversData WHERE serverId = {interaction.guild.id}"
        dbconn = sqlite3.connect("serversConfig.db")
        dbcursor = dbconn.cursor()
        dbcursor.execute(query)
        row = dbcursor.fetchone()
        if row is None:
            await interaction.response.send_message(f"No SQL record found for this server. This is a rare error, please contact **{creatorUsername}** and send him your server id so he can debug my crappy data processing. ಥ_ಥ")
            return
    if bool(row[2]) == True:
        CreateServerEconomyRecordIfNotExists(
            interaction.guild.id, interaction.user.id)
        randomChoice = random.choice(workMessages)
        message = randomChoice[0]
        rewardAmount = int(random.uniform(.25, .75) * randomChoice[1])
        addCurrency(interaction.guild.id, interaction.user.id, rewardAmount)
        await interaction.response.send_message(message % (rewardAmount, row[3]))
    else:
        await interaction.response.send_message(
            "Sorry, the bot's currency system is disabled for this server")


@tree.command(name="balance", description="Returns the specified users balance of the servers currency (Returns yours if no user is specified)")
async def slash_command(interaction: discord.Interaction, user: discord.User = None):
    if user == None:
        await interaction.response.send_message(
            f"Your balance is: {getBalance(interaction.guild.id, interaction.user.id)}{getCurrencyEmoji(interaction.guild.id)}")
    else:
        await interaction.response.send_message(
            f"{user.name}'s balance is: {getBalance(interaction.guild.id, user.id)}{getCurrencyEmoji(interaction.guild.id)}")

client.run(botToken)
