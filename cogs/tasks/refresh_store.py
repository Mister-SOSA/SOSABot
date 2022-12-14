"""
This task runs every night at 12:00 AM and refreshes the store.
"""

import asyncio
import datetime
import random
import discord
import discord
from discord.ext import commands, tasks
import db_manager
from web.flask import item_db_manager

class RefreshStore(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.num_items = 8
        self.refresh_store.start()
        
    @tasks.loop(hours=24)
    async def refresh_store(self):
        await asyncio.sleep(seconds_until(6, 0))
        
        buyables = item_db_manager.fetch_buyable_items()
        
        shop_odds = {
            'Elite': 0.95,
            'Legendary': 0.85,
            'Epic': 0.7,
            'Rare': 0.6,
            'Uncommon': 0.3,
            'Common': 0
        }
        
        new_shop = [] 
        
        for i in range(self.num_items):
            chance = random.random()
            new_shop.append(random.choice([x for x in buyables if chance > shop_odds[x['item_rarity']]]))
        
        item_db_manager.set_new_shop(new_shop)
        item_db_manager.restock_shop()

def seconds_until(hours, minutes):
    """
    This function returns the amount of seconds until a certain time.
    """
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(
            now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()
        
def setup(client):
    client.add_cog(RefreshStore(client))