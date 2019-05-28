# Works with Python 3.6
import discord
import os
import time
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import requests
import json

client = commands.Bot(command_prefix = "!")

status = "vnllastatus.png"
down = "vnllastatusdown.png"

fileName = "notifylist.json"
with open(fileName, "r") as f:
	notifylist = json.load(f)

def image():
	url = 'https://minecraft-mp.com/half-banner-134764.png'
	r = requests.get(url, allow_redirects=True)
	open("vnllastatus.png", 'wb').write(r.content)
	return "vnllastatus.png"

def vnllastatus():
	image()
	if open(status,"rb").read() == open(down,"rb").read():
		return False
	else:
		return True

async def vnllastatusloop():
	await client.wait_until_ready()
	downtime = 0
	while not client.is_closed:
		if vnllastatus() == True:
			await client.change_presence(status=discord.Status.do_not_disturb, game=discord.Game(name="Down for {a} min".format(a=downtime)))
			if downtime < 5:
				await client.change_presence(status=discord.Status.idle, game=discord.Game(name="Down for {a} min".format(a=downtime)))
			if downtime == 5:
				for people in notifylist:
					await client.send_message(await client.get_user_info(people), "Vnlla has been down for 5 minutes.")
			downtime += 1
		else:
			await client.change_presence(status=discord.Status.online, game=discord.Game(name="Server Online"))
			if downtime > 0:
				for people in notifylist:
					await client.send_message(await client.get_user_info(people), "Vnlla is back online.")
			downtime = 0
		await asyncio.sleep(60)

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

@client.command(pass_context = True)
async def vnlla(ctx):
	await client.send_file(ctx.message.channel, image())

@client.command(pass_context = True)
async def add(ctx):
	global notifylist
	notifylist.append(ctx.message.author.id)
	with open(fileName, "w") as f:
			json.dump(notifylist, f)
	await client.say("You've been added to the server notification list.\nUse `!remove` to get off the list.")

@client.command(pass_context = True)
async def remove(ctx):
	global notifylist
	notifylist.remove(ctx.message.author.id)
	with open(fileName, "w") as f:
			json.dump(notifylist, f)
	await client.say("You've been removed from the server notification list.\nUse `!add` to get on the list.")

client.loop.create_task(vnllastatusloop())
client.run("Blocked")