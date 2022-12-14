import discord
import helper
from discord.ext import commands, bridge
import permission_manager as perm
import traceback
import requests


################ Module Start ################

class SetAvatar(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':frame_photo:',
        'name': 'Set Avatar',
        'description': 'Change the bot\'s profile picture',
        'aliases': [],
        'permission_level': 'SOSA'
    }

    @bridge.bridge_command(name="setavatar", aliases=metadata['aliases'], description=metadata['description'])
    async def status(self, ctx, url: discord.Option(str, description="The URL of the image to use as the bot's avatar")):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        
        try:
            img = requests.get(url).content
            await self.client.user.edit(avatar=img)
            embed = discord.Embed(title="Success!", description="Avatar changed successfully!", color=discord.Color.green())
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error!", description=f"An error occurred while changing the avatar: \n\n`{traceback.format_exc()}`", color=discord.Color.red())
            await ctx.reply(embed=embed)
        
        


################ Module End ################

def setup(client):
    client.add_cog(SetAvatar(client))