"""
Main script which connects the client to the API.

This script handles:
    - Connecting to the API
    - Handling @client.event events
    - Importing commands from the commands folder
    - Identifying commands and passing them to command_handler.py
    - Gluing the rest of the modules together

This is currently in the process of being rewritten to use the discord.ext.bridge library.
Excuse the mess.
The client events are being moved to dedicated listener cogs, so this file
will soon be a lot cleaner.
"""

import asyncio
import datetime
import os
import random
import discord
from rich import print
import db_manager as database
from discord.ext import tasks, bridge
import resources.rlshop as rlshop
import resources.val_hist as val_hist
from get_lines import get_lines, get_characters
import item_loader
import web.flask.item_db_manager as item_db
import cogs.commands.assets.pickpocket_db_manager as ppdb
import shutil
from config import token, airdrop_config
import mods.airdrop_mod as airdrop_mod

# declare the intents of the bot (permissions)
client = bridge.Bot(intents=discord.Intents.all(), command_prefix='=')

for filename in os.listdir('./cogs/commands'):
    if filename.endswith('.py') and not filename.startswith('_'):
        client.load_extension(f'cogs.commands.{filename[:-3]}')
        print(f'[green]>> Loaded Cog: {filename[:-3]}[/green]')


for filename in os.listdir('./cogs/listeners'):
    if filename.endswith('.py') and not filename.startswith('_'):
        client.load_extension(f'cogs.listeners.{filename[:-3]}')
        print(f'[blue]>> Loaded Listener: {filename[:-3]}[/blue]')


for filename in os.listdir('./cogs/tasks'):
    if filename.endswith('.py') and not filename.startswith('_'):
        client.load_extension(f'cogs.tasks.{filename[:-3]}')
        print(f'[yellow]>> Loaded Task: {filename[:-3]}[/yellow]')


monkeycoin = '<:monkeycoin:1038242128045809674>'


async def verify_database():
    """
    Verifies that all users in the server are in the database sosabot.db in the table DISCORD_USERS
    Uses db_manager.py to interact with the database
    """
    for guild in client.guilds:
        for user in guild.members:
            if not database.user_exists(user):
                print(f'[red]>> User {user} not in database, adding...[/red]')
                database.add_user(user)
                print(
                    f'[bold red]Added {user.name}#{user.discriminator} to database[/bold red]')
            if (f'{user.name}' not in database.fetch_usernames()) and database.user_exists(user):
                database.update_username(user, f'{user.name}')
                print(
                    f'[bold red]Updated {user.name}#{user.discriminator} in database[/bold red]')

    print('[green]>> Database verified')


@client.event
async def on_ready():
    """
    This function is called when the bot is ready to start working.
    Imports commands from the commands folder, sets bot status, and starts the background tasks.
    """
    # await command_handler.import_commands()
    await item_loader.import_items()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="{:,} lines of code".format(get_lines("./"))))
    await verify_database()
    airdrop.start()
    payouts.start()
    monkey_squad.start()
    valorant_payout.start()
    database_backup.start()
    print(f'Bot is currently {int(get_characters("./")):,} characters long!')
    print('[b i green]Client is ready[/b i green]')


@tasks.loop(hours=24)
async def payouts():
    """
    This function is called every 24 hours to pay out coins to all users.
    """

    guild = client.get_guild(734646852154163211)
    await asyncio.sleep(seconds_until(6, 0))
    print('[yellow]>> Starting payouts...[/yellow]')

    for user in guild.members:
        print(user)
        if database.is_mobile(user):
            continue

        payout_amount = database.fetch_user_payout_amount_by_id(user.id)

        if payout_amount > 1:
            database.update_balance_by_id(user.id, payout_amount)
            database.new_transaction(
                'TYCOON PAYOUT',
                user.name,
                user.id,
                database.fetch_balance_by_id(user.id),
                'TYCOON',
                '0',
                0,
                payout_amount,
                f'Your Tycoon made {payout_amount} coins today.'
            )

            embed = discord.Embed(
                title=':bank: Tycoon Payout',
                description=f'Tycoon check just hit.',
                color=0x00ff00
            )

            embed.add_field(
                name='__Amount__',
                value=f'{monkeycoin} {payout_amount}',
            )

            if database.fetch_tycoon_level_by_id(user.id) >= item_db.fetch_tycoon_level_by_name('Interceptor'):

                loot_items = []

                elite_threshold = 0.995
                legendary_threshold = 0.99
                epic_threshold = 0.9
                rare_threshold = 0.8
                uncommon_threshold = 0.7
                common_threshold = 0

                for i in range(5):

                    chance = random.random()

                    if chance >= elite_threshold:
                        item_type = 'Elite'
                    elif chance >= legendary_threshold:
                        item_type = 'Legendary'
                    elif chance >= epic_threshold:
                        item_type = 'Epic'
                    elif chance >= rare_threshold:
                        item_type = 'Rare'
                    elif chance >= uncommon_threshold:
                        item_type = 'Uncommon'
                    elif chance >= common_threshold:
                        item_type = 'Common'

                    scavenged_item = random.choice(
                        item_db.fetch_lootable_items_by_rarity(item_type))
                    loot_items.append(scavenged_item)
                    database.add_to_inventory_by_item_id(
                        user.id, scavenged_item['item_id'])

                embed.add_field(
                    name='🚚 __Interceptor Loot__',
                    value='\n'.join(
                        [f'{item["item_emoji"]} {item["item_name"]}' for item in loot_items]),
                    inline=False
                )

            await user.send(embed=embed)


