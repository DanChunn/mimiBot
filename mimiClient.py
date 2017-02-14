import discord
from discord.ext import commands
import random
import requests
import re
from bs4 import BeautifulSoup
import pickle
import asyncio
import logging
import sys
import operator
from mimiMember import mimiMember
import mimiSettings

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def saveData(data):
    with open('data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadData():
    with open('data.pickle', 'rb') as handle:
        b = pickle.load(handle)
        return b


masterDict = {}
try:
    masterDict = loadData()
except Exception as err:
    saveData(masterDict)

bot = commands.Bot(command_prefix='!')
pointName = "bits"
initialPoints = mimiSettings.initialPoints
marryCost = mimiSettings.marryCost
pointsAllot = mimiSettings.pointsAllot
denounceAmt = mimiSettings.denounceAmt
denounceRelief = mimiSettings.denounceRelief
intervalString = mimiSettings.intervalString
yesNoList = mimiSettings.yesNoList

#replace 'token' with your bot token
token = 'token'

@bot.command()
async def roll(limit:int = None):
    """  :Rolls between 1-100      | Ex: !roll, !roll 20"""
    if limit is None:
        limit = 100

    result = random.randint(1,limit)
    await bot.say(result)

@bot.command()
async def dice(numOfDice:int = None):
    """  :Rolls a die              | Ex: !dice, !dice 5"""
    if numOfDice is None:
        numOfDice = 1

    result = ', '.join(str(random.randint(1, 6)) for i in range(numOfDice))
    await bot.say(result)

@bot.command()
async def d20(numOfDice:int = None):
    """  :Rolls a d20 die          | Ex: !d20, !d20 3"""
    if numOfDice is None:
        numOfDice = 1

    result = ', '.join(str(random.randint(1, 20)) for i in range(numOfDice))
    await bot.say(result)

@bot.command()
async def coin(numOfCoins:int = None):
    """  :Flips a coin             | Ex: !coin"""
    if numOfCoins is None:
        numOfCoins = 1
    result = random.randint(0, 1)
    if result == 0:
        coin = "Tails"
    else:
        coin = "Heads"
    await bot.say(coin)

@bot.command()
async def yt(search:str, *args):
    """  :Get a YT Video           | Ex: !yt queen dont stop me now"""
    search = search+"+" + '+'.join(args[0:])
    url = "https://www.youtube.com/results?search_query=" + search
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    content = soup.find_all("h3", {"class":"yt-lockup-title"})
    regex = re.compile(r'''href="/watch?.*?"''')
    for i in range(len(content)):
        mo = regex.search(str(content[i]))
        if mo is not None:
            n = str(mo.group())
            break;

    youtubeLink = "https://www.youtube.com/watch?v=" + n[15:-1]
    await bot.say(youtubeLink)
    #await bot.say("Search for more videos here:\n"+ url)

@bot.command()
async def mimi(text:str = None):
    """  :Ask me a yes no question | Ex: !mimi do you love me"""
    if text is None:
        await bot.say("You must ask me a yes or no question!")
        return
    limit = len(yesNoList) - 1
    i = random.randint(0, limit)
    result = yesNoList[i]
    await bot.say(result)


@bot.command(pass_context=True)
async def denounce(ctx, member:discord.Member, message:str = None, *args):
    """  :Denounce someone!        | Ex: !denounce @someone"""
    if message is None:
        message = "You make me sick"
    author = ctx.message.author
    server = author.server
    memList = memberList(server)
    mimiMem = memList[member.id]
    mimiMem.incrementDenounced(denounceAmt)
    message = message + " " + " ".join(args[0:])
    mimiAuthor = memList[author.id]
    denounceCost = int(denounceAmt * pointsAllot * 1.2)

    if not enoughPoints(author, denounceCost):
        await sendErrorMsg(author)
        return
    subPointsToMember(author, denounceCost)
    if message is None:
        newMessage = ""
    else:
        message = message.strip()
        newMessage = '"'+message+'!"'
    fmt = "{msg} - {authorMention} has denounced {memberMention} at the cost of {amount}! {member} will stop receiving {pointName} for {length} {interval}!"
    d = { 'msg': newMessage, 'authorMention': author.mention, 'memberMention':member.mention, 'member':member.name, 'amount':str(denounceCost), 'pointName':pointName, 'length':mimiMem.denounced, 'interval':intervalString }
    content = fmt.format(**d)
    await bot.say(content)

@bot.command(pass_context=True)
async def marry(ctx, member:discord.Member = None):
    """  :Get a YT Video           | Ex: !yt queen dont stop me now"""
    if member is None:
        return
    proposeCost = int(initialPoints * .4)
    author = ctx.message.author
    if not enoughPoints(author, proposeCost):
        await sendErrorMsg(author)
        return
    subPointsToMember(author, proposeCost)
    server = author.server
    memList = memberList(server)
    mimiAuthor = memList[author.id]
    mimiMember = memList[member.id]
    mimiAuthor.spouse = member.id
    mimiMember.spouse = author.id
    await bot.say(server.get_member(author.id).name + " is now married to " + server.get_member(mimiAuthor.spouse).name+"!")


@bot.command()
async def pr():
    """  """
    logging.info("Printing masterDict")
    for servId, memList in masterDict.items():
        server = bot.get_server(servId)
        logging.info("Server: " +server.name)
        logging.info("------------------------")
        for memId in memList:
            mem = server.get_member(memId)
            mimiMem = memList[memId]
            logging.info(mem.name +":"+ str(mimiMem.points)+":" +str(mimiMem.denounced))
        logging.info("")

#TODO
@bot.command(pass_context=True)
async def leaderboard(ctx):
    """  :Prints top 5 richest     | Ex: !leaderboard"""
    count = 0
    server = ctx.message.author.server
    memList = memberList(server)
    pass

@bot.command(pass_context=True)
async def bits(ctx, member:discord.Member = None):
    """  :Display user's bits      | Ex: !bits, !bits @someone"""
    if member is None:
        member = ctx.message.author
    server = member.server
    memList = memberList(server)
    content = member.mention + " has " + str(getPoints(member)) + " " + pointName
    await bot.say(content)


@bot.command(pass_context=True)
async def tip(ctx, member:discord.Member = None, points:int = None):
    """  :Gift bits to someone     | Ex: !tip @someone 100"""
    if member is None or points is None:
        return
    giver = ctx.message.author
    if member is giver:
        content = giver.mention + " You can't tip yourself!"
        await bot.send_message(giver, content)
        return
    if not enoughPoints(giver, points):
        await sendErrorMsg(giver)
        return
    subPointsToMember(giver, points)
    addPointsToMember(member, points)
    content = giver.mention + " has tipped " + member.mention+ " " + str(points) + " " + pointName + "!"
    await bot.say(content)


async def sendErrorMsg(member:discord.Member):
    content = member.mention + " Not enough " + pointName + " for that action!"
    await bot.send_message(member, content)

def addPointsToMember(member:discord.Member = None, points:int = None):
    if points is None or member is None:
        return
    server = member.server
    memList = memberList(server)
    mimiMember = memList[member.id]
    mimiMember.incrementPoints(points)

def subPointsToMember(member:discord.Member = None, points:int = None):
    if points is None or member is None:
        return
    server = member.server
    memList = memberList(server)
    mimiMember = memList[member.id]
    mimiMember.decrementPoints(points)


def memberList(server:discord.Server):
    return masterDict[server.id]

def getPoints(member:discord.Member):
    server = member.server
    memList = memberList(server)
    return memList[member.id].points

def enoughPoints(member:discord.Member, points:int):
    return getPoints(member) >= points


def addPointsToAll(points:int = None):
    if points is None:
        return
    
    logging.info("Incrementing " + str(points) + " points to all users on all servers")
    for servId, memList in masterDict.items():
        server = bot.get_server(servId)
        for memId in memList:
            mimiMember = memList[memId]
            if(mimiMember.denounced <= 0):
                mimiMember.incrementPoints(points)
            

def decrementDenounced():
    logging.info("Decrementing denounced to all users on all servers")
    for servId, memList in masterDict.items():
        server = bot.get_server(servId)
        for memId in memList:
            mimiMember = memList[memId]
            mimiMember.decrementDenounced(denounceRelief)

async def timedPointsAllot():
    points = pointsAllot
    interval = 60
    
    await bot.wait_until_ready()
    while not bot.is_closed:
        await asyncio.sleep(interval)# task runs every x seconds
        addPointsToAll(points)
        decrementDenounced()
        saveData(masterDict)

@bot.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    addMemberToPointList(member)
    await bot.send_message(server, fmt.format(member, server))

def addMemberToPointList(member):
    logging.info("Adding " + member.name + " to masterDict...")
    mimiMem = mimiMember(member, initialPoints)
    masterDict[member.server.id].setdefault(member.id, mimiMem)
    logging.info("Member added to masterDict")
    logging.info("")
    
def populate():
    logging.info("Populating masterDict...")
    for server in bot.servers:
        servId = server.id
        masterDict.setdefault(servId, {})
        for member in server.members:
            mimiMem = mimiMember(member, initialPoints)
            masterDict[servId].setdefault(member.id, mimiMem)
    logging.info("masterDict populated")
    logging.info("")
    saveData(masterDict)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------') 
    populate()
    bot.loop.create_task(timedPointsAllot())
    

bot.run(token)
