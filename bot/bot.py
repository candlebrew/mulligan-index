import discord
from discord.ext import commands
# import random
import typing
import os
import asyncio
import asyncpg
import datetime
import DiscordUtils

from configsql import *

db = None

modDict = {
    1: -5,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 5,
    22: 6,
    23: 6,
    24: 7,
    25: 7}

# https://discord.com/api/oauth2/authorize?client_id=843224909958479933&permissions=268823632&scope=bot

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
    await db.execute(charProfilesSQL)
    await db.execute(sheetProfilesSQL)
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN')
devID = int(os.environ.get('DEV_ID'))
adminID = int(os.environ.get('ADMIN_ID'))
devEmail = os.environ.get('DEV_EMAIL')

client = discord.Client()

bot = commands.Bot(command_prefix='mi!', db=db)

def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == devID
    return commands.check(predicate)
    
def is_admin():
    def predicate(ctx):
        return ctx.message.author.id == adminID
    return commands.check(predicate)

## Code Here ----------------------------------------------------------

@bot.group(invoke_without_command=True,aliases=["char"])
async def character(ctx, name: str):
    nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",name)
    if nameCheck is None:
        await ctx.send("I couldn't find a character with the nickname '" + name + "'")
    else:
        embed = discord.Embed(colour=8163583)

        fullName = await db.fetchval("SELECT fullname FROM characters WHERE nickname = $1;",name)
        if fullName is None:
            fullName = name
        fullName += "\u200B\u200B"
        pronouns = await db.fetchval("SELECT pronouns FROM characters WHERE nickname = $1;",name)
        if pronouns is None:
            pronouns = "-"
        pronouns += "\u200B\u200B"
        creationAge = await db.fetchval("SELECT age FROM characters WHERE nickname = $1;",name)
        if creationAge is None:
            creationAge = "-"
        creationAge += "\u200B\u200B"
        creationDate = await db.fetchval("SELECT date FROM characters WHERE nickname = $1;",name)
        if creationDate is None:
            creationDate = "-"
        creationDate += "\u200B\u200B"
        tribe = await db.fetchval("SELECT tribe FROM characters WHERE nickname = $1;",name)
        if tribe is None:
            tribe = "-"
        tribe += "\u200B\u200B"
        rank = await db.fetchval("SELECT rank FROM characters WHERE nickname = $1;",name)
        if rank is None:
            rank = "-"
        rank += "\u200B\u200B"
        appearance = await db.fetchval("SELECT appearance FROM characters WHERE nickname = $1;",name)
        if appearance is None:
            appearance = "-"
        personality = await db.fetchval("SELECT personality FROM characters WHERE nickname = $1;",name)
        if personality is None:
            personality = "-"
        sheetURL =  await db.fetchval("SELECT sheet FROM characters WHERE nickname = $1;",name)
        if sheetURL is None:
            sheetURL = "-"
        image = await db.fetchval("SELECT image FROM characters WHERE nickname = $1;",name)
        ownerID = await db.fetchval("SELECT owner_uid FROM characters WHERE nickname = $1;",name)

        if image != None:
            embed.set_image(url=image)

        embed.set_thumbnail(url="https://i.imgur.com/Qpen3fF.png")

        embed.add_field(name="Full Name", value=fullName, inline=True)
        embed.add_field(name="Pronouns", value=pronouns, inline=True)
        embed.add_field(name="Age on Creation", value=creationAge, inline=True)
        embed.add_field(name="Tribe", value=tribe, inline=True)
        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Date of Creation", value=creationDate, inline=True)
        embed.add_field(name="Appearance", value=appearance, inline=False)
        embed.add_field(name="Personality", value=personality, inline=False)
        embed.add_field(name="Character Sheet Url", value=sheetURL, inline=False)

        await ctx.send(embed=embed)
    
@character.command()
async def new(ctx, nickname: str, *, fullName: typing.Optional[str]):
    user = ctx.message.author.id
    nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",nickname)
    if nameCheck != None:
        await ctx.send("A character already exists with that nickname.")
    else:
        await db.execute("INSERT INTO characters (nickname,fullname,owner_uid) VALUES ($1,$2,$3);",nickname,fullName,user)
        await ctx.send("Character has been saved with nickname '" + nickname + "'")
        
