"""
Common database functions for the item database.
This version of the DB manager is not protected from SQL injection.
These commands are explicitly called by the client, so it is not a concern.
"""

import item_loader
import sqlite3
import re
import discord
import sys
sys.path.insert(1, '/home/ubuntu/discord_bot')

db_path = '/home/ubuntu/discord_bot/databases/shop_items.db'


class DBManager:
    """
    A Class with common database functions.
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert(self, table_name, values):
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({values})")
        self.conn.commit()

    def select(self, table_name, columns, condition=None):
        if condition:
            self.cursor.execute(
                f"SELECT {columns} FROM {table_name} WHERE {condition}")
        else:
            self.cursor.execute(f"SELECT {columns} FROM {table_name}")
        return self.cursor.fetchall()

    def update(self, table_name, column, value, condition):
        self.cursor.execute(
            f"UPDATE {table_name} SET {column} = {value} WHERE {condition}")
        self.conn.commit()

    def delete(self, table_name, condition):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
        self.conn.commit()

    def close(self):
        self.conn.close()


def parse_item(item: tuple) -> dict:
    """
    A function which allows you to parse an item from the database.
    Accepts one argument:
        - item: A tuple representing the item to parse.
    """

    item_id = item[0]
    item_name = item[1]
    item_description = item[2]
    item_price = item[3]
    item_quantity = item[4]
    item_emoji = item[5]
    item_status = item[6]
    maximum_allowed = item[7]
    burnout_seconds = item[8]
    must_be_activated = item[9]
    buyable = item[10]
    emoji_url = item[11]
    item_rarity = item[12]
    lootable = item[13]
    craftable = item[14]

    return {
        'item_id': item_id,
        'item_name': item_name,
        'item_description': item_description,
        'item_price': item_price,
        'item_quantity': item_quantity,
        'item_emoji': item_emoji,
        'item_status': item_status,
        'maximum_allowed': maximum_allowed,
        'burnout_seconds': burnout_seconds,
        'must_be_activated': must_be_activated,
        'buyable': buyable,
        'emoji_url': emoji_url,
        'item_rarity': item_rarity,
        'lootable': lootable,
        'craftable': craftable
    }


def fetch_item_price(item_id):
    """
    Fetches the price of an item from the database.
    """
    db = DBManager(db_path)
    price = db.select("SHOP_ITEMS", "ITEM_PRICE", f"ITEM_ID = {item_id}")
    db.close()
    return price[0][0]


def fetch_all_items():
    """
    Fetches all items from the database.
    """
    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "*")
    db.close()
    return items


def fetch_all_items_parsed():
    """
    Fetches all items from the database and parses them.
    Returns a list of dictionaries sorted by Rarity.
    """
    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "*")
    db.close()

    order = ['Elite', 'Legendary', 'Epic', 'Rare', 'Uncommon', 'Common']

    parsed_items = [parse_item(item) for item in items]

    return sorted(parsed_items, key=lambda item: order.index(item['item_rarity']))


def fetch_item_by_id(id):
    """
    Fetches an item from the database by its ID.
    """
    db = DBManager(db_path)
    item = db.select("SHOP_ITEMS", "*", f"ITEM_ID = {id}")
    db.close()
    return item[0]


def fetch_maximum_allowed_by_id(id):
    """
    Fetches the maximum allowed of an item from the database by its ID.
    """
    db = DBManager(db_path)
    max_allowed = db.select("SHOP_ITEMS", "MAXIMUM_ALLOWED", f"ITEM_ID = {id}")
    db.close()
    return max_allowed[0][0]


def reduce_item_quantity_by_id(id, amount):
    """
    Reduces the quantity of an item by X.
    """
    db = DBManager(db_path)
    db.update("SHOP_ITEMS", "ITEM_QUANTITY",
              f"ITEM_QUANTITY - {amount}", f"ITEM_ID = {id}")
    db.close()


def fetch_lootable_items_by_rarity(rarity):
    """
    Fetches all lootable items from the database by their rarity.
    """
    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "*",
                      f"ITEM_RARITY = '{rarity}' AND LOOTABLE = 'TRUE'")
    db.close()

    return [parse_item(item) for item in items]


def fetch_item_by_name(item_id):
    """
    Fetches an item from the database by its name.
    """
    db = DBManager(db_path)
    item = db.select("SHOP_ITEMS", "*", f"ITEM_NAME = '{item_id}'")
    db.close()

    if not item:
        return None

    return item[0]


def fetch_stringify_by_id(item_id):
    """
    Fetches an item from the database by its ID and returns it as a string.
    """
    db = DBManager(db_path)
    item = db.select("SHOP_ITEMS", "*", f"ITEM_ID = {item_id}")
    db.close()
    return f'{item[0][5]} {item[0][2]}'


def fetch_item_names():
    """
    Fetches all item names from the database.
    """
    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "ITEM_NAME")
    db.close()
    return [item[0] for item in items]


def fetch_discord_autocomplete_items(ctx: discord.AutocompleteContext):
    """
    Fetches all items from the database for the autocomplete feature.
    """
    return [f'{item["item_emoji"]} {item["item_name"]}' for item in item_loader.item_search(re.sub(r'\W+', '', ctx.value))]


def fetch_item_emoji_by_id(item_id):
    """
    Fetches an item's emoji from the database by its ID.
    """
    db = DBManager(db_path)
    emoji = db.select("SHOP_ITEMS", "ITEM_EMOJI", f"ITEM_ID = {item_id}")
    db.close()
    return emoji[0][0]


def fetch_item_description_by_id(item_id):
    """
    Fetches an item's description from the database by its ID.
    """
    db = DBManager(db_path)
    description = db.select(
        "SHOP_ITEMS", "ITEM_DESCRIPTION", f"ITEM_ID = {item_id}")
    db.close()
    return description[0][0]


def fetch_tycoon_items():
    """
    Fetches all tycoon items from the database.
    """
    db = DBManager(db_path)
    items = db.select("TYCOON_ITEMS", "*",
                      "ITEM_ID IS NOT NULL ORDER BY cast(ITEM_ID as int) ASC")
    db.close()

    tycoon_items = {}

    for item in items:
        tycoon_items[item[0]] = {
            'item_id': item[0],
            'item_name': item[1],
            'item_description': item[2],
            'payout_amount': item[3],
            'item_emoji': item[4],
            'item_price': item[5],
            'item_type': item[6]
        }

    return tycoon_items


def fetch_tycoon_item_by_id(item_id):
    """
    Fetches a tycoon item from the database by its ID.
    """
    db = DBManager(db_path)
    item = db.select("TYCOON_ITEMS", "*", f"ITEM_ID = {item_id}")
    db.close()
    return item[0]


def fetch_payout_by_id(item_id):
    """
    Fetches a tycoon item's payout amount from the database by its ID.
    """
    db = DBManager(db_path)
    payout = db.select("TYCOON_ITEMS", "PAYOUT_AMOUNT", f"ITEM_ID = {item_id}")
    db.close()
    return payout[0][0]


def fetch_tycoon_level_by_name(item_name):
    """
    Fetches a tycoon item's level from the database by its name.
    """
    db = DBManager(db_path)
    level = db.select("TYCOON_ITEMS", "ITEM_ID",
                      f"ITEM_NAME = '{item_name}'")[0][0]
    db.close()
    return int(level)


def restock_shop_item(item_id, amount):
    """
    Restocks an item in the shop by X.
    """
    db = DBManager(db_path)
    db.update("SHOP_ITEMS", "ITEM_QUANTITY",
              f"ITEM_QUANTITY + {amount}", f"ITEM_ID = {item_id}")
    db.close()

    return f'Restocked {fetch_item_by_id(item_id)[1]} by {amount}.'


def fetch_buyable_items() -> list:
    """
    Fetches all buyable items from the database.
    """
    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "*", "BUYABLE = 'TRUE'")
    db.close()

    return [parse_item(item) for item in items]


def set_shop_status(item_id, status):
    """
    Sets the status of an item in the shop.
    """
    db = DBManager(db_path)
    db.update("SHOP_ITEMS", "ITEM_STATUS",
              f"'{status}'", f"ITEM_ID = {item_id}")
    db.close()


def set_new_shop(shop_items: list):
    """
    Clears the old shop by setting all items ITEM_STATUS to 'INACTIVE'
    Then sets the new shop by setting each item in shop_items ITEM_STATUS to 'ACTIVE' in the database.
    """
    db = DBManager(db_path)
    db.update("SHOP_ITEMS", "ITEM_STATUS", "'INACTIVE'", "ITEM_ID IS NOT NULL")
    db.close()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for item in shop_items:
        c.execute(
            "UPDATE SHOP_ITEMS SET ITEM_STATUS = 'ACTIVE' WHERE ITEM_ID = ?", (item['item_id'],))
    conn.commit()
    conn.close()


def restock_shop():
    stock_amounts = {
        'Elite': 1,
        'Legendary': 1,
        'Epic': 5,
        'Rare': 10,
        'Uncommon': 20,
        'Common': 50
    }

    db = DBManager(db_path)
    items = db.select("SHOP_ITEMS", "*", "ITEM_STATUS = 'ACTIVE'")
    db.close()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for item in items:
        c.execute("UPDATE SHOP_ITEMS SET ITEM_QUANTITY = ? WHERE ITEM_ID = ?",
                  (stock_amounts[item[12]], item[0]))
    conn.commit()
    conn.close()
