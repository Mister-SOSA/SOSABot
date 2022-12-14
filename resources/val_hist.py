"""
A module for fetching player data from the Valorant API.
Specifically fetches the last match data for calculating coin rewards.
"""

import aiohttp


async def fetch_player_data(full_username: str) -> dict:
    """
    A coroutine that fetches the player's last match data.'
        - full_username: The player's full username, including the tag.
    """
    region = 'na'
    username = full_username.split("#")[0]
    tag = full_username.split("#")[1]

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.henrikdev.xyz/valorant/v1/account/{username}/{tag}') as resp:
            player_info = await resp.json()

        async with session.get(f'https://api.henrikdev.xyz/valorant/v3/matches/{region}/{username}/{tag}') as resp:
            match_history = await resp.json()
            last_match = match_history['data'][0]
            last_match_players = last_match['players']['all_players']
            last_match_gamemode = last_match['metadata']['mode']

            last_match_you = [
                player for player in last_match_players if player['puuid'] == player_info['data']['puuid']][0]

            last_match_data = {
                'match_id': last_match['metadata']['matchid'].replace('-', ''),
                'match_timestamp': last_match['metadata']['game_start'],
                'match_date': last_match['metadata']['game_start_patched'],
                'puuid': last_match_you['puuid'].replace('-', ''),
                'username': last_match_you['name'],
                'tag': last_match_you['tag'],
                'character': last_match_you['character'],
                'rank_num': last_match_you['currenttier'],
                'rank': last_match_you['currenttier_patched'],
                'gamemode': last_match_gamemode,
                'map': last_match['metadata']['map'],
                'kills': last_match_you['stats']['kills'],
                'deaths': last_match_you['stats']['deaths'],
                'assists': last_match_you['stats']['assists'],
                'bodyshots': last_match_you['stats']['bodyshots'],
                'headshots': last_match_you['stats']['headshots'],
                'legshots': last_match_you['stats']['legshots'],
                'credits_spent': last_match_you['economy']['spent']['overall'],
                'damage_dealt': last_match_you['damage_made'],
                'damage_taken': last_match_you['damage_received']
            }

            return last_match_data


async def fetch_map_photo_by_map_name(map_name):
    """
    A coroutine that fetches the map photo for the given map name.
    Used for generating the map photo in the payout embed.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://valorant-api.com/v1/maps') as resp:
            maps = await resp.json()
            map_photo = [map['splash'] for map in maps['data']
                         if map['displayName'] == map_name][0]

            return map_photo
