"""
This listener is called when a member is banned from the server.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import big_brother_channel

class OnMemberBan(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title=f'{user.name}#{user.discriminator} was banned from the server',
            description=f'',
            color=0xff0000
        ).set_author(name=f'🔨 ', icon_url=user.avatar)
        
        await self.client.get_channel(big_brother_channel).send(embed=embed)
        
def setup(client):
    client.add_cog(OnMemberBan(client))