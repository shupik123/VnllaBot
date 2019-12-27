# Works with Python 3.6

import asyncio
import io
import json
import math
import os
import random
import sys
import time
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import requests

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

from mcstatus import MinecraftServer

starttime = None
bot_devs = [280043108782178305, 276514261390327811]

server = MinecraftServer.lookup("vnlla.net:25565")

client = commands.Bot(command_prefix = "!")
client.remove_command('help')

shupik = "C:\\Users\\Shupik desu\\Desktop\\Programing\\python\\Bot\\"
xelada = "C:\\Users\\alexd\\Desktop\\git\\VnllaBot\\"
vps = "/home/vnlla/"

# discord token
try:
	with open(vps+"Vnllatoken.json", "r") as f:
		token = json.load(f)[0]
except:
	try:
		with open(shupik+"Vnllatoken.json", "r") as f:
			token = json.load(f)[0]
	except:
		try:
			with open(xelada+"Vnllatoken.json", "r") as f:
				token = json.load(f)[0]
		except:
			print("No valid discord token found.")
			sys.exit(0)

# ksoft token
# try:
# 	with open(vps+"KsoftToken.json", "r") as f:
# 		ksoft_token = json.load(f)[0]
# except:
# 	try:
# 		with open(shupik+"KsoftToken.json", "r") as f:
# 			ksoft_token = json.load(f)[0]
# 	except:
# 		try:
# 			with open(xelada+"KsoftToken.json", "r") as f:
# 				ksoft_token = json.load(f)[0]
# 		except:
# 			print("No valid ksoftapi token found.")
# 			sys.exit(0)

# ksoft_client = ksoftapi.Client(api_key=ksoft_token)

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


# updates status every 30s
async def vnllastatusloop():
	global notifylist
	global plot_data

	await client.wait_until_ready()
	downtime = 0
	while True:
		plot_data_static = plot_data

		try:
			status = server.status()
			# if downtime >= 5:
			# 	for tags in notifylist:
			# 		# notify all people on list that server is up
			# 		user = await client.fetch_user(tags)
			# 		await user.send("Vnlla is back online.")

			await client.change_presence(status=discord.Status.online, activity=discord.Game("Server Online ({0}/{1})".format(status.players.online,status.players.max)))
			downtime = 0

			# plot data
			if status.players.online >= 3:
				plot_data_static['x'].append(time.time())
				plot_data_static['y'].append(status.players.online)


		except IOError:
			if downtime < 5:
				await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("Down for {a} min".format(a=downtime)))

			# else:
			# 	await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("Down for {a} min".format(a=downtime)))
			
			# if downtime == 5:
			# 	for tags in notifylist:
			# 		# notify all people on list that server is down
			# 		user = await client.fetch_user(tags)
			# 		await user.send("Vnlla has been down for 5 minutes.")

			downtime += 0.5

			# plot data
			if downtime > 5:
				plot_data_static['x'].append(time.time())
				plot_data_static['y'].append(0)

		with open("plot.json", "w") as f:
			json.dump(plot_data_static, f)
		plot_data = plot_data_static
			
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
	embed.add_field(name='!stats [`time unit` in past to view] [time unit: (h, d, w)]', value='Shows you a high tech graph of activity on vnlla.net!', inline=False)
	embed.add_field(name='**NEW:** !appeal', value='Explains to you the appeal process', inline=False)
	embed.set_footer(text="<argument>: required input | [argument]: optional input | Ping @shupik#2705 for any needs.")
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
async def stats(ctx, stop_time=-1.0, stop_u ='d', regression=''):
	global plot_data
	# make plot_data not change with temp
	temp_pd = plot_data

	# convert time unit input
	if stop_time <= 0:
		stop_sec = time.time() - temp_pd['x'][0]
		last_time = 'eternity'
		stop_time = ""
	elif stop_u in ['m', 'mn', 'month', 'months']:
		stop_sec = stop_time * 7 * 86400 * 4 #months
		last_time = 'months'
	elif stop_u in ['w', 'wk', 'week', 'weeks']:
		stop_sec = stop_time * 7 * 86400 #weeks
		last_time = 'weeks'
	elif stop_u in ['d', 'day', 'days']:
		stop_sec = stop_time * 86400 #days
		last_time = 'days'
	elif stop_u in ['h', 'hr', 'hour', 'hours']:
		stop_sec = stop_time * 3600 #hours
		last_time = 'hours'
	else:
		embed = discord.Embed(title=':warning: Error! :warning:', description='Time unit {} was not recognized!'.format(stop_u), color=0xff0000)
		return await ctx.send(embed=embed)
	
	# generate x,y data relative to current time
	data_x = []
	data_y = []
	
	i = time.time() - stop_sec;
	index, t = min(enumerate(temp_pd['x']), key=lambda x:abs(x[1]-i))
	
	for _ in range(int(t), int(time.time())):
		print(index)
		print(len(temp_pd['x']))
		if 0 > index >= len(temp_pd['x'])-30 or temp_pd['x'][index] > t:
			data_x.append(t-time.time());
			#data_y.append(temp_pd['y'][index-20160]);
			data_y.append(40);
		else:
			data_x.append((temp_pd['x'][index] - time.time()))
			data_y.append(temp_pd['y'][index])
			index += 1;
		t += 30;

	# test for not enough data points
	if len(data_y) < 2:
		embed = discord.Embed(title=':warning: Error! :warning:', description='Time frame was too small to show any data!', color=0xff0000)
		return await ctx.send(embed=embed)

	# figure out time unit for xlabel
	if (data_x[0] - data_x[-1]) / 60 <= 120: #minutes
		for i in range(len(data_x)):
			data_x[i] = data_x[i] / 60
			x_time = 'minutes'
	elif (data_x[0] - data_x[-1]) / 3600 <= 48: #hours
		for i in range(len(data_x)):
			data_x[i] = data_x[i] / 3600
			x_time = 'hours'
	elif (data_x[0] - data_x[-1]) / 86400 <= 14: #days
		for i in range(len(data_x)):
			data_x[i] = data_x[i] / 86400
			x_time = 'days'
	elif (data_x[0] - data_x[-1]) / 604800 <= 8: #weeks
		for i in range(len(data_x)): 
			data_x[i] = data_x[i] / 604800
			x_time = 'weeks'
	else: # months
		for i in range(len(data_x)): 
			data_x[i] = data_x[i] / 2419200
			x_time = 'months'

	new_x = data_x.copy()
	new_y = data_y.copy()
	df = pd.DataFrame(new_y, index=new_x)
	df_average = df.rolling(min_periods=1, center=True, window=int(len(data_x)/75)).mean() # smaller window = more spikes. 
	# Therefore, more data = less spikes (easier to look at)
	plt.plot(new_x, df_average, color="green", linewidth=2, label="Rolling")

	# create regression data
	fit = np.polyfit(data_x, data_y, 1)
	fit_fn = np.poly1d(fit)
	data_ry = [fit_fn(data_x[0]), fit_fn(data_x[-1])]
	data_rx = [data_x[0], data_x[-1]]

	# making plot
	plt.plot(data_x, data_y, color='navy', linewidth=1, label='Main', alpha=0.1)

	if regression == '-r':
		plt.plot(data_rx, data_ry, color='orange', linewidth=5, label='Regression')
		plt.legend()
	plt.xlabel('Time in {} before now'.format(x_time))
	plt.ylabel('Number of players')
	plt.title('vnlla.net activity')

	# max player check
	server = MinecraftServer.lookup('vnlla.net:25565')
	try:
		status = server.status()
		max_players = status.players.max
	except IOError:
		max_players = 40
	plt.ylim([0, max_players])

	# send picture
	buf = io.BytesIO()
	plt.savefig(buf, edgecolor='none', format='png')
	buf.seek(0)

	if stop_sec == math.inf:
		embed = discord.Embed(title='Displaying available activity data for **all time**.', color=0x57de45)
	else:
		embed = discord.Embed(title='Displaying available activity data for the last **{0} {1}**.'.format(abs(round(data_x[-1])), x_time), color=0x57de45)

	embed.add_field(name='__Mean Player Count__', value='**{}**'.format(round(sum(data_y)/len(data_y), 2)), inline=False)

	myfile = discord.File(buf, 'stats.png')
	embed.set_image(url='attachment://stats.png')

	await ctx.send(embed=embed, file=myfile)

	plt.clf()
	

