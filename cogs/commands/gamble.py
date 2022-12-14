import asyncio
import os
import random
import discord
import helper
import db_manager
import requests
import math
import web.flask.item_db_manager as item_db
from PIL import Image
from discord.ext import commands, bridge
import permission_manager as perm

errors = {}

################ Module Start ################
game_in_progress = False
enabled_channels = [1028507716622229554,
                    1035296751923511306, 702666848499531796]

monkeycoin = '<:monkeycoin:1038242128045809674>'
available_games = ['🪙 Coin Flip', '🎲 Dice', '🎰 Slots', '🚀 Crash', '🏇 Horse Racing', '🃏 Blackjack']
casino_investor_level = item_db.fetch_tycoon_level_by_name('Casino Investor')

class Gamble(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    metadata = {
        'emoji': ':slot_machine:',
        'name': 'Gamble',
        'description': 'Initiate a gambling session',
        'aliases': ['gam'],
        'permission_level': 'Member',
    }
    
    
    
    async def game_search(ctx: discord.AutocompleteContext):
        return [game for game in available_games if game[2:].lower().startswith(ctx.value.lower())]
    
    @bridge.bridge_command(
        name="gamble",
        aliases=metadata['aliases'],
        description=metadata['description']
    )
    async def gamble(self, 
                     ctx, 
                     game: discord.Option(str, "Select a Game", autocomplete=game_search), 
                     bet: discord.Option(str, "Enter your bet amount (i.e. 10, 5k, 1m, etc.)"), 
                     speed: discord.Option(str, "Enable Fast Mode", choices=['Fast', 'Normal']) = 'Normal'):
        
        if speed == 'Fast':
            fast = True
        else:
            fast = False

        try:
            gamble_amount = int(bet)
        except:
            try:
                if bet.endswith('k'):
                    gamble_amount = int(bet[:-1]) * 1000
                elif bet.endswith('m'):
                    gamble_amount = int(bet[:-1]) * 1000000
                elif bet.endswith('b'):
                    gamble_amount = int(bet[:-1]) * 1000000000
                else:
                    embed = discord.Embed(
                        title=':x: Error', description='Invalid amount', color=0xff0000)
                    await ctx.reply(embed=embed)
                    return
            except:
                embed = discord.Embed(
                    title=':x: Error', description='You must specify an amount to gamble.', color=0xff0000)
                
                await ctx.reply(embed=embed)
                return
                        

        if gamble_amount < 0:
            error_embed = discord.Embed(
                title=':x: Error',
                description='You cannot gamble negative amounts.',
                color=0xff0000
            )
            await ctx.reply(embed=error_embed)
            return

        if db_manager.is_mobile(ctx.author):
            embed = discord.Embed(
                title=':x: Error',
                description='You cannot gamble from an alt account.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if ctx.channel.id not in enabled_channels:
            embed = discord.Embed(
                title=':x: Error',
                description=f'Gambling must be done in {ctx.get_channel(1035296751923511306).mention}.',
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
            return

        game = game[2:].lower()
        
        if game == 'coin flip':
            await self.coin_flip(ctx, gamble_amount, fast=fast)

        elif game == 'dice':
            await self.dice_roll(ctx, gamble_amount, fast=fast)

        elif game == 'slots':
            await self.slots(ctx, gamble_amount, fast=fast)

        elif game == 'crash':
            await self.crash(ctx, gamble_amount, fast=fast)

        elif game == 'horse racing':
            await self.horse_race(ctx, gamble_amount, fast=fast)
            
        elif game == 'blackjack':
            await self.blackjack(ctx, gamble_amount, fast=fast)
        
        else:
            await ctx.reply('Invalid game.')


    async def coin_flip(self, ctx, stakes, fast=False):
        global game_in_progress

        if game_in_progress:
            embed = discord.Embed(
                title=':x: Error',
                description='A game is already in progress. Please wait for it to finish.',
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=3)
            return

        game_in_progress = True

        class CoinFlipView(discord.ui.View): 
            @discord.ui.button(label="Heads", custom_id="heads_button", style=discord.ButtonStyle.primary) 
            async def heads_button(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 'heads')
            @discord.ui.button(label="Tails", custom_id="tails_button", style=discord.ButtonStyle.success) 
            async def tails_button(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 'tails')
        
        if fast:
            seconds = 4
        else:
            seconds = 10

        participants = {}

        embed = discord.Embed(
            title=':coin: Coin Flip',
            description=f'Coinflip session started by {ctx.author.mention} for {monkeycoin} **{stakes:,}**',
            color=0x00ff00
        )

        embed.add_field(
            name='Heads',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='Tails',
            value='*...*',
            inline=True
        )

        embed.set_footer(text=f'Coin will flip in {seconds} seconds.')

        coin_flip_message = await ctx.reply(embed=embed, view=CoinFlipView())

        try:
            coin_flip_message = await coin_flip_message.original_response()
        except:
            pass

        async def update_participants():
            nonlocal embed
            nonlocal participants

            heads = []
            tails = []

            for user in participants:
                if participants[user] == 'heads':
                    heads.append(f'{user.mention}')
                elif participants[user] == 'tails':
                    tails.append(f'{user.mention}')

            embed.set_field_at(0, name='Heads', value='\n'.join(
                heads) if heads else '*...*')
            embed.set_field_at(1, name='Tails', value='\n'.join(
                tails) if tails else '*...*')

            await coin_flip_message.edit(embed=embed)

        async def add_participant(user, stance):

            user_balance = db_manager.fetch_coin_balance(user)[0]
            
            if user_balance < stakes:

                embed = discord.Embed(
                    title=f':x: No dollas {user.name}?',
                    description='You\'re too broke to play',
                    color=0xff0000
                )
                await ctx.reply(embed=embed, delete_after=3)
                return
            else:
                participants[user] = stance

            await update_participants()

        while seconds > 0:
            seconds -= 1
            embed.set_footer(text=f'Coin will flip in {seconds} seconds.')
            await update_participants()
            await coin_flip_message.edit(embed=embed)
            await asyncio.sleep(1)

        await coin_flip_message.edit(view=None)

        for user in participants:
            db_manager.update_coin_balance(user.id, -stakes)

        result = random.choice(['Heads', 'Tails'])
        winners = []
        losers = []

        winnings = stakes * 2

        if stakes == 0:
            winnings = 1

        for user in participants:
            if participants[user] == result.lower():
                winners.append(user)
            else:
                losers.append(user)

        if len(winners) == 0:
            embed = discord.Embed(
                title=':coin: Coin Flip',
                description=f'**{result}**!\n\nNobody won.',
                color=0xff0000
            )

            await coin_flip_message.edit(embed=embed)
        else:
            embed = discord.Embed(
                title=':coin: Coin Flip',
                description=f'**{result}**!\n\n{monkeycoin} {winnings:,} paid out to: \n{", ".join([f"{user.mention}" for user in winners])}',
                color=0x00ff00
            )

            await coin_flip_message.edit(embed=embed)

        for user in winners:
            db_manager.update_coin_balance(user.id, winnings)
            db_manager.update_winnings(user, winnings)
            db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Coin Flip',
                'WIN',
                winnings,
                stakes            
            )

        for user in losers:
            db_manager.update_winnings(user, -stakes)
            db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Coin Flip',
                'LOSS',
                -stakes,
                stakes            
            )
            
        if len(winners) > 0:
        
            for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(casino_investor_level):
                if investor_id in [player.id for player in winners]:
                    continue
                
                investor = await self.client.fetch_user(investor_id)
                royalty = math.ceil(winnings * 0.01) * len(winners)
                db_manager.update_balance_by_id(investor_id, royalty)
                db_manager.new_transaction(
                    'CASINO ROYALTY',
                    investor.name,
                    investor.id,
                    db_manager.fetch_balance_by_id(investor_id),
                    'TYCOON',
                    '0',
                    0,
                    royalty,
                    f'Casino royalty of {royalty} coins from a coin flip win')

                

        game_in_progress = False

        return


    async def dice_roll(self, ctx, stakes, fast=False):
        global game_in_progress

        if game_in_progress:
            embed = discord.Embed(
                title=':x: Error',
                description='A game is already in progress. Please wait for it to finish.',
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=3)
            return

        game_in_progress = True

        if fast:
            seconds = 3
        else:
            seconds = 10

        participants = {}
        
        class DiceRollView(discord.ui.View):
            @discord.ui.button(label="1",row=0, style=discord.ButtonStyle.primary) 
            async def dice_bet_1(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 1)
            @discord.ui.button(label="2",row=0, style=discord.ButtonStyle.primary) 
            async def dice_bet_2(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 2)
            @discord.ui.button(label="3",row=0, style=discord.ButtonStyle.primary)
            async def dice_bet_3(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 3)
            @discord.ui.button(label="4",row=1, style=discord.ButtonStyle.primary)
            async def dice_bet_4(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 4)
            @discord.ui.button(label="5",row=1, style=discord.ButtonStyle.primary)
            async def dice_bet_5(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 5)
            @discord.ui.button(label="6",row=1, style=discord.ButtonStyle.primary)
            async def dice_bet_6(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, 6)
            
            
        embed = discord.Embed(
            title=':game_die: Dice Roll',
            description=f'Dice roll session started by {ctx.author.mention} for {monkeycoin} **{stakes:,}**',
            color=0x00ff00
        )

        embed.add_field(
            name='__1__',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='__2__',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='__3__',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='__4__',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='__5__',
            value='*...*',
            inline=True
        )

        embed.add_field(
            name='__6__',
            value='*...*',
            inline=True
        )

        embed.set_footer(text=f'Dice will roll in {seconds} seconds.')

        dice_roll_message = await ctx.reply(embed=embed, view=DiceRollView())

        try:
            dice_roll_message = await dice_roll_message.original_response()
        except:
            pass

        result = random.randint(1, 6)

        async def update_participants():
            nonlocal embed
            nonlocal participants

            for field in range(6):
                users = []

                for user in participants:
                    if participants[user] == field + 1:
                        users.append(f'{user.mention}')

                embed.set_field_at(field, name=f'__{field + 1}__',
                                value='\n'.join(users) if users else '*...*')

            await dice_roll_message.edit(embed=embed)

        async def add_participant(user, stance):

            user_balance = db_manager.fetch_coin_balance(user)[0]
            if user_balance < stakes:

                embed = discord.Embed(
                    title=f':x: No dollas {user.name}?',
                    description='You\'re too broke to play',
                    color=0xff0000
                )
                await ctx.reply(embed=embed, delete_after=3)
                return

            else:
                participants[user] = stance

            await update_participants()

        while seconds > 0:
            seconds -= 1
            embed.set_footer(text=f'Dice will roll in {seconds} seconds.')
            await update_participants()
            await dice_roll_message.edit(embed=embed)
            await asyncio.sleep(1)

        await dice_roll_message.edit(view=None)

        for user in participants:
            db_manager.update_coin_balance(user.id, -stakes)

        winners = []
        losers = []
        winnings = stakes * len(participants) * 3

        image_file = discord.File(
            f'./commands/assets/dice/{result}.png', filename='dice.png')

        if stakes == 0:
            winnings = 2

        for user in participants:
            if participants[user] == result:
                winners.append(user)

        for user in participants:
            if participants[user] != result:
                losers.append(user)

        if len(winners) == 0:
            embed = discord.Embed(
                title=':game_die: Dice Roll',
                description=f'Nobody won.',
                color=0xff0000
            )

            embed.set_thumbnail(url=f'attachment://dice.png')

            await dice_roll_message.edit(embed=embed, file=image_file)
        else:
            embed = discord.Embed(
                title=':game_die: Dice Roll',
                description=f'{monkeycoin} {winnings:,} paid out to: \n{", ".join([f"{user.mention}" for user in winners])}',
                color=0x00ff00
            )

            embed.set_thumbnail(url=f'attachment://dice.png')

            await dice_roll_message.edit(embed=embed, file=image_file)

        for user in winners:
            db_manager.update_coin_balance(user.id, winnings)
            db_manager.update_winnings(user, winnings)
            db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Dice',
                'WIN',
                winnings,
                stakes            
            )

        for user in losers:
            db_manager.update_winnings(user, -stakes)
            db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Dice',
                'LOSS',
                -stakes,
                stakes            
            )
        
        if len(winners) > 0 and stakes > 0:    
            for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(casino_investor_level):
                if investor_id in [player.id for player in winners]:
                    continue
                investor = await self.client.fetch_user(investor_id)
                royalty = math.ceil(winnings * 0.01) * len(winners)
                db_manager.update_balance_by_id(investor_id, royalty)
                db_manager.new_transaction(
                    'CASINO ROYALTY',
                    investor.name,
                    investor.id,
                    db_manager.fetch_balance_by_id(investor_id),
                    'TYCOON',
                    '0',
                    0,
                    royalty,
                    f'Casino royalty of {royalty} coins from a Dice Roll win')

        game_in_progress = False

        return


    async def slots(self, ctx, stakes, fast=False, start_with_player=[]):

        global game_in_progress

        self_context = self
        
        if game_in_progress:
            embed = discord.Embed(
                title=':x: Game in progress',
                description='There is already a game in progress',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        game_in_progress = True

        if fast:
            seconds = 5
        else:
            seconds = 10
            
        participants = []

        class SlotsView(discord.ui.View): 
            @discord.ui.button(label=f"Buy a ticket | 🪙 {stakes:,}", style=discord.ButtonStyle.primary) 
            async def buy_ticket_button(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user)
                
        class ReplayView(discord.ui.View): 
            @discord.ui.button(label=f"Play Again", emoji="🔁", custom_id="play_again", style=discord.ButtonStyle.green) 
            async def play_again(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.slots(self_context, ctx, stakes, fast, [interaction.user])
            @discord.ui.button(label=f"Double Up", emoji="⬆️", custom_id="double_up", style=discord.ButtonStyle.red) 
            async def double_up(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.slots(self_context, ctx, stakes * 2, fast, [interaction.user])

        embed = discord.Embed(
            title=':slot_machine: Slots',
            color=0x00ff00
        )

        if len(start_with_player) > 0:
            embed.description=f'Slots session started by {start_with_player[0].mention}. Tickets cost {monkeycoin} **{stakes:,}**.'
        else:
            embed.description=f'Slots session started by {ctx.author.mention}. Tickets cost {monkeycoin} **{stakes:,}**.'
        embed.add_field(
            name='__Participants__',
            value='*...*',
            inline=True
        )

        embed.set_footer(text=f'Slots will roll in {seconds} seconds.')

        slots_message = await ctx.reply(embed=embed, view=SlotsView())

        try:
            slots_message = await slots_message.original_response()
        except:
            pass

        async def update_participants():
            nonlocal embed
            nonlocal participants

            players = []

            for user in participants:
                players.append(f'{user.mention}')

            embed.set_field_at(0, name='__Participants__',
                            value='\n'.join(players) if players else '*...*')

            await slots_message.edit(embed=embed)
            
        async def add_participant(user):
            user_balance = db_manager.fetch_coin_balance(user)[0]
            
            if user_balance < stakes:
                embed = discord.Embed(
                    title=f':x: No dollas {user.name}?',
                    description='You\'re too broke to play',
                    color=0xff0000
                )
                await ctx.reply(embed=embed, delete_after=3)
                return
            
            else:
                if user not in participants:
                    participants.append(user)

            await update_participants()

        for player in start_with_player:
                await add_participant(player)

        while seconds > 0:
            seconds -= 1
            embed.set_footer(text=f'Slots will roll in {seconds} seconds.')
            await update_participants()
            await slots_message.edit(embed=embed)
            await asyncio.sleep(1)

        await slots_message.clear_reactions()

        if len(participants) == 0:
            embed = discord.Embed(
                title=':slot_machine: Slots',
                description=f'Nobody bought a ticket.',
                color=0xff0000
            )

            game_in_progress = False
            await slots_message.edit(embed=embed, view=ReplayView())
        else:

            winnings = 0

            slot_wheel = ['🍎', '🍊', '🍇', '🍒', '🍓', '🍑', '🐒', '🍋', '⚡', '🧩',
                    '🍉', '♥️', '♦️', '🍗', '🍅', '🧲', '🔔', '🥒', '💎', '🧀',
                    '🎗️', '💀', '💥', '🎰', '🌀', '🃏', '🎯', '⌛', '🧿',
                    '🔱', '💫', '🎴', '🧬', '🥠', '🍬', '☢️', '🎵', '🔶', '⚖️', '🥎',
                    '🍍', '🪝', '⚜️', '🐟', '🍀', '☄️', '🧸', '🧨', '🔮', '🧿',
                    '<:monkeycoin:1038242128045809674>']

            slot1 = random.choice(slot_wheel)
            slot2 = random.choice(slot_wheel)
            slot3 = random.choice(slot_wheel)

            breakdown = []

            slots_results = [slot1, slot2, slot3]

            def all_same(items):
                return all(x == items[0] for x in items)

            def all_different(items):
                return len(set(items)) == len(items)

            def two_same(items):
                return len(set(items)) == 2

            if all_different(slots_results):
                winnings = -stakes
                breakdown = 'Nothing : -100%'

            if all_different(slots_results) and '🎗️' in slots_results:
                winnings = round(-stakes / 2)
                breakdown = '🎗️ : -50%'

            if all_different(slots_results) and '🔱' in slots_results:
                winnings = round(-stakes / 4)
                breakdown = '🔱 : -25%'

            if all_different(slots_results) and '🍀' in slots_results:
                winnings = 0
                breakdown = '🍀 : Loss negated'

            if all_different(slots_results) and '🎰' in slots_results:
                winnings = stakes * 2
                breakdown = '🎰 : 2x'

            if all_different(slots_results) and '<:monkeycoin:1038242128045809674>' in slots_results:
                winnings = stakes * 3
                breakdown = '<:monkeycoin:1038242128045809674> : 3x'

            if all_different(slots_results) and '💎' in slots_results:
                winnings = stakes * 4
                breakdown = '💎 : 4x'

            if all_different(slots_results) and '🎰' in slots_results and '💎' in slots_results:
                winnings = stakes * 8
                breakdown = '🎰 : 2x\n💎 : 4x'

            if all_different(slots_results) and '🪝' in slots_results and '🐟' in slots_results:
                winnings = stakes * 3
                breakdown = '🪝 + 🐟 : 3x'

            if two_same(slots_results):
                winnings = stakes * 3
                breakdown = 'Doubles : 3x'

            if two_same(slots_results) and '🎰' in slots_results:
                winnings = stakes * 6
                breakdown = '🎰 : 2x\nDoubles : 3x'

            if two_same(slots_results) and '<:monkeycoin:1038242128045809674>' in slots_results:
                winnings = stakes * 9
                breakdown = '<:monkeycoin:1038242128045809674> : 3x\nDoubles : 3x'

            if two_same(slots_results) and '💎' in slots_results:
                winnings = stakes * 12
                breakdown = '💎 : 4x\nDoubles : 3x'

            if two_same(slots_results) and '🎰' in slots_results and '💎' in slots_results:
                winnings = stakes * 18
                breakdown = (''.join(slots_results) + ' Full House: 18x')

            if two_same(slots_results) and '🪝' in slots_results and '🐟' in slots_results:
                winnings = stakes * 15
                breakdown = (''.join(slots_results) + ' Big Catch: 15x')

            if all_same(slots_results):
                winnings = stakes * 20
                breakdown = 'Triples : 20x'

            if all_same(slots_results) and '🎰' in slots_results:
                winnings = stakes * 50
                breakdown = 'Triple 🎰 : 50x'

            if all_same(slots_results) and '💎' in slots_results:
                winnings = stakes * 100
                breakdown = 'Jackpot 💎 : 100x'

            if '🃏' in slots_results and winnings > 0:
                winnings *= 2
                breakdown += '\nJoker : 2x'

            if '🧸' in slots_results and winnings > 0:
                winnings = 0
                breakdown += '\n🧸 : Win negated'

            winnings = int(winnings)

            embed = discord.Embed(
                title=':slot_machine: Slots',
                description=f'Rolling...',
                color=0x00ff00
            )

            embed.add_field(
                name='__Participants__',
                value='\n'.join(
                    [f'{user.mention}' for user in participants]),
                inline=True
            )

            await slots_message.edit(embed=embed, view=None)

            await asyncio.sleep(1)

            for i, result in enumerate(slots_results):
                embed = discord.Embed(
                    title=':slot_machine: Slots',
                    description=f'{" | ".join(slots_results[:i + 1])}',
                    color=0x00ff00
                )

                embed.add_field(
                    name='__Participants__',
                    value='\n'.join(
                        [f'{user.mention}' for user in participants]),
                    inline=True
                )

                await slots_message.edit(embed=embed, view=None)

                await asyncio.sleep(1)

            embed = discord.Embed(
                title=':slot_machine: Slots',
                description=f'{slot1} | {slot2} | {slot3}',
                color=0x00ff00
            )

            embed.add_field(
                name='__Participants__',
                value='\n'.join(
                    [f'{user.mention}' for user in participants]),
                inline=True
            )

            if winnings > 0:
                embed.add_field(
                    name=':confetti_ball: Winner :confetti_ball:',
                    value=f'**{monkeycoin} +{winnings:,}**',
                    inline=True
                )
            else:
                embed.add_field(
                    name=':x: Loser :x:',
                    value=f'{monkeycoin} **{winnings:,}**',
                    inline=True
                )

            embed.add_field(
                name='Breakdown',
                value=breakdown,
                inline=False
            )
            
            game_in_progress = False
            
            await slots_message.edit(embed=embed, view=ReplayView())
            
            if winnings > 0:
                outcome = 'WIN'
                if stakes > 0:    
                    for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(casino_investor_level):
                        if investor_id in [player.id for player in participants]:
                            continue
                        investor = await self.client.fetch_user(investor_id)
                        royalty = math.ceil(winnings * 0.01) * len(participants)
                        db_manager.update_balance_by_id(investor_id, royalty)
                        db_manager.new_transaction(
                            'CASINO ROYALTY',
                            investor.name,
                            investor.id,
                            db_manager.fetch_balance_by_id(investor_id),
                            'TYCOON',
                            '0',
                            0,
                            royalty,
                            f'Casino royalty of {royalty} coins from a Slots win')
            else:
                outcome = 'LOSS'
                
            for user in participants:
                db_manager.update_coin_balance(user.id, winnings)
                db_manager.update_winnings(user, winnings)
                db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Slots',
                outcome,
                winnings,
                stakes            
                )
            
            
            
        
            
            

            await asyncio.sleep(20)

            await slots_message.edit(view=None)


        return


    async def crash(self, ctx, stakes, fast=False):
        global game_in_progress

        self_context = self

        if game_in_progress:
            embed = discord.Embed(
                title=':x: Game in progress',
                description='There is already a game in progress.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        class CrashLobbyView(discord.ui.View): 
            @discord.ui.button(label=f"Hop on | 🪙 {stakes:,}", emoji='🚀', style=discord.ButtonStyle.primary) 
            async def buy_ticket_button(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user)
                    
        class CrashGameView(discord.ui.View):
            @discord.ui.button(label='Cash Out!', emoji='💰', style=discord.ButtonStyle.red)
            async def crash_button(self, button, interaction):
                await interaction.response.defer()
                await cash_out(interaction.user)

        participants = {}
        game_in_progress = True
        multiplier = 1.0
        winnings = 0

        if fast:
            timer = 4
        else:
            timer = 10

        in_lobby = True

        embed = discord.Embed(
            title='🚀 Crash',
            description=f'{ctx.author.mention} has started a crash game!\nTickets cost {monkeycoin} **{stakes:,}**',
            color=0x00ff00
        )

        embed.add_field(
            name='__Participants__',
            value='*...*',
            inline=True
        )

        embed.set_footer(text=f'Rocket will take off in {timer} seconds.')

        crash_message = await ctx.reply(embed=embed, view=CrashLobbyView())

        try:
            crash_message = await crash_message.original_response()
        except:
            pass

        async def update_participants():
            nonlocal participants
            if in_lobby:
                embed.set_field_at(
                    0,
                    name='__Participants__',
                    value='\n'.join(
                        [f'{user.mention}' for user in participants.keys()]),
                    inline=True
                )

            if not in_lobby:
                embed.set_field_at(
                    0,
                    name='__Multiplier__',
                    value=f'**{multiplier:.2f}x**',
                    inline=True
                )

                embed.set_field_at(
                    1,
                    name='__Winnings__',
                    value=f'**{monkeycoin} +{current_winnings:,}**',
                    inline=False
                )

                embed.set_field_at(
                    2,
                    name='__In__',
                    value='...',
                    inline=True
                )

                embed.set_field_at(
                    3,
                    name='__Out__',
                    value='...',
                    inline=True
                )

            await crash_message.edit(embed=embed, view=CrashLobbyView())

            embed.set_footer(text=f'Rocket will take off in {timer} seconds.')

            await crash_message.edit(embed=embed, view=CrashLobbyView())

        async def add_participant(user):
            nonlocal in_lobby
            nonlocal multiplier
            nonlocal winnings
            nonlocal current_winnings
            nonlocal participants

            if in_lobby:
                user_balance = db_manager.fetch_coin_balance(user)[0]

                if user_balance < stakes:

                    embed = discord.Embed(
                        title=f':x: No dollas {user.name}?',
                        description='You\'re too broke to play',
                        color=0xff0000
                    )
                    await ctx.reply(embed=embed, delete_after=3)
                    return

                participants[user] = -stakes

                await update_participants()
                
        async def cash_out(user):
            if user in participants.keys() and participants[user] == -stakes:
                participants[user] = current_winnings

        while timer >= 0 and in_lobby:
            embed.set_footer(text=f'Rocket will take off in {timer} seconds.')
            await crash_message.edit(embed=embed)
            await asyncio.sleep(1)
            timer -= 1

        adding_values = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                        0.7, 0.8, 0.9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        current_winnings = stakes

        in_lobby = False

        while True:
            crash_chance = random.randint(
                1, int(math.floor(1000-(multiplier * 2.5))))
            current_winnings = math.ceil(stakes * multiplier) - stakes

            if crash_chance < 32:
                await crash_message.clear_reactions()
                break

            multiplier += adding_values[int(
                math.floor(math.sqrt(multiplier) * 2) - 2)]

            embed = discord.Embed(
                title='🚀 Crash',
                description=f'**The rocket is flying!**',
                color=0x00ff00
            )

            embed.add_field(
                name='__Multiplier__',
                value=f'**{multiplier:.2f}x**',
                inline=True
            )

            embed.add_field(
                name='__Winnings__',
                value=f'**{monkeycoin} +{current_winnings:,}**',
                inline=False
            )

            in_field = '\n'.join(
                [f'{user.mention}' for user in participants.keys() if participants[user] < 0])

            out_field = '\n'.join(
                [f'{user.mention}: +{winnings:,}' for user, winnings in participants.items() if participants[user] >= 0])

            if in_field == '':
                in_field = '*...*'

            if out_field == '':
                out_field = '*...*'

            embed.add_field(
                name='__In__',
                value=in_field,
                inline=True
            )

            embed.add_field(
                name='__Out__',
                value=out_field,
                inline=True
            )

            await crash_message.edit(embed=embed, view=CrashGameView())

            await asyncio.sleep(0.75)

        in_lobby = False
        
        class ReplayView(discord.ui.View): 
            @discord.ui.button(label=f"Play Again", emoji="🔁", custom_id="play_again", style=discord.ButtonStyle.green) 
            async def play_again(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.crash(self_context, ctx, stakes, fast)
            @discord.ui.button(label=f"Double Up", emoji="⬆️", custom_id="double_up", style=discord.ButtonStyle.red) 
            async def double_up(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.crash(self_context, ctx, stakes * 2, fast)

        embed = discord.Embed(
            title=':boom: Crash',
            description=f'The rocket crashed at **{multiplier:.2f}x**\nwith a maximum profit of {monkeycoin} **{current_winnings:,}**.',
            color=0x00ff00
        )

        winners_field = '\n'.join(
            [f'{user.mention}: +{winnings:,}' for user, winnings in participants.items() if winnings >= 0])

        losers_field = '\n'.join(
            [f'{user.mention}: {winnings:,}' for user, winnings in participants.items() if winnings < 0])

        if winners_field == '':
            winners_field = '*...*'

        if losers_field == '':
            losers_field = '*...*'

        embed.add_field(
            name='__Winners__',
            value=winners_field,
            inline=True
        )

        embed.add_field(
            name='__Losers__',
            value=losers_field,
            inline=True
        )

        embed.set_thumbnail(
            url='https://upload.wikimedia.org/wikipedia/commons/5/57/Explosion-155624_icon.svg')

        await crash_message.edit(embed=embed, view=ReplayView())

        winners = {}
        
        for user, winnings in participants.items():
            
            if winnings > 0:
                outcome = 'WIN'
                winners[user] = winnings
            else:
                outcome = 'LOSS'
            
            
            db_manager.update_coin_balance(user.id, winnings)
            db_manager.update_winnings(user, winnings)
            db_manager.new_gambling_entry(
                user.name,
                user.id,
                'Crash',
                outcome,
                winnings,
                stakes            
            )
            
        if len(winners) > 0 and stakes > 0:
            for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(casino_investor_level):
                if investor_id in [player.id for player, winnings in winners.items()]:
                    continue
                investor = await self.client.fetch_user(investor_id)
                royalty = math.ceil(sum([winnings for player, winnings in winners.items()]) * 0.01)
                db_manager.update_balance_by_id(investor_id, royalty)
                db_manager.new_transaction(
                    'CASINO ROYALTY',
                    investor.name,
                    investor.id,
                    db_manager.fetch_balance_by_id(investor_id),
                    'TYCOON',
                    '0',
                    0,
                    royalty,
                    f'Casino royalty of {royalty} coins from a Crash win')
            

        game_in_progress = False

        await asyncio.sleep(10)

        await crash_message.edit(view=None)


    async def horse_race(self, ctx, gamble_amount, fast=False):
        global game_in_progress
        
        self_cache = self

        in_lobby = False
        
        if game_in_progress:
            embed = discord.Embed(
                title=':x: Error',
                description='A game is already in progress. Please wait for it to finish.',
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=3)
            return

        game_in_progress = True
        in_lobby = True

        if fast:
            timer = 5
        else:
            timer = 20

        participants = {}

        stakes = gamble_amount

        horse_names = ['Sally', 'Mustang', 'Pegasus', 'Friday', 'Bonnie', 'Clyde',
                    'Tucker', 'Kansas', 'Fargo', 'Candy', 'Cannon', 'Nacho', 'Apache', 'Ace']

        class Racehorse:

            horse_number = 1

            def __init__(self):
                self.horse_num = Racehorse.horse_number
                self.name = random.choice(horse_names)
                self.breed = ['Speedy', 'Steady', 'Lucky'][self.horse_num % 3]
                self.positions = []
                
                if self.breed == 'Speedy':
                    self.speed = random.randint(7, 10)
                    self.stamina = random.randint(3, 7)
                    self.luck = random.randint(0, 3)
                
                if self.breed == 'Steady':
                    self.speed = random.randint(3, 7)
                    self.stamina = random.randint(7, 10)
                    self.luck = random.randint(0, 5)
                    
                if self.breed == 'Lucky':
                    self.speed = random.randint(2, 6)
                    self.stamina = random.randint(1, 4)
                    self.luck = random.randint(7, 10)
                    
                    
                self.overall = (self.speed + self.stamina + self.luck) / 20
                self.emoji = '🏇'
                self.reward = math.ceil(
                    (100 - (self.speed * 3) - (self.stamina * 3)) / 12)
                self.position = 79
                self.tick_num = 1

                Racehorse.horse_number += 1
                horse_names.remove(self.name)

            def move(self):
                bonus = 0
                bonus_chance = random.randint(1, 600)
                if bonus_chance <= self.luck ** 2:
                    bonus = math.ceil(random.randint(10, 20) / 4)

                speed_coefficient = random.randint(1, math.ceil(self.speed ** 1.8))
                stamina_decay = self.stamina - ((99 - self.position) / 50)
                stamina_coefficient = (self.stamina ** 2) / (200 - (self.position * 2)) * stamina_decay
                
                self.position -= math.ceil((speed_coefficient + stamina_coefficient) / 20) + bonus

                self.tick_num += 1
                
                if self.position < 0:
                    self.position = 0

            def __str__(self):
                return f'{self.emoji} {self.name}'
        
        embed = discord.Embed(
            title='🐴 Horse Race',
            description=f'Horse Race started by {ctx.author.mention} for {monkeycoin} **{stakes:,}**.\nSelect a horse by reacting to its corresponding number.',
            color=0x00ff00
        )

        horse_list = [Racehorse() for _ in range(6)]
        horse_list.sort(key=lambda x: x.speed, reverse=True)
        
        for i, horse in enumerate(horse_list):
            horse_list[i].reward = i + 2
        
        horse_list.sort(key=lambda x: x.horse_num, reverse=False)
        
        class HorseRaceView(discord.ui.View):
            @discord.ui.button(label=f"1️⃣ | {horse_list[0]}",row=0, style=discord.ButtonStyle.secondary) 
            async def bet_horse_1(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[0])
            @discord.ui.button(label=f"2️⃣ | {horse_list[1]}",row=0, style=discord.ButtonStyle.secondary)
            async def bet_horse_2(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[1])
            @discord.ui.button(label=f"3️⃣ | {horse_list[2]}",row=0, style=discord.ButtonStyle.secondary)
            async def bet_horse_3(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[2])
            @discord.ui.button(label=f"4️⃣ | {horse_list[3]}",row=1, style=discord.ButtonStyle.secondary)
            async def bet_horse_4(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[3])
            @discord.ui.button(label=f"5️⃣ | {horse_list[4]}",row=1, style=discord.ButtonStyle.secondary)
            async def bet_horse_5(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[4])
            @discord.ui.button(label=f"6️⃣ | {horse_list[5]}",row=1, style=discord.ButtonStyle.secondary)
            async def bet_horse_6(self, button, interaction):
                await interaction.response.defer()
                await add_participant(interaction.user, horse_list[5])
            
            
        class ReplayView(discord.ui.View): 
            @discord.ui.button(label=f"Play Again", emoji="🔁", custom_id="play_again", style=discord.ButtonStyle.green) 
            async def play_again(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.horse_race(self_cache, ctx, stakes, fast)
            @discord.ui.button(label=f"Double Up", emoji="⬆️", custom_id="double_up", style=discord.ButtonStyle.red) 
            async def double_up(self, button, interaction):
                await interaction.response.defer()
                await interaction.message.edit(view=None)
                await Gamble.horse_race(self_cache, ctx, stakes * 2, fast)
                
                
        for horse in horse_list:
            embed.add_field(
                name=f'__{horse.horse_num}__. | 🐴 __{horse.name}__',
                value=f'**Breed:** {horse.breed}\n**Speed:** {horse.speed}\n**Stamina:** {horse.stamina}\n**Luck:** {horse.luck}\n**Reward:** {horse.reward}x',
                inline=True
            )

        embed.add_field(
            name='__Participants__',
            value='*...*',
            inline=False
        )

        embed.set_footer(text=f'Horses will race in {timer} seconds.')

        horse_race_message = await ctx.reply(embed=embed, view=HorseRaceView())

        try:
            horse_race_message = await horse_race_message.original_response()
        except:
            pass
        
        num_to_emoji = {
            1: '1️⃣',
            2: '2️⃣',
            3: '3️⃣',
            4: '4️⃣',
            5: '5️⃣',
            6: '6️⃣'
        }

        async def update_participants():
            nonlocal participants

            participants_field = ''

            for participant, horse in participants.items():
                participants_field += f'{participant.mention}: {horse}\n'

            if participants_field == '':
                participants_field = '*...*'

            embed.set_field_at(6,
                            name=f'__Participants__',
                            value=participants_field,
                            inline=False)

            await horse_race_message.edit(embed=embed)

        async def add_participant(user, stance):
            nonlocal in_lobby
            nonlocal participants
            
            user_balance = db_manager.fetch_coin_balance(user)[0]

            if user_balance < stakes:

                embed = discord.Embed(
                    title=f':x: No dollas {user.name}?',
                    description='You\'re too broke to play',
                    color=0xff0000
                )
                await ctx.reply(embed=embed, delete_after=3)
                return

                
            participants[user] = stance


            await update_participants()

        while timer > 0:
            timer -= 1        
            embed.set_footer(text=f'Horses Racing in {timer} seconds.')
            await update_participants()
            await asyncio.sleep(1)

        in_lobby = False
        
        await horse_race_message.edit(view=None)

        track = '🏁' + '-' * 78 + '|'

        lanes = {
            1: f'{track}1️⃣',
            2: f'{track}2️⃣',
            3: f'{track}3️⃣',
            4: f'{track}4️⃣',
            5: f'{track}5️⃣',
            6: f'{track}6️⃣'
        }

        await horse_race_message.edit(embed=embed)

        async def update_track():
            nonlocal lanes
            nonlocal num_to_emoji

            for horse in horse_list:
                lanes[horse.horse_num] = f'{track[:horse.position]}{horse.emoji}{track[horse.position + 1:]}{num_to_emoji[horse.horse_num]}'

            embed = discord.Embed(
                title='🏇 Race Track',
                description='\n\n'.join(lanes.values()),
                color=0x00ff00
            )

            participants_field = ''

            for participant, horse in participants.items():
                participants_field += f'{num_to_emoji[horse.horse_num]} {participant.mention}: **{horse.name}** for {horse.reward}x\n'

            if participants_field == '':
                participants_field = '*No one bet on a horse...*'
            
            embed.add_field(
                name=f'__Participants__',
                value=participants_field,
                inline=False)

            embed.set_footer(text='Horses are racing!')
            
            await horse_race_message.edit(embed=embed)

        while not any([horse.position <= 0 for horse in horse_list]):
            await update_track()

            for horse in horse_list:
                horse.move()

            await asyncio.sleep(1)

        import matplotlib.pyplot as plt
        
        # plot each horse's position over time
        
        for horse in horse_list:
            plt.plot(horse.positions)

        plt.legend([f'{horse.name}({horse.speed}/{horse.stamina}/{horse.luck})' for horse in horse_list])
        plt.xlabel('Time (seconds)')
        
        plt.savefig('horse_race.png')


        
        await update_track()

        await asyncio.sleep(1)

        winning_horse = []

        for horse in horse_list:
            if horse.position <= 0:
                winning_horse.append(horse)

        if len(winning_horse) > 1:
            winning_horse = random.choice(winning_horse)

            horse_list.sort(key=lambda x: x.position)

            horse_list.insert(0, horse_list.pop(horse_list.index(winning_horse)))

            leaderboard = '\n'.join(
                [f'{horse_list.index(horse) + 1}. {horse.emoji} {horse.name} *({horse.breed})* | __{horse.overall}% Overall__' for horse in horse_list])

            embed = discord.Embed(
                title='🏁 Horse Race',
                description=f'That was a close race... it almost looked like a tie!\n\n \
                    After further review, it looks like **{winning_horse}** came in a split second faster!\n\n \
                        Winners won {monkeycoin} **{(stakes * winning_horse.reward):,}**!\n\n \
                            __**Results**__\n' + leaderboard,
                color=0x00ff00
            )

            winners_field = "\n".join(
                [f'{participant.mention}: {monkeycoin} +{int(participants[participant].reward * stakes):,}' for participant in participants.keys() if participants[participant] == winning_horse])
            losers_field = "\n".join(
                [f'{participant.mention}: {monkeycoin} -{stakes:,}' for participant in participants.keys() if participants[participant] != winning_horse])

            if winners_field == '':
                winners_field = '*No one*'
            if losers_field == '':
                losers_field = '*No one*'

            embed.add_field(
                name='__Winners__',
                value=winners_field,
                inline=True
            )

            embed.add_field(
                name='__Losers__',
                value=losers_field,
                inline=True
            )

            embed.set_thumbnail(
                url='https://upload.wikimedia.org/wikipedia/commons/c/c3/F1_chequered_flag_Animated.gif')

            await horse_race_message.edit(embed=embed, view=ReplayView())

        else:
            winning_horse = random.choice(winning_horse)

            horse_list.sort(key=lambda x: x.position)

            leaderboard = '\n'.join(
                [f'{horse_list.index(horse) + 1}. {horse.emoji} {horse.name} *({horse.breed})* | __{math.floor(horse.overall * 100)}% Overall__' for horse in horse_list])

            embed = discord.Embed(
                title='🏁 Horse Race',
                description=f'**{winning_horse}** came in first place!\n\n \
                    Winners won {monkeycoin} **{(stakes * winning_horse.reward):,}**!\n\n \
                        __**Results**__\n' + leaderboard,
                color=0x00ff00
            )

            winners_field = "\n".join(
                [f'{participant.mention}: {monkeycoin} +{int(participants[participant].reward * stakes):,}' for participant in participants.keys() if participants[participant] == winning_horse])
            losers_field = "\n".join(
                [f'{participant.mention}: {monkeycoin} -{stakes:,}' for participant in participants.keys() if participants[participant] != winning_horse])

            if winners_field == '':
                winners_field = '*No one*'
            if losers_field == '':
                losers_field = '*No one*'

            embed.add_field(
                name='__Winners__',
                value=winners_field,
                inline=True
            )

            embed.add_field(
                name='__Losers__',
                value=losers_field,
                inline=True
            )

            embed.set_thumbnail(
                url='https://upload.wikimedia.org/wikipedia/commons/c/c3/F1_chequered_flag_Animated.gif')

            await horse_race_message.edit(embed=embed, view=ReplayView())

        winners = {}
        
        for participant in participants.keys():

            if participants[participant] == winning_horse:
                winners[participant] = int(participants[participant].reward * stakes)
                db_manager.update_coin_balance(
                    participant.id, (int(participants[participant].reward) * stakes) - stakes)
        
                db_manager.update_winnings(participant, (int(
                    participants[participant].reward) * stakes) - stakes)
                db_manager.new_gambling_entry(
                participant.name,
                participant.id,
                'Horse Racing',
                'WIN',
                (int(participants[participant].reward) * stakes) - stakes,
                stakes            
            )
            else:
                
                db_manager.update_coin_balance(participant.id, -stakes)
                db_manager.update_winnings(participant, -stakes)
                db_manager.new_gambling_entry(
                participant.name,
                participant.id,
                'Horse Racing',
                'LOSS',
                -stakes,
                stakes            
            )

        if len(winners) > 0 and stakes > 0:
            for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(casino_investor_level):
                if investor_id in [player.id for player, winnings in winners.items()]:
                    continue
                investor = await self.client.fetch_user(investor_id)
                royalty = math.ceil(sum([winnings for player, winnings in winners.items()]) * 0.01)
                db_manager.update_balance_by_id(investor_id, royalty)
                db_manager.new_transaction(
                    'CASINO ROYALTY',
                    investor.name,
                    investor.id,
                    db_manager.fetch_balance_by_id(investor_id),
                    'TYCOON',
                    '0',
                    0,
                    royalty,
                    f'Casino royalty of {royalty} coins from a Horse Race win')
        
        game_in_progress = False

        await asyncio.sleep(10)

        await horse_race_message.edit(view=None)

        return

    async def blackjack(self, ctx, gamble_amount, fast=False):
        global game_in_progress
        cards_dir = "./resources/card_game/cards/"
        table_dir = "./resources/card_game/table.png"
        
        self_cache = self

        if game_in_progress:
            embed = discord.Embed(
                title=':x: Game in progress',
                description='There is already a game in progress',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return
        
        if db_manager.fetch_balance_by_id(ctx.author.id) < gamble_amount:
            embed = discord.Embed(
                title=':x: Not enough coins',
                description=f'You do not have enough coins to gamble {monkeycoin} {gamble_amount}.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return
        
        game_in_progress = True

        class Card:
            def __init__(self, suit, value):
                self.suit = suit
                self.value = value
                self.name = f'{value} of {suit}'
                self.image_dir = cards_dir + f'{self.value}{self.suit}.png'
                self.image = Image.open(self.image_dir)
                    
            def unhide(self):
                self.image = Image.open(self.image_dir)
                
            def hide(self):
                self.image = Image.open(cards_dir + 'red_back.png')

        class Deck:
            def __init__(self):
                self.cards = []
                self.build()

            def build(self):
                for suit in ['H', 'S', 'C', 'D']:
                    for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                        self.cards.append(Card(suit, value))

            def show(self):
                for card in self.cards:
                    card.show()

            def shuffle(self):
                for i in range(len(self.cards)-1, 0, -1):
                    r = random.randint(0, i)
                    self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

            def draw_card(self):
                return self.cards.pop()
            

        class Table(object):
            def __init__(self):
                self.image = Image.open(table_dir)
                self.image = self.image.convert("RGBA")
                self.dealer_cards = []
                self.player_cards = []
                self.hands = [self.dealer_cards, self.player_cards]

            def add_card(self, card, player):
                if player == "dealer":
                    self.dealer_cards.append(card)
                else:
                    self.player_cards.append(card)
            
            def draw(self, hidden_second_card=True):
                with Image.open(table_dir) as self.image:     
                    table_center_x = self.image.size[0] // 2
                    table_center_y = self.image.size[1] // 2

                    img_w = self.dealer_cards[0].image.size[0]
                    img_h = self.dealer_cards[0].image.size[1]

                    start_y = table_center_y - \
                        (((len(self.hands)*img_h) + (len(self.hands)-1)*15) // 2)

                    for hand in self.hands:
                        start_x = table_center_x - \
                            ((len(hand)*img_w + (len(hand)-1)*10) // 2)
                        for card in hand:
                            self.image.alpha_composite(card.image, (start_x, start_y))
                            start_x += img_w + 10
                        start_y += img_h + 15

                    return self.image
            
        
        class Hand(object):
            def __init__(self):
                self.cards = []
                self.value = 0
                self.aces = 0

            def add_card(self, card):
                self.cards.append(card)
                self.value += values[card.value]
                if card.value == 'A':
                    self.aces += 1

            def adjust_for_ace(self):
                while self.value > 21 and self.aces:
                    self.value -= 10
                    self.aces -= 1
                    
        values = {
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'J': 10,
            'Q': 10,
            'K': 10,
            'A': 11
        }
            
            
        
        class ReplayView(discord.ui.View): 
            @discord.ui.button(label=f"Play Again", emoji="🔁", custom_id="play_again", style=discord.ButtonStyle.green) 
            async def play_again(self, button, interaction):
                await interaction.response.defer()
                
                if interaction.user != ctx.author:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'This is {ctx.author.mention}\'s game. Go play your own, weirdo.',
                        color=discord.Color.red()
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
                
                await interaction.message.edit(view=None)
                await Gamble.blackjack(self_cache, ctx, gamble_amount, fast)
            @discord.ui.button(label=f"Double Up", emoji="⬆️", custom_id="double_up", style=discord.ButtonStyle.red) 
            async def double_up(self, button, interaction):
                await interaction.response.defer()
                
                if interaction.user != ctx.author:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'This is {ctx.author.mention}\'s game. Go play your own, weirdo.',
                        color=discord.Color.red()
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
                
                await interaction.message.edit(view=None)
                await Gamble.blackjack(self_cache, ctx, gamble_amount*2, fast)
        
        class BlackJackView(discord.ui.View):  
            @discord.ui.button(custom_id='hit', label='Hit', style=discord.ButtonStyle.green)
            async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
                global game_in_progress
                await interaction.response.defer()
                
                if interaction.user != ctx.author:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'This is {ctx.author.mention}\'s game. Go play your own, weirdo.',
                        color=discord.Color.red()
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
                
                embed = discord.Embed(
                    title='♦️ Blackjack',
                    description=f'{ctx.author.mention} hits',
                    color=discord.Color.green()
                )
                
                embed.set_image(url='attachment://table.png')
                
                await interaction.message.edit(view=None, embed=embed)
                
                await asyncio.sleep(1)
                
                if player_hand.value > 21:
                    embed.description = f'{ctx.author.mention} busts at {player_hand.value}'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ Dealer wins', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, -gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'LOSS',
                        -gamble_amount,
                        gamble_amount            
                    )
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                
                player_hand.add_card(deck.draw_card())
                player_hand.adjust_for_ace()
                
                table.add_card(player_hand.cards[-1], "player")
                table_image = table.draw()
                table_image.save('table.png')
                await interaction.message.edit(file=discord.File('table.png'), view=None)
                
                await asyncio.sleep(1)
                
                await interaction.message.edit(view=self)
                
                if player_hand.value > 21:
                    embed.description = f'{ctx.author.mention} busts at **{player_hand.value}**'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ Dealer wins', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, -gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'LOSS',
                        -gamble_amount,
                        gamble_amount            
                    )
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                
            @discord.ui.button(custom_id='stand', label='Stand', style=discord.ButtonStyle.blurple)
            async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
                global game_in_progress
                await interaction.response.defer()
                
                if interaction.user != ctx.author:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'This is {ctx.author.mention}\'s game. Go play your own, weirdo.',
                        color=discord.Color.red()
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
                
                embed = discord.Embed(
                    title = f'♦️ Blackjack',
                    description = f'{ctx.author.mention} stands at **{player_hand.value}**',
                    color = discord.Color.yellow()
                )
                
                embed.set_image(url='attachment://table.png')
                
                await interaction.message.edit(embed=embed, view=None)
                
                await asyncio.sleep(1)
                
                dealer_hand.cards[1].unhide()
                
                table_image = table.draw()
                table_image.save('table.png')
                
                embed.set_image(url='attachment://table.png')
                
                await interaction.message.edit(embed=embed, file=discord.File('table.png'), view=None)
                
                await asyncio.sleep(1)
                
                while dealer_hand.value < 17 and dealer_hand.value < player_hand.value:
                    dealer_hand.add_card(deck.draw_card())
                    dealer_hand.adjust_for_ace()
                    table.add_card(dealer_hand.cards[-1], "dealer")
                    table_image = table.draw()
                    table_image.save('table.png')
                    await interaction.message.edit(file=discord.File('table.png'), view=None)
                    await asyncio.sleep(1)
                    
                table_image = table.draw()
                table_image.save('table.png')

                if dealer_hand.value > 21:
                    embed.description = f'Dealer busted at **{dealer_hand.value}**!'
                    embed.color = discord.Color.green()
                    embed.add_field(name='✅ You win', value=f'**+ {monkeycoin} {gamble_amount * 2:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'WIN',
                        gamble_amount,
                        gamble_amount            
                    )
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                if dealer_hand.value > player_hand.value:
                    embed.description = f'Dealer wins with **{dealer_hand.value}**!'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ Dealer wins', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                elif dealer_hand.value < player_hand.value:
                    embed.description = f'{ctx.author.mention} wins with **{player_hand.value}**!'
                    embed.color = discord.Color.green()
                    embed.add_field(name='✅ You win', value=f'**+ {monkeycoin} {gamble_amount * 2:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed)
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'WIN',
                        gamble_amount,
                        gamble_amount            
                    )
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                else:
                    embed.description = f'Dealer and {ctx.author.mention} tie with **{player_hand.value}**! Push!'
                    await interaction.message.edit(view=ReplayView(), embed=embed)
                    game_in_progress = False
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                
            @discord.ui.button(custom_id='double', label='Double', style=discord.ButtonStyle.red, disabled=False)
            async def double(self, button: discord.ui.Button, interaction: discord.Interaction):
                global game_in_progress
                nonlocal gamble_amount
                
                if interaction.user != ctx.author:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'This is {ctx.author.mention}\'s game. Go play your own, weirdo.',
                        color=discord.Color.red()
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
                
                gamble_amount *= 2
                
                await interaction.response.defer()
                
                            
                embed = discord.Embed(
                    title = f'♦️ Blackjack',
                    description = f'{ctx.author.mention} doubled down to **{monkeycoin} {gamble_amount:,}**',
                    color = discord.Color.gold()
                )
                
                embed.set_image(url='attachment://table.png')
                
                await interaction.message.edit(embed=embed, view=None)
                
                await asyncio.sleep(1)
                
                dealer_hand.cards[1].unhide()
                
                table_image = table.draw()
                table_image.save('table.png')
                
                embed.set_image(url='attachment://table.png')
            
                await interaction.message.edit(embed=embed, file=discord.File('table.png'), view=None)
                
                await asyncio.sleep(1)
                
                if player_hand.value > 21:
                    embed.description = f'{ctx.author.mention} busted at **{player_hand.value}**!'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ You lose', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    db_manager.update_balance_by_id(ctx.author.id, -gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'LOSS',
                        -gamble_amount,
                        gamble_amount            
                    )
                    game_in_progress = False
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                
                player_hand.add_card(deck.draw_card())
                player_hand.adjust_for_ace()
                table.add_card(player_hand.cards[-1], "player")
                table_image = table.draw()
                table_image.save('table.png')

                if player_hand.value > 21:
                    embed.description = f'{ctx.author.mention} busted at **{player_hand.value}**!'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ You lose', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, -gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'LOSS',
                        -gamble_amount,
                        gamble_amount            
                    )
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                while dealer_hand.value < 16:
                    dealer_hand.add_card(deck.draw_card())
                    dealer_hand.adjust_for_ace()
                    table.add_card(dealer_hand.cards[-1], "dealer")
                    table_image = table.draw()
                    table_image.save('table.png')
                    await interaction.message.edit(file=discord.File('table.png'), view=None)
                    await asyncio.sleep(1)


                    
                table_image = table.draw()
                table_image.save('table.png')
                
                await interaction.message.edit(file=discord.File('table.png'), view=None, embed=embed)
                
                if dealer_hand.value > 21:
                    embed.description = f'{ctx.author.mention} won by dealer busting at **{dealer_hand.value}**!'
                    embed.color = discord.Color.green()
                    embed.add_field(name='✅ You win', value=f'**+ {monkeycoin} {gamble_amount * 2:,}**')
                    await interaction.message.edit(embed=embed, file=discord.File('table.png'), view=ReplayView())
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'WIN',
                        gamble_amount,
                        gamble_amount            
                    )
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                if dealer_hand.value > player_hand.value:
                    embed.description = f'{ctx.author.mention} lost to **{dealer_hand.value}**!'
                    embed.color = discord.Color.red()
                    embed.add_field(name='❌ Dealer wins', value=f'**- {monkeycoin} {gamble_amount:,}**')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, -gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'LOSS',
                        -gamble_amount,
                        gamble_amount            
                    )
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                elif dealer_hand.value < player_hand.value:
                    embed.description = f'{ctx.author.mention} won!'
                    embed.color = discord.Color.green()
                    embed.add_field(name='✅ You win', value=f'+ {monkeycoin} {gamble_amount * 2:,}')
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    db_manager.update_balance_by_id(ctx.author.id, gamble_amount)
                    db_manager.new_gambling_entry(
                        ctx.author.name,
                        ctx.author.id,
                        'Blackjack',
                        'WIN',
                        gamble_amount,
                        gamble_amount            
                    )
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                else:
                    embed.description = f'{ctx.author.mention} tied! Push!'
                    embed.color = discord.Color.gold()
                    await interaction.message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
                    game_in_progress = False
                    gamble_amount = int(gamble_amount / 2)
                    await asyncio.sleep(7)
                    await interaction.message.edit(view=None)
                    return
                
            async def on_timeout(self):
                await self.message.delete()
                return
            
        
        deck = Deck()
        deck.shuffle()
        
        player_hand = Hand()
        dealer_hand = Hand()
        
        player_hand.add_card(deck.draw_card())
        dealer_hand.add_card(deck.draw_card())
        player_hand.add_card(deck.draw_card())
        dealer_hand.add_card(deck.draw_card())
        
        dealer_hand.cards[1].hide()
        
        table = Table()
        
        table.add_card(player_hand.cards[0], "player")
        table.add_card(dealer_hand.cards[0], "dealer")
        table.add_card(player_hand.cards[1], "player")
        table.add_card(dealer_hand.cards[1], "dealer")

        table_image = table.draw()
        
        table_image.save('table.png')

        embed = discord.Embed(
            title='♦️ Blackjack',
            description=f'{ctx.author.mention} has started a game of Blackjack for **{monkeycoin} {gamble_amount:,}**.',
            color=0x00ff00
        )
        
        embed.set_image(url='attachment://table.png')
        
        view = BlackJackView()
        
        blackjack_message = await ctx.reply(embed=embed, file=discord.File('table.png'))

        try:
            blackjack_message = await blackjack_message.original_response()
        except:
            pass
        
        await asyncio.sleep(1)
        
        if player_hand.value == 21:
            embed.description = f'{ctx.author.mention} has blackjack!'
            embed.color = discord.Color.green()
            embed.add_field(name='✅ You win', value=f'+ {monkeycoin} {gamble_amount * 2:,}')
            
            await blackjack_message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
            game_in_progress = False
            await asyncio.sleep(7)
            await blackjack_message.edit(view=None)
            return
        
        elif dealer_hand.value == 21:
            dealer_hand.cards[1].unhide()
            
            table_image = table.draw()
            table_image.save('table.png')
            
            embed.description = f'Dealer has blackjack!'
            embed.color = discord.Color.red()
            embed.add_field(name='❌ Dealer wins', value=f'- {monkeycoin} {gamble_amount:,}')

            await blackjack_message.edit(view=ReplayView(), embed=embed, file=discord.File('table.png'))
            game_in_progress = False
            await asyncio.sleep(7)
            await blackjack_message.edit(view=None)
            return
        
        await blackjack_message.edit(view=view)
    
        



    ################ Module End ################

def setup(client):
    client.add_cog(Gamble(client))
