import discord
import helper
import datetime
import pytz
from discord.ext import commands, bridge
import permission_manager as perm

errors = {}

################ Module Start ################

central = pytz.timezone('US/Central')

class Commit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    metadata = {
        'emoji': ':arrow_heading_up:',
        'name': 'Commit',
        'description': 'Publish changes to changelog',
        'aliases': [],
        'permission_level': 'SOSA',
    }
        
    @bridge.bridge_command(name="commit", aliases=metadata['aliases'], description=metadata['description'])
    async def commit(self, ctx, test: bool = True):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        
        changelog_channel = self.client.get_channel(1039219068563103754)
        test_channel = self.client.get_channel(702666848499531796)
        
        class CommitModal(discord.ui.Modal):
            def __init__(self, *args, **kwargs):
                super().__init__(timeout=None, *args, **kwargs)                
                self.add_item(discord.ui.InputText(label="Commit Title", custom_id="commit_message"))
                self.add_item(discord.ui.InputText(label="Commit Description", custom_id="commit_description", style=discord.InputTextStyle.long))
                
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                embed = discord.Embed(
                    title=f':white_check_mark: {self.children[0].value}',
                    description=f'{self.children[1].value}',
                    color=0x00ff00
                )
                embed.set_footer(
                    text=f'Commit by {ctx.author.name} at {datetime.datetime.now(central).strftime("%m/%d/%Y %I:%M %p")}')

                if test:
                    commit_message = await test_channel.send(embed=embed)
                else:
                    commit_message = await changelog_channel.send(embed=embed)
                    
                await commit_message.add_reaction('👍')
                await commit_message.add_reaction('👎')
                

        await ctx.send_modal(CommitModal(title='Commit'))


    ################ Module End ################
    
def setup(client):
    client.add_cog(Commit(client))