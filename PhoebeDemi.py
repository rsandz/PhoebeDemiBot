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

timezone_offset = -7.0
tzinfo = timezone(timedelta(hours=timezone_offset))

#========================================================================================#

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    sendTimedMessages.start()

@client.event
async def on_member_join(member):
    server = client.guilds[0]
    channel = client.get_channel(int(welcome_channel))
    rules = get(server.channels, name='rules')
    intro = get(server.channels, name='introduce-yourself')
    role = get(server.channels, name='role-picker')

    message = "Hello {member.mention}! Welcome to the Official Warp Speed and Witchcraft Server! Consider checking out {rules.mention}, giving yourself a role in {role.mention}, and introducing yourself in {intro.mention}!"
    await channel.send(message.format(member = member, rules = rules, intro = intro, role = role))

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    emoji = payload.emoji.name
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
        if emoji in colour_emoji_list:
            role = get(server.roles, name=colour_roles[emoji])
            await member.add_roles(role)
    
    
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


@client.command()
async def question(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send("you need to ask a question, silly!")
        return

    await ctx.channel.send(random.choice(answers))


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

        
@client.command()
@commands.has_role('Ya Boi')
async def stage(ctx, *args):
    if len(args) <= 2:
        await ctx.channel.send("Not enough arguments" )
        return

    date = args[0]
    time = args[1]

    try:
        dateTime = pytz.UTC.localize(datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S"))
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
        dateTime = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S")
        del messageList[dateTime]
    except:
        await ctx.channel.send("That doesn't exist")

    await ctx.channel.send("Stage List:" )
    if len(messageList) == 0:
        await ctx.channel.send("`No messages staged`")
        return
    for message in messageList:
        await ctx.channel.send("`" + str(message) + " : " + messageList[message] + "`" )


@tasks.loop(minutes=3.0)
async def sendTimedMessages():
    print("timed")
    server = client.guilds[0]
    for message in messageList:
        if message <= datetime.now(tzinfo):
            channel = get(server.channels, name='announcements')
            await channel.send(messageList[message])
            del messageList[message]
            return


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

