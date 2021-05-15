import discord
from discord.ext import commands
# import random
import typing
import os
import asyncio
import asyncpg
import datetime

db = None

# https://discord.com/api/oauth2/authorize?client_id=843224909958479933&permissions=268823632&scope=bot

charProfilesSQL = '''
    CREATE TABLE IF NOT EXISTS characters (
        id SERIAL,
        nickname TEXT,
        fullname TEXT,
        pronouns TEXT,
        age TEXT,
        date TEXT,
        tribe TEXT,
        rank TEXT,
        appearance TEXT,
        personality TEXT,
        sheet TEXT,
        image TEXT,
        owner_uid BIGINT
    );'''

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
    await db.execute(charProfilesSQL)
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN')
devID = int(os.environ.get('DEV_ID'))

client = discord.Client()

bot = commands.Bot(command_prefix='mi!', db=db)

def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == devID
    return commands.check(predicate)

## Code Here ----------------------------------------------------------

@bot.group(invoke_without_command=True)
async def character(ctx, name: str):
    embed = discord.Embed(colour=discord.Colour(0xa6c6e4))
    
    fullName = await db.fetchval("SELECT fullname FROM characters WHERE nickname = $1;",name)
    if fullName is None:
        fullName = name
    fullName += "\u200B"
    pronouns = await db.fetchval("SELECT pronouns FROM characters WHERE nickname = $1;",name)
    if pronouns is None:
        pronouns = "-"
    pronouns += "\u200B"
    creationAge = await db.fetchval("SELECT age FROM characters WHERE nickname = $1;",name)
    if creationAge is None:
        creationAge = "-"
    creationAge += "\u200B"
    creationDate = await db.fetchval("SELECT date FROM characters WHERE nickname = $1;",name)
    if creationDate is None:
        creationDate = "-"
    creationDate += "\u200B"
    tribe = await db.fetchval("SELECT tribe FROM characters WHERE nickname = $1;",name)
    if tribe is None:
        tribe = "-"
    tribe += "\u200B"
    rank = await db.fetchval("SELECT rank FROM characters WHERE nickname = $1;",name)
    if rank is None:
        rank = "-"
    rank += "\u200B"
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
            if characterUser != user:
                await ctx.send("That character does not belong to you.")
            else:
                inputLength = len(newValue)
                if (newValue == None) and (setType == "nickname"):
                    await ctx.send("You must set what the new value is.")
                elif (inputLength > 1024):
                    await ctx.send("Your new value must be 1024 characters or fewer.")
                else:
                    sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                    await db.execute(sqlText,newValue,nickname)
                    await ctx.send("Character " + nickname + " has been updated.")
                
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
    

## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
