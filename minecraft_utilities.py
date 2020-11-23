import sys
import time
import asyncio
import mcstatus
import discord
from discord.ext import commands, tasks


def server_embed(server, server_address):
    server_data = server.status().raw

    number_online = server_data['players']['online']
    online_max = server_data['players']['max']

    server_stats = discord.Embed(title='Server is Online', description=server_data['description']['text'], color=discord.Color.green())

    server_stats.add_field(name='Server Address', value=server_address)
    server_stats.add_field(name='Version', value=server_data['version']['name'])
    server_stats.add_field(name='Number of Players Online', value=str(number_online)+'/'+str(online_max))

    if number_online > 0:
        players = []

        for i in range(len(server_data['players']['sample'])):
            players.append(server_data['players']['sample'][i]['name'])

        formatted_players = ', '.join(players)

        server_stats.add_field(name='Players Online', value=formatted_players, inline=False)

    return server_stats


start_time = time.time()


command_prefixes = ['.mu ','!mu ']
default_server_address = 'xps.apmonitor.com' # 136.36.192.233
channel_id = 772220260589240363
role_id = 759862142508990544


status_message = None
current_server_status = None
status_prefix = 'server status: '
ping_message = '<@&{}> the server is online!'.format(role_id)
default_server = mcstatus.MinecraftServer.lookup(default_server_address)


bot = commands.Bot(command_prefix=command_prefixes)


@bot.event
async def on_ready():
    print('bot is ready')
    await default_server_status.start()


@tasks.loop(minutes=1)
async def default_server_status():
    global current_server_status
    status_channel = bot.get_channel(channel_id)

    try:
        default_server.ping()

        if current_server_status != 'online':
            current_server_status = 'online'
            print(status_prefix + current_server_status)

        await server_online(status_channel)

    except:
        if current_server_status != 'offline':
            current_server_status = 'offline'
            print(status_prefix + current_server_status)

        await server_offline()


async def server_online(channel):
    global status_message

    if status_message != None:
        await status_message.edit(embed=server_embed(default_server, default_server_address))
        print('edited status message')

    elif status_message == None:
        status_message = await channel.send(ping_message, embed=server_embed(default_server, default_server_address))
        print('status message sent')


async def server_offline():
    global status_message

    if status_message != None:
        await status_message.delete()
        print('status message deleted')
        status_message = None


@bot.command(aliases=['status','s'], help="Checks a Minecraft server's status")
async def server(ctx, address):
    server_lookup = mcstatus.MinecraftServer.lookup(address)

    try:
        server_lookup.ping()
        await ctx.send(embed=server_embed(server_lookup, address))

    except:
        await ctx.send('Looks like that server is offline. Try a different address or try again later.')


@bot.command(aliases=['ping','l'], help="Returns the bot's latency")
async def latency(ctx):
    await ctx.send("My latency is **"+str(bot.latency)+"** seconds.")


@bot.command(aliases=['r'], help="Returns how long the bot has been running")
async def running(ctx):
    await ctx.send("I have been running for **"+str(time.time()-start_time)+"** seconds.")


@commands.is_owner()
@bot.command(aliases=['u'], help="Updates the bot's code. This can only be used by the bot owner.")
async def update(ctx):
    await ctx.send('Updating... Please wait a minute for the bot to go online again.')
    sys.exit()


bot.run('Nzc4NDI2NTEyMjY4NTkxMTE3.X7R0Lg.ogul_Yi1PDKVoNp4hezHdsJe9SI')