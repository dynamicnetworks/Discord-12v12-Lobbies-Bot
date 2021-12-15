import json
import discord
import requests
from discord.ext import commands


def get_players(x):
    try:
        return int(x[1].split('/')[0])
    except:
        return 0


class Info:
    def __init__(self):
        self.url = "https://api.dotaworkshop.com/v2/GetAllLobbiesById/1576297063"

    def get_list(self):
        return requests.request("GET", self.url).text

    def get_lobbies(self):
        lobbies = json.loads(self.get_list())
        board = []
        for lobby in lobbies:
            players = "{}/{}".format(lobby['member_count'], lobby['max_player_count'])
            board.append([
                lobby['leader_name'],
                players,
                lobby['server_region'],
                lobby['has_pass_key']
            ])
        return board


class Stats:
    def __init__(self):
        self.url = "https://api.dotaworkshop.com/v2/GetGameStats/1576297063"

    def get_list(self):
        return requests.request("GET", self.url).text

    def get_stats(self):
        return json.loads(self.get_list())[0]


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        info = Info()
        board = info.get_lobbies()
        board.sort(key=get_players, reverse=True)
        count = str(len(board))
        leader_list = []
        players_list = []
        region_list = []

        for lobbies in board:
            if lobbies[3]:
                leader_list.append("??" + lobbies[0])
            else:
                leader_list.append(lobbies[0])
            players_list.append(lobbies[1])
            region_list.append(lobbies[2])

        await self.client.change_presence(
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
        message = await ctx.send(embed=embed)
        message_id = message.id
        channel_id = message.channel.id
        guild_id = message.guild.id

        with open('config.json') as f:
            config = json.load(f)
        config['message_id'] = message_id
        config['channel_id'] = channel_id
        config['server_id'] = guild_id

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)


def setup(client):
    client.add_cog(Status(client))