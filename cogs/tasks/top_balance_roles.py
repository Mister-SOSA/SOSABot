"""
This function is called every 15 seconds to update the top balance roles.
"""

import discord
import discord
from discord.ext import commands, tasks
import db_manager

class TopBalanceRoles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.top_balance_roles.start()

    @tasks.loop(seconds=30)
    async def top_balance_roles(self):
        first_place_role_id = 1035380118564110396
        second_place_role_id = 1035380342632218654
        third_place_role_id = 1035380439499677716
        
        guild = await self.client.fetch_guild(734646852154163211)
        
        first_place_role = guild.get_role(first_place_role_id)
        second_place_role = guild.get_role(second_place_role_id)
        third_place_role = guild.get_role(third_place_role_id)

        role_objects = [first_place_role, second_place_role, third_place_role]
        
        members = await guild.fetch_members(limit=None).flatten()
        
        users = await self.top_3_users()
        
        for member in members:
            for role in role_objects:
                if role in member.roles and member.id != users[role_objects.index(role)]['id']:
                    await member.remove_roles(role)
                    
        
        
        emojis = ['🥇', '🥈', '🥉']
        
        for i, user in enumerate(users):
            user_object = await guild.fetch_member(user['id'])
            await user_object.add_roles(role_objects[i])
            
        for i, user in enumerate(users):
            await role_objects[i].edit(name=f"{emojis[i]} {users[i]['balance']:,} coins", position=8 - i)
            


    async def top_3_users(self):
        users_sorted = db_manager.fetch_users_sorted_by_balance()
        
        users = []
        
        for user in users_sorted[:3]:
            users.append(
                {
                    'id': user[1],
                    'snowflake':  f'{user[0]}#{user[9]}',
                    'balance': user[4]
                }
            )
            
        return users
    
        
def setup(client):
    client.add_cog(TopBalanceRoles(client))