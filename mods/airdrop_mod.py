"""
A module for handling the airdrop system.
"""

import discord
import random
import asyncio
import time
import web.flask.item_db_manager as item_db
import db_manager as database

monkeycoin = '<:monkeycoin:1038242128045809674>'


async def drop(ctx, drop_channel: discord.TextChannel, spawned=False):
    """
    Drops an airdrop in the given channel.
    Contains all the logic, including embeds and views.
    """

    rarity_colors = {
        "Common": 0x3a3a3c,
        "Uncommon": 0x3fd158,
        "Rare": 0x0c84ff,
        "Epic": 0xbf5af2,
        "Legendary": 0xffd608,
        "Elite": 0xffffff
    }

    airdrop_chance = .8
    random_delay = random.randint(60, 7200)
    drop_time = 30

    if spawned == True:
        airdrop_chance = 1
        random_delay = 0

    await asyncio.sleep(random_delay)

    if random.random() < airdrop_chance:
        timestamp = int(time.time()) - 21600
        airdrop_channel = drop_channel

        elite_threshold = 0.998
        legendary_threshold = 0.98
        epic_threshold = 0.9
        rare_threshold = 0.6
        uncommon_threshold = 0.20
        common_threshold = 0.00

        rarity = random.random()

        if rarity >= elite_threshold:
            prize_rarity = 'Elite'
            prize_type = random.choice(['coins', 'item'])
            if prize_type == 'coins':
                prize_coins = random.randint(5000, 10000)
                prize_string = f'{monkeycoin} {prize_coins:,}'

            if prize_type == 'item':
                prize_quantity = 1
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_string = f'1x {prize_item["item_name"]}'

        elif rarity >= legendary_threshold:
            prize_rarity = 'Legendary'
            prize_type = random.choice(['coins', 'item'])
            if prize_type == 'coins':
                prize_coins = random.randint(1000, 5000)
                prize_string = f'{monkeycoin} {prize_coins:,}'

            if prize_type == 'item':
                prize_quantity = 1
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_string = f'1x {prize_item["item_name"]}'

        elif rarity > epic_threshold:
            prize_rarity = 'Epic'
            prize_type = random.choice(['coins', 'item'])
            if prize_type == 'coins':
                prize_coins = random.randint(200, 400)
                prize_string = f'{monkeycoin} {prize_coins:,}'

            if prize_type == 'item':
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_quantity = random.randint(1, 3)
                prize_string = f'{prize_quantity}x {prize_item["item_name"]}'

        elif rarity > rare_threshold:
            prize_rarity = 'Rare'
            prize_type = random.choice(['coins', 'item'])
            if prize_type == 'coins':
                prize_coins = random.randint(100, 200)
                prize_string = f'{monkeycoin} {prize_coins:,}'

            if prize_type == 'item':
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_quantity = random.randint(2, 4)
                prize_string = f'{prize_quantity}x {prize_item["item_name"]}'

        elif rarity > uncommon_threshold:
            prize_rarity = 'Uncommon'
            prize_type = random.choice(['coins', 'item'])
            if prize_type == 'coins':
                prize_coins = random.randint(50, 100)
                prize_string = f'{monkeycoin} {prize_coins:,}'

            if prize_type == 'item':
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_quantity = random.randint(3, 5)
                prize_string = f'{prize_quantity}x {prize_item["item_name"]}'

        else:
            prize_rarity = 'Common'
            prize_type = random.choice(['coins', 'item'])

            if prize_type == 'coins':
                prize_coins = random.randint(20, 50)
                prize_string = f'{monkeycoin} {prize_coins:,}'
                database.log_airdrop(timestamp, f'COINS={prize_coins}')

            if prize_type == 'item':
                prize_item = random.choice(
                    item_db.fetch_lootable_items_by_rarity(prize_rarity))
                prize_quantity = random.randint(6, 10)
                prize_string = f'{prize_quantity}x {prize_item["item_name"]}'

        embed = discord.Embed(
            title='🪂 Airdrop is landing in 30 seconds...',
            color=0x151515
        )

        if spawned:
            try:
                embed.title = f'🪂 {ctx.author.display_name}\'s Airdrop is landing in 30 seconds...'
                embed.description = f'{ctx.author.mention} used a **Geomarker** to call in an airdrop.'
            except:
                pass

        embed.set_image(
            url='https://c.tenor.com/3OfANUFdfFMAAAAd/airdrop-box-opening.gif')

        airdrop_message = await airdrop_channel.send(embed=embed)

        await asyncio.sleep(drop_time)

        class AirDropView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.timeout = None

            @discord.ui.button(label='Claim', style=discord.ButtonStyle.green, emoji='🫳')
            async def claim(self, button: discord.ui.Button, interaction: discord.Interaction):
                if database.airdrop_is_grabbed(timestamp):
                    await interaction.response.send_message('*This airdrop has already been claimed!*', ephemeral=True)
                    return
                else:
                    user = interaction.user
                    embed = discord.Embed(
                        title='🪂 Airdrop', description=f'{interaction.user.mention} claimed: \n**{prize_string}** from the Airdrop.', color=rarity_colors[prize_rarity])

                    if prize_type == 'item':
                        embed.set_thumbnail(url=prize_item['emoji_url'])
                        embed.add_field(
                            name='__**Item Description**__', value=prize_item['item_description'])
                        embed.add_field(
                            name='__**Total Value**__', value=f'{monkeycoin} {(int(prize_item["item_price"]) * int(prize_quantity)):,}')

                    embed.set_footer(text=f'Airdrop Rarity: {prize_rarity}')

                    await interaction.response.edit_message(embed=embed, view=None)
                    embed.set_footer(text=f'Rarity: {prize_rarity}')
                    database.grab_airdrop(
                        interaction.user.id, interaction.user.name)
                    if prize_type == 'coins':
                        database.update_coin_balance(user.id, prize_coins)
                        database.new_transaction('AIRDROP', user.name, user.id, database.fetch_balance_by_id(
                            user.id), 'SERVER', '0', 0, prize_coins, f'AIRDROP CLAIMED: {prize_rarity} - {prize_coins:,} coins')
                        pass
                    elif prize_type == 'item':
                        prize_image = prize_item['emoji_url']
                        prize_item_id = prize_item['item_id']
                        for i in range(prize_quantity):
                            database.add_to_inventory_by_item_id(
                                user.id, prize_item_id)
                        embed.set_thumbnail(url=prize_image)
                    return

            async def on_timeout(self):
                if database.airdrop_is_grabbed(timestamp):
                    return

                await airdrop_message.edit(embed=discord.Embed(title='🪂 Airdrop', description='*The Airdrop has expired.*', color=0xff0000), view=None)

                return

        embed = discord.Embed(
            title='📦 Airdrop',
            color=rarity_colors[prize_rarity]
        )
        embed.set_footer(
            text=f'Airdrop landed at {time.strftime("%I:%M %p", time.localtime(timestamp))}')

        await airdrop_message.edit(embed=embed, view=AirDropView())

    else:
        return
