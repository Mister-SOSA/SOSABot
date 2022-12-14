import discord
import helper
from discord.ext import commands, bridge
import permission_manager as perm


################ Module Start ################

statuses = ['Listening', 'Playing', 'Watching', 'Streaming', 'Reset']

class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':robot:',
        'name': 'Status',
        'description': 'Change the bot\'s activity status.',
        'aliases': [],
        'permission_level': 'Member'
    }

    @bridge.bridge_command(name="status", aliases=metadata['aliases'], description=metadata['description'])
    async def status(self, ctx, status_type: discord.Option(str, description="The type of status to change to.", choices=statuses), activity: discord.Option(str, description="Activity to set the bot to.")=None):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        
        if status_type.lower() == 'listening':
            await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
        elif status_type.lower() == 'playing':
            await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activity))
        elif status_type.lower() == 'watching':
            await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        elif status_type.lower() == 'streaming':
            await ctx.bot.change_presence(activity=discord.Streaming(name=activity, url='https://www.twitch.tv/nickeh30'))
        elif status_type.lower() == 'reset':
            await ctx.bot.change_presence(activity=None)

        embed = discord.Embed(
            title=':white_check_mark: Status changed',
            color=0x00ff00
        )
        await ctx.reply(embed=embed)


################ Module End ################

def setup(client):
    client.add_cog(Status(client))