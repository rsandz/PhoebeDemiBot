import discord
from discord.utils import get
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timezone, timedelta
import pytz

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '.', intents=intents)

load_dotenv()
gender_message = os.getenv('GENDER_MESSAGE')
creator_message = os.getenv('CREATOR_MESSAGE')
colour_message = os.getenv('COLOUR_MESSAGE')
welcome_channel = os.getenv('WELCOME_CHANNEL')
rules_channel = os.getenv('RULES_CHANNEL')
roles_channel = os.getenv('ROLES_CHANNEL') 
intro_channel = os.getenv('INTRO_CHANNEL')
announce_channel = os.getenv('ANNOUNCE_CHANNEL')
server_id = os.getenv('SERVER_ID')

messageList = {}

gender_roles = {
    '❤️' : 'he/him',
    '🧡' : 'he/they',
    '💛' : 'they/them',
    '💚' : 'she/they',
    '💙' : 'she/her'
}
gender_emoji_list = gender_roles.keys()

colour_roles = {
    '✨' : 'From Another Realm',
    '🚀' : 'From the Far Future'
}
colour_emoji_list = colour_roles.keys()

answers = [
    "absolutely!",
    "yes",
    "possibly...",
    "not sure...",
    "don't count on it",
    "no",
    "definitely not!"
]

tzinfo = pytz.timezone("America/Edmonton")


# ========== HELPER FUNCTIONS ========== #

def storeStaged():
    f = open('staged.txt', 'w')
    for message in messageList.keys():
        f.write(str(message) + '\n')
        f.write(messageList[message] + '\n')
    f.close()


def getStaged():
    with open('staged.txt', 'r') as f:
        lines = f.readlines()
        holder = ""
        for i in range(len(lines)):
            if i % 2 == 0:
                holder =  datetime.strptime(lines[i][:-7], "%Y-%m-%d %H:%M:%S").astimezone(tzinfo)
            else:
                messageList[holder] = lines[i].rstrip()


#========================================================================================#


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    getStaged()
    sendTimedMessages.start()

# Sneding a message when a member joins
@client.event
async def on_member_join(member):
    channel = client.get_channel(int(welcome_channel))
    rules = client.get_channel(int(rules_channel))
    intro = client.get_channel(int(intro_channel))
    role = client.get_channel(int(roles_channel))

    message = "Hello {member.mention}! Welcome to the Official Warp Speed and Witchcraft Server! Consider checking out {rules.mention}, giving yourself a role in {role.mention}, and introducing yourself in {intro.mention}!"
    await channel.send(message.format(member = member, rules = rules, intro = intro, role = role))

# Detection for roles pickers
@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    emoji = payload.emoji.name
    channel = client.get_channel(payload.channel_id)
    server = client.get_guild(int(server_id))
    member = server.get_member(payload.user_id)

    # gender roles
    if message_id == int(gender_message):
        if emoji in gender_emoji_list:
            role = get(server.roles, name=gender_roles[emoji])
            await member.add_roles(role)

    # creator role
    if message_id == int(creator_message):
        if emoji == '📝':
            role = get(server.roles, name="Creator")
            await member.add_roles(role)
    
    # colour roles
    if message_id == int(colour_message):
        future_role =  get(server.roles, name='From the Far Future')
        realm_role = get(server.roles, name='From Another Realm')
        message = await channel.fetch_message(payload.message_id)
        if emoji == '✨':
            if future_role in member.roles:
                await member.remove_roles(future_role)
                await message.remove_reaction('🚀', member)
            await member.add_roles(realm_role)
        if emoji == '🚀':
            if realm_role in member.roles:
                await member.remove_roles(realm_role)
                await message.remove_reaction('✨', member)
            await member.add_roles(future_role)
    

# Detection for removing a role 
@client.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    emoji = payload.emoji.name
    server = client.get_guild(int(server_id))
    member = server.get_member(payload.user_id)

    # gender roles
    if message_id == int(gender_message):
        if emoji in gender_emoji_list:
            role = get(server.roles, name=gender_roles[emoji])
            await member.remove_roles(role)
    
    # creator role
    if message_id == int(creator_message):
        if emoji == '📝':
            role = get(server.roles, name="Creator")
            await member.remove_roles(role)
    
    # colour roles
    if message_id == int(colour_message):
        if emoji in colour_emoji_list:
            role = get(server.roles, name=colour_roles[emoji])
            await member.remove_roles(role)


