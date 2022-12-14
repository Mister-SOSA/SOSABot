import discord
from discord.ext import commands, bridge
import permission_manager as perm


################ Module Start ################

class Avatar(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':frame_photo:',
        'name': 'Display Avatar',
        'description': 'Displays the avatar of the specified user in full size.',
        'aliases': [],
        'permission_level': 'Member'
    }

    @bridge.bridge_command(name="avatar", aliases=metadata['aliases'], description=metadata['description'])
    async def status(self, ctx, user: discord.Option(discord.User, description="The user whose avatar you want to display.")):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        embed = discord.Embed(
            title=f"{user.name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=user.avatar.url)

        await ctx.reply(embed=embed)

        return


################ Module End ################

def setup(client):
    client.add_cog(Avatar(client))
