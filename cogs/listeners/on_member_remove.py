"""
This function is called when a member leaves the server.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import big_brother_channel

class OnMemberRemove(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title=f'{member.name}#{member.discriminator} left the server',
            description=f'',
            color=0xff0000
        ).set_author(name=f'👋 ', icon_url=member.avatar)
        
        await self.client.get_channel(big_brother_channel).send(embed=embed)
    
        
def setup(client):
    client.add_cog(OnMemberRemove(client))