from datetime import timedelta
import math
import os
import discord
from math import ceil
import asyncio
import random
import helper
from discord.ext import commands, bridge
import permission_manager as perm

################ Module Start ################

class VoteKick(commands.Cog):
    def __init__(self, client):
        self.client = client

    metadata = {
        'emoji': ':boot:',
        'name': 'Vote Kick',
        'description': 'Vote to kick a user from the server',
        'aliases': ['vk'],
        'permission_level': 'Member'
    }

    @bridge.bridge_command(name="votekick", aliases=metadata['aliases'], description=metadata['description'])
    async def votekick(self, ctx, user: discord.Member):

        if user == ctx.bot.user:
            embed = discord.Embed(
                title=':x: Error',
                description='I can\'t vote kick myself.',
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return

        votes_needed = 5
        author = ctx.author

        embed = discord.Embed(
            title=':boot: Vote Kick',
            description=f'{user.mention} has been called for a vote kick.',
            color=0x00ffff
        ).add_field(
            name='Vote',
            value=f'`0/{votes_needed}`'
        ).set_footer(
            text=f'Vote started by {author} | Vote ends in 30 seconds'
        )

        vote_message = await ctx.reply(embed=embed)

        await vote_message.add_reaction('✅')

        votes = 1

        timer = 30

        while True:
            if timer > 0 and votes < votes_needed:
                await asyncio.sleep(1)
                timer -= 1
                live_embed = await ctx.channel.fetch_message(vote_message.id)
                votes = live_embed.reactions[0].count

                embed.set_field_at(
                    0, name='Vote', value=f'`{votes}/{votes_needed}`')

                embed.set_footer(
                    text=f'Vote started by {author} | Vote ends in {timer} seconds')

                await vote_message.edit(embed=embed)
            elif timer <= 0 and votes < votes_needed:
                failed_embed = discord.Embed(
                    title=':x: Vote Failed',
                    description=f'Vote to kick {user.mention} failed with {votes}/{votes_needed} votes.',
                    color=0xff0000
                )
                await vote_message.clear_reactions()
                await vote_message.edit(embed=failed_embed)
                break
            elif votes >= votes_needed:
                if user.id == 268974144593461248 or user.id == 725049469934239795:
                    embed = discord.Embed(
                        title='🫵😂 It was worth a shot lol',
                        description=f'Everyone point and laugh at {ctx.author.mention}',
                        color=0xff0000
                    ).set_image(url='https://c.tenor.com/hQLVCo4FTRQAAAAC/bugs-bunny-backfire.gif')
                    await vote_message.edit(embed=embed)
                    await ctx.author.move_to(None)
                    return

                image_dir = '/home/ubuntu/discord_bot/commands/assets/vote_disconnect_images'
                images = os.listdir(image_dir)
                image_path = os.path.join(image_dir, random.choice(images))
                image = discord.File(
                    image_path, filename=image_path.split('/')[-1])
                await user.kick(reason=f'Vote kicked by {ctx.author}')

                success_embed = discord.Embed(
                    title=f':boot: You just got bodied by democracy.',
                    description=f'Sent his ass to the shadow realm 💀💀💀',
                    color=0x00ff00,
                ).set_image(url=f'attachment://{image.filename}').set_author(
                    name=f'Time to go, {user.name}!',
                    icon_url=user.avatar
                )
                await vote_message.clear_reactions()
                await vote_message.edit(embed=success_embed, file=image)
                break


################ Module End ################


def setup(client):
    client.add_cog(VoteKick(client))
