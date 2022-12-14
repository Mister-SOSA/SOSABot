import discord
import helper
import db_manager as db
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

class Request(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':palms_up_together:',
        'name': 'Request',
        'description': 'Request coins from another user',
        'aliases': ['req', 'rq'],
        'permission_level': 'Member'
    }


    @bridge.bridge_command(name="request", aliases=metadata['aliases'], description=metadata['description'])
    async def request(self, ctx, user: discord.Member, amount: str):

        request_from_user = user

        if request_from_user.bot:
            embed = discord.Embed(
                title=':x: Error',
                description='You cannot request coins from a bot.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if request_from_user == ctx.author:
            embed = discord.Embed(
                title=':x: Error',
                description='You cannot request coins from yourself.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if db.is_mobile(request_from_user):
            embed = discord.Embed(
                title=':x: Error',
                description='Alt accounts cannot be requested from.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if db.is_mobile(ctx.author):
            embed = discord.Embed(
                title=':x: Error',
                description='Alt accounts cannot request coins.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        try:
            amount = int(amount)
        except:
            if amount.endswith('k'):
                amount = int(amount[:-1]) * 1000

            elif amount.endswith('m'):
                amount = int(amount[:-1]) * 1000000

            elif amount.endswith('b'):
                amount = int(amount[:-1]) * 1000000000

            else:
                embed = discord.Embed(
                    title=':x: Error',
                    description='Invalid amount.',
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
                return


        embed = discord.Embed(
            title=':moneybag: Request',
            description=f'{ctx.author.mention} has requested {monkeycoin} **{amount:,}** from {request_from_user.mention}.',
            color=0x00ff00
        )

        class RequestView(discord.ui.View):
            @discord.ui.button(label='Pay', style=discord.ButtonStyle.green, emoji='💵')
            async def pay(self, button, interaction):
                if interaction.user != request_from_user:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'You cannot pay for someone else, {interaction.user.mention}.',
                        color=0xff0000
                    )

                    await interaction.response.send_message(embed=embed, delete_after=2)
                    return

                await interaction.response.defer()
                
                if db.fetch_coin_balance(request_from_user)[0] < amount:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'{request_from_user.mention} does not have enough coins to fulfill this request.',
                        color=0xff0000
                    )
                    await request_message.edit(embed=embed, view=None)
                    return

                db.update_coin_balance(ctx.author.id, amount)
                db.update_coin_balance(request_from_user.id, -amount)

                db.new_transaction(trans_type='PAYMENT',
                                recip_username=ctx.author.name,
                                recip_id=ctx.author.id,
                                recip_newbal=db.fetch_coin_balance(ctx.author)[0],
                                sender_username=request_from_user.name,
                                sender_id=request_from_user.id,
                                sender_newbal=db.fetch_coin_balance(request_from_user)[0],
                                amount=amount,
                                note=f'Payment from {ctx.author.name}#{ctx.author.discriminator} of {amount} coins via !request command.')
                db.new_transaction(trans_type='PAYMENT',
                                    recip_username=request_from_user.name,
                                    recip_id=request_from_user.id,
                                    recip_newbal=db.fetch_coin_balance(request_from_user)[0],
                                    sender_username=ctx.author.name,
                                    sender_id=ctx.author.id,
                                    sender_newbal=db.fetch_coin_balance(ctx.author)[0],
                                    amount=-amount,
                                    note=f'Payment to {request_from_user.name}#{request_from_user.discriminator} of {amount} coins via !request command.')
                
                
                embed = discord.Embed(
                    title=':moneybag: Request Accepted',
                    description=f'{request_from_user.mention} has sent **{amount:,}** coins to {ctx.author.mention}.',
                    color=0x00ff00
                )

                await request_message.edit(embed=embed, view=None)

            @discord.ui.button(label='Decline', style=discord.ButtonStyle.red, emoji='⛔')
            async def decline(self, button, interaction):
                if interaction.user != request_from_user:
                    embed = discord.Embed(
                        title=':x: Error',
                        description=f'You cannot decline for someone else, {interaction.user.mention}.',
                        color=0xff0000
                    )

                    await interaction.response.send_message(embed=embed)
                    return

                await interaction.response.defer()

                embed = discord.Embed(
                    title=':no_entry_sign: Request Declined',
                    description=f'{request_from_user.mention} has declined {ctx.author.mention}\'s request for {monkeycoin} **{amount:,}**.',
                    color=0xff0000
                )

                await request_message.edit(embed=embed, view=None)


        request_message = await ctx.reply(embed=embed, view=RequestView())

        try:
            request_message = await request_message.original_response()
        except:
            pass



################ Module End ################

def setup(client):
    client.add_cog(Request(client))