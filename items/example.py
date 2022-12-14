"""
An example item module.
All item modules must have a metadata dict and a main() coroutine in order to be loaded.
Almost all of the metadata is pulled from the database, you only need to specify the item_id and optionally aliases (plus ingredients if the item is craftable).
The main() coroutine is where you put the logic for your item. It will use the bot context (ctx) to perform actions. In this example, the item will move a random user out of voice chat.
Some items may allow for additional arguments to be passed in (like a user to target). You can do this by adding **kwargs to the main() coroutine and then passing in the arguments when you call the item.
"""

import random
import discord
import web.flask.item_db_manager as item_db
import db_manager


async def main(ctx: discord.ext.commands.Context, user: discord.Member, **kwargs):
    """
    The main coroutine for the item.
    This is where you put the logic for your item.
        - ctx: The bot context. This is where you can access the message, author, etc.
        - user: The user who used the item.
        - kwargs: Any additional arguments that were passed in.
    """

    user = ctx.author

    # check if user has item in inventory
    user_quantity = db_manager.fetch_inventory_quantity_by_user_id(
        user.id, metadata['item_id'])

    if user_quantity < 1:
        embed = discord.Embed(
            title=":x: Error",
            description=f"You do not have \"{metadata['item_name']}\" in your inventory.\n \
                Obtain this item first and try again.",
            color=0xff0000
        )

        await ctx.reply(embed=embed)

        return

    voice_users = []

    for member in ctx.guild.members:
        if member.voice != None:
            voice_users.append(member)

    if len(voice_users) > 0:
        random_user = random.choice(voice_users)

        try:
            await random_user.move_to(None)
        except discord.errors.Forbidden:
            embed = discord.Embed(
                title=":x: Error",
                description=f"I do not have permission to move {random_user.mention} out of voice chat.",
                color=0xff0000
            )

            await ctx.reply(embed=embed)

            return

        db_manager.use_item(user.id, metadata['item_id'])

        embed = discord.Embed(
            title=":crystal_ball: Crystal Ball",
            description=f"{user.mention}'s crystal ball bodied {random_user.mention} out of voice chat.",
            color=0x00ff00
        )

        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            title=":crystal_ball: Crystal Ball",
            description=f"{user.mention}'s crystal ball couldn't find anyone in voice chat.",
            color=0x00ff00
        )

        await ctx.reply(embed=embed)

    return

################ Meta Start ################

item_id = 19

result = item_db.fetch_item_by_id(item_id)
number_in_circulation = db_manager.fetch_number_in_circulation_by_item_id(
    item_id)

metadata = {
    'aliases': ['exam', 'example'],
    'item_id': result[0],
    'item_name': result[1],
    'item_description': result[2],
    'item_price': result[3],
    'item_quantity': result[4],
    'item_emoji': result[5],
    'item_status': result[6],
    'maximum_allowed': result[7],
    'burnout_seconds': result[8],
    'must_be_activated': result[9],
    'buyable': result[10],
    'emoji_url': result[11],
    'item_rarity': result[12],
    'lootable': result[13],
    'number_in_circulation': number_in_circulation,
    'craftable': result[14],
    'recipe': [
        {
            'name': 'Ingredient Name',
            'quantity': 1,
        },
        {
            'name': 'Ingredient Name',
            'quantity': 1,
        }
    ],
    'function': main
}