# generates a random answer
@client.command()
async def question(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send("you need to ask a question, silly!")
        return

    await ctx.channel.send(random.choice(answers))

# ========== QUOTES ========== #

@client.command()
async def quote(ctx, *args): 
    n = 1
    if len(args) > 0 and str.isdigit(args[0]):
        if (int(args[0]) > 5):
            await ctx.channel.send("I can only give up to 5 quotes at a time.")
            return
        n = int(args[0])
    with open('quotes.txt', 'r') as f:
        quotes = [line.strip() for line in f]
        for i in range(n):
            quote = random.choice(quotes)
            await ctx.channel.send(quote)


@client.command()
@commands.has_role('Ya Boi')
async def quotes(ctx):
    await ctx.send(file=discord.File('quotes.txt'))

@client.command()
@commands.has_role('Ya Boi')
async def newquote(ctx, *args):
    line = " ".join(args)
    f = open("quotes.txt", "a")
    f.write("\n")
    f.write(line)
    f.close()
    await ctx.channel.send("new quote added: `" + line + "`")

#https://stackoverflow.com/questions/1877999/delete-final-line-in-file-with-python
@client.command()
@commands.has_role('Ya Boi')
async def deletequote(ctx, *args):
    with open('quotes.txt', "r+", encoding = "utf-8") as file:
        file.seek(0, os.SEEK_END)
        pos = file.tell() - 1
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()
    await ctx.channel.send("quote deleted.")

# ========== RECOMMENDS ========== #

@client.command()
async def recommend(ctx, *args): 
    with open('recommend.txt', 'r') as f:
        recs = [line.strip() for line in f]
        choice = random.randint(0, (len(recs) / 2) - 1)
        await ctx.channel.send(recs[choice * 2])
        await ctx.channel.send(recs[(choice * 2)+ 1])
      
@client.command()
@commands.has_role('Ya Boi')
async def recommends(ctx):
    await ctx.send(file=discord.File('recommend.txt'))

@client.command()
@commands.has_role('Ya Boi')
async def newrec(ctx, *args):
    lines = (" ".join(args)).split("*")
    f = open("recommend.txt", "a")
    f.write("\n" + lines[0] + "\n" + lines[1])
    f.close()
    await ctx.channel.send("new rec added: `" + lines[0] + " \n " + lines[1] + "`")

#https://stackoverflow.com/questions/1877999/delete-final-line-in-file-with-python
@client.command()
@commands.has_role('Ya Boi')
async def deleterec(ctx, *args):
    with open('recommend.txt', "r+", encoding = "utf-8") as file:
        for i in range(2):
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1
            while pos > 0 and file.read(1) != "\n":
                pos -= 1
                file.seek(pos, os.SEEK_SET)
            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()
    await ctx.channel.send("recommendation deleted.")

# ========== STAGED MESSAGES ========== #

@client.command()
@commands.has_role('Ya Boi')
async def stage(ctx, *args):
    if len(args) <= 2:
        await ctx.channel.send("Not enough arguments" )
        return

    date = args[0]
    time = args[1]

    try:
        dateTime = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S").astimezone(tzinfo)
    except:
        await ctx.channel.send("Date and time incorrect. Format: `y-m-d h:m:s`" )
        return

    message = ""
    if args[2] == "$":
        message = "@everyone, A new episode of Warp Speed and Witchcraft is out! https://www.webtoons.com/en/challenge/warp-speed-and-witchcraft/convention-con-4/viewer?title_no=644747&episode_no=" + args[3]

    else:
        for i in  range(2, len(args)):
            if args[i] == "@":
                 message = message + "@everyone "
            else:
                message = message + args[i] + " "
    
    allowed_mentions = discord.AllowedMentions(everyone = True)
    messageList[dateTime] = message
    storeStaged()
    await ctx.channel.send("Staged Message: " + "`" + str(dateTime) + " : " + messageList[dateTime] + "`", allowed_mentions = allowed_mentions)


@client.command()
@commands.has_role('Ya Boi')
async def stagelist(ctx):
    if len(messageList) == 0:
        await ctx.channel.send("`No messages staged`")
        return
    for message in messageList:
        await ctx.channel.send("`" + str(message) + " : " + messageList[message] + "`" )


@client.command()
@commands.has_role('Ya Boi')
async def dropstage(ctx, *args):
    date = args[0]
    time = args[1]
    try:
        dateTime = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S").astimezone(tzinfo)
        del messageList[dateTime]
    except:
        await ctx.channel.send("That doesn't exist")

    await ctx.channel.send("Stage List:" )
    if len(messageList) == 0:
        await ctx.channel.send("`No messages staged`")
        return
    for message in messageList:
        await ctx.channel.send("`" + str(message) + " : " + messageList[message] + "`" )


@tasks.loop(seconds=30.0)
async def sendTimedMessages():
    print("timed")
    server = client.guilds[0]
    for message in messageList:
        if message <= datetime.now(tzinfo):
            channel = client.get_channel(int(announce_channel))
            await channel.send(messageList[message])
            del messageList[message]
            return


# ========== OTHER ========== #

# https://stackoverflow.com/questions/43465082/python-discord-py-delete-all-messages-in-a-text-channel
@client.command(pass_context = True)
@commands.has_role('Ya Boi')
async def clear(ctx, amount = 1000):
    await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_role('Ya Boi')
async def time(ctx):
     await ctx.channel.send("The current bot time is: `" + str(datetime.now(tzinfo)) + "`")

client.run(os.getenv('DISCORD_TOKEN'))

