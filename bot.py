import json
import asyncio
import datetime
import discord
from discord.ext import commands
from cogs import command_status

config = json.load(open('config.json'))

client = commands.Bot(command_prefix=config['prefix'])


@client.event
async def on_ready():
    while True:
        ids = json.load(open('config.json'))
        while ids['message_id'] == -1:
            ids = json.load(open('config.json'))
            print("Please set a channel with the 'status' command.")
            await asyncio.sleep(5)
        try:
            info = command_status.Info()
            board = info.get_lobbies()
            now = datetime.datetime.now()
            current_time = str(now.strftime("%I:%M:%S"))
            board.sort(key=command_status.get_players, reverse=True)
            count = str(len(board))
            leader_list = []
            players_list = []
            region_list = []
            for lobbies in board:
                if lobbies[3]:
                    leader_list.append("🔒" + lobbies[0])
                else:
                    leader_list.append(lobbies[0])
                players_list.append(lobbies[1])
                region_list.append(lobbies[2])

            stats = command_status.Stats().get_stats()

            await client.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(name="{} lobbies".format(count), type=discord.ActivityType.watching)
            )
            embed = discord.Embed(
                color=0x7E1212,
                title="Current Lobbies",
            )

            embed.add_field(name='Leader', value="{}".format('\n'.join(leader_list)), inline=True)
            embed.add_field(name='Players', value="{}".format('\n'.join(players_list)), inline=True)
            embed.add_field(name='Region', value="{}".format('\n'.join(str(region) for region in region_list)), inline=True)

            embed.add_field(name='Total Players', value="{}".format(stats['player_count']), inline=True)
            embed.add_field(name='Total Spectators', value="{}".format(stats['spectator_count']), inline=True)
            embed.add_field(name='Subscriptions', value="{}".format(stats['subscriptions']), inline=False)
            embed.add_field(name='Favorites', value="{}".format(stats['favorites']), inline=True)
            embed.add_field(name='Last Dota 12v12 Update', value="{}".format(datetime.datetime.fromtimestamp(stats['last_update'])), inline=False)
            embed.set_footer(text="List updated at: " + current_time + " CST")
            embed.set_thumbnail(url="https://steamuserimages-a.akamaihd.net/ugc/1244631126935143961/5A8B4A6E5E7995FA06E1D18025DBCB2DED15D3D3/")
            msg = await \
                client.get_guild(ids['server_id']).get_channel(ids['channel_id']).fetch_message(ids['message_id'])
            await msg.edit(embed=embed)
        except:
            pass
        await asyncio.sleep(5)


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx):
    client.unload_extension('cogs.command_status')
    client.load_extension('cogs.command_status')
    await ctx.send("Reloaded.")
    print("Reloaded status cog.")


client.load_extension('cogs.command_status')
client.run(config['token'])