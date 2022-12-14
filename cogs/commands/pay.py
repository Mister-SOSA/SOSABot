import db_manager
import discord
import helper
from discord.ext import commands, bridge
import permission_manager as perm

errors = {}

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

class Pay(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':money_with_wings:',
        'name': 'Pay',
        'description': 'Send coins to another user.',
        'aliases': ['send'],
        'permission_level': 'Member'
    }

    @bridge.bridge_command(name="pay", aliases=metadata['aliases'], description=metadata['description'])   
    async def pay(self, ctx, user: discord.Member, amount: discord.Option(str, description="Amount of coins to send.")):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
            
        if user.id == ctx.author.id:
            embed = discord.Embed(
                title=':x: Error',
                description='You can\'t pay yourself.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if db_manager.is_mobile(user):
            embed = discord.Embed(
                title=':x: Error',
                description='You cannot pay alt accounts.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if db_manager.is_mobile(ctx.author):
            embed = discord.Embed(
                title=':x: Error',
                description='Alt accounts cannot pay.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        try:
            amount = int(amount)
        except:
            if amount == 'all':
                amount = db_manager.fetch_coin_balance(ctx.author)
            
            elif amount.endswith('%'):
                try:
                    percent = int(amount.replace('%', ''))
                    amount = int(db_manager.fetch_coin_balance(ctx.author) * (percent / 100))
                except:
                    embed = discord.Embed(
                        title=':x: Error',
                        description='Invalid amount.',
                        color=0xff0000
                    )
                    await ctx.reply(embed=embed)
                    return
            
            elif amount.endswith('k'):
                try:
                    amount = int(amount[:-1]) * 1000
                except:
                    embed = discord.Embed(
                        title=':x: Error',
                        description='Invalid amount.',
                        color=0xff0000
                    )
            
            elif amount.endswith('m'):
                try:
                    amount = int(amount[:-1]) * 1000000
                except:
                    embed = discord.Embed(
                        title=':x: Error',
                        description='Invalid amount.',
                        color=0xff0000
                    )

            else:
                embed = discord.Embed(
                    title=':x: Error',
                    description='Invalid amount.',
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
                return

        if amount < 1:
            embed = discord.Embed(
                title=':x: Error',
                description='The amount must be greater than 0.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if amount > db_manager.fetch_coin_balance(ctx.author)[0]:
            embed = discord.Embed(
                title=':x: Error',
                description=f'You cannot afford to pay {monkeycoin} **{amount}**.',
            )

            await ctx.reply(embed=embed)
            return

        try:
            db_manager.update_coin_balance(user.id, amount)
            db_manager.update_coin_balance(ctx.author.id, -amount)
            db_manager.new_transaction(trans_type='PAYMENT',
                                        recip_username=ctx.author.name,
                                        recip_id=ctx.author.id,
                                        recip_newbal=db_manager.fetch_coin_balance(ctx.author)[0],
                                        sender_username=user.name,
                                        sender_id=user.id,
                                        sender_newbal=db_manager.fetch_coin_balance(user)[0],
                                        amount=-amount,
                                        note=f'Payment to {user.name}#{user.discriminator} of {amount} coins via !pay command.')
            db_manager.new_transaction(trans_type='PAYMENT',
                                        recip_username=user.name,
                                        recip_id=user.id,
                                        recip_newbal=db_manager.fetch_coin_balance(user)[0],
                                        sender_username=ctx.author.name,
                                        sender_id=ctx.author.id,
                                        sender_newbal=db_manager.fetch_coin_balance(ctx.author)[0],
                                        amount=amount,
                                        note=f'Payment from {ctx.author.name}#{ctx.author.discriminator} of {amount} coins via !pay command.')
            

            embed = discord.Embed(
                title=':bank: Success!',
                description=f'{ctx.author.mention} has paid {user.mention} {monkeycoin} {amount:,}',
                color=0x00ff00
            )
            await ctx.reply(embed=embed)
        except:
            embed = discord.Embed(
                title=':x: Error',
                description='Failed to pay.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return


################ Module End ################

def setup(client):
    client.add_cog(Pay(client))
