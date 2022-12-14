import discord
import helper
import permission_manager as perms
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

class Ban(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    metadata = {
        'emoji': ':hammer:',
        'name': 'Ban',
        'description': 'Ban a user from the server.',
        'aliases': [],
        'permission_level': 'Admin',
        'syntax': '!ban <@user_mention>',
        'usage_examples': ['!ban @Big Iron#2222']
    }

    @bridge.bridge_command(name="ban", aliases=metadata['aliases'], description=metadata['description'])
    async def ban(self, ctx, member: discord.Member):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        try:
            await ctx.guild.ban(member)
            ban_embed = discord.Embed(
                title=':hammer: Sent user.name to the shadow realm',
                description=f'{member.mention} has been banned by {ctx.author.mention}.',
                color=0x0000ff
            ).set_image(url='https://media.tenor.com/Gh9SFp64h8wAAAAC/banned-and-you-are-banned.gif')

            await ctx.reply(embed=ban_embed)
            
        except:
            error_embed = discord.Embed(
                title=':x: Error',
                description=f'Failed to ban {member.mention}.',
                color=0xff0000
            )
            await ctx.reply(embed=error_embed)

    ################ Module End ################
    
def setup(client):
    client.add_cog(Ban(client))