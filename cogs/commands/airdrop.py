import discord
import web.flask.item_db_manager as item_db
from discord.ext import commands, bridge
import permission_manager as perm
import mods.airdrop_mod as airdrop_mod

errors = {}

################ Module Start ################

class SpawnAirdrop(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    metadata = {
        'emoji': ':parachute:',
        'name': 'Airdrop',
        'description': 'Summon an airdrop on command.',
        'aliases': [],
        'permission_level': 'SOSA'
    }

    @bridge.bridge_command(name="spawnairdrop", aliases=metadata['aliases'], description=metadata['description'])
    async def spawn_airdrop(self, ctx, target_channel: discord.TextChannel):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        await ctx.reply(f'Airdrop Summoned in {target_channel.mention}!', ephemeral=True)
        await airdrop_mod.drop(self.client, target_channel, spawned=True)
        
        

    ################ Module End ################

def setup(client):
    client.add_cog(SpawnAirdrop(client))