@client.command(pass_context = True)
async def appeal(ctx):
	embed=discord.Embed(title=" ", description="So, you've been banned for some reason. You want to appeal? These links should help you out!", color=0x800000)
	embed.set_author(name="How to appeal")
	embed.add_field(name="Create a forum account:", value="http://forum.vnlla.org/ucp.php?mode=register", inline=False)
	embed.add_field(name="Create a ban appeal:", value="http://forum.vnlla.org/posting.php?mode=post&f=16", inline=False)
	embed.set_footer(text="Go to #discussion_staff_contact for any needs. | Don't spam the staff.")
	await ctx.send(embed=embed)


@client.command(pass_context = True)
async def data_purge(ctx, confirmation=''):
	global plot_data
	if ctx.author.id not in bot_devs:
		embed = discord.Embed(title=':warning: Error! :warning:', description='This command is exclusive to bot developers!', color=0xff0000)
		return await ctx.send(embed=embed)

	if confirmation != 'PURGE':
		embed = discord.Embed(title=':warning: Error! :warning:', description='You must enter `!data_purge PURGE` to confirm this command.', color=0xff0000)
		return await ctx.send(embed=embed)

	plot_data_static = plot_data
	for i in range(len(plot_data_static['y'])):
		if plot_data_static['y'][i] < 3:
			plot_data_static['x'].pop(i)
			plot_data_static['y'].pop(i)
			
	
	with open("plot.json", "w") as f:
		json.dump(plot_data_static, f)
	
	plot_data = plot_data_static

	embed = discord.Embed(title='Player data points of `y<3` removed!', description='I hope you wanted this command...', color=0xffff00)
	return await ctx.send(embed=embed)


# @client.command(pass_context = True)
# async def meme(ctx, *search):
# 	search = ' '.join(search)
# 	img = await ksoft_client.random_meme()

# 	embed = discord.Embed(title=img.title, url=img.source)
# 	embed.set_image(url=img.url)
# 	embed.set_footer(text="▲{0.upvotes} | ▼{0.downvotes}".format(img))
# 	await ctx.send(embed=embed)


@client.command(pass_context = True)
async def echo(ctx, channel: int, *text):
	if ctx.author.id not in bot_devs:
		return
	text = ' '.join(text)

	channel = client.get_channel(channel)
	await channel.send(text)
	

client.loop.create_task(vnllastatusloop())
client.run(token)