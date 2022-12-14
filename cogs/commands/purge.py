import discord
import helper
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################


class Purge(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':wastebasket:',
        'name': 'Purge',
        'description': 'Clears the current channel of X messages.',
        'aliases': ['p'],
        'permission_level': 'Admin',
    }

    @bridge.bridge_command(name="purge", aliases=metadata['aliases'], description=metadata['description'])
    async def purge(self, ctx, number_of_messages: discord.Option(int, description="Number of messages to delete", required=True, min=1, max=100)):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        await ctx.channel.purge(limit=number_of_messages)
        await ctx.interaction.response.send_message(f"Deleted {number_of_messages} messages.", ephemeral=True, delete_after=2)


    


################ Module End ################


def setup(client):
    client.add_cog(Purge(client))