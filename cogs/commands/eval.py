import discord
import helper
import db_manager
import asyncio
import random
import web.flask.item_db_manager as item_db
from discord.ext import commands, bridge
import permission_manager as perm

errors = {}

################ Module Start ################

class Eval(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    metadata = {
        'emoji': ':floppy_disk:',
        'name': 'Eval.py',
        'description': 'Evaluate raw Python code on the server.',
        'aliases': [],
        'permission_level': 'SOSA'
    }

    @bridge.bridge_command(name="eval", aliases=metadata['aliases'], description=metadata['description'])
    async def evalpy(self, ctx, *, code):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
    
        response = eval(code)
        
        embed = discord.Embed(
            title="Eval",
            description=f"__**Input**__\n```py\n{code}```\n__**Output**__\n```py\n{response}```",
            color=discord.Color.green()
        )
        
        await ctx.reply( embed=embed )
        

    ################ Module End ################

def setup(client):
    client.add_cog(Eval(client))