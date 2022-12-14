"""
This function is called when a user's voice state is updated.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import big_brother_channel

class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.client.user.id:
            return
        try:
            if before.channel.guild.id == 702361904735322172:
                return
        
        except:
            pass
        
        try:
            if after.channel.guild.id == 702361904735322172:
                return
        
        except:
            pass
        
        try:
            if after.channel.id == 777739521458438174:
                return
        except:
            pass

        try:
            if before.channel.id == 777739521458438174:
                return
        except:
            pass

        if before.channel is None and after.channel:
            channel = after.channel
            embed = discord.Embed(
                title=f'',
                description=f'{member.name}#{member.discriminator} joined {channel.name}',
                color=0x00ff00
            ).set_author(name=f'🔊 ', icon_url=member.avatar)
            await self.client.get_channel(big_brother_channel).send(embed=embed)
        elif before.channel and after.channel is None:
            if '[AFK]' in member.name:
                await member.edit(nick=before.name.replace('[AFK] ', ''))

            channel = before.channel
            embed = discord.Embed(
                title=f'',
                description=f'{member.name}#{member.discriminator} left {channel.name}',
                color=0xff0000
            ).set_author(name=f'🔇 ', icon_url=member.avatar)
            await self.client.get_channel(big_brother_channel).send(embed=embed)
        
def setup(client):
    client.add_cog(OnVoiceStateUpdate(client))