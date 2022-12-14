import discord
import helper
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

class Poll(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':bar_chart:',
        'name': 'Poll',
        'description': 'Create a poll for others to vote on.',
        'aliases': ['vote'],
        'permission_level': 'Member'
    }


    @bridge.bridge_command(name="poll", aliases=metadata['aliases'], description=metadata['description'])
    async def poll(self, ctx, question: discord.Option(str, description="The question to ask"), option_1: discord.Option(str, description="The first option"), option_2: discord.Option(str, description="The second option")):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        class VoteView(discord.ui.View):
            def __init__(self, question, option_1, option_2):
                super().__init__(timeout=300)
                self.votes = {}
                self.question = question
                self.option_1 = option_1
                self.option_2 = option_2

                button_1 = discord.ui.Button(label=self.option_1, custom_id="option_1", style=discord.ButtonStyle.blurple, row=0)
                button_2 = discord.ui.Button(label=self.option_2, custom_id="option_2", style=discord.ButtonStyle.red, row=0)

                button_1.callback = self.option_1_callback
                button_2.callback = self.option_2_callback

                self.add_item(button_1)
                self.add_item(button_2)

            async def update_view(self):
                embed = discord.Embed(
                    title=":bar_chart: Poll",
                    description=f"__**Question:**__\n*{self.question}*",
                    color=discord.Color.blurple()
                )

                embed.add_field(name=f'__**{self.option_1}**__', value=len([x for x in self.votes.values() if x == self.option_1]))
                embed.add_field(name=f'__**{self.option_2}**__', value=len([x for x in self.votes.values() if x == self.option_2]))

                embed.set_footer(text=f"Poll created by {ctx.author.display_name}")

                await poll_message.edit(embed=embed, view=self)

            async def option_1_callback(self, interaction):
                await interaction.response.defer()
                self.votes[interaction.user.id] = self.option_1
                await self.update_view()

            async def option_2_callback(self, interaction):
                await interaction.response.defer()
                self.votes[interaction.user.id] = self.option_2
                await self.update_view()
            
            async def on_timeout(self):
                embed = discord.Embed(
                    title=":bar_chart: Poll Results",
                    description=f"__**Question:**__ {self.question}",
                    color=discord.Color.blurple()
                )

                embed.add_field(name=f'__**{self.option_1}**__', value=len([x for x in self.votes.values() if x == self.option_1]))
                embed.add_field(name=f'__**{self.option_2}**__', value=len([x for x in self.votes.values() if x == self.option_2]))

                embed.set_footer(text=f"Poll created by {ctx.author.name}")

                await poll_message.edit(embed=embed, view=None)

        embed = discord.Embed(
            title=":bar_chart: Poll",
            description=f"__**Question:**__\n*{question}*",
            color=discord.Color.blurple()
        )

        embed.add_field(name=f'__**{option_1}**__', value='0')
        embed.add_field(name=f'__**{option_2}**__', value='0')

        embed.set_footer(text=f"Poll created by {ctx.author.display_name}")

        view = VoteView(question, option_1, option_2)

        poll_message = await ctx.reply(embed=embed, view=view)

        try:
            poll_message = await poll_message.original_response()
        except:
            pass

################ Module End ################

def setup(client):
    client.add_cog(Poll(client))