@tasks.loop(hours=4)
async def airdrop():
    airdrop_channels = airdrop_config['airdrop_channels']
    await airdrop_mod.drop(client, client.get_channel(random.choice(airdrop_channels)))


monkey_squad_level = item_db.fetch_tycoon_level_by_name('Monkey Squad')
pickpocket_in_progress = False


@tasks.loop(hours=4)
async def monkey_squad():
    try:
        pp_chance = 1
        valid_channels = [734646852154163214, 1035296751923511306]

        if random.random() < pp_chance:
            global pickpocket_in_progress
            random_delay = random.randint(0, 7200)
            await asyncio.sleep(random_delay)
            attacker_id = random.choice(
                database.fetch_user_ids_by_minimum_tycoon_level(monkey_squad_level))
            attacker = client.get_user(attacker_id)
            user_id_pool = [x[1] for x in database.fetch_normal_users()]
            user_id_pool.remove(attacker_id)
            victim_id = random.choice(user_id_pool)
            victim = client.get_user(victim_id)

            if victim_id == attacker_id:
                return

            victim_balance = database.fetch_balance_by_id(victim_id)

            timer = 60

            amount = random.randint(int(round(victim_balance * .03)),
                                    int(round(victim_balance * .08)))

            if amount < 1:
                amount = 1

            pickpocket_in_progress = True

            pp_channel = client.get_channel(random.choice(valid_channels))

            dm_embed = discord.Embed(
                title="🚨 Pickpocket Alarm", description=f"You are being pickpocketed by {attacker.mention}\'s `Monkey Squad` in {pp_channel.mention}!\nYou have {timer} seconds to stop it...", color=0xff0000)

            try:
                await victim.send(embed=dm_embed)
            except discord.errors.Forbidden:
                pass

            async def stop_pickpocket(user):
                global pickpocket_in_progress
                if (user == victim or user.id == 268974144593461248):
                    pickpocket_in_progress = False
                    embed = discord.Embed(
                        title=":no_entry_sign: Pickpocket Stopped", description=f"{victim.mention} stopped {attacker.mention}\'s `Monkey Squad` from pickpocketing and saved {monkeycoin} **{amount:,}**!", color=0xff0000)

                    await pickpocket_message.edit(embed=embed, view=None)

                    ppdb.add_entry(attacker, victim, amount, 'FAIL')

                    return

            class PickpocketView(discord.ui.View):
                @discord.ui.button(label=f"Stop the Pickpocket", emoji="🚫", row=0, style=discord.ButtonStyle.secondary)
                async def stop_pickpocket_button(self, button, interaction):
                    await stop_pickpocket(interaction.user)
                    await interaction.response.defer()

            pickpocket_embed = discord.Embed(
                title="🐒 Pickpocket Attempt", description=f"{attacker.mention}\'s `Monkey Squad` is attempting to pickpocket {victim.mention}...", color=0x00ff00)

            pickpocket_embed.set_footer(
                text=f'{victim.name} has {timer} seconds to stop the pickpocket.')

            pickpocket_message = await pp_channel.send(embed=pickpocket_embed, view=PickpocketView())

            while timer > 0 and pickpocket_in_progress:
                timer -= 1
                pickpocket_embed.set_footer(
                    text=f'{victim.name} has {timer} seconds to stop the pickpocket.')
                await pickpocket_message.edit(embed=pickpocket_embed)
                await asyncio.sleep(1)

            if pickpocket_in_progress:

                database.update_coin_balance(attacker.id, amount)
                database.update_coin_balance(victim.id, -amount)

                database.new_transaction(trans_type='PICKPOCKET',
                                         recip_username=attacker.name,
                                         recip_id=attacker.id,
                                         recip_newbal=database.fetch_coin_balance(attacker)[
                                             0],
                                         sender_username=victim.name,
                                         sender_id=victim.id,
                                         sender_newbal=database.fetch_coin_balance(victim)[
                                             0],
                                         amount=amount,
                                         note=f'Pickpocketed {amount:,} coins from {victim.name} thanks to your Monkey Squad.')
                database.new_transaction(trans_type='PICKPOCKET',
                                         recip_username=victim.name,
                                         recip_id=victim.id,
                                         recip_newbal=database.fetch_coin_balance(victim)[
                                             0],
                                         sender_username=attacker.name,
                                         sender_id=attacker.id,
                                         sender_newbal=database.fetch_coin_balance(attacker)[
                                             0],
                                         amount=-amount,
                                         note=f'Lost {amount:,} coins to a pickpocket from {attacker.name}\'s Monkey Squad.')

                database.add_theft_profit(attacker, amount)
                database.add_theft_loss(victim, amount)

                pickpocket_embed = discord.Embed(
                    title="🐒 Pickpocket Successful", description=f"{attacker.mention}\'s `Monkey Squad` successfully pickpocketed {monkeycoin} **{amount:,}** from {victim.mention}!", color=0x00ff00)

                ppdb.add_entry(attacker, victim, amount, 'SUCCESS')

                pickpocket_in_progress = False

                await pickpocket_message.edit(embed=pickpocket_embed, view=None)

                return

    except Exception as e:
        print(e)
        pass


