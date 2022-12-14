"""
This listener is called when a reaction is added to a message.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import big_brother_channel, protected_ids

class OnReactionAdd(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id in protected_ids:
            return

        if reaction.count >= 3 and reaction.emoji == "👎":
            await reaction.message.delete()
        
def setup(client):
    client.add_cog(OnReactionAdd(client))