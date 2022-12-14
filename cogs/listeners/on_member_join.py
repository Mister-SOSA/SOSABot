"""
This function is called when a user joins the server.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import big_brother_channel

class OnMemberJoin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
        title=f'{member.name}#{member.discriminator} joined the server',
        description=f'',
        color=0x00ff00
        ).set_author(name=f'👋 ', icon_url=member.avatar)
            
        await self.client.get_channel(big_brother_channel).send(embed=embed)
        
def setup(client):
    client.add_cog(OnMemberJoin(client))