@character.command()
async def set(ctx, setType: typing.Optional[str], nickname: typing.Optional[str], *, newValue: typing.Optional[str]):
    if setType is None:
        await ctx.send("You can set: *nickname, fullname, pronouns, age, date, tribe, rank, appearance, personality, sheet, image*")
    elif setType not in ["nickname","fullname","pronouns","age","date","tribe","rank","appearance","personality","sheet","image"]:
        await ctx.send("I don't recognize " + setType + " as a valid value. Please use one of the following: *nickname, fullname, pronouns, age, date, tribe, rank, appearance, personality, sheet, image*")
    else:
        nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",nickname)
        if nameCheck is None:
            await ctx.send("I couldn't find a character with the nickname '" + nickname + "'")
        else:
            characterUser = await db.fetchval("SELECT owner_uid FROM characters WHERE nickname = $1;",nickname)
            user = ctx.message.author.id
            if (characterUser != user) and (user != adminID) and (user != devID):
                await ctx.send("That character does not belong to you.")
            else:
                if newValue is not None:
                    inputLength = len(newValue)
                else:
                    inputLength = 0
                if (newValue == None) and (setType == "nickname"):
                    await ctx.send("You must set what the new value is.")
                elif (inputLength > 1024):
                    await ctx.send("Your new value must be 1024 characters or fewer.")
                else:
                    sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                    await db.execute(sqlText,newValue,nickname)
                    await ctx.send("Character " + nickname + " has been updated.")


