import requests
import discord
import re
import helper
from discord.ext import commands, bridge
import permission_manager as perm

errors = {
    'fetch_failed': ':warning: An error occurred while fetching data.',
    'player_not_found': ':x: Player not found.',
    'query': ':x: Please specify a username and tag in the format `player#1234`.',
    'element': ':warning: Critical error occurred when populating embed.'
}

################ Module Start ################

rank_colors = {
    'Iron': 0x9e9e9e,
    'Bronze': 0x8d6e63,
    'Silver': 0xb0bec5,
    'Gold': 0xffd54f,
    'Platinum': 0x4fc3f7,
    'Diamond': 0x4dd0e1,
    'Ascendant': 0x17653d,
    'Immortal': 0x81c784,
    'Radiant': 0xff8a65
}

class Valorant(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':crossed_swords:',
        'name': 'Valorant',
        'description': 'Fetch the rank and level of a player in Valorant.',
        'aliases': ['val', 'rank'],
        'permission_level': 'Member'
    }


    @bridge.bridge_command(name="valorant", aliases=metadata['aliases'], description=metadata['description'])
    async def valorant(self, ctx, player: discord.Option(str, description="The username of the player to fetch. (Format: player#1234)")):

        searching_embed = discord.Embed(
            title=':mag: Searching for player...',
            color=0x9e9e9e
        )

        try:
            region = 'na'
            username = player.split('#')[0]
            tag = player.split('#')[1]
        except:
            query_error_embed = discord.Embed(
                title=':x: Invalid query.',
                description='Please specify a username and tag in the format `player#1234`.',
                color=discord.Color.red()
            )
            await ctx.reply(embed=query_error_embed)
            return

        searching_message = await ctx.reply(embed=searching_embed)

        try:
            searching_message = await searching_message.original_response()
        except:
            pass

        try:
            player_info = requests.get(
                f'https://api.henrikdev.xyz/valorant/v1/account/{username}/{tag}')

            rank_data = requests.get(
                f'https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{username}/{tag}')

        except:
            embed = discord.Embed(
                title=':x: An error occurred while fetching data.',
                description=errors['fetch_failed'],
                color=discord.Color.red()
            )

            await searching_message.edit(embed=embed)
            return

        if rank_data.status_code == 200 and player_info.status_code == 200:
            rank_json = rank_data.json()
            player_json = player_info.json()

            try:
                embed = discord.Embed(
                    color=rank_colors[re.sub(r'\d+', '', rank_json["data"]["current_data"]["currenttierpatched"]).strip()])
            except:
                embed = discord.Embed(
                    color=rank_colors['Iron'])
            try:
                embed.set_thumbnail(
                    url=rank_json['data']['current_data']['images']['small'])

                embed.add_field(
                    name='Level', value=player_json['data']['account_level'], inline=True)

                embed.add_field(
                    name='Rank', value=f'{rank_json["data"]["current_data"]["currenttierpatched"]} ({rank_json["data"]["current_data"]["ranking_in_tier"]}/100)', inline=True)

                embed.set_author(
                    name=f'{rank_json["data"]["name"]}#{rank_json["data"]["tag"]}', icon_url=f'{player_json["data"]["card"]["small"]}')
            except:
                await ctx.reply(errors['element'])
                return

            await searching_message.edit(embed=embed)

        else:
            not_found_embed = discord.Embed(
                title=errors["player_not_found"],
                color=0xff0000
            ).set_footer(
                text='Make sure you entered the correct username and tag.')

            await searching_message.edit(embed=not_found_embed)


################ Module End ################

def setup(client):
    client.add_cog(Valorant(client))