import discord
import requests
from io import BytesIO
import helper
import db_manager
from discord.ext import commands, bridge
import permission_manager as perm
import replicate

################ Module Start ################
rep_client = replicate.Client(
    api_token='a657041920ed5fec361f2a759c24b8e4d72f201f'
)

model = replicate.models.get("prompthero/openjourney")
version = model.versions.get("9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb")


class Replicate(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':robot:',
        'name': 'Replicate AI',
        'description': 'Generates an AI image from text',
        'aliases': ['rep'],
        'permission_level': 'Member',
    }
    
    @bridge.bridge_command(name="replicate", aliases=metadata['aliases'], description=metadata['description'])
    async def dallecmd(self, ctx, prompt: discord.Option(str, description="The prompt to generate an image from", required=True)):

        if ctx.channel.id != 951037482173075497 and ctx.author.id != 268974144593461248:
            forbidden_embed = discord.Embed(
                title=':x: Error',
                description='This command can only be used in <#951037482173075497>.',
                color=0xff0000
            )
            await ctx.reply(embed=forbidden_embed)
            return

        if db_manager.fetch_coin_balance(ctx.author)[0] < 100:
            error_embed = discord.Embed(
                title=':x: No dollas',
                description='You are {} coins short.'.format(
                    100 - db_manager.fetch_coin_balance(ctx.author)[0]),
                color=0xff0000
            )

            error_embed.set_footer(text='You need 100 coins to use this command.')

            await ctx.reply(embed=error_embed)
            return

        db_manager.update_coin_balance(ctx.author.id, -100)
        db_manager.new_transaction(trans_type='COMMAND',
                                recip_username=ctx.author.name,
                                recip_id=ctx.author.id,
                                recip_newbal=db_manager.fetch_coin_balance(ctx.author)[0],
                                sender_username='AI',
                                sender_id=0,
                                sender_newbal=0,
                                amount=-100,
                                note='Used Replicate Command')

        try:

            embed = discord.Embed(
                title=':mag: Replicate AI',
                description='Generating...',
                color=0x9e9e9e
            ).add_field(
                name='Query',
                value=prompt
            )

            dalle_embed = await ctx.reply(embed=embed)

            generations = output = version.predict(
                prompt = f'mdjrny-v4 style {prompt}',
                width = 512,
                height = 512,
                num_outputs = 4
            )

            await dalle_embed.delete_original_response()

            photo_embeds = []

            for generation in generations:
                photo = discord.Embed(
                    title='Results [Replicate AI]',
                    description=f'**Query:**\n{prompt}',
                    url='https://cdn.discordapp.com/'
                ).set_image(url=generation).set_footer(text=f'Generated by: {ctx.author.display_name} | {db_manager.fetch_coin_balance(ctx.author)[0]} coins remaining')

                photo_embeds.append(photo)

            await ctx.reply(embeds=photo_embeds)
            return

        except Exception as e:
            print(e)
            query_error_embed = discord.Embed(
                title=':x: Error',
                description='Failed to generate image. The server returned:\n```{}```'.format(
                    e),
                color=0xff0000
            )
            await ctx.channel.send(embed=query_error_embed)
            return

    ################ Module End ################

def setup(client):
    client.add_cog(Replicate(client))