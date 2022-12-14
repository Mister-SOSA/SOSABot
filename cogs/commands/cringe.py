import discord
import helper
import db_manager
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

class Cringe(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    metadata = {
        'emoji': '🤮',
        'name': 'Cringe',
        'description': 'Add a cringe reaction to a message',
        'aliases': [],
        'permission_level': 'Member',
        'subcommands': []
    }
    
    @commands.message_command(name='Cringe')
    async def cringe(self, ctx, message: discord.Message):
        await message.add_reaction('🇨')
        await message.add_reaction('🇷')
        await message.add_reaction('🇮')
        await message.add_reaction('🇳')
        await message.add_reaction('🇬')
        await message.add_reaction('🇪')

        await ctx.reply('Cringe reaction added to message', delete_after=2, ephemeral=True)


################ Module End ################

def setup(client):
    client.add_cog(Cringe(client))