@bot.group(invoke_without_command=True)
async def sheet(ctx, name: str):
    nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",name)
    if nameCheck is None:
        await ctx.send("I couldn't find a character with the nickname '" + name + "'")
    else:
        fullName = await db.fetchval("SELECT fullname FROM characters WHERE nickname = $1;",name)
        if fullName is None:
            fullName = name
        physical = str(await db.fetchval("SELECT physical FROM characters WHERE nickname = $1;",name))
        if physical is None:
        	physical = "-"
        mental = str(await db.fetchval("SELECT mental FROM characters WHERE nickname = $1;",name))
        if mental is None:
        	mental = "-"
        maxPhysical = str(await db.fetchval("SELECT maxphysical FROM characters WHERE nickname = $1;",name))
        if maxPhysical is None:
        	maxPhysical = "-"
        maxMental = str(await db.fetchval("SELECT maxmental FROM characters WHERE nickname = $1;",name))
        if maxMental is None:
        	maxMental = "-"
        defense = str(await db.fetchval("SELECT defense FROM characters WHERE nickname = $1;",name))
        if defense is None:
        	defense = "-"
        confidence = str(await db.fetchval("SELECT confidence FROM characters WHERE nickname = $1;",name))
        if confidence is None:
        	confidence = "-"
        fortitude = str(await db.fetchval("SELECT fortitude FROM characters WHERE nickname = $1;",name))
        if fortitude is None:
        	fortitude = "-"
        fortMod = str(await db.fetchval("SELECT fortmod FROM characters WHERE nickname = $1;",name))
        if fortMod is None:
        	fortMod = "-"
        brute = str(await db.fetchval("SELECT brute FROM characters WHERE nickname = $1;",name))
        if brute is None:
        	brute = "-"
        force = str(await db.fetchval("SELECT force FROM characters WHERE nickname = $1;",name))
        if force is None:
        	force = "-"
        swimming = str(await db.fetchval("SELECT swimming FROM characters WHERE nickname = $1;",name))
        if swimming is None:
        	swimming = "-"
        digging = str(await db.fetchval("SELECT digging FROM characters WHERE nickname = $1;",name))
        if digging is None:
        	digging = "-"
        lithe = str(await db.fetchval("SELECT lithe FROM characters WHERE nickname = $1;",name))
        if lithe is None:
        	lithe = "-"
        litheMod = str(await db.fetchval("SELECT lithemod FROM characters WHERE nickname = $1;",name))
        if litheMod is None:
        	litheMod = "-"
        careful = str(await db.fetchval("SELECT careful FROM characters WHERE nickname = $1;",name))
        if careful is None:
        	careful = "-"
        contortion = str(await db.fetchval("SELECT contortion FROM characters WHERE nickname = $1;",name))
        if contortion is None:
        	contortion = "-"
        leaping = str(await db.fetchval("SELECT leaping FROM characters WHERE nickname = $1;",name))
        if leaping is None:
        	leaping = "-"
        throwing = str(await db.fetchval("SELECT throwing FROM characters WHERE nickname = $1;",name))
        if throwing is None:
        	throwing = "-"
        constitution = str(await db.fetchval("SELECT constitution FROM characters WHERE nickname = $1;",name))
        if constitution is None:
        	constitution = "-"
        conMod = str(await db.fetchval("SELECT conmod FROM characters WHERE nickname = $1;",name))
        if conMod is None:
        	conMod = "-"
        precoup = str(await db.fetchval("SELECT precoup FROM characters WHERE nickname = $1;",name))
        if precoup is None:
        	precoup = "-"
        mrecoup = str(await db.fetchval("SELECT mrecoup FROM characters WHERE nickname = $1;",name))
        if mrecoup is None:
        	mrecoup = "-"
        diet = str(await db.fetchval("SELECT diet FROM characters WHERE nickname = $1;",name))
        if diet is None:
        	diet = "-"
        exposure = str(await db.fetchval("SELECT exposure FROM characters WHERE nickname = $1;",name))
        if exposure is None:
        	exposure = "-"
        immunity = str(await db.fetchval("SELECT immunity FROM characters WHERE nickname = $1;",name))
        if immunity is None:
        	immunity = "-"
        empathy = str(await db.fetchval("SELECT empathy FROM characters WHERE nickname = $1;",name))
        if empathy is None:
        	empathy = "-"
        charisma = str(await db.fetchval("SELECT charisma FROM characters WHERE nickname = $1;",name))
        if charisma is None:
        	charisma = "-"
        memory = str(await db.fetchval("SELECT memory FROM characters WHERE nickname = $1;",name))
        if memory is None:
        	memory = "-"
        reasoning = str(await db.fetchval("SELECT reasoning FROM characters WHERE nickname = $1;",name))
        if reasoning is None:
        	reasoning = "-"
        perform = str(await db.fetchval("SELECT perform FROM characters WHERE nickname = $1;",name))
        if perform is None:
        	perform = "-"
        Self = str(await db.fetchval("SELECT self FROM characters WHERE nickname = $1;",name))
        if Self is None:
        	Self = "-"
        trait = str(await db.fetchval("SELECT trait FROM characters WHERE nickname = $1;",name))
        if trait is None:
        	trait = "-"
        inventory = str(await db.fetchval("SELECT inventory FROM characters WHERE nickname = $1;",name))
        if inventory is None:
        	inventory = "-"
        image = await db.fetchval("SELECT image FROM characters WHERE nickname = $1;",name)
        ownerID = await db.fetchval("SELECT owner_uid FROM characters WHERE nickname = $1;",name)
        
        embed1 = discord.Embed(colour=8163583,title="Character Sheet: "+fullName)
        embed2 = discord.Embed(colour=8163583,title="Character Sheet: "+fullName)
        
        counter = 0

        if image != None:
            embed1.set_image(url=image)
            embed2.set_image(url=image)

        embed1.set_thumbnail(url="https://i.imgur.com/Qpen3fF.png")
        embed2.set_thumbnail(url="https://i.imgur.com/Qpen3fF.png")

        embed1.add_field(name="Vitality", value="Physical: "+physical+"/"+maxPhysical+"\nMental: "+mental+"/"+maxMental, inline=True)
        embed1.add_field(name="Defense", value=defense, inline=True)
        embed1.add_field(name="Confidence", value=confidence, inline=True)
        embed1.add_field(name="Fortitude: "+fortitude+"("+fortMod+")", value="Brute Attack:"+brute+"\nUse Force: "+force+"\nSwimming: "+swimming+"\nDigging: "+digging, inline=True)
        embed1.add_field(name="Lithe: "+lithe+"("+litheMod+")", value="Careful Attack:"+careful+"\nContortion: "+contortion+"\nLeaping: "+leaping+"\nThrowing: "+throwing, inline=True)
        embed1.add_field(name="Constitution: "+constitution+"("+conMod+")", value="Physical Recoup:"+precoup+"\nMental Recoup: "+mrecoup+"\nDiet: "+diet+"\nEExposure: "+exposure+"\nImmunity: "+immunity, inline=True)
        embed1.add_field(name="Empathy: ("+empathy+")", value="\n**Reasoning: ("+reasoning+")**", inline=True)
        embed1.add_field(name="Charisma: ("+charisma+")", value="**Perform: ("+perform+")**", inline=True)
        embed1.add_field(name="Memory: ("+memory+")", value="**Self: ("+Self+")**", inline=True)
        
        embed1.add_field(name="Unique Trait", value=trait, inline=False)
        
        embed2.add_field(name="Inventory", value=inventory, inline=False)
        
        embed1.set_footer(text="Page 1/2")
        embed2.set_footer(text="Page 2/2")
        
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('1️⃣', "page 0")
        paginator.add_reaction('2️⃣', "page 1")

        embeds = [embed1, embed2]
        
        await paginator.run(embeds)

