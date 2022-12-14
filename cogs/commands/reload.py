import discord
import helper
import db_manager
import asyncio
import random
import web.flask.item_db_manager as item_db
from discord.ext import commands, bridge
import permission_manager as perm
import item_loader
import os

################ Module Start ################

class Reload(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    metadata = {
        'emoji': ':arrows_counterclockwise:',
        'name': 'Reload',
        'description': 'Reload cogs from the bot.',
        'aliases': [],
        'permission_level': 'SOSA'
    }

    @bridge.bridge_command(name="reload", aliases=metadata['aliases'], description=metadata['description'])
    async def reload_cmd(self, ctx, cog_type: discord.Option(str, description="The type of cog to reload.", choices=['items', 'commands', 'events', 'client', 'all']), cog_name: discord.Option(str, description="The name of the cog to reload.")=None):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
    
        if cog_type == 'items':
            await item_loader.reload_items()
            await ctx.reply("Reloaded items.")
        
        elif cog_type == 'commands':
            if cog_name == None:
                await ctx.reply("Please specify a cog name.")
                return
            self.client.reload_extension(f'cogs.commands.{cog_name}')
            
            embed = discord.Embed(
                title=":arrows_counterclockwise: Reloaded Cog",
                description=f"Reloaded cog `{cog_name}`.",
                color=discord.Color.dark_magenta()
            )
            
            await ctx.reply(embed=embed)
        
        elif cog_type == 'events':
            if cog_name == None:
                await ctx.reply("Please specify a cog name.")
                return
            self.client.reload_extension(f'cogs.events.{cog_name}')
            
            embed = discord.Embed(
                title=":arrows_counterclockwise: Reloaded Cog",
                description=f"Reloaded cog `{cog_name}`.",
                color=discord.Color.dark_magenta()
            )
            
            await ctx.reply(embed=embed)
            
        elif cog_type == 'all':
            await item_loader.reload_items()
            self.client.reload_extension('cogs.commands')
            self.client.reload_extension('cogs.events')
            
            embed = discord.Embed(
                title=":arrows_counterclockwise: Reloaded All",
                description=f"Reloaded all cogs and items.",
                color=discord.Color.dark_magenta()
            )
            
            await ctx.reply(embed=embed)
            
        elif cog_type == 'client':
            
            embed = discord.Embed(
                title=":arrows_counterclockwise: Restarting",
                description=f"Restarting the bot.",
                color=discord.Color.dark_magenta()
            )
            
            await ctx.reply(embed=embed)
            
            os.system('python3 bot.py')
        

    ################ Module End ################

def setup(client):
    client.add_cog(Reload(client))