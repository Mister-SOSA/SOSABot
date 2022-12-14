"""
This function is called when a message is edited.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import private_big_brother_channel

class OnMessageEdit(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        
        embed = discord.Embed(
            title=f'{before.author.name}#{before.author.discriminator} edited a message in #{before.channel.name}',
            description=f'Before:\n{before.content}\n\nAfter:\n{after.content}',
            color=0xffff00
        ).set_author(name=f'📝 ', icon_url=before.author.avatar)
        
        await self.client.get_channel(private_big_brother_channel).send(embed=embed)
        
def setup(client):
    client.add_cog(OnMessageEdit(client))