"""
This function is called when a user's presence is updated.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import private_big_brother_channel

class OnPresenceUpdate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.guild.id == 702361904735322172:
            return

        if before.status == discord.Status.online and after.status == discord.Status.idle and before.voice is not None:
            await before.edit(nick=f'[AFK] {before.display_name}')

        if before.status == discord.Status.idle and after.status == discord.Status.online and '[AFK]' in before.display_name:
            await before.edit(nick=before.name.replace('[AFK] ', ''))

        if before.status != after.status:
            color = 0x000000
            if after.status == discord.Status.online:
                color = 0x00ff00
                emoji = '🟢'
            elif after.status == discord.Status.offline:
                color = 0x000000
                emoji = '⚫'
            elif after.status == discord.Status.idle:
                color = 0xffff00
                emoji = '🌙'
            elif after.status == discord.Status.dnd:
                color = 0xff0000
                emoji = '🔴'
                
            presence_embed = discord.Embed(
                title=f'',
                description=f'{before} went from {before.status} to {after.status}',
                color=color
            ).set_author(name=f'{emoji}', icon_url=after.avatar)
            
            await self.client.get_channel(private_big_brother_channel).send(embed=presence_embed)
        
def setup(client):
    client.add_cog(OnPresenceUpdate(client))