@tasks.loop(minutes=5)
async def valorant_payout():

    valorant_players = database.fetch_valorant_players()

    for username in valorant_players:
        try:
            player_data = await val_hist.fetch_player_data(username)
        except:
            continue
        if database.match_already_logged(player_data):
            continue

        user_id = database.fetch_discord_user_id_by_valorant_username(
            player_data['username'], player_data['tag'])

        if user_id == None:
            print(f'No user found for {username}')
            continue

        user = await client.fetch_user(user_id)

        if user == None:
            print(f'User {username} not found')
            continue

        database.new_valorant_match(player_data)

        if player_data['gamemode'] != 'Competitive' and player_data['gamemode'] != 'Unrated':
            continue

        if player_data['gamemode'] == 'Unrated':
            reward = (player_data['kills'] * 3) + \
                (player_data['assists'] * 2) + (player_data['headshots'] * 2)

        if player_data['gamemode'] == 'Competitive':
            reward = (player_data['kills'] * 4) + \
                (player_data['assists'] * 3) + (player_data['headshots'] * 4)

        embed = discord.Embed(
            title="🎮 Valorant Match Reward",
            description=f"You made {monkeycoin} **{reward}** from your *{player_data['gamemode']}* match on **{player_data['map']}** as **{player_data['character']}**.",
            color=0xf54f50
        )

        embed.add_field(
            name="Breakdown",
            value=f"{player_data['kills']} kills = {monkeycoin} **{player_data['kills'] * 2}**\n{player_data['assists']} assists = {monkeycoin} **{player_data['assists']}**\n{player_data['headshots']} headshots = {monkeycoin} **{player_data['headshots']}**\n\n__**Total**__ = {monkeycoin} **{reward}**",
        )

        embed.set_footer(text=f"Match Date: {player_data['match_date']}")

        embed.set_thumbnail(url=await val_hist.fetch_map_photo_by_map_name(player_data['map']))

        await user.send(embed=embed)

        database.update_balance_by_id(user_id, reward)

        database.new_transaction(
            'VALORANT',
            user.name,
            user.id,
            database.fetch_coin_balance(user)[0],
            'SERVER',
            '0',
            0,
            reward,
            f'Valorant Match Reward of {reward} coins for your match on {player_data["map"]} as {player_data["character"]}'

        )


@tasks.loop(minutes=10)
async def database_backup():
    backup_dir = os.path.join(os.getcwd(), 'backups')

    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    sosabot_backup_file = os.path.join(
        backup_dir, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}-sosabot.db')
    shop_items_backup_file = os.path.join(
        backup_dir, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}-shop_items.db')

    shutil.copyfile('./databases/sosabot.db', sosabot_backup_file)
    shutil.copyfile('./databases/shop_items.db', shop_items_backup_file)

    while len(os.listdir(backup_dir)) > 500:
        oldest_backup = min(os.listdir(backup_dir), key=os.path.getctime)
        os.remove(os.path.join(backup_dir, oldest_backup))

    print(f'Backed up databases to {backup_dir}')


def seconds_until(hours, minutes):
    """
    This function returns the amount of seconds until a certain time.
    """
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(
            now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


# Run the bot
if __name__ == "__main__":
    client.run(token)
