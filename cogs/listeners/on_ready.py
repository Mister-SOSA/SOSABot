"""
This listener is called when the bot is ready to start working.
Imports cogs from the commands folder, sets bot status, and starts the background tasks.
"""

import discord
from discord.ext import commands, bridge


class OnReady(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        print('Ready')


def setup(client):
    client.add_cog(OnReady(client))
