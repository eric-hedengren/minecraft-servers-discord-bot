import os
import sys
import time
#import sqlite3

import aiosqlite
import mcstatus
import discord
from discord.ext import commands, tasks

import discord_config


# server embed
def create_server_embed(server_data, server_address, server_name = 'Server is Online'):
    # description
    full_description = ''

    for list_item in server_data['description']['extra']:
        full_description += list_item['text']

    # main embed
    server_embed = discord.Embed(title=server_name, description=full_description, color=discord.Color.green())

    server_embed.add_field(name='Server Address', value=server_address)
    server_embed.add_field(name='Version', value=server_data['version']['name'])

    # number of players
    number_online = server_data['players']['online']
    online_max = server_data['players']['max']

    server_embed.add_field(name='Number of Players Online', value=str(number_online)+'/'+str(online_max))

    # player names
    if 'sample' in server_data['players']:
        players = []

        for player in server_data['players']['sample']:
            players.append(player['name'])

        formatted_players = ', '.join(players)

        server_embed.add_field(name='Players Online', value=formatted_players, inline=False)

    return server_embed


# discord initial variables
bot = commands.Bot(command_prefix=['.ms '])
status_channel = None # remove
ping_role = '<@&{}>'.format(discord_config.ping_role) # remove


# database initial connection
# conn = sqlite3.connection(data.db) # with aiosqlite
# conn.execute("PRAGMA foreign_keys = True")
# cur = conn.cursor()


# servers dictionary creation
default_server_addresses = {'136.36.192.233':"Michael's Server"}
default_servers_data = {}

for address in default_server_addresses:
    default_servers_data[address] = {'server_object': mcstatus.MinecraftServer(address), 'server_name':default_server_addresses[address], 'server_status': None, 'status_message': None}


# runs on ready
@bot.event
async def on_ready():
    global status_channel
    status_channel = bot.get_channel(discord_config.status_channel)

    activity = discord.Activity(type=discord.ActivityType.watching, name='your servers')
    await bot.change_presence(activity=activity)

    await default_servers_check.start()


# edit to take info from database with aiosqlite (server addresses, status message ids, etc)
# remove print debug statements

# servers background check
@tasks.loop(minutes=1)
async def default_servers_check():
    for server_address in default_servers_data:
        # initial variables
        debug_prefix = '({})'.format(server_address)

        server_object = default_servers_data[server_address]['server_object']
        server_status = default_servers_data[server_address]['server_status']
        status_message = default_servers_data[server_address]['status_message']

        # online
        try:
            server_data = server_object.status().raw

            # server status handling
            if server_status != 'online':
                default_servers_data[server_address]['server_status'] = 'online'
                print(debug_prefix, 'status: online')

            server_name = default_servers_data[server_address]['server_name']

            # edit status message
            if status_message != None:
                await status_message.edit(embed=create_server_embed(server_data, server_address, server_name))

            # send status message
            elif status_message == None:
                ping_message = '{role} {name} is online!'.format(role=ping_role, name=server_name)
                default_servers_data[server_address]['status_message'] = await status_channel.send(ping_message, embed=create_server_embed(server_data, server_address, server_name))
                print(debug_prefix, 'status message sent')

        # offline
        except:
            # server status handling
            if server_status != 'offline':
                default_servers_data[server_address]['server_status'] = 'offline'
                print(debug_prefix, 'status: offline')

            # delete status message
            if status_message != None:
                await status_message.delete()
                default_servers_data[server_address]['status_message'] = None
                print(debug_prefix, 'status message deleted')


# server status command 
@bot.command(aliases=['status','s'], help="Checks a Minecraft server's status")
async def server(ctx, address):
    # restricted addresses
    if address == 'localhost':
        await ctx.send("'**{}**' is an invalid server address and therefore does not exist. Please check your spelling or try a different server address.".format(address))
        return

    server_object = mcstatus.MinecraftServer.lookup(address)

    # online
    try:
        data = server_object.status().raw
        await ctx.send(embed=create_server_embed(data, address))

    # offline | failed
    except Exception as e:
        # offline
        if str(e) == 'timed out':
            await ctx.send("Looks like that server is offline. Please check back later or try a different server address.")

        # invalid
        elif str(e) == '[Errno 11001] getaddrinfo failed':
            await ctx.send("'**{}**' is an invalid server address and therefore does not exist. Please check your spelling or try a different server address.".format(address))

        # no response
        elif str(e) == 'Server did not respond with any information!':
            await ctx.send("That server did not respond with any information. It could be restricted or just starting up.")

        # other
        else:
            await ctx.send("Sorry, an unknown error occured. Please try a different server address or check back later.")

            bot_owner = bot.get_user(discord_config.bot_owner)
            await bot_owner.send("**Server Status Unknown Error:**\nIP address: {address}\nError: {error}\nError Type: {type}".format(address=address, error=e, type=type(e)))


# latency command
@bot.command(aliases=['l'], help="Returns the bot's latency")
async def latency(ctx):
    latency = "Latency: **{:.2f}** ms".format(bot.latency * 1000)
    await ctx.send(latency)

# perms (server owner?)
# guild config (add status channel/role to ping)
@bot.command(aliases=['c'], help="")
async def config(ctx):
    await ctx.send(ctx.message.guild.id)
    # ask for channel id
    # ask for role id (optional)

    # add data to discord database table with aiosqlite


# add address
@bot.command(aliases=['a'])
async def add():
    print()

# remove address
@bot.command(aliases=['r'])
async def remove():
    print()


# update command
@commands.is_owner()
@bot.command(help="Updates the bot's code")
async def update(ctx):
    await ctx.send("Updating the bot...")

    default_servers_check.cancel()
    print('stopped background check')

    for server_address in default_servers_data:
        status_message = default_servers_data[server_address]['status_message']

        if status_message != None:
            await status_message.delete()
            print('({})'.format(server), 'status message deleted')

    # close connection to database

    sys.exit()


bot.run(discord_config.bot_token)