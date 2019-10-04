# Works with Python 3.6

import os
import time
import requests
import json
import random

import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot

from mcstatus import MinecraftServer

import io
import matplotlib.pyplot as plt
import math

starttime = None

server = MinecraftServer.lookup("vnlla.net:25565")

client = commands.Bot(command_prefix = "!")
client.remove_command('help')

shupik = "C:\\Users\\Shupik desu\\Desktop\\Programing\\python\\Bot\\Vnllatoken.json"
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
		notifylist = []

# getting the plot data
try:
	fileName = "plot.json"
	with open(fileName, "r") as f:
		plot_data = json.load(f)
except:
	with open(fileName, "w") as f:
		json.dump({}, f)
		plot_data = {'x':[],'y':[]}

# updates status every minute
async def vnllastatusloop():
	global notifylist
	global plot_data

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

			# plot data
			plot_data['x'].append(time.time())
			plot_data['y'].append(status.players.online)


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

			downtime += 0.5

			# plot data
			plot_data['x'].append(time.time())
			plot_data['y'].append(0)

		with open("plot.json", "w") as f:
			json.dump(plot_data, f)
			
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
	embed=discord.Embed(title="Github Link", url="https://github.com/shupik123/VnllaBot", color=0x62f3ff)
	embed.add_field(name='!help', value='You already know.', inline=False)
	embed.add_field(name='!vnlla', value='Tells you the status of the vnlla minecraft server.', inline=False)
	embed.add_field(name='!notify', value='Will ping you when a spot on the server opens up.', inline=False)
	embed.add_field(name='!add', value='Adds you to the notification list of when vnlla goes down and back up.', inline=False)
	embed.add_field(name='!remove', value='Removes you from the notification list.', inline=False)
	embed.add_field(name='!botstatus', value='Tells you how long the bot has been running.', inline=False)
	embed.add_field(name='!stats <days in past to view>', value='**NEW!** Shows you a high tech graph of activity on vnlla.net!', inline=False)
	embed.set_footer(text="[argument]: required input\n <argument>: optional input\nPing @shupik#2705 for any needs.")
	await ctx.send(embed=embed)


@client.command(pass_context = True)
async def vnlla(ctx):
	try:
		status = server.status()
		pass
	except IOError:
		return await ctx.send("The server is currently offline.")
	await ctx.send(embed=discord.Embed(title="The server has **{0}/{1}** players.".format(status.players.online, status.players.max), color=0x1f3354))


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
async def hack(ctx):
	progress = 0
	await ctx.send("Hacking started...")
	
	hacking = await ctx.send("Progress: `----------`")
	visual = None
	while progress < 10:
		progress += random.randint(1,10)/10
		msg = "Progress: `{0}{1}`".format('█'*int(progress), '-'*(10-int(progress)))
		await hacking.edit(content=msg)
		await asyncio.sleep(3)
	await ctx.send('Hacking successful! To confirm you are an actual person please verify yourself with this link to gain access to VnllaBot!\n<https://tinyurl.com/vnlla-bot>')


@client.command(pass_context = True)
async def test(ctx):
	await ctx.send("Test command invoked at `{0} > {1}`".format(str(ctx.guild),str(ctx.channel)))
	print("Test command invoked at `{0} > {1}`".format(str(ctx.guild),str(ctx.channel)))

@client.command(pass_context = True)
async def stats(ctx, time_span=math.inf):
	global plot_data
	
	time_span *= 86400

	# generate x data relative to current time
	data_x = []
	data_y = []
	for i in range(0, len(plot_data['x'])):
		if plot_data['x'][i] > time_span:
			break
		else:
			data_x.append((plot_data['x'][i] - time.time()) / 86400)
			data_y.append(plot_data['y'][i])

	# making plot
	plt.plot(data_x, data_y)
	plt.xlabel('Time in days before now')
	plt.ylabel('Number of players')

	# send picture
	buf = io.BytesIO()
	plt.savefig(buf, edgecolor='none', format='png')
	buf.seek(0)

	embed = discord.Embed(title='Displaying available activity data for the last **{} days**.'.format(time_span/86400), color=0xffffff)
	embed.add_field(name='__Mean Player Count__', value='**{}**'.format(sum(data_y)/len(data_y)), inline=False)
	await ctx.send(embed=embed)

	await ctx.send(file=discord.File(buf, 'stats.png'))
	plt.clf()
	

client.loop.create_task(vnllastatusloop())
client.run(token)