import discord
import helper
import db_manager
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

class Balance(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    metadata = {
        'emoji': ':coin:',
        'name': 'Coin Balance',
        'description': 'Check coin balance.',
        'aliases': ['bal'],
        'permission_level': 'Member',
        'subcommands': []
    }
    
    async def balance_exec(self, ctx, user: discord.Member = None):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        
        if not user:
            user = ctx.author
        
        class ViewMore(discord.ui.View): 
            def __init__(self):
                super().__init__()
                url = f'http://sosabot.net/me/'
                self.add_item(discord.ui.Button(label='More', url=url))

        balance = db_manager.fetch_coin_balance(user)[0]
        winnings = db_manager.fetch_winnings(user.name)[0]

        if winnings >= 0:
            winnings = f'+{winnings:,}'
        else:
            winnings = f'{winnings:,}'

        theft_profit = db_manager.fetch_theft_profit(user)[0]
        theft_loss = db_manager.fetch_theft_loss(user)[0]

        embed = discord.Embed(
            title=f":bank: {user.name}'s Balance",
            color=0x00ff00
        )
        embed.add_field(name=":coin: __**Balance**__",
                        value=f"{monkeycoin} **{balance:,}**", inline=False)
        embed.add_field(name=":game_die: __**Gambling Net Profit**__",
                        value=f"{monkeycoin} **{winnings}**", inline=False)
        embed.add_field(name=":inbox_tray: __**Theft Gains**__",
                        value=f"{monkeycoin} **{theft_profit:,}**", inline=True)
        embed.add_field(name=":outbox_tray: __**Theft Loss**__",
                        value=f"{monkeycoin} **-{theft_loss:,}**", inline=True)

        embed.set_thumbnail(url=user.avatar)

        await ctx.reply(embed=embed, view=ViewMore())
    
    @bridge.bridge_command(name="balance", aliases=metadata['aliases'], description=metadata['description'])
    async def balance(self, ctx):
        await self.balance_exec(ctx, user=None)
    
    @commands.user_command(name='Check Balance')
    async def balance_app(self, ctx, user: discord.Member):
        await self.balance_exec(ctx, user)


################ Module End ################

def setup(client):
    client.add_cog(Balance(client))
