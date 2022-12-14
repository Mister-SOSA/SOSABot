import discord
import helper
import db_manager
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

class SetBal(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':bank:',
        'name': 'Set Balance',
        'description': 'Set a user\'s coin balance.',
        'aliases': ['sb'],
        'permission_level': 'SOSA'
    }


    @bridge.bridge_command(name="setbalance", aliases=metadata['aliases'], description=metadata['description'])
    async def setbal(self, ctx, user: discord.Member, amount: int):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        try:
            old_balance = db_manager.fetch_coin_balance(user)
            db_manager.set_coin_balance(user.id, amount)
            new_balance = db_manager.fetch_coin_balance(user)
            db_manager.new_transaction(trans_type='SETBALANCE',
                                    recip_username=user.name,
                                    recip_id=user.id,
                                    recip_newbal=amount,
                                    sender_username='SERVER',
                                    sender_id='0',
                                    sender_newbal=0,
                                    amount= new_balance[0] - old_balance[0],
                                    note=f'Balance set to {amount} by {ctx.author.name}#{ctx.author.discriminator} via !setbalance command.')
        except Exception as e:
            error_embed = discord.Embed(
                title=':x: Error',
                description='Failed to set balance.\n\n```{}```'.format(e),
                color=0xff0000
            )
            await ctx.channel.send(embed=error_embed)
            return

        embed = discord.Embed(
            title=':bank: Success!',
            description=f'{user.mention}\'s balance has been set to {monkeycoin} **{amount:,}**.',
            color=0x00ff00
        )
        await ctx.reply(embed=embed)


################ Module End ################

def setup(client):
    client.add_cog(SetBal(client))