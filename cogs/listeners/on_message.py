"""
This function is called when a user sends a message.
"""

import discord
import discord
from discord.ext import commands, bridge
from config import locked_channels, clips_channel_id

class OnMessage(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        clips_channel = self.client.get_channel(clips_channel_id)

        if message.author == self.client.user:
            return

        if message.channel.id in locked_channels and message.author.id != 268974144593461248:
            await message.delete()
            return

        if message.content.startswith('!'):
            invalid_command_embed = discord.Embed(
                title=':warning: Prefix Commands Deprecated',
                description='Prefix commands are deprecated. They will no longer work. Please use slash commands instead.\nRead more about this change [here](https://discord.com/channels/734646852154163211/1039219068563103754/1047419611437617274).',
                color=0xff0000
            )
            await message.channel.send(embed=invalid_command_embed)

        if 'https://medal.tv/' in message.content:
            if message.channel.id != clips_channel_id:
                if message.channel.id == 1029471885571915866:
                    return

                await message.delete()

                clip_moved_embed = discord.Embed(
                    title='↩ Clip Moved',
                    description='Your clip got sent to <#859611805608574997>, where CLIPS go.',
                    color=0xff0000
                )
                clip_moved_embed.set_footer(
                    text='This message will be deleted in 30 seconds')
                await message.channel.send(embed=clip_moved_embed, delete_after=30)

                await clips_channel.send(message.content)

                embed = discord.Embed(
                    title=f':clapper: {message.author} would like to share a clip.',
                    description=f'Unfortunately, they can\'t read so I moved the link to the right channel.',

                    color=0xff0000
                )
                await clips_channel.send(embed=embed)
                moved_clip = await clips_channel.send(f'Their message: {message.content}')
                moved_clip.add_reaction('👍')
                moved_clip.add_reaction('👎')

            await message.add_reaction('👍')
            await message.add_reaction('👎')
        
def setup(client):
    client.add_cog(OnMessage(client))