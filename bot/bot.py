import discord
from discord.ext import commands
import random
import typing
import os
import asyncio
import asyncpg
import datetime
import DiscordUtils

from configsql import *
from configlists import *

db = None

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

intents = discord.Intents.default() # save time typing this shit by saying it here
intents.members = True

bot = commands.Bot(command_prefix='mi!', db=db, intents=intents)

def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == devID
    return commands.check(predicate)
    
def is_admin():
    def predicate(ctx):
        return ctx.message.author.id == adminID
    return commands.check(predicate)

## CHARACTER PROFILES ----------------------------------------------------------
@bot.group(invoke_without_command=True,aliases=["char"])
async def character(ctx, name: str):
    nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",name)
    if nameCheck is None:
        await ctx.send("I couldn't find a character with the nickname '" + name + "'")
    else:
        fullName = await db.fetchval("SELECT fullname FROM characters WHERE nickname = $1;",name)
        if fullName is None:
            fullName = name
        pronouns = await db.fetchval("SELECT pronouns FROM characters WHERE nickname = $1;",name)
        if pronouns is None:
            pronouns = "-"
        creationAge = await db.fetchval("SELECT age FROM characters WHERE nickname = $1;",name)
        if creationAge is None:
            creationAge = "-"
        creationDate = await db.fetchval("SELECT date FROM characters WHERE nickname = $1;",name)
        if creationDate is None:
            creationDate = "-"
        tribe = await db.fetchval("SELECT tribe FROM characters WHERE nickname = $1;",name)
        if tribe is None:
            tribe = "-"
        rank = await db.fetchval("SELECT rank FROM characters WHERE nickname = $1;",name)
        if rank is None:
            rank = "-"
        appearance = await db.fetchval("SELECT appearance FROM characters WHERE nickname = $1;",name)
        personality = await db.fetchval("SELECT personality FROM characters WHERE nickname = $1;",name)
        backstory = await db.fetchval("SELECT backstory FROM characters WHERE nickname = $1;",name)
        sheetURL =  await db.fetchval("SELECT sheet FROM characters WHERE nickname = $1;",name)
        if sheetURL is None:
            sheetURL = "-"
        quote = await db.fetchval("SELECT quote FROM characters WHERE nickname = $1;",name)
        emoji = await db.fetchval("SELECT emoji FROM characters WHERE nickname = $1;",name)
        if emoji is None:
            emoji = ""
        else:
            emoji += " "
        color = await db.fetchval("SELECT color FROM characters WHERE nickname = $1;",name)
        if color is None:
            color = 8163583
        note1 = await db.fetchval("SELECT note1 FROM characters WHERE nickname = $1;",name)
        note2 = await db.fetchval("SELECT note2 FROM characters WHERE nickname = $1;",name)
        note3 = await db.fetchval("SELECT note3 FROM characters WHERE nickname = $1;",name)
        note4 = await db.fetchval("SELECT note4 FROM characters WHERE nickname = $1;",name)
        note1name = await db.fetchval("SELECT note1name FROM characters WHERE nickname = $1;",name)
        note2name = await db.fetchval("SELECT note2name FROM characters WHERE nickname = $1;",name)
        note3name = await db.fetchval("SELECT note3name FROM characters WHERE nickname = $1;",name)
        note4name = await db.fetchval("SELECT note4name FROM characters WHERE nickname = $1;",name)
        image = await db.fetchval("SELECT image FROM characters WHERE nickname = $1;",name)
        ownerID = await db.fetchval("SELECT owner_uid FROM characters WHERE nickname = $1;",name)

        if quote is not None:
            quote = "*" + quote + "*"
            embed1 = discord.Embed(colour=color,title=quote)
        else:
            embed1 = discord.Embed(colour=color)
            
        embed2 = discord.Embed(colour=color)

        if image != None:
            embed1.set_image(url=image)
            embed2.set_image(url=image)

        embed1.set_thumbnail(url="https://i.imgur.com/Qpen3fF.png")
        embed2.set_thumbnail(url="https://i.imgur.com/Qpen3fF.png")
        
        embed1.add_field(name=emoji+"Full Name", value=fullName, inline=True)
        embed1.add_field(name=emoji+"Pronouns", value=pronouns, inline=True)
        embed1.add_field(name=emoji+"Age on Creation", value=creationAge, inline=True)
        embed1.add_field(name=emoji+"Tribe", value=tribe, inline=True)
        embed1.add_field(name=emoji+"Rank", value=rank, inline=True)
        embed1.add_field(name=emoji+"Date of Creation", value=creationDate, inline=True)
        
        if appearance is not None:
            embed1.add_field(name=emoji+"Appearance", value=appearance, inline=False)
        embed1.add_field(name=emoji+"Character Sheet Url", value=sheetURL, inline=False)
        if personality is not None:
            embed2.add_field(name=emoji+"Personality", value=personality, inline=False)
        if backstory is not None:
            embed2.add_field(name=emoji+"Backstory", value=backstory, inline=False)
        
        if note1 is not None:
            if note1name is None:
                note1name = "Note 1"
            embed1.add_field(name=note1name, value=note1, inline=False)
        if note2 is not None:
            if note2name is None:
                note2name = "Note 2"
            embed1.add_field(name=note2name, value=note2, inline=False)
        if note3 is not None:
            if note3name is None:
                note3name = "Note 3"
            embed1.add_field(name=note3name, value=note3, inline=False)
        if note4 is not None:
            if note4name is None:
                note4name = "Note 4"
            embed1.add_field(name=note4name, value=note4, inline=False)
            
        if "<" in emoji:
            emoji = ""

        embed1.set_footer(text=emoji+"Page 1/2")
        embed2.set_footer(text=emoji+"Page 2/2")
            
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('1️⃣', "page 0")
        paginator.add_reaction('2️⃣', "page 1")

        embeds = [embed1, embed2]
        
        await paginator.run(embeds)
    
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
        await ctx.send("You can set: *nickname, quote, color, emoji, fullname, pronouns, age, date, tribe, rank, appearance, sheet, personality, backstory, note1(2,3,4), note1(2,3,4)name, image*")
    elif setType not in ["nickname","fullname","pronouns","age","date","tribe","rank","appearance","personality","sheet","image","backstory","note1","note2","note3","note4","note1name","note2name","note3name","note4name","color","colour","emoji","quote"]:
        await ctx.send("I don't recognize " + setType + " as a valid value. Please use one of the following: *nickname, quote, color, emoji, fullname, pronouns, age, date, tribe, rank, appearance, sheet, personality, backstory, note1(2,3,4), note1(2,3,4)name, image*")
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
                    if setType in ["colour","color"]:
                        setType = "color"
                        
                        if newValue is not None:
                            newValue = newValue.replace("#","")
                            newValue = int(newValue, 16)
                        
                    sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                    await db.execute(sqlText,newValue,nickname)
                    await ctx.send("Character " + nickname + " has been updated.")

