# test
# Works with Python 3.6
import discord
import os
import time
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import requests
import json
from mcstatus import MinecraftServer

server = MinecraftServer.lookup("vnlla.net:25565")

client = commands.Bot(command_prefix = "!")

client.remove_command('help')

shupik = "C:\\Users\\Shupik desu\\Desktop\\Programing\\Bot\\Vnllatoken.json"
# XELADA INPUT DIRECTORY HERE
xelada = "/home/vnlla/Vnllatoken.json"

try:
	with open(shupik, "r") as f:
		token = json.load(f)[0]
except:
	with open(xelada, "r") as f:
		token = json.load(f)[0]

# getting the list of people that want to be notified
try:
	fileName = "notifylist.json"
	with open(fileName, "r") as f:
		notifylist = json.load(f)
except:
	with open(fileName, "w") as f:
		json.dump([], f)

# updates status every minute
async def vnllastatusloop():
	global notifylist
	await client.wait_until_ready()
	downtime = 0
	while True:
		try:
			status = server.status()
			if downtime >= 5:
				for tags in notifylist:
					# notify all people on list that server is up
					user = await client.fetch_user(tags)
					await user.send("Vnlla is back online.")

			await client.change_presence(status=discord.Status.online, activity=discord.Game("Server Online ({0}/{1})".format(status.players.online,status.players.max)))
			downtime = 0

		except IOError:
			if downtime < 5:
				# if it is down for less than 5 minutes set to idle status
				
				await client.change_presence(status=discord.Status.idle, activity=discord.Game("Down for {a} min".format(a=downtime)))
			else:
				await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("Down for {a} min".format(a=downtime)))
			
			if downtime == 5:
				for tags in notifylist:
					# notify all people on list that server is down
					user = await client.fetch_user(tags)
					await user.send("Vnlla has been down for 5 minutes.")

				all_channels = client.get_all_channels()
				for channel in all_channels:
					if str(channel) == "server_down_reporting":
						server_down_channel = channel
						break
				guild = client.get_guild(205205049335349248)
				owner = guild.get_role(205210339141222400)
				# pings in the server_down_channel
				await server_down_channel.send("The server is down!\n{0}".format(owner.mention))

			downtime += 0.5

		await asyncio.sleep(30)


@client.event
async def on_ready():
	# just saying that the bot is on
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	global starttime
	starttime = time.time()

@client.command(pass_context = True)
async def help(ctx):
	helphelp = "`!help` : you already know.\n"
	vnllahelp = "`!vnlla` : tells you the status of the vnlla minecraft server.\n"
	notifyhelp = "`!notify` : will ping you when a spot on the server opens up.\n"
	addhelp = "`!add` : adds you to the notification list of when vnlla goes down and back up.\n"
	removehelp = "`!remove` : removes you from the notification list.\n"
	botstatushelp = "`!botstatus` : tells you which Discord servers the bot is on and for how long it has been running.\n\n"
	invite = "To invite the bot to your own server: https://discordapp.com/oauth2/authorize?client_id=582302540784205870&scope=bot&permissions=39936\n"
	github = "Check out our github here: https://github.com/shupik123/VnllaBot"
	
	allhelp = helphelp + vnllahelp + notifyhelp + addhelp + removehelp + memehelp + botstatushelp + invite + github
	await ctx.send(allhelp)

@client.command(pass_context = True)
async def vnlla(ctx):
	try:
		status = server.status()
		pass
	except IOError:
		return await ctx.send("The server is currently offline.")
	await ctx.send(embed=discord.Embed(title="The server has **{0}/{1}** players.".format(status.players.online, status.players.max), color=0x1f3354)


@client.command(pass_context=True)
async def notify(ctx):
	try:
		status = server.status()
		pass
	except IOError:
		return await ctx.send("The server is currently offline.")
	
	if status.players.online != status.players.max:
		return await ctx.send("A spot on the server is open right now!")

	msg = await ctx.send("I will notify you when a spot opens up.")
	while status.players.online == status.players.max:
		status = server.status()
		await asyncio.sleep(2)
	await msg.delete()
	return await ctx.send("<@{0}> A spot on the server is open right now!".format(ctx.message.author.id))


@client.command(pass_context = True)
async def botstatus(ctx):
	serverlist = "**Servers the bot is in:**```\n"
	for server in client.guilds:
		# gets the names of all the servers
		serverlist = serverlist + "{a} owned by {b}\n".format(a=server.name,b=server.owner)
	serverlist = serverlist + "```"
	await ctx.send(serverlist)

	# gets the current up time of the bot
	global starttime
	current_time = round(time.time() - starttime)
	second = current_time % 60
	minute = (current_time // 60) % 60
	hour = current_time // 3600
	
	await ctx.send("{name} has been running for {hour} hr, {minute} min, {second} sec.".format(name=client.user.name, hour=hour, minute=minute, second=second))
		

@client.command(pass_context = True)
async def add(ctx):
	# adds to the list of people to be notified
	global notifylist
	if ctx.message.author.id in notifylist:
		return await ctx.send("You are already on the notify list.\nUse `!remove` to get off the list.")
	notifylist.append(int(ctx.message.author.id))
	print("{person} was added to notifylist".format(person = ctx.message.author))
	with open(fileName, "w") as f:
		# writes the new person to the .json file
		json.dump(notifylist, f)
	await ctx.send("You've been added to the server notification list.\nUse `!remove` to get off the list.")


@client.command(pass_context = True)
async def remove(ctx):
	global notifylist
	if ctx.message.author.id not in notifylist:
		return await ctx.send("You are not on the notify list.\nUse `!add` to get on the list.")
	notifylist.remove(int(ctx.message.author.id))
	print("{person} was removed from notifylist".format(person = ctx.message.author))
	with open(fileName, "w") as f:
		# removes the new person from the .json file
		json.dump(notifylist, f)
	await ctx.send("You've been removed from the server notification list.\nUse `!add` to get on the list.")


@client.command(pass_context = True)
async def meme(ctx):
	await ctx.send("Sorry, the meme command is gone!\n:upsettimyspaghetti:")

@client.command(pass_context = True)
async def test(ctx):
	await ctx.send("Test command invoked at `{0} > {1}`".format(str(ctx.guild),str(ctx.channel)))
	print("Test command invoked at `{0} > {1}`".format(str(ctx.guild),str(ctx.channel)))


client.loop.create_task(vnllastatusloop())
client.run(token)