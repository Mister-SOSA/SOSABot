"""
This event cog executes every 90 seconds to manage the Clash Royale Payouts
""" 

import asyncio
import discord
from discord.ext import commands, tasks
import db_manager
from resources import royale_hist as royale

monkeycoin = '<:monkeycoin:1038242128045809674>'

class ClashRoyalePayout(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.clash_royale.start()

    @tasks.loop(seconds=90)
    async def clash_royale(self):
        sosa = await self.client.fetch_user(268974144593461248)
        royale_players = db_manager.fetch_royale_players()
        
        for player in royale_players:
            try:
                player_data = await royale.fetch_player_data(player)
            except:
                continue
            
            if player_data is None:
                continue
            
            if db_manager.royale_match_already_logged(player_data):
                continue

            user_id = db_manager.fetch_discord_user_id_by_royale_tag(player_data['player_tag'])

            if user_id is None:
                print(f'No user ID found for {player_data["player_tag"]}')
                continue
            
            user = await self.client.fetch_user(user_id)

            
            if user is None:
                print(f'No Discord user found for {user_id}')
                continue
            try:
                db_manager.new_royale_match(player_data)
            except:
                continue
            
            reward = await calculate_reward(player_data)

            if reward == 'Invalid Match':
                continue
            
            embed = await create_embed(player_data, reward)

            transaction_note = await create_transaction_note(player_data, reward)
            
            db_manager.update_balance_by_id(user_id, reward)

            if player_data['type'] == 'clanMate':
                opponent_user_id = db_manager.fetch_discord_user_id_by_royale_tag(list(player_data["opponent"].items())[0][1]["tag"])
                opponent_user = await self.client.fetch_user(opponent_user_id)

                db_manager.new_transaction (
                    'CLASH ROYALE',
                    user.name,
                    user.id,
                    db_manager.fetch_balance_by_id(user.id),
                    opponent_user.name,
                    opponent_user.id,
                    db_manager.fetch_balance_by_id(opponent_user.id),
                    reward,
                    transaction_note
                )

            else:
                db_manager.new_transaction (
                    'CLASH ROYALE',
                    user.name,
                    user.id,
                    db_manager.fetch_balance_by_id(user.id),
                    'SERVER',
                    '0',
                    0,
                    reward,
                    transaction_note
                )
            try:
                await user.send(embed=embed)
            except discord.errors.Forbidden:
                await sosa.send(f'Unable to send message to {user.name} ({user.id})')   
            except Exception as e:
                await sosa.send(f'Unable to send message to {user.name} ({user.id})\n\n```{e}```')

            
async def calculate_reward(player_data):
    approved_game_types = ['pathOfLegend', 'PvP', 'casual2v2', 'clanMate']
    
    if player_data['type'] not in approved_game_types:
        return 'Invalid Match'
    
    reward = 0
    opponent_has_megaknight = False
    
    if player_data['crowns'] <= 2:
        reward += (player_data['crowns'] * 5)
    else:
        reward += 20

    if player_data['team'][player_data['player_tag']]['elixir_leaked'] < 3:
        reward += 10

    if player_data['result'] == 'WIN':
        reward *= 2
        
    for opponent in player_data['opponent']:
        if await card_in_deck('Mega Knight', player_data['opponent'][opponent]['deck']):
            opponent_has_megaknight = True
            break

    if opponent_has_megaknight and player_data['result'] == 'WIN':
        reward *= 2
        
    if await card_in_deck("Mega Knight", player_data['team'][player_data['player_tag']]['deck']):
        reward /= 2

    if player_data['type'] == 'clanMate':
        
        reward = 0

        if len(player_data['team']) > 1:
            return 'Invalid Match'

        user_id = db_manager.fetch_discord_user_id_by_royale_tag(player_data['player_tag'])
        opponent_user_id = db_manager.fetch_discord_user_id_by_royale_tag(list(player_data["opponent"].items())[0][1]["tag"])

        if player_data['result'] == 'WIN':
            reward = int(db_manager.fetch_balance_by_id(opponent_user_id) * 0.02)

        if player_data['result'] == 'LOSS':
            reward = -int(db_manager.fetch_balance_by_id(user_id) * 0.02)

    return reward
            
        
        

        
async def get_card_names(deck) -> list:
    cards = []

    for card in deck:
        cards.append(card['name'])

    return cards

async def card_in_deck(card, deck):
    for card in deck:
        if card['name'] == card:
            return True

    return False

async def create_embed(player_data, reward):
    embed = discord.Embed(
        title = f'🕹️ Clash Royale Payout',
        description = '',
        color = discord.Color.blue()
    )

    if player_data['type'] == 'clanMate':
        embed.description = f'You {"received" if reward > 0 else "lost"} {monkeycoin} {int(reward)} from a wager friendly match against **{list(player_data["opponent"].items())[0][1]["username"]}**'
    
    else:
        embed.description = f'You received {monkeycoin} **{int(reward)}** from your `{player_data["type"]}` match against **{list(player_data["opponent"].items())[0][1]["username"]}**'
        
        embed.description += f'\n\n__**Breakdown**__'

        embed.description += f'\n {monkeycoin} **{player_data["crowns"] * 5 if player_data["crowns"] <= 2 else 20}** for getting **{player_data["crowns"]}** crowns.'

        if player_data['team'][player_data['player_tag']]['elixir_leaked'] < 3:
            embed.description += f'\n {monkeycoin} **10** for leaking less than 3 elixir.'

        if player_data['result'] == 'WIN':
            embed.description += f'\n **2x** for Winning.'

        if await card_in_deck('Mega Knight', player_data['opponent'][list(player_data['opponent'].keys())[0]]['deck']):
            embed.description += f'\n **2x** for beating a Mega Knight deck.'

        if await card_in_deck('Mega Knight', player_data['team'][player_data['player_tag']]['deck']):
            embed.description += f'\n **0.5x** for using a Mega Knight deck.'

        

    return embed

async def create_transaction_note(player_data, reward):
    if player_data['type'] == 'clanMate':
        return f'CLASH ROYALE {player_data["result"]} - Friendly Match against {list(player_data["opponent"].items())[0][1]["username"]}'

    if player_data['type'] == 'pathOfLegend':
        return f'CLASH ROYALE {player_data["result"]} - Path of Legend match against {list(player_data["opponent"].items())[0][1]["username"]}'

    if player_data['type'] == 'PvP':
        return f'CLASH ROYALE {player_data["result"]} - PvP match against {list(player_data["opponent"].items())[0][1]["username"]}'

    if player_data['type'] == 'casual2v2':
        return f'CLASH ROYALE {player_data["result"]} - Casual 2v2 match against {list(player_data["opponent"].items())[0][1]["username"]}'

    else:
        return 'Invalid Match'

def setup(client):
    client.add_cog(ClashRoyalePayout(client))