## CHARACTER SHEETS -------------------------------------------------------------------------
@bot.group(invoke_without_command=True)
async def sheet(ctx, name: str):
    nameCheck = await db.fetchval("SELECT nickname FROM characters WHERE nickname = $1;",name)
    if nameCheck is None:
        await ctx.send("I couldn't find a character with the nickname '" + name + "'")
    else:
        fullName = await db.fetchval("SELECT fullname FROM characters WHERE nickname = $1;",name)
        if fullName is None:
            fullName = name
        physical = await db.fetchval("SELECT physical FROM characters WHERE nickname = $1;",name)
        if physical is None:
        	physical = "-"
        mental = await db.fetchval("SELECT mental FROM characters WHERE nickname = $1;",name)
        if mental is None:
        	mental = "-"
        maxPhysical = await db.fetchval("SELECT maxphysical FROM characters WHERE nickname = $1;",name)
        if maxPhysical is None:
        	maxPhysical = "-"
        maxMental = await db.fetchval("SELECT maxmental FROM characters WHERE nickname = $1;",name)
        if maxMental is None:
        	maxMental = "-"
        defense = await db.fetchval("SELECT defense FROM characters WHERE nickname = $1;",name)
        if defense is None:
        	defense = "-"
        confidence = await db.fetchval("SELECT confidence FROM characters WHERE nickname = $1;",name)
        if confidence is None:
        	confidence = "-"
        fortitude = await db.fetchval("SELECT fortitude FROM characters WHERE nickname = $1;",name)
        if fortitude is None:
        	fortitude = "-"
        fortMod = await db.fetchval("SELECT fortmod FROM characters WHERE nickname = $1;",name)
        if fortMod is None:
        	fortMod = "-"
        brute = await db.fetchval("SELECT brute FROM characters WHERE nickname = $1;",name)
        if brute is None:
        	brute = "-"
        force = await db.fetchval("SELECT force FROM characters WHERE nickname = $1;",name)
        if force is None:
        	force = "-"
        swimming = await db.fetchval("SELECT swimming FROM characters WHERE nickname = $1;",name)
        if swimming is None:
        	swimming = "-"
        digging = await db.fetchval("SELECT digging FROM characters WHERE nickname = $1;",name)
        if digging is None:
        	digging = "-"
        lithe = await db.fetchval("SELECT lithe FROM characters WHERE nickname = $1;",name)
        if lithe is None:
        	lithe = "-"
        litheMod = await db.fetchval("SELECT lithemod FROM characters WHERE nickname = $1;",name)
        if litheMod is None:
        	litheMod = "-"
        careful = await db.fetchval("SELECT careful FROM characters WHERE nickname = $1;",name)
        if careful is None:
        	careful = "-"
        contortion = await db.fetchval("SELECT contortion FROM characters WHERE nickname = $1;",name)
        if contortion is None:
        	contortion = "-"
        leaping = await db.fetchval("SELECT leaping FROM characters WHERE nickname = $1;",name)
        if leaping is None:
        	leaping = "-"
        throwing = await db.fetchval("SELECT throwing FROM characters WHERE nickname = $1;",name)
        if throwing is None:
        	throwing = "-"
        constitution = await db.fetchval("SELECT constitution FROM characters WHERE nickname = $1;",name)
        if constitution is None:
        	constitution = "-"
        conMod = await db.fetchval("SELECT conmod FROM characters WHERE nickname = $1;",name)
        if conMod is None:
        	conMod = "-"
        precoup = await db.fetchval("SELECT precoup FROM characters WHERE nickname = $1;",name)
        if precoup is None:
        	precoup = "-"
        mrecoup = await db.fetchval("SELECT mrecoup FROM characters WHERE nickname = $1;",name)
        if mrecoup is None:
        	mrecoup = "-"
        diet = await db.fetchval("SELECT diet FROM characters WHERE nickname = $1;",name)
        if diet is None:
        	diet = "-"
        exposure = await db.fetchval("SELECT exposure FROM characters WHERE nickname = $1;",name)
        if exposure is None:
        	exposure = "-"
        immunity = await db.fetchval("SELECT immunity FROM characters WHERE nickname = $1;",name)
        if immunity is None:
        	immunity = "-"
        empathy = await db.fetchval("SELECT empathy FROM characters WHERE nickname = $1;",name)
        if empathy is None:
        	empathy = "-"
        charisma = await db.fetchval("SELECT charisma FROM characters WHERE nickname = $1;",name)
        if charisma is None:
        	charisma = "-"
        memory = await db.fetchval("SELECT memory FROM characters WHERE nickname = $1;",name)
        if memory is None:
        	memory = "-"
        reasoning = await db.fetchval("SELECT reasoning FROM characters WHERE nickname = $1;",name)
        if reasoning is None:
        	reasoning = "-"
        perform = await db.fetchval("SELECT perform FROM characters WHERE nickname = $1;",name)
        if perform is None:
        	perform = "-"
        Self = await db.fetchval("SELECT self FROM characters WHERE nickname = $1;",name)
        if Self is None:
        	Self = "-"
        trait = await db.fetchval("SELECT trait FROM characters WHERE nickname = $1;",name)
        if trait is None:
        	trait = "-"
        inventory = await db.fetchval("SELECT inventory FROM characters WHERE nickname = $1;",name)
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

        embed1.add_field(name="Vitality", value="Physical: "+str(physical)+"/"+str(maxPhysical)+"\nMental: "+str(mental)+"/"+str(maxMental), inline=True)
        embed1.add_field(name="Defense", value=(defense), inline=True)
        embed1.add_field(name="Confidence", value=(confidence), inline=True)
        embed1.add_field(name="Fortitude: "+str(fortitude)+" ("+str(fortMod)+")", value="Brute Attack:"+str(brute)+"\nUse Force: "+str(force)+"\nSwimming: "+str(swimming)+"\nDigging: "+str(digging), inline=True)
        embed1.add_field(name="Lithe: "+str(lithe)+" ("+str(litheMod)+")", value="Careful Attack:"+str(careful)+"\nContortion: "+str(contortion)+"\nLeaping: "+str(leaping)+"\nThrowing: "+str(throwing), inline=True)
        embed1.add_field(name="Constitution: "+str(constitution)+" ("+str(conMod)+")", value="Physical Recoup:"+str(precoup)+"\nMental Recoup: "+str(mrecoup)+"\nDiet: "+str(diet)+"\nExposure: "+str(exposure)+"\nImmunity: "+str(immunity), inline=True)
        embed1.add_field(name="Empathy: ("+str(empathy)+")", value=" \n**Reasoning: ("+str(reasoning)+")**", inline=True)
        embed1.add_field(name="Charisma: ("+str(charisma)+")", value="**Perform: ("+str(perform)+")**", inline=True)
        embed1.add_field(name="Memory: ("+str(memory)+")", value="**Self: ("+str(Self)+")**", inline=True)
        
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
    elif setType not in ["physical", "mental", "maxphysical", "maxmental", "defense", "confidence", "fortitude", "fortMod", "brute", "force", "swimming", "digging", "lithe", "litheMod", "careful", "contortion", "leaping", "throwing", "constitution", "conMod", "precoup", "mrecoup", "diet", "exposure", "immunity", "empathy", "charisma", "memory", "reasoning", "perform", "self", "trait", "inventory"]:
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
                    if setType in ["physical", "mental", "maxphysical", "maxmental", "defense", "confidence", "fortitude", "fortMod", "brute", "force", "swimming", "digging", "lithe", "litheMod", "careful", "contortion", "leaping", "throwing", "constitution", "conMod", "precoup", "mrecoup", "diet", "exposure", "immunity", "empathy", "charisma", "memory", "reasoning", "perform", "self"]:
                        newValue = int(newValue)
                
                    sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                    await db.execute(sqlText,newValue,nickname)
                    
                    if setType in ["constitution","lithe","fortitude"]:
                        newValue -= 10
                        
                        if setType == "constitution":
                            setType = "conMod"
                        elif setType == "lithe":
                            setType = "litheMod"
                        elif setType == "fortitude":
                            setType = "fortMod"
                        
                        sqlText = "UPDATE characters SET " + setType + " = $1 WHERE nickname = $2;"
                        await db.execute(sqlText,newValue,nickname)
                    
                    await ctx.send("Character " + nickname + " has been updated.")

