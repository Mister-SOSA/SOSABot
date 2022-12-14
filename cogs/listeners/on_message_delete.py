"""
This function is called when a message is deleted.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import private_big_brother_channel

class OnMessageDelete(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        embed = discord.Embed(
            title=f'{message.author.name}#{message.author.discriminator} deleted a message in #{message.channel.name}',
            description=f'Deleted Message:\n{message.content}',
            color=0xff0000
        ).set_author(name=f'🗑️ ', icon_url=message.author.avatar)
        
        await self.client.get_channel(private_big_brother_channel).send(embed=embed)
        
def setup(client):
    client.add_cog(OnMessageDelete(client))