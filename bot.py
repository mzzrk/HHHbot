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

#gives random map to command user
@bot.command(
    pass_context = True,
    help = "Gives random map. Can specify easy/medium/hard (optional)",
    cooldown_after_parsing = True
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def map(ctx, difficulty = ""):
    with open("reach_maps.json", "r") as f:
        map_list = json.load(f)
    if difficulty == "":
        random_map = random.randint(0,(len(map_list)-1))
        chosen = map_list[random_map]
        await ctx.send(f"**{chosen[1]}** by **{chosen[0]}** ({chosen[2]})")
    else:
        shortlist = []
        diff_upper = difficulty.upper()
        diff_options = ["EASY", "MEDIUM", "HARD"]
        if diff_upper in diff_options:
            for i in map_list:
                if i[2] == diff_upper:
                    shortlist.append(i)
            random_map = random.randint(0,(len(shortlist)-1))
            chosen = shortlist[random_map]
            await ctx.send(f"**{chosen[1]}** by **{chosen[0]}** ({chosen[2]})")
        else:
            await ctx.send("Invalid argument. Use !map without arguments or specify !map [easy/medium/hard]")
            map.reset_cooldown(ctx)

bot.run(TOKEN)