## RANDOM COMMANDS -------------------------------------------------------
@bot.command(aliases=["r","d","dice"])
async def roll(ctx, dice: str, *, mod: typing.Optional[str]):
    try: 
        numDice, sides = map(int, dice.split('d'))
    except Exception:
        await ctx.send("Sorry, please rewrite your command as **mi!roll #d#**!")
        return
        
    if mod is not None:
        mod = int(mod.replace(" ",""))

    user = ctx.message.author
    userMention = user.mention

    resultTotal = 0
    resultText = ""

    for r in range(numDice):
        tempResult = random.randint(1,sides)
        resultTotal = resultTotal + tempResult
        if r == 0:
            resultText = resultText + str(tempResult)
        else:
            resultText = resultText + " + " + str(tempResult)
            
        if mod is not None:
            resultTotal += mod
            
    if mod is not None:
        if mod >= 0:
            modText = " + "
        else:
            mod *= -1
            modText = " - "
            
    if numDice == 1:
        resultText = ""
        if mod is not None:
            resultText = " (" + str(tempResult) + modText + str(mod) + ")"
    else:
        resultText = " (" + resultText + ")"
        if mod is not None:
            if mod >= 0:
                modText = " + "
            else:
                mod *= -1
                modText = " - "
            modAmount = mod * numDice
            resultText += modText + str(modAmount)

    await ctx.send(userMention + " You rolled " + dice + " for a total of " + str(resultTotal) + resultText)
    
@bot.command()
async def plant(ctx):
    user = ctx.message.author.id
    if user not in [devID, adminID]:
        await ctx.send("Only the admin can use this command.")
    else:
        plantChoice = random.choice(plantList)
    
        await ctx.send("Your plant is " + plantChoice)

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
 
