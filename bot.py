import aiofiles
import aiohttp
import discord
import json
import os
import patoolib
import re
import requests
import shutil
from datetime import datetime
from discord.errors import HTTPException
from discord.ext import commands

with open("config.json", "r") as config:
    cfg = json.load(config)

# bot related
TOKEN = cfg["token"]
PREFIX = cfg["prefix"]

# server related
IP = cfg["server_ip"]
PORT = int(cfg["server_port"])
MAPS_FOLDER = cfg["maps_folder"]

# discord related
ADMIN_IDS = cfg["admin_ids"]
THUMBNAIL = cfg["thumbnail"]
MAPS_CHANNEL = int(cfg["maps_channel"])

bot = commands.Bot(command_prefix=PREFIX)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}


@bot.event
async def on_ready():
    print("ready")


# download map function
@bot.command(aliases=["dl", "dm", "dlmap" "mapdl"], brief="Download a map using a map name")
# @commands.cooldown(1, 5, commands.BucketType.guild)
async def downloadmap(ctx, arg):
    embed = discord.Embed(timestamp=datetime.utcnow())
    embed.set_thumbnail(url=THUMBNAIL)
    embed.colour = 0x35cbdb

    mapname = str(arg)
    maps_channel = bot.get_channel(MAPS_CHANNEL)

    # avacado/fastdl.me method
    download_url = "https://main.fastdl.me/maps/"
    fastdlme_file = mapname + ".bsp.bz2"
    map_not_found = 0

    if requests.head(f"{download_url}{fastdlme_file}", headers=headers).status_code == 302:
        embed.set_author(name="Map Downloader - fastdl.me")
        embed.description = f"Downloading **{fastdlme_file}** from fastdl.me"
        msg = await ctx.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{download_url}{fastdlme_file}") as resp:

                map_file = await aiofiles.open(f"{MAPS_FOLDER}/{fastdlme_file}", mode="wb")
                await map_file.write(await resp.read())
                await map_file.close()

                embed.description = f"Extracting **{fastdlme_file}**..."
                await msg.edit(embed=embed)

                patoolib.extract_archive(f"{MAPS_FOLDER}/{fastdlme_file}", outdir=f"{MAPS_FOLDER}", interactive=False)

                os.remove(f"{MAPS_FOLDER}/{fastdlme_file}")
                embed.description = f"Successfully added **{mapname}**."
                await msg.edit(embed=embed)
                
    else:
        map_not_found += 1
        if map_not_found == 4:
            embed.set_author(name="Map Downloader - fastdl.me")
            embed.description = f"Unable to find map on fastdl.me"
            embed.color = 0xd2222d
            await ctx.send(embed=embed)

bot.run(TOKEN)
