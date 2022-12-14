import discord
import helper
import cogs.commands.assets.pickpocket_db_manager as ppdb
import db_manager as db
import asyncio
import random
from discord.ext import commands, bridge
import permission_manager as perm

errors = {}

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

pickpocket_in_progress = False

class Pickpocket(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':ninja:',
        'name': 'Pickpocket',
        'description': 'Attempt to pickpocket another user\'s coins.',
        'aliases': ['pick', 'pp'],
        'permission_level': 'Member'
    }
    @commands.user_command(name="Pickpocket")
    async def pickpocket_app(self, ctx, victim: discord.Member):
        await self.pickpocket_start(ctx, victim)
    
    @bridge.bridge_command(name="pickpocket", aliases=metadata['aliases'], description=metadata['description'])
    async def pickpocket(self, ctx, victim: discord.Member):
        await self.pickpocket_start(ctx, victim)

    async def pickpocket_start(self, ctx, victim: discord.Member):
        global pickpocket_in_progress

        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return

        attacker = ctx.author

        if victim == ctx.author:
            embed = discord.Embed(
                title=":x: Error", description="You can't pickpocket yourself. Retard moment", color=0xff0000)
            await ctx.reply(embed=embed)
            return

        if victim.bot:
            embed = discord.Embed(
                title=":x: Error", description="You can't pickpocket a bot stupidass.", color=0xff0000)
            await ctx.reply(embed=embed)
            return

        if pickpocket_in_progress:
            embed = discord.Embed(
                title=":x: Error", description="A pickpocket is already in progress.", color=0xff0000)
            await ctx.reply(embed=embed)
            return

        if db.is_mobile(attacker):
            embed = discord.Embed(
                title=':x: Error',
                description='Alt accounts cannot pickpocket.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        if db.is_mobile(victim):
            embed = discord.Embed(
                title=':x: Error',
                description='Alt accounts cannot be pickpocketed.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        victim_balance = db.fetch_coin_balance(victim)[0]

        if victim_balance < 1:
            embed = discord.Embed(
                title=":x: Error", description="That user doesn't have any coins to steal.", color=0xff0000)
            await ctx.reply(embed=embed)
            return

        if ppdb.is_on_cooldown(attacker):
            embed = discord.Embed(
                title=":clock10: Cooldown", description="You're pickpocketting too often. Lay low for a while...", color=0xff0000)
            await ctx.reply(embed=embed)
            return

        timer = 60

        amount = random.randint(int(round(victim_balance * .03)),
                                int(round(victim_balance * .08)))

        if amount < 1:
            amount = 1

        pickpocket_in_progress = True

        dm_embed = discord.Embed(
            title="🚨 Pickpocket Alarm", description=f"You are being pickpocketed by {attacker.mention} in {ctx.channel.mention}!\nYou have {timer} seconds to stop it...", color=0xff0000)

        try:
            await victim.send(embed=dm_embed)
        except discord.errors.Forbidden:
            pass
        
        async def stop_pickpocket(user):
            global pickpocket_in_progress
            if (user == victim or user.id == 268974144593461248):
                global pickpocket_in_progress
                pickpocket_in_progress = False
                embed = discord.Embed(
                    title=":no_entry_sign: Pickpocket Stopped", description=f"{victim.mention} stopped the pickpocket attempt and saved {monkeycoin} **{amount:,}**!", color=0xff0000)

                await pickpocket_message.edit(embed=embed, view=None)

                ppdb.add_entry(attacker, victim, amount, 'FAIL')

                return
        
        class PickpocketView(discord.ui.View):
            @discord.ui.button(label=f"Stop the Pickpocket", emoji="🚫", row=0, style=discord.ButtonStyle.secondary) 
            async def stop_pickpocket_button(self, button, interaction):
                await stop_pickpocket(interaction.user)
                await interaction.response.defer()
        
        pickpocket_embed = discord.Embed(
            title="💸 Pickpocket Attempt", description=f"{attacker.mention} is attempting to pickpocket {victim.mention}...", color=0x00ff00)

        pickpocket_embed.set_footer(
            text=f'{victim.name} has {timer} seconds to stop the pickpocket.')

        pickpocket_message = await ctx.reply(embed=pickpocket_embed, view=PickpocketView())

        try:
            pickpocket_message = await pickpocket_message.original_response()
        except:
            pass

        while timer > 0 and pickpocket_in_progress:
            timer -= 1
            pickpocket_embed.description = f"{attacker.mention} is attempting to pickpocket {victim.mention}..."
            pickpocket_embed.set_footer(
                text=f'{victim.name} has {timer} seconds to stop the pickpocket.')
            await pickpocket_message.edit(embed=pickpocket_embed)
            await asyncio.sleep(1)

        if pickpocket_in_progress:

            db.update_coin_balance(attacker.id, amount)
            db.update_coin_balance(victim.id, -amount)
            
            db.new_transaction(trans_type='PICKPOCKET',
                                        recip_username=attacker.name,
                                        recip_id=attacker.id,
                                        recip_newbal=db.fetch_coin_balance(attacker)[0],
                                        sender_username=victim.name,
                                        sender_id=victim.id,
                                        sender_newbal=db.fetch_coin_balance(victim)[0],
                                        amount=amount,
                                        note=f'Pickpocketed {amount:,} coins from {victim.name}.')
            db.new_transaction(trans_type='PICKPOCKET',
                                        recip_username=victim.name,
                                        recip_id=victim.id,
                                        recip_newbal=db.fetch_coin_balance(victim)[0],
                                        sender_username=attacker.name,
                                        sender_id=attacker.id,
                                        sender_newbal=db.fetch_coin_balance(attacker)[0],
                                        amount=-amount,
                                        note=f'Lost {amount:,} coins to a pickpocket from {attacker.name}.')

                            
                                
            db.add_theft_profit(attacker, amount)
            db.add_theft_loss(victim, amount)

            pickpocket_embed = discord.Embed(
                title="💸 Pickpocket Successful", description=f"{attacker.mention} successfully pickpocketed {monkeycoin} **{amount:,}** from {victim.mention}!", color=0x00ff00)

            ppdb.add_entry(attacker, victim, amount, 'SUCCESS')

            pickpocket_in_progress = False

            await pickpocket_message.edit(embed=pickpocket_embed, view=None)

            return

    ################ Module End ################

def setup(client):
    client.add_cog(Pickpocket(client))