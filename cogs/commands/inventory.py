import math
import discord
import helper
import db_manager
import web.flask.item_db_manager as item_db
from discord.ext import commands, bridge
import permission_manager as perm
import item_loader
import re
from config import rarity_colors

################ Module Start ################

monkeycoin = '<:monkeycoin:1038242128045809674>'

class Inventory(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    metadata = {
        'emoji': ':school_satchel:',
        'name': 'Inventory',
        'description': 'Commands for managing your inventory',
        'aliases': ['inv'],
        'permission_level': 'Member',
    }
    
    @bridge.bridge_command(name="inventory", aliases=metadata['aliases'], description=metadata['description'])
    async def inventory(self, ctx, target: str = None):
        if not perm.has_permission(ctx.author, self.metadata):
            embed = perm.no_perms_embed(self.metadata)
            await ctx.reply(embed=embed)
            return
        
        class CloseView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None
                
            @discord.ui.button(label="Close", emoji="❎", style=discord.ButtonStyle.red)
            async def close(self, button, interaction):
                await interaction.message.delete()
                await interaction.response.defer()

            async def on_timeout(self):
                await self.message.delete()
        
        if target is None:
            target = ctx.author
        else:
            if ctx.author.id != 268974144593461248:
                embed = discord.Embed(title=":x: Error", description="You are now allowed to view other people's inventories!", color=discord.Color.red())
            
            try:
                target = await self.client.fetch_user(int(target))
            except:
                await ctx.reply("User not found")
                return

        user_inventory = parse_user_inventory(target.id)
    
        embed = discord.Embed(
            title = f":school_satchel: {target.name}'s Inventory",
            color = 0x00ff00
        )
        
        if not user_inventory:
            embed.description = f"Some dust and a dead cricket...\n\n{target.name} has nothing in their inventory."
        else:
            for item in user_inventory:
                embed.add_field(name=f"{item['ITEM_EMOJI']} __{item['ITEM_NAME']} ({item['ITEM_QUANTITY']})__", value=f"*{item['ITEM_DESCRIPTION']}*", inline=False)
            
        await ctx.reply(embed=embed, view=CloseView())
        
    @bridge.bridge_command(name="sell", description="Sell an item from your inventory")
    async def sell(self, ctx):
        user = ctx.author
        user_inventory = parse_user_inventory(user.id)
        select_options = []
        for item in user_inventory:
            select_options.append(discord.SelectOption(label=f"{item['ITEM_NAME']}", emoji=f'{item["ITEM_EMOJI"]}', value=f"{item['ITEM_NAME']}"))
        
        ephemeral_message = None
        sell_to = None
        sell_item = None
        sell_quantity = None
        sell_amount = None
        
        class SellToView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.value = None

            @discord.ui.button(label="Sell to Shop", emoji="🛒", style=discord.ButtonStyle.green)
            async def sell_to_shop(self, button: discord.ui.button, interaction: discord.Interaction):
                if interaction.user != user:
                    await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                    return
                
                nonlocal sell_to
                sell_to = 'SHOP'
                nonlocal ephemeral_message
                
                embed = discord.Embed(
                    title=":school_satchel: Select an Item",
                    description="Select an item from your inventory to sell back to the shop for 50% of its value.",
                    color=0x00ff00
                )
                await interaction.message.delete()
                ephemeral_message = await interaction.response.send_message(embed=embed, view=ChooseItemView(), ephemeral=True)
                
            @discord.ui.button(label="Custom Listing", emoji="📰", style=discord.ButtonStyle.primary, disabled=False)
            async def custom_listing(self, button: discord.ui.button, interaction: discord.Interaction):
                if interaction.user != user:
                    await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                    return
                
                nonlocal sell_to
                sell_to = 'USER'
                nonlocal ephemeral_message
                await interaction.message.delete()
                ephemeral_message = await interaction.response.send_message(embed=discord.Embed(
                    title = f":newspaper: Custom Listing",
                    description=f"Choose an item to sell to another user.",
                    color = 0xff0000
                ), view=ChooseItemView(), ephemeral=True)

            
            
        class ChooseItemView(discord.ui.View):
            @discord.ui.select(options=select_options, placeholder="Choose an item to sell...")
            async def dropdown(self, select: discord.ui.Select, interaction: discord.Interaction):
                nonlocal sell_item
                nonlocal ephemeral_message
                sell_item = await item_loader.fetch_item_by_name(select.values[0])

                if sell_to == 'SHOP':
                    embed = discord.Embed(
                        title = f":moneybag: Sell to Shop",
                        description=f"How many {sell_item['item_name']} would you like to sell back to the shop for 50% value?",
                        color = 0xff0000
                    )

                    class ChooseQuantityView(discord.ui.View):
                        options = [discord.SelectOption(label=f"{i}", value=f"{i}") for i in range(1, fetch_num_in_inventory(user.id, sell_item['item_id'])+1)]
                        if len(options) > 25:
                            options = options[:25]
                        options[-1].label = f'All ({fetch_num_in_inventory(user.id, sell_item["item_id"])})'
                        options[-1].value = f'{fetch_num_in_inventory(user.id, sell_item["item_id"])}'

                        @discord.ui.select(options=options, placeholder="Choose a quantity...")
                        async def dropdown(self, select: discord.ui.Select, interaction: discord.Interaction):

                            nonlocal sell_quantity
                            sell_quantity = select.values[0]
                            nonlocal ephemeral_message
                            sell_amount = int(sell_item['item_price']) * int(sell_quantity) * 0.5

                            embed = discord.Embed(
                                title = f":moneybag: Sell to Shop",
                                description=f"Are you sure you want to sell {sell_quantity} {sell_item['item_emoji']} {sell_item['item_name']} for {monkeycoin} {int(sell_amount):,}?",
                                color = 0xff0000
                            )

                            class ConfirmView(discord.ui.View):
                                @discord.ui.button(label="Sell", emoji="💰", style=discord.ButtonStyle.green)
                                async def yes(self, button: discord.ui.button, interaction: discord.Interaction):
                                    if interaction.user != user:
                                        await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                                        return

                                    nonlocal ephemeral_message
                                    nonlocal sell_quantity
                                    nonlocal sell_amount
                                    nonlocal sell_item

                                    sell_quantity = int(sell_quantity)
                                    sell_amount = int(sell_amount)

                                    for i in range(sell_quantity):
                                        db_manager.remove_from_inventory_by_id(ctx.author.id, sell_item['item_id'])

                                    await interaction.response.edit_message(embed=discord.Embed(
                                        title = f":moneybag: Sold!",
                                        color = 0x00ff00
                                    ), view=None)

                                    db_manager.update_balance_by_id(ctx.author.id, sell_amount)
                                    db_manager.new_transaction(trans_type='ITEM SALE',
                                                                    recip_username=ctx.author.name,
                                                                    recip_id=ctx.author.id,
                                                                    recip_newbal=db_manager.fetch_coin_balance(ctx.author)[0],
                                                                    sender_username='SHOP',
                                                                    sender_id='0',
                                                                    sender_newbal=0,
                                                                    amount=sell_amount,
                                                                    note=f"Sold {sell_quantity} {sell_item['item_emoji']} {sell_item['item_name']} back to the SHOP for {sell_amount} coins.")
                                    
                                    await ctx.reply(embed=discord.Embed(
                                        title = f":moneybag: Sold to Shop!",
                                        description=f'{ctx.author.mention} sold {sell_quantity} {sell_item["item_emoji"]} {sell_item["item_name"]} back to the shop for {monkeycoin} {sell_amount:,}!',
                                        color = 0xff0000
                                    ))


                                @discord.ui.button(label="Cancel", emoji="🗑️", style=discord.ButtonStyle.red)
                                async def no(self, button: discord.ui.button, interaction: discord.Interaction):
                                    if interaction.user != user:
                                        await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                                        return

                                    nonlocal ephemeral_message
                                    await interaction.response.edit_message(embed=discord.Embed(
                                        title = f":moneybag: Sell to Shop",
                                        description=f"Cancelled.",
                                        color = 0xff0000
                                    ), view=None)
                                
                            await interaction.response.edit_message(embed=embed, view=ConfirmView())
                    
                    await interaction.response.edit_message(embed=embed, view=ChooseQuantityView())

                elif sell_to == 'USER':
                    
                    embed = discord.Embed(
                        title = f":moneybag: Custom Listing",
                        description=f"Choose an amount to sell to another user.",
                        color = 0xff0000
                    )
                    
                    class ChooseQuantityView(discord.ui.View):
                        options = [discord.SelectOption(label=f"{i}", value=f"{i}") for i in range(1, fetch_num_in_inventory(user.id, sell_item['item_id'])+1)]
                        options[-1].label = f'All ({fetch_num_in_inventory(user.id, sell_item["item_id"])})'

                        @discord.ui.select(options=options, placeholder="Choose a quantity...")
                        async def dropdown(self, select: discord.ui.Select, interaction: discord.Interaction):

                            nonlocal sell_quantity
                            sell_quantity = select.values[0]
                            nonlocal ephemeral_message
                            nonlocal sell_amount

                            class PriceModal(discord.ui.Modal):
                                def __init__(self, *args, **kwargs):
                                    super().__init__(*args, **kwargs)
                                    
                                    self.add_item(discord.ui.InputText(
                                        label=f"Sell Price",
                                        placeholder=f'How many coins would you like to sell {sell_quantity} {sell_item["item_name"]} for?',
                                        min_length=1,
                                        max_length=7
                                    ))

                                    self.add_item(discord.ui.InputText(
                                        label=f"Listing Description",
                                        placeholder=f'Why are you selling this item?',
                                        min_length=1,
                                        max_length=200,
                                        style=discord.InputTextStyle.long
                                    ))
                                    
                                async def on_timeout(self):
                                    await ctx.reply("You took too long to respond.")
                                    
                                async def on_close(self):
                                    await ctx.reply("Modal closed.")
                                    
                                async def callback(self, interaction: discord.Interaction):
                                    
                                    class ConfirmView(discord.ui.View):
                                        @discord.ui.button(label="Create", emoji="📰", style=discord.ButtonStyle.green)
                                        async def yes(self, button: discord.ui.button, interaction: discord.Interaction):
                                            if interaction.user != user:
                                                await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                                                return

                                            nonlocal ephemeral_message
                                            nonlocal sell_quantity
                                            nonlocal sell_amount
                                            nonlocal sell_item

                                            sell_quantity = int(sell_quantity)
                                            try:
                                                sell_amount = int(sell_amount)
                                            except:
                                                embed = discord.Embed(
                                                    title = f":x: Error",
                                                    description=f"Please enter a valid number for price.",
                                                    color = 0xff0000
                                                )

                                                await interaction.response.edit_message(embed=embed, view=ConfirmView())
                                                return
                                            
                                            db_manager.remove_x_items_from_inventory_by_id(ctx.author.id, sell_item['item_id'], sell_quantity)
                                            db_manager.create_sell_listing(sell_item['item_id'], sell_item['item_name'], ctx.author.id, ctx.author.name, sell_quantity, sell_amount, listing_desc)

                                            class ViewListing(discord.ui.View): 
                                                def __init__(self):
                                                    super().__init__()
                                                    url = f'http://sosabot.net/listings'
                                                    self.add_item(discord.ui.Button(label='View Listing', emoji='📰', url=url))
                                                


                                            embed=discord.Embed(
                                                title = f":newspaper: Listing Created!",
                                                description=f'{ctx.author.mention} created a listing!',
                                                color = 0xff0000
                                            )
                                            
                                            embed.add_field(name="Selling", value=f"{sell_item['item_emoji']} {sell_item['item_name']} ({sell_quantity})", inline=True)
                                            embed.add_field(name="Price", value=f"{monkeycoin} {sell_amount:,}", inline=True)

                                            custom_listing_message = await ctx.reply(embed=embed, view=ViewListing())
                                            
                                            await custom_listing_message.pin()

                                            await interaction.response.defer()
                                            
                                            

                                        @discord.ui.button(label="Cancel", emoji="🗑️", style=discord.ButtonStyle.red)
                                        async def no(self, button: discord.ui.button, interaction: discord.Interaction):
                                            if interaction.user != user:
                                                await interaction.response.send_message("You did not create this interaction", ephemeral=True)
                                                return

                                            nonlocal ephemeral_message
                                            await interaction.response.edit_message(embed=discord.Embed(
                                                title = f":newspaper: Custom Listing",
                                                description=f"Cancelled.",
                                                color = 0xff0000
                                            ), view=None)

                                    
                                    nonlocal sell_amount
                                    sell_amount = int(self.children[0].value)
                                    listing_desc = self.children[1].value
                                    embed = discord.Embed(
                                        title = f":newspaper: Custom Listing",
                                        description=f"Are you sure you want to create this listing?\n{sell_quantity} {sell_item['item_emoji']} {sell_item['item_name']} for {monkeycoin} {sell_amount:,}?",
                                        color = 0xff0000
                                    )
                                    
                                    await interaction.response.edit_message(embed=embed, view=ConfirmView())
                                        
                            await interaction.response.send_modal(PriceModal(title="Sell Price"))
                    
                    await interaction.response.edit_message(embed=embed, view=ChooseQuantityView())
        
        embed = discord.Embed(
            title = f":moneybag: Sell",
            description=f"Choose where you would like to sell your items.",
            color = 0xff0000
        )

        await ctx.reply(embed=embed, view=SellToView())
        
        return
    
    @bridge.bridge_command(name="craft", description="Craft an item using components from your inventory.")
    async def craft(self, ctx, item_name: discord.Option(str, description="What item would you like to craft?", autocomplete=item_db.fetch_discord_autocomplete_items)):
        try:
            # remove all non-alphanumeric characters
            item_name = re.sub(r'\W+', '', item_name).lower()
            item = await item_loader.fetch_item_by_name(item_name)
        except:
            embed = discord.Embed(
                title = f":x: Error",
                description=f"{item_name} not found.",
                color = 0xff0000
            )

            await ctx.reply(embed=embed)
            return
        
        if item['craftable'] == 'FALSE':
            embed = discord.Embed(
                title = f":x: Error",
                description=f"{item['item_emoji']} **{item['item_name']}** is not craftable.",
                color = 0xff0000
            )

            await ctx.reply(embed=embed)
            return
        
        if item['craftable'] == 'TRUE':
            recipe = item['recipe']
            can_craft = True
            for ingredient in recipe:
                ingredient_meta = item_db.fetch_item_by_name(ingredient['name'])
                user_quantity = db_manager.fetch_inventory_quantity_by_user_id(ctx.author.id, ingredient_meta[0])
                if user_quantity < ingredient['quantity']:
                    can_craft = False
                    break                
            
            if not can_craft:
                embed = discord.Embed(
                    title = f":x: Error",
                    description=f"You do not have enough ingredients to craft {item['item_emoji']} **{item['item_name']}**.",
                    color = 0xff0000
                )
                
                embed.add_field(name="__Ingredients__", value='\n'.join([f"{item_db.fetch_item_by_name(ingredient['name'])[5]} **{ingredient['name']}** | {ingredient['quantity']}x" for ingredient in recipe]), inline=False)

                await ctx.reply(embed=embed)
                return
            
            if can_craft:
                for ingredient in recipe:
                    ingredient_meta = item_db.fetch_item_by_name(ingredient['name'])
                    db_manager.remove_x_items_from_inventory_by_id(ctx.author.id, ingredient_meta[0], ingredient['quantity'])
                
                db_manager.add_to_inventory_by_item_id(ctx.author.id, item['item_id'])
                
                embed = discord.Embed(
                    title = f":white_check_mark: Success",
                    description=f"{ctx.author.mention} crafted 1x {item['item_emoji']} **{item['item_name']}**.",
                    color = 0xff0000
                )

                await ctx.reply(embed=embed)
                return
            
        return

    @bridge.bridge_command(name="use", description="Use an item from your inventory.")
    async def use(self, ctx, item_name: discord.Option(str, description="What item would you like to use?", autocomplete=item_db.fetch_discord_autocomplete_items), target: discord.Option(discord.Member, description="Choose a target (if applicable).", required=False)=None):
        item_name = re.sub(r'\W+', '', item_name).lower()

        user = ctx.author

        try:
            item_data = await item_loader.fetch_item_by_name(item_name)
        
        except:
            embed = discord.Embed(
                title = f":x: Error",
                description=f"Could not find item `{item_name}`.",
                color = 0xff0000
            )
            
            await ctx.reply(embed=embed)
            return
        
        if item_data['item_id'] not in db_manager.fetch_inventory_by_id(user.id):
            embed = discord.Embed(
                title = f":x: Error",
                description=f"You do not have `{item_data['item_name']}` in your inventory.",
                color = 0xff0000
            )
            
            await ctx.reply(embed=embed)
            return

        if item_data['item_status'] == 'unavailable':
            embed = discord.Embed(
                title = f":x: Error",
                description=f"`{item_data['item_name']}` is unavailable.",
                color = 0xff0000
            )
            
            await ctx.reply(embed=embed)
            return
        
        await item_data['function'](ctx, user, target=target)

        return
    
    @bridge.bridge_command(name="inspect", description="View information about an item.")
    async def inspect(self, ctx, item_name: discord.Option(str, description="What item would you like to inspect?", autocomplete=item_db.fetch_discord_autocomplete_items)):
        item_name = re.sub(r'\W+', '', item_name).lower()

        user = ctx.author

        try:
            item_data = await item_loader.fetch_item_by_name(item_name)
        
        except:
            embed = discord.Embed(
                title = f":x: Error",
                description=f"Could not find item `{item_name}`.",
                color = 0xff0000
            )
            
            await ctx.reply(embed=embed)
            return
        
        embed = discord.Embed(
            title = f":mag: {item_data['item_name']}",
            description=f"{item_data['item_description']}",
            color = rarity_colors[item_data['item_rarity']]
        )
        
        embed.add_field(name="__Lootable__", value=f"{'Yes' if item_data['lootable'] == 'TRUE' else 'No'}", inline=True)
        embed.add_field(name="__Rarity__", value=f"{item_data['item_rarity']}", inline=True)
        embed.add_field(name="__MSRP__", value=f"{monkeycoin} **{int(item_data['item_price']):,}**", inline=True)
        embed.add_field(name="__Number in Circulation__", value=f"{int(item_data['number_in_circulation']):,}", inline=True)
        embed.add_field(name="__Craftable__", value=f"{'Yes' if item_data['craftable'] == 'TRUE' else 'No'}", inline=True)

        if item_data['craftable'] == 'TRUE':
            embed.add_field(name="__Recipe__", value='\n'.join([f"{item_db.fetch_item_by_name(ingredient['name'])[5]} **{ingredient['name']}** | {ingredient['quantity']}x" for ingredient in item_data['recipe']]), inline=True)
        else:
            embed.add_field(name="__Recipe__", value="N/A", inline=True)
        
        embed.set_thumbnail(url=item_data['emoji_url'])
        embed.set_footer(text=f"Item ID: {item_data['item_id']}")
        
        await ctx.reply(embed=embed)
        return
    

def parse_user_inventory(user_id):
    user_inventory = db_manager.fetch_inventory_by_id(user_id)
    inventory_parsed = []
    
    try:
        for item_id in set(user_inventory.split(',')):
            item = item_db.fetch_item_by_id(item_id)
            inventory_parsed.append(
                {
                    'ITEM_ID' : item[0],
                    'ITEM_NAME' : item[1],
                    'ITEM_DESCRIPTION' : item[2],
                    'ITEM_PRICE' : f'{int(item[3]):,}',
                    'MUST_BE_ACTIVATED' : item[9],
                    'ITEM_QUANTITY' : user_inventory.split(',').count(item_id),
                    'ITEM_EMOJI' : item[5]
                }
            )

        return inventory_parsed
    except:
        return []

def fetch_num_in_inventory(user_id, item_id):
    user_inventory = db_manager.fetch_inventory_by_id(user_id).split(',')
    return user_inventory.count(item_id) 

################ Module End ################

def setup(client):
    client.add_cog(Inventory(client))