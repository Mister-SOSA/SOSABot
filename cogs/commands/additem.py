import discord
import item_loader
import db_manager
from discord.ext import commands, bridge
import permission_manager as perm
import web.flask.item_db_manager as item_db
import re

################ Module Start ################


class AddItem(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':heavy_plus_sign:',
        'name': 'Add Item',
        'description': 'Add an item to a user\'s inventory.',
        'aliases': [],
        'permission_level': 'SOSA',
    }

    @bridge.bridge_command(name="additem", aliases=metadata['aliases'], description=metadata['description'])
    async def additem(self, ctx, user: discord.Member, item: discord.Option(str, "Select an item", autocomplete=item_db.fetch_discord_autocomplete_items), amount: int = 1):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        try:
            item_name = re.sub(r'\W+', '', item).lower()
            item_data = await item_loader.fetch_item_by_name(item_name)

        except:
            embed = discord.Embed(
                title=f":x: Error",
                description=f"Could not find item `{item}`.",
                color=0xff0000
            )

            await ctx.reply(embed=embed)
            return

        db_manager.add_x_items_to_inventory_by_id(
            user.id, item_data["item_id"], amount)

        embed = discord.Embed(
            title=f":white_check_mark: Success",
            description=f"Added {amount} `{item_data['item_name']}` to {user.mention}'s inventory.",
            color=0x00ff00
        )

        await ctx.reply(embed=embed)

        return

    ################ Module End ################


def setup(client):
    client.add_cog(AddItem(client))
