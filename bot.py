# bot.py

import os #for getenv
import random #for randoming
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio #for async
import time #for making timestamps
import simplejson as json #for reading/writing json
import sheet #import the google sheets commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

#bot event notifying host that bot is initialized
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#frog leap/fro lwao event. used in event form to prevent requiring command prefix
@bot.event
async def on_message(message):
    #preventing communication with other bots
    if message.author.bot:
        return
    #logic for frog leap
    if message.content.lower().startswith("frog leap"):
        frogroll = random.randint(1,10)
        #fro lwao is 10% chance rn
        if frogroll > 1:
            await message.channel.send("frog leap")
        else:
            await message.channel.send("fro lwao")
    await bot.process_commands(message)

#error handling event
@bot.event
async def on_command_error(ctx, error):
    #error handling for cooldown
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Command on cooldown! Wait for {round(error.retry_after, 0)} seconds before trying again.")

#tell bot to update reach_maps.json with newest information (if someone updates the sheet)
@bot.command(
    help = "Updates sheet info. MOD or ADMIN use only.",
    hidden = True
)
@commands.has_any_role("ADMIN", "MOD")
async def refresh(ctx):
    try:
        sheet_data = sheet.get_google_sheet_data(sheet.spreadsheet_id, sheet.sheet_name, sheet.KEY)
        maps = list(sheet_data.values())[2]
        reach_maps = sheet.make_reach(maps)
        sheet.update_maps(reach_maps)
        await ctx.send("Local data updated!")
    except:
        await ctx.send("uhhhh smth went wrong lol")

#gives random map to user from list depending on specifications
@bot.command(
        help = "Gives random map. Takes optional parameters for difficulty, forger name, and map type.\n\nDifficulty: any combination of easy/medium/hard. Defaults to any difficulty.\n\nForger name: forger's name as it is spelled in the verified maps sheet (case sensitive). For forgers with names with spaces in them, surround the name in quotation marks (eg. \"find pain\"). Defaults to any forger.\n\nMap type: jump/mongoose/all. Defaults to jump maps.",
        cooldown_after_parsing = True
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def map(ctx, *args):
    #args: difficulty (easy, medium, hard), forger (case sensitive), type (jump, mongoose, all)
    #read reach_maps.json and store as list
    args_case = list(x.casefold() for x in args)
    with open("reach_maps.json", "r") as f:
        map_list= json.load(f)

    #create all possible accepted options for each search filter
    difficulty_list = ["easy", "medium", "hard"]
    forger_list = []
    for i in map_list:
        if i[0] not in forger_list:
            forger_list.append(i[0].casefold())
    map_type_list = ["all", "mongoose", "jump"]

    #establish what search filter parameters were given by user
    select_difficulty = set(args_case).intersection(difficulty_list)
    select_forger = set(args_case).intersection(forger_list)
    select_map_type = set(args_case).intersection(map_type_list)

    #create lists for each search parameter
    difficulty_maps = []
    forger_maps = []
    type_maps = []

    #handling search filter options for difficulty
    if select_difficulty == set():
        difficulty_maps = map_list
    else:
        for i in select_difficulty:
            for j in map_list:
                if i == j[2].casefold() and j not in difficulty_maps:
                    difficulty_maps.append(j)

    #handling search filter options for forger
    if select_forger == set():
        forger_maps = map_list
    else:
        for i in select_forger:
            for j in map_list:
                if i in j[0].casefold() and j not in forger_maps:
                    forger_maps.append(j)

    #handling search filter options for map type
    #default behaviour is to ignore mongoose maps
    if select_map_type == set():
        for i in map_list:
            if "mongoose" not in i[8]:
                type_maps.append(i)
    else:
        for i in select_map_type:
            for j in map_list:
                if i == "all" and j not in type_maps:
                    type_maps.append(j)
                elif i == "jump" and j not in type_maps:
                    if "mongoose" not in j[8]:
                        type_maps.append(j)
                elif i == "mongoose":
                    if "mongoose" in j[8] and j not in type_maps:
                        type_maps.append(j)

    #intersection of map queries
    query_list = set(tuple(x) for x in difficulty_maps).intersection(set(tuple(x) for x in forger_maps),set(tuple(x)for x in type_maps))
    if query_list == set():
        #if search is too exclusive and no maps fit all criteria
        await ctx.send("No maps found :(\nPlease try again with different arguments.")
        map.reset_cooldown(ctx)
    else:
        #choose random map out of queried options
        random_map = random.randint(0, len(query_list) - 1)
        chosen = list(query_list)[random_map]
        await ctx.send(f"**{chosen[1]}** by **{chosen[0]}** ({chosen[2]})")

bot.run(TOKEN)