@sheet.command()
async def set(ctx, setType: typing.Optional[str], nickname: typing.Optional[str], *, newValue: typing.Optional[str]):
    if setType is None:
        await ctx.send("You can set: *physical, mental, maxphysical, maxmental, defense, confidence, fortitude, brute, force, swimming, digging, lithe, careful, contortion, leaping, throwing, constitution, precoup, mrecoup, diet, exposure, immunity, empathy, charisma, memory, reasoning, perform, self, trait, inventory*")
    elif setType not in ["physical", "mental", "maxPhysical", "maxMental", "defense", "confidence", "fortitude", "fortMod", "brute", "force", "swimming", "digging", "lithe", "litheMod", "careful", "contortion", "leaping", "throwing", "constitution", "conMod", "precoup", "mrecoup", "diet", "exposure", "immunity", "empathy", "charisma", "memory", "reasoning", "perform", "self", "trait", "inventory"]:
        await ctx.send("I don't recognize " + setType + " as a valid value. Please use one of the following: *physical, mental, maxphysical, maxmental, defense, confidence, fortitude, brute, force, swimming, digging, lithe, careful, contortion, leaping, throwing, constitution, precoup, mrecoup, diet, exposure, immunity, empathy, charisma, memory, reasoning, perform, self, trait, inventory*")
    else:
        nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",nickname)
        if nameCheck is None:
            await ctx.send("I couldn't find a character with the nickname '" + nickname + "'")
        else:
            characterUser = await db.fetchval("SELECT owner_uid FROM characters WHERE nickname = $1;",nickname)
            user = ctx.message.author.id
            if (characterUser != user) and (user != adminID) and (user != devID):
                await ctx.send("That character does not belong to you.")
            else:
                if newValue is not None:
                    inputLength = len(newValue)
                else:
                    inputLength = 0
                if (inputLength > 1024):
                    await ctx.send("Your new value must be 1024 characters or fewer.")
                else:
                    if setType in ["constitution","lithe","fortitude"]:
                        newValue = modDict[newValue]
                        if setType == "constitution":
                            setType = "conMod"
                        elif setType == "lithe":
                            setType = "litheMod"
                        elif setType == "fortitude":
                            setType = "fortMod"
                
                    sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                    await db.execute(sqlText,newValue,nickname)
                    await ctx.send("Character " + nickname + " has been updated.")


## DEV COMMANDS --------------------------------------------------------
@bot.group()
async def dev(ctx):
    pass

@dev.group()
async def delete(ctx):
    pass

@delete.command()
@is_dev()
async def character(ctx, id: int):
    await db.execute("DELETE FROM characters WHERE id = $1;",id)
    await ctx.send("Deletion completed.")
    
@dev.command()
@is_dev()
async def email(ctx):
    await ctx.send("Your email is " + devEmail)

## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
