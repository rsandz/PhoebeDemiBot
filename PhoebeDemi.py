from ast import arg
import discord
from discord.utils import get
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

from torch import rand

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '.', intents=intents)

load_dotenv()
gender_message = os.getenv('GENDER_MESSAGE')
creator_message = os.getenv('CREATOR_MESSAGE')
colour_message = os.getenv('COLOUR_MESSAGE')
welcome_channel = os.getenv('WELCOME_CHANNEL')
server_id = os.getenv('SERVER_ID')


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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
    answer = random.randint(0,6)

    if len(args) < 1:
        await ctx.channel.send("you need to ask a question, silly!")
        return

    if answer == 1:
        await ctx.channel.send("absolutely!")
    elif answer == 2:
        await ctx.channel.send("yes")
    elif answer == 3:
        await ctx.channel.send("possibly...")
    elif answer == 4:
        await ctx.channel.send("not sure...")
    elif answer == 5:
        await ctx.channel.send("don't count on it")
    elif answer == 6: 
        await ctx.channel.send("no")
    elif answer == 0:
        await ctx.channel.send("definitely not!")


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
async def recommend(ctx, *args): 
    with open('recommend.txt', 'r') as f:
        recs = [line.strip() for line in f]
        choice = random.randint(0, (len(recs) / 2) - 1)
        await ctx.channel.send(recs[choice * 2])
        await ctx.channel.send(recs[(choice * 2)+ 1])
        


client.run(os.getenv('DISCORD_TOKEN'))