"""
A large collection of functions which allow you to interact with the database.
Many of the functions are specific-use and serve as helpers for other functions.
There's a whole lot of janky logic in here to allow f-strings and prevent SQL injection.
"""

import sqlite3
import discord
import web.flask.item_db_manager as item_db
import time
import datetime
import re

# The path to the main SQLite database file
db_path = '/path/to/database.db'


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
        # Use placeholders and a tuple to pass values to the query
        # to prevent SQL injection
        self.cursor.execute(
            f"INSERT INTO {table_name} VALUES (?, ?)", values)
        self.conn.commit()

    def select(self, table_name, columns, condition=None):
        if condition:
            # Use placeholders and a tuple to pass values to the query
            # to prevent SQL injection
            self.cursor.execute(
                f"SELECT {columns} FROM {table_name} WHERE {condition}", condition)
        else:
            self.cursor.execute(f"SELECT {columns} FROM {table_name}")
        return self.cursor.fetchall()

    def update(self, table_name, column, value, condition):
        # Use placeholders and a tuple to pass values to the query
        # to prevent SQL injection
        self.cursor.execute(
            f"UPDATE {table_name} SET {column} = ? WHERE {condition}", value)
        self.conn.commit()

    def delete(self, table_name, condition):
        # Use placeholders and a tuple to pass values to the query
        # to prevent SQL injection
        self.cursor.execute(
            f"DELETE FROM {table_name} WHERE {condition}", condition)
        self.conn.commit()

    def close(self):
        self.conn.close()


def daterange(start_date: datetime.date, end_date: datetime.date) -> datetime.date:
    """
    A generator which allows you to iterate through a range of dates.
    Accepts two arguments:
        - start_date: A datetime.date object representing the start date.
        - end_date: A datetime.date object representing the end date.
    """

    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def parse_epoch_to_datetime(epoch: int) -> str:
    """
    A function which converts an epoch timestamp to a datetime object.
    Accepts one argument, an integer representing the epoch timestamp.
    """

    return datetime.datetime.fromtimestamp(epoch).strftime('%m-%d-%Y %I:%M:%S%p')


def add_user(user: discord.User) -> None:
    """
    Adds a user to the database.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    db.insert('DISCORD_USERS',
              f'"{user.name}", "{user.id}", "{user.name}", "Member", 0, 0, "NORMAL", 0, 0, {user.discriminator}, {None}, {None}')
    db.close()


def user_exists(user: discord.User) -> bool:
    """
    A function to check if a user exists in the database.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', '*', f'USER_ID = "{user.id}"')
    db.close()
    if result:
        return True
    else:
        return False


def change_permission(user: str, permission: str) -> None:
    """
    A function to change a user's permission level in the database.
    Accepts two arguments:
        - user: A string representing at least part of the user's username.
        - permission: A string representing the desired permission level.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'PERMISSION_LEVEL',
              f'"{permission}"', f'USERNAME LIKE "%{user}%"')
    db.close()


def fetch_username(user: str) -> str:
    """
    A function which allows you to quickly fetch a user's username from a short query.
    Accepts one argument, a string representing at least part of the user's username.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USERNAME',
                       f'USERNAME LIKE "%{user}%"')
    db.close()
    return result[0]


def fetch_username_by_id(user_id: str) -> str:
    """
    A function which allows you to fetch a user's username by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USERNAME',
                       f'USER_ID == "{user_id}"')
    db.close()
    return result[0][0]


def fetch_permission(user: discord.User) -> str:
    """
    A function which allows you to fetch the permission level of a user.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'PERMISSION_LEVEL',
                       f'USER_ID == "{user.id}"')
    db.close()
    return result[0]


def fetch_coin_balance(user: discord.User) -> int:
    """
    A function which allows you to fetch the coin balance of a user.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'COINS',
                       f'USER_ID == "{user.id}"')
    db.close()
    return result[0]


def fetch_balance_by_username(username: str) -> int:
    """
    A function which allows you to fetch the coin balance of a user by their username.
    Accepts one argument, a string representing at least part of the user's username.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'COINS',
                       f'USERNAME == "{username}"')
    db.close()
    return result[0]


def fetch_users_sorted_by_balance():
    """
    A function which allows you to fetch all users sorted by their coin balance.
    Accepts no arguments.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', '*',
                       f'COINS IS NOT NULL ORDER BY COINS DESC')
    db.close()

    return result


def fetch_id_by_snowflake(snowflake: str) -> str:
    """
    A function which allows you to fetch the user ID of a user by their snowflake.
    Accepts one argument, a string representing the user's snowflake.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USER_ID',
                       f'USERNAME == "{snowflake.split("#")[0]}" AND DISCRIMINATOR == "{snowflake.split("#")[1]}"')
    db.close()
    return result[0][0]


def update_coin_balance(id, amount):
    """
    A function which allows you to update the coin balance of a user.
    Accepts two arguments:
        - id: A string representing the user's ID.
        - amount: An integer representing the amount to add to the user's balance.
    Can be used to add or subtract coins. To subtract coins, pass a negative integer.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS',
              f'COINS + {amount}', f'USER_ID == "{id}"')
    db.close()


def set_coin_balance(id, amount):
    """
    A function which allows you to set the coin balance of a user to a specific number.
    Accepts two arguments:
        - id: A string representing the user's ID.
        - amount: An integer representing the amount to set the user's balance to.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS',
              f'{amount}', f'USER_ID == "{id}"')
    db.close()


def set_balance_all(amount):
    """
    A function which allows you to set the coin balance of all users to a specific number.
    Accepts one argument, an integer representing the amount to set the user's balance to.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS',
              f'{amount}', f'USER_ID != "0"')
    db.close()


def fetch_winnings(user):
    """
    A function which allows you to fetch the winnings of a user.
    Accepts one argument, a string representing the user's username.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'COINS_WON',
                       f'USERNAME == "{user}"')
    db.close()
    return result[0]


def update_winnings(user, amount):
    """
    A function which allows you to update the winnings of a user.
    Accepts two arguments:
        - user: A string representing the user's username.
        - amount: An integer representing the amount to add to the user's winnings.
    Can be used to add or subtract winnings. To subtract winnings, pass a negative integer.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS_WON',
              f'COINS_WON + {amount}', f'USER_ID == "{user.id}"')
    db.close()


def fetch_users():
    """
    A function which allows you to fetch all users from the database.
    Accepts no arguments.
    """
    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', '*')
    db.close()
    return result


def add_coins_to_all(amount):
    """
    A function which allows you to add coins to all users.
    Accepts one argument, an integer representing the amount to add to all users.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS',
              f'COINS + {amount}', f'ACCOUNT_TYPE == "NORMAL"')
    db.close()


def fetch_normal_users():
    """
    A function which allows you to fetch all normal users from the database.
    Accepts no arguments.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', '*', f'ACCOUNT_TYPE == "NORMAL"')
    db.close()

    return result


fetch_normal_users()


def is_mobile(user):
    """
    A function which allows you to check if a user is using a mobile device.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'ACCOUNT_TYPE',
                       f'USER_ID == "{user.id}"')
    db.close()

    if result[0] == 'MOBILE':
        return True
    else:
        return False


def fetch_theft_profit(user):
    """
    A function which allows you to fetch the theft profit of a user.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'THEFT_PROFIT',
                       f'USER_ID == "{user.id}"')
    db.close()
    return result[0]


def fetch_theft_loss(user):
    """
    A function which allows you to fetch the theft loss of a user.
    Accepts one argument, a discord.User object.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'THEFT_LOSS',
                       f'USER_ID == "{user.id}"')
    db.close()
    return result[0]


def fetch_balance_by_id(id):
    """
    A function which allows you to fetch the coin balance of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'COINS',
                       f'USER_ID == "{id}"')
    db.close()
    return result[0][0]


def add_theft_profit(user, amount):
    """
    A function which allows you to add to a user's theft profit.
    Accepts two arguments:
        - user: A discord.User object.
        - amount: An integer representing the amount to add to the user's theft profit.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'THEFT_PROFIT',
              f'THEFT_PROFIT + {amount}', f'USER_ID == "{user.id}"')
    db.close()


def add_theft_loss(user, amount):
    """
    A function which allows you to add to a user's theft loss.
    Accepts two arguments:
        - user: A discord.User object.
        - amount: An integer representing the amount to add to the user's theft loss.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'THEFT_LOSS',
              f'THEFT_LOSS + {amount}', f'USER_ID == "{user.id}"')
    db.close()


def set_daily_payout_by_id(id, amount):
    """
    A function which allows you to set the daily payout of a user by their ID.
    Accepts two arguments:
        - id: A string representing the user's ID.
        - amount: An integer representing the amount to set the user's daily payout to.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'DAILY_PAYOUT',
              f'{amount}', f'USER_ID == "{id}"')
    db.close()


def update_daily_payout_by_id(id, amount):
    """
    A function which allows you to update the daily payout of a user by their ID.
    Accepts two arguments:
        - id: A string representing the user's ID.
        - amount: An integer representing the amount to add to the user's daily payout.
    Can be used to add or subtract daily payout. To subtract daily payout, pass a negative integer.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'DAILY_PAYOUT',
              f'DAILY_PAYOUT + {amount}', f'USER_ID == "{id}"')
    db.close()


def fetch_daily_payout_by_id(id):
    """
    A function which allows you to fetch the daily payout of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'DAILY_PAYOUT',
                       f'USER_ID == "{id}"')
    db.close()
    return result[0][0]


def fetch_usernames():
    """
    A function which allows you to fetch all usernames from the database.
    Accepts no arguments.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USERNAME')
    db.close()

    usernames = []

    for username in result:
        usernames.append(username[0])

    return usernames


def update_username(user, username):
    """
    A function which allows you to update a user's username.
    Accepts two arguments:
        - user: A discord.User object.
        - username: A string representing the new username.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'USERNAME',
              f'"{username}"', f'USER_ID == "{user.id}"')
    db.update('DISCORD_USERS', 'DISCRIMINATOR',
              f'"{user.discriminator}"', f'USER_ID == "{user.id}"')
    db.close()


def update_balance_by_id(id, amount):
    """
    A function which allows you to update the coin balance of a user by their ID.
    Accepts two arguments:
        - id: A string representing the user's ID.
        - amount: An integer representing the amount to add to the user's balance.
    Can be used to add or subtract coins. To subtract coins, pass a negative integer.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'COINS',
              f'COINS + {amount}', f'USER_ID == "{id}"')
    db.close()


def fetch_all_balances():
    """
    A function which allows you to fetch all user balances.
    Accepts no arguments.
    Returns user names and balances.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USERNAME, COINS, ACCOUNT_TYPE')
    db.close()
    return result


def fetch_all_winnings():
    """
    A function which allows you to fetch all user winnings.
    Accepts no arguments.
    Returns user names and winnings.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USERNAME, COINS_WON, ACCOUNT_TYPE')
    db.close()
    return result


def fetch_user_by_full_username(username, discriminator):
    """
    A function which allows you to fetch a user by their full username.
    Accepts two arguments:
        - username: A string representing the user's username.
        - discriminator: A string representing the user's discriminator.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', '*',
                       f'USERNAME == "{username}" AND DISCRIMINATOR == "{discriminator}"')
    db.close()
    return result[0][0]


def fetch_user_id_by_full_username(username, discriminator):
    """
    A function which allows you to fetch a user's ID by their full username.
    Accepts two arguments:
        - username: A string representing the user's username.
        - discriminator: A string representing the user's discriminator.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USER_ID',
                       f'USERNAME == "{username}" AND DISCRIMINATOR == "{discriminator}"')
    db.close()
    return result[0][0]


def fetch_winnings_by_id(id):
    """
    A function which allows you to fetch the coin winnings of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'COINS_WON',
                       f'USER_ID == "{id}"')
    db.close()
    return result[0][0]


def fetch_inventory_by_id(id) -> list:
    """
    A function which allows you to fetch the inventory of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'INVENTORY',
                       f'USER_ID == "{id}"')
    db.close()
    if not result[0][0]:
        return None

    return result[0][0]


def add_to_inventory_by_id(id, item):
    """
    A function which allows you to add an item to a user's inventory by their ID.
    Accepts two arguments:
        - item: A string representing the item to add to the user's inventory.
        - id: A string representing the user's ID.
    """
    item_id = item[0]
    current_inventory = fetch_inventory_by_id(id)
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    current_inventory.append(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{id}"')
    db.close()


def add_to_inventory_by_item_id(user_id, item_id):
    """
    A function which allows you to add an item to a user's inventory by their ID.
    Accepts two arguments:
        - item_id: A string representing the item ID to add to the user's inventory.
        - user_id: A string representing the user's ID.
    """
    current_inventory = fetch_inventory_by_id(user_id)
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    current_inventory.append(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{user_id}"')
    db.close()


def remove_from_inventory_by_id(id, item_id):
    """
    A function which allows you to remove an item from a user's inventory by their ID.
    Accepts two arguments:
        - item: A string representing the item to remove from the user's inventory.
        - id: A string representing the user's ID.
    """
    current_inventory = fetch_inventory_by_id(str(id))
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    current_inventory.remove(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{id}"')
    db.close()


def remove_x_items_from_inventory_by_id(user_id, item_id, number):
    """
    A function which allows you to remove x items from a user's inventory by their ID.
    Accepts three arguments:
        - item: A string representing the item to remove from the user's inventory.
        - id: A string representing the user's ID.
        - number: An integer representing the number of items to remove.

    """
    current_inventory = fetch_inventory_by_id(str(user_id))
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    for i in range(number):
        current_inventory.remove(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{user_id}"')
    db.close()


def add_x_items_to_inventory_by_id(user_id, item_id, number):
    """
    A function which allows you to add x items to a user's inventory by their ID.
    Accepts three arguments:
        - item: A string representing the item to add to the user's inventory.
        - id: A string representing the user's ID.
        - number: An integer representing the number of items to add.

    """
    current_inventory = fetch_inventory_by_id(str(user_id))
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    for i in range(number):
        current_inventory.append(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{user_id}"')
    db.close()


def add_to_inventory_by_item_id(user_id, item_id):
    """
    A function which allows you to add an item to a user's inventory by their ID.
    Accepts two arguments:
        - item_id: A string representing the item ID to add to the user's inventory.
        - user_id: A string representing the user's ID.
    """

    item_id = str(item_id)
    current_inventory = fetch_inventory_by_id(user_id)
    if not current_inventory:
        current_inventory = []
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    current_inventory.append(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{user_id}"')
    db.close()


def fetch_inventory_quantity_by_user_id(user_id, item_id):
    """
    A function which allows you to fetch the quantity of an item in a user's inventory by their ID.
    Accepts two arguments:
        - user_id: A string representing the user's ID.
        - item_id: A string representing the item's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'INVENTORY',
                       f'USER_ID == "{user_id}"')
    db.close()
    if not result[0][0]:
        return 0

    inventory = result[0][0].split(',')

    return inventory.count(item_id)


def use_item(user_id, item_id):
    """
    A function which allows you to use an item in a user's inventory by their ID.
    Accepts two arguments:
        - user_id: A string representing the user's ID.
        - item_id: A string representing the item's ID.
    """

    current_inventory = fetch_inventory_by_id(user_id)
    if not current_inventory:
        return
    elif len(current_inventory) == 1:
        current_inventory = [current_inventory]
    else:
        current_inventory = current_inventory.split(',')

    current_inventory.remove(item_id)

    new_inventory_str = ','.join(current_inventory)

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'INVENTORY',
              f'"{new_inventory_str}"', f'USER_ID == "{user_id}"')
    db.close()


def add_active_item(item_id, item_name, user_id, user_name, valid_until_epoch, uses_left, status):
    """
    A function which allows you to add an active item to the database.
    Accepts six arguments:
        - item_id: A string representing the item's ID.
        - item_name: A string representing the item's name.
        - user_id: A string representing the user's ID.
        - user_name: A string representing the user's name.
        - valid_until_epoch: An integer representing the epoch time when the item will expire.
        - uses_left: An integer representing the number of uses left for the item.
        - status: A string representing the status of the item.
    """

    db = DBManager(db_path)
    db.insert('ACTIVE_ITEMS', (item_id, item_name, user_id,
              user_name, valid_until_epoch, uses_left, status))
    db.close()


def new_transaction(trans_type, recip_username, recip_id, recip_newbal, sender_username, sender_id, sender_newbal, amount, note):
    """
    A function which allows you to create a new transaction.
    Accepts eight arguments:
        - type: A string representing the type of transaction.
        - recip_username: A string representing the recipient's username.
        - recip_id: A string representing the recipient's ID.
        - recip_newbal: An integer representing the recipient's new balance.
        - sender_username: A string representing the sender's username.
        - sender_id: A string representing the sender's ID.
        - sender_newbal: An integer representing the sender's new balance.
        - amount: An integer representing the amount of coins transferred.
        - note: A string representing the note attached to the transaction.
    """

    db = DBManager(db_path)
    db.insert('TRANSACTION_LOG',
              f'{int(time.time()) - 21600}, "{trans_type}", "{recip_username}", "{recip_id}", {recip_newbal}, "{sender_username}", "{sender_id}", {sender_newbal}, {amount}, "{note}"')
    db.close()


def new_gambling_entry(username: str, user_id: str, game_played: str, outcome: str, amount_won: int, bet_amount: int):
    """
    A function which allows you to add a new gambling entry to the database.
    Accepts six arguments:
        - username: A string representing the user's username.
        - user_id: A string representing the user's ID.
        - game_played: A string representing the game played.
        - outcome: A string representing the outcome of the game.
        - amount_won: An integer representing the amount won.
        - bet_amount: An integer representing the amount bet.
    """
    new_transaction('GAMBLING', username, user_id, fetch_balance_by_id(
        user_id), 'CASINO', '0', 0, amount_won, f'CASINO: {game_played} - {outcome}')

    db = DBManager(db_path)
    db.insert('GAMBLING_LOG',
              f'{int(time.time() - 21600)}, "{username}", "{user_id}", "{game_played}", "{outcome}", {amount_won}, {bet_amount}')
    db.close()


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        curr_frequency = List.count(i)
        if (curr_frequency > counter):
            counter = curr_frequency
            num = i

    return num


def fetch_favorite_game_by_id(id):
    """
    A function which allows you to fetch a user's favorite game by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'GAME_PLAYED',
                       f'USER_ID == "{id}"')
    db.close()

    if not result:
        return 'No Games Played'
    else:
        return (most_frequent(result)[0])


def fetch_number_of_games_played_by_id(id):
    """
    A function which allows you to fetch the number of games played by a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'GAME_PLAYED',
                       f'USER_ID == "{id}"')
    db.close()
    if not result:
        return 0

    return len(result)


def fetch_average_bet_by_id(id):
    """
    A function which allows you to fetch the average bet of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'BET_AMOUNT',
                       f'USER_ID == "{id}"')
    db.close()

    if not result:
        return 0

    return int(sum([bet[0] for bet in result]) / len(result))


def fetch_average_winnings_by_id(id):
    """
    A function which allows you to fetch the average win of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'AMOUNT_WON',
                       f'USER_ID == "{id}"')
    db.close()

    if not result:
        return 0

    return int(sum([win[0] for win in result]) / len(result))


def fetch_winrate_by_id(id):
    """
    A function which allows you to fetch the winrate of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'OUTCOME',
                       f'USER_ID == "{id}"')
    db.close()
    wins = 0

    if not result:
        return 0

    for game in result:
        if game[0] == 'WIN':
            wins += 1

    return (wins / len(result)) * 100


def fetch_biggest_win_by_id(id):
    """
    A function which allows you to fetch the biggest win of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'AMOUNT_WON',
                       f'USER_ID == "{id}"')
    db.close()

    if not result:
        return 0

    return max([win[0] for win in result])


def fetch_biggest_loss_by_id(id):
    """
    A function which allows you to fetch the biggest loss of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'AMOUNT_WON',
                       f'USER_ID == "{id}"')
    db.close()

    if not result:
        return 0

    return min([bet[0] for bet in result])


def fetch_highest_balance_by_id(user_id):
    """
    A function which allows you to fetch the highest balance of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', 'RECIPIENT_NEW_BALANCE',
                       f'RECIPIENT_ID == "{user_id}"')
    db.close()

    if not result:
        return 0

    return max([balance[0] for balance in result])


def fetch_last_receive_amount_by_id(user_id):
    """
    A function which allows you to fetch the last amount received by a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', '*',
                       f'RECIPIENT_ID == "{user_id}" AND TRANSACTION_AMOUNT > 0 ORDER BY TIMESTAMP DESC LIMIT 1')
    db.close()

    if not result:
        return {
            'amount': None,
            'type': None,
            'description': None
        }

    return {
        'amount': result[0][8],
        'type': result[0][1],
        'description': result[0][9]
    }


def fetch_user_transactions_by_id(user_id):
    """
    A function which allows you to fetch all transactions of a user by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', '*',
                       f'RECIPIENT_ID == "{user_id}" ORDER BY TIMESTAMP DESC')
    db.close()

    if not result:
        return []

    return result


def fetch_all_transactions():
    """
    A function which allows you to fetch all transactions.
    """

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', '*',
                       f'RECIPIENT_ID != "10" ORDER BY TIMESTAMP DESC')
    db.close()

    if not result:
        return []

    return result


def fetch_user_balance_by_day_by_id(user_id):
    """
    A function which allows you to fetch a user's daily balance by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', '*',
                       f'RECIPIENT_ID == "{user_id}" ORDER BY TIMESTAMP ASC')
    db.close()

    closing_balance_by_date = {}

    todays_date_central = (datetime.datetime.now() -
                           datetime.timedelta(hours=5)).strftime('%m-%d-%Y')

    for transaction in result:
        date = datetime.datetime.fromtimestamp(
            transaction[0]).strftime('%m-%d-%Y')
        closing_balance_by_date[date] = transaction[4]

    closing_balance_by_date[todays_date_central] = fetch_balance_by_id(user_id)

    balances_sorted = dict(sorted(closing_balance_by_date.items()))

    if not result:
        return {}

    return balances_sorted


def fetch_earnings_distribution_by_id(user_id):
    """
    A function which allows you to fetch a user's earnings distribution by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    distribution = {}

    db = DBManager(db_path)
    result = db.select('TRANSACTION_LOG', '*',
                       f'RECIPIENT_ID == "{user_id}"')
    db.close()

    if not result:
        return {}

    for transaction in result:
        if transaction[8] > 0:
            if transaction[1] in distribution:
                distribution[transaction[1]] += transaction[8]
            else:
                distribution[transaction[1]] = transaction[8]

    if 'GAMBLING' in distribution:
        distribution['GAMBLING'] = fetch_gambling_net_by_id(user_id)

    return distribution


def fetch_top_income_source_by_id(user_id):
    """
    A function which allows you to fetch a user's top income source by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    distribution = fetch_earnings_distribution_by_id(user_id)

    if not distribution:
        return None

    return max(distribution, key=distribution.get)


def fetch_gambling_net_by_day_by_id(user_id):
    """
    A function which allows you to fetch a user's daily gambling net by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', '*',
                       f'USER_ID == "{user_id}" ORDER BY TIMESTAMP ASC')
    db.close()

    net_by_date = {}

    todays_date_central = (datetime.datetime.now() -
                           datetime.timedelta(hours=5)).strftime('%m-%d-%Y')

    for transaction in result:
        date = datetime.datetime.fromtimestamp(
            transaction[0]).strftime('%m-%d-%Y')
        if date in net_by_date:
            net_by_date[date] += transaction[5]
        else:
            net_by_date[date] = transaction[5]

    if todays_date_central not in net_by_date:
        net_by_date[todays_date_central] = 0

    net_sorted = dict(sorted(net_by_date.items()))

    try:
        for date in daterange(datetime.datetime.fromtimestamp(result[0][0]), datetime.datetime.now()):
            date = date.strftime('%m-%d-%Y')
            if date not in net_sorted.keys():
                net_sorted[date] = 0

        net_sorted = dict(sorted(net_sorted.items()))
    except:
        return {}

    if not result:
        return {}

    return net_sorted


def fetch_gambling_net_by_id(user_id):
    """
    A function which allows you to fetch a user's gambling net by their ID.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', '*',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return 0

    return sum([transaction[5] for transaction in result])


def fetch_number_in_circulation_by_item_id(item_id):
    """
    A function which allows you to fetch the number of a specific item in circulation by its ID.
    Accepts one argument, a string representing the item's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'INVENTORY', 'INVENTORY IS NOT NULL')
    db.close()

    num_item = 0
    for inventory in result:
        if len(inventory[0]) == 1:
            if inventory[0] == str(item_id):
                num_item += 1
        else:
            if str(item_id) in inventory[0].split(','):
                num_item += inventory[0].split(',').count(str(item_id))

    return num_item


def parse_user_inventory(user_id):
    user_inventory = fetch_inventory_by_id(user_id)
    inventory_parsed = []

    try:
        for item_id in set(user_inventory.split(',')):
            item = item_db.fetch_item_by_id(item_id)
            inventory_parsed.append(
                {
                    'ITEM_ID': item[0],
                    'ITEM_NAME': item[1],
                    'ITEM_DESCRIPTION': item[2],
                    'ITEM_PRICE': f'{int(item[3]):,}',
                    'MUST_BE_ACTIVATED': item[9],
                    'ITEM_QUANTITY': user_inventory.split(',').count(item_id),
                    'ITEM_EMOJI': item[5]
                }
            )

        return inventory_parsed
    except:
        return []


def fetch_user_inventory_autocomplete(ctx: discord.AutocompleteContext):
    """
    Fetches user inventory for autocomplete.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'INVENTORY',
                       f'USER_ID == "{ctx.author.id}"')
    db.close()

    item_strings = [
        f'{item[5]} {item[1]}' for item in parse_user_inventory(ctx.author.id)]

    return [item for item in item_strings if re.sub(r'\W+', '', ctx.value).lower() in re.sub(r'\W+', '', item).lower()]


def fetch_server_games_played():
    """
    A function which allows you to fetch the number of games played on the server.
    """

    db = DBManager(db_path)
    result = db.select('GAMBLING_LOG', 'COUNT(*)')
    db.close()

    return result[0][0]


def fetch_joe_crypto_balance():
    """
    A function which allows you to fetch the balance of Joe.
    Used in the Floppy Disk puzzle.
    """

    db = DBManager(db_path)
    result = db.select('JOE', '*')
    db.close()

    return result[0][0]


def set_joe_crypto_balance(balance):
    """
    Set the value of the first row of the JOE table to the given balance.
    """

    db = DBManager(db_path)
    db.update('JOE', 'BALANCE', balance, 'BALANCE != 999999999')
    db.close()


def create_sell_listing(item_id, item_name, seller_id, seller_name, number_for_sale, buy_price, listing_desc):
    """
    A function which allows you to create a sell listing for an item.
    Accepts six arguments, a string representing the item's ID, a string representing the item's name,
    a string representing the seller's ID, a string representing the seller's name, an integer representing
    the number of items for sale, and an integer representing the buy price.
    """

    db = DBManager(db_path)
    db.insert('CUSTOM_LISTINGS',
              f'"{item_id}", "{item_name}", "{seller_id}", "{seller_name}", {number_for_sale}, {buy_price}, {int(time.time()) - 21600}, "{listing_desc}", "OPEN"')
    db.close()


def close_listing_by_timestamp(timestamp):
    """
    A function which allows you to close a listing by its timestamp.
    Accepts one argument, an integer representing the listing's timestamp.
    """

    db = DBManager(db_path)
    db.update('CUSTOM_LISTINGS', 'STATUS', f"'CLOSED'",
              f'LISTING_TIMESTAMP == {timestamp}')
    db.close()


def fetch_listings() -> list:
    """
    A function which allows you to fetch all listings.
    """

    db = DBManager(db_path)
    result = db.select('CUSTOM_LISTINGS', '*',
                       'LISTING_TIMESTAMP IS NOT NULL ORDER BY LISTING_TIMESTAMP DESC')
    db.close()

    listings = []

    for listing in result:

        listing_age = round(((time.time() - 21600) - listing[6]) / 60)
        listing_age_string = f'{listing_age} minutes ago'

        if listing_age > 60:
            listing_age = round(listing_age / 60)
            listing_age_string = f'{listing_age} hours ago'

        if listing_age > 24 and listing_age < 48:
            listing_age = round(listing_age / 24)
            listing_age_string = f'yeserday'

        if listing_age > 48:
            listing_age = round(listing_age / 24)
            listing_age_string = f'{listing_age} days ago'

        listings.append({
            'item_id': listing[0],
            'item_name': listing[1],
            'item_description': item_db.fetch_item_description_by_id(listing[0]),
            'seller_id': listing[2],
            'seller_name': listing[3],
            'number_for_sale': listing[4],
            'buy_price': listing[5],
            'timestamp': listing[6],
            'item_emoji': item_db.fetch_item_emoji_by_id(listing[0]),
            'listing_desc': listing[7],
            'listing_age': round(((time.time() - 21600) - listing[6]) / 60),
            'listing_age_string': listing_age_string,
            'status': listing[8]
        })

    return listings


def fetch_listing_by_timestamp(timestamp):
    """
    A function which allows you to fetch a listing by its timestamp.
    Accepts one argument, a string representing the listing's timestamp.
    """

    db = DBManager(db_path)
    result = db.select('CUSTOM_LISTINGS', '*',
                       f'LISTING_TIMESTAMP == "{timestamp}"')
    db.close()

    if not result:
        return {}

    return {
        'item_id': result[0][0],
        'item_name': result[0][1],
        'seller_id': result[0][2],
        'seller_name': result[0][3],
        'number_for_sale': result[0][4],
        'buy_price': result[0][5],
        'timestamp': result[0][6],
        'listing_desc': result[0][7],
        'status': result[0][8]
    }


def remove_listing_by_timestamp(timestamp):
    """
    A function which allows you to remove a listing by its timestamp.
    Accepts one argument, a string representing the listing's timestamp.
    """

    db = DBManager(db_path)
    db.update('CUSTOM_LISTINGS', 'STATUS', f"'REMOVED'",
              f'LISTING_TIMESTAMP == {timestamp}')
    db.close()


def fetch_tycoon_level_by_id(user_id):
    """
    A function which allows you to fetch a user's tycoon level.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'TYCOON_LEVEL',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return 0

    return result[0][0]


def set_tycoon_level_by_id(user_id, level):
    """
    A function which allows you to set a user's tycoon level.
    Accepts two arguments, a string representing the user's ID, and an integer representing the level.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'TYCOON_LEVEL',
              level, f'USER_ID == "{user_id}"')
    db.close()


def update_tycoon_level_by_id(user_id, amount):
    """
    A function which allows you to update a user's tycoon level.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to add.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS', 'TYCOON_LEVEL',
              f'TYCOON_LEVEL + {amount}', f'USER_ID == "{user_id}"')
    db.close()


def log_airdrop(timestamp, airdrop_content, grabbed_by_username=None, grabbed_by_id=None):
    """
    A function which allows you to log an airdrop.
    Accepts three arguments, a string representing the airdrop's content, a string representing the user's username,
    and a string representing the user's ID.
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO AIRDROPS (TIMESTAMP, AIRDROP_CONTENT, GRABBED_BY_USERNAME, GRABBED_BY_ID) VALUES (?, ?, ?, ?)',
              (timestamp, airdrop_content, grabbed_by_username, grabbed_by_id))
    conn.commit()
    conn.close()


def last_airdrop_seconds_ago():
    """
    A function which allows you to fetch the amount of seconds since the last airdrop.
    """

    db = DBManager(db_path)
    result = db.select('AIRDROPS', 'TIMESTAMP',
                       'TIMESTAMP IS NOT NULL ORDER BY TIMESTAMP DESC')
    db.close()

    if not result:
        return 0

    return round((time.time() - 21600) - result[0][0])


def grab_airdrop(user_id, username):
    """
    A function which allows you to grab the last airdrop.
    Accepts two arguments, a string representing the user's ID, and a string representing the user's username.
    """

    db = DBManager(db_path)
    db.update('AIRDROPS', 'GRABBED_BY_USERNAME',
              f'"{username}"', 'GRABBED_BY_USERNAME IS NULL')
    db.update('AIRDROPS', 'GRABBED_BY_ID',
              f'"{user_id}"', 'GRABBED_BY_ID IS NULL')
    db.close()


def airdrop_is_grabbed(timestamp):
    """
    A function which allows you to check if an airdrop has been grabbed.
    Accepts one argument, a string representing the airdrop's timestamp.
    """

    db = DBManager(db_path)
    result = db.select('AIRDROPS', 'GRABBED_BY_ID',
                       f'TIMESTAMP == {timestamp}')
    db.close()

    if not result:
        return False

    if result[0][0] == None:
        return False

    return True


def fetch_user_payout_amount_by_id(user_id):
    """
    A function which allows you to fetch a user's payout amount.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    tycoon_level = db.select(
        'DISCORD_USERS', 'TYCOON_LEVEL', f'USER_ID == "{user_id}"')[0][0]
    db.close()

    if tycoon_level == 0:
        return 0

    return item_db.fetch_payout_by_id(tycoon_level)


def fetch_user_ids_by_minimum_tycoon_level(minimum_tycoon_level):
    """
    A function which allows you to fetch a list of user IDs by a minimum tycoon level.
    Accepts one argument, an integer representing the minimum tycoon level.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USER_ID',
                       f'TYCOON_LEVEL >= {minimum_tycoon_level}')
    db.close()

    if not result:
        return []

    return [r[0] for r in result]


def has_tycoon_level_by_id(tycoon_item_name, user_id):
    """
    A function which allows you to check if a user has a tycoon level.
    Accepts two arguments, a string representing the tycoon item name, and a string representing the user's ID.
    """

    db = DBManager(db_path)
    tycoon_level = db.select(
        'DISCORD_USERS', 'TYCOON_LEVEL', f'USER_ID == "{user_id}"')[0][0]
    db.close()

    if tycoon_level == 0:
        return False

    if tycoon_level >= item_db.fetch_tycoon_level_by_name(tycoon_item_name):
        return True


def fetch_valorant_username_by_id(user_id):
    """
    A function which allows you to fetch a user's Valorant username.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'VALORANT_USER',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return None

    return {
        'username': result[0][0].split('#')[0],
        'tag': result[0][0].split('#')[1]
    }


def fetch_valorant_players():
    """
    A function which allows you to fetch a list of Valorant players.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'VALORANT_USER',
                       'VALORANT_USER IS NOT NULL')
    db.close()

    if not result:
        return []

    return [r[0] for r in result]


def new_valorant_match(match: dict):
    """
    A function which allows you to log a new Valorant match.
    Accepts one argument, a dictionary representing the match.
    """
    # db = DBManager(db_path)
    # db.insert('VALORANT_MATCHES',
    #           f"'{match['match_id']}', '{match['match_timestamp']}', '{match['match_date']}', '{match['puuid']}', {match['username']}, '{match['tag']}', '{match['character']}', {match['rank_num']}, '{match['rank']}', '{match['gamemode']}', '{match['map']}', {match['kills']}, {match['deaths']}, {match['assists']}, {match['bodyshots']}, {match['headshots']}, {match['legshots']}, {match['credits_spent']}, {match['damage_dealt']}, {match['damage_taken']}")
    # db.close()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"INSERT INTO VALORANT_MATCHES VALUES ('{match['match_id']}', '{match['match_timestamp']}', '{match['match_date']}', '{match['puuid']}', '{match['username']}', '{match['tag']}', '{match['character']}', {match['rank_num']}, '{match['rank']}', '{match['gamemode']}', '{match['map']}', {match['kills']}, {match['deaths']}, {match['assists']}, {match['bodyshots']}, {match['headshots']}, {match['legshots']}, {match['credits_spent']}, {match['damage_dealt']}, {match['damage_taken']})")
    conn.commit()
    conn.close()


def match_already_logged(match: dict):
    """
    A function which allows you to check if a match has already been logged.
    Accepts one argument, a dictionary representing the match.
    """

    db = DBManager(db_path)
    result = db.select('VALORANT_MATCHES', 'MATCH_ID',
                       f"MATCH_ID == '{match['match_id']}' AND PUUID == '{match['puuid']}'")
    db.close()

    if not result:
        return False

    return True


def fetch_discord_user_id_by_valorant_username(username: str, tag: str):
    """
    A function which allows you to fetch a user's Discord ID by their Valorant username.
    Accepts two arguments, a string representing the user's Valorant username, and a string representing the user's Valorant tag.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USER_ID',
                       f"VALORANT_USER == '{username}#{tag}'")
    db.close()

    if not result:
        return None

    return result[0][0]


def fetch_royale_tag_by_id(user_id):
    """
    A function which allows you to fetch a user's Royale username.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'ROYALE_TAG',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return None

    return result[0][0]


def fetch_royale_players():
    """
    A function which allows you to fetch a list of Royale players.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'ROYALE_TAG', 'ROYALE_TAG IS NOT NULL')
    db.close()

    if not result:
        return []

    return [r[0] for r in result]


def new_royale_match(match: dict):
    """
    A function which allows you to log a new Royale match.
    Accepts one argument, a dictionary representing the match.
    """

    db = DBManager(db_path)
    db.insert('ROYALE_MATCHES',
              f'"{match["player_tag"]}", "{match["match_id"]}", "{match["type"]}", "{match["gamemode"]}", "{match["is_ladder_tournament"]}", "{match["team"]}", "{match["opponent"]}", {match["crowns"]}, "{match["result"]}"')
    db.close()


def royale_match_already_logged(match: dict):
    """
    A function which allows you to check if a Royale match has already been logged.
    Accepts one argument, a dictionary representing the match.
    """

    db = DBManager(db_path)
    result = db.select('ROYALE_MATCHES', 'MATCH_ID',
                       f"MATCH_ID == '{match['match_id']}' AND PLAYER_TAG == '{match['player_tag']}'")
    db.close()

    if not result:
        return False

    return True


def fetch_discord_user_id_by_royale_tag(tag: str):
    """
    A function which allows you to fetch a user's Discord ID by their Royale username.
    Accepts one argument, a string representing the user's Royale tag.
    """

    if tag.startswith('#'):
        tag = tag[1:]

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'USER_ID', f"ROYALE_TAG == '{tag}'")
    db.close()

    if not result:
        return None

    return result[0][0]


def fetch_bank_balance_by_id(user_id):
    """
    A function which allows you to fetch a user's bank balance.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'BANK_BALANCE',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return None

    return result[0][0]


def fetch_interest_earned_by_id(user_id):
    """
    A function which allows you to fetch a user's interest earned.
    Accepts one argument, a string representing the user's ID.
    """

    db = DBManager(db_path)
    result = db.select('DISCORD_USERS', 'INTEREST_EARNED',
                       f'USER_ID == "{user_id}"')
    db.close()

    if not result:
        return None

    return result[0][0]


def update_bank_balance_by_id(user_id, amount):
    """
    A function which allows you to update a user's bank balance.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to add or remove from the user's balance.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'BANK_BALANCE = BANK_BALANCE + {amount}', f'USER_ID == "{user_id}"')
    db.close()


def update_interest_earned_by_id(user_id, amount):
    """
    A function which allows you to update a user's interest earned.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to add or remove from the user's interest earned.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'INTEREST_EARNED = INTEREST_EARNED + {amount}', f'USER_ID == "{user_id}"')
    db.close()


def set_bank_balance_by_id(user_id, amount):
    """
    A function which allows you to set a user's bank balance.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to set the user's balance to.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'BANK_BALANCE = {amount}', f'USER_ID == "{user_id}"')
    db.close()


def set_interest_earned_by_id(user_id, amount):
    """
    A function which allows you to set a user's interest earned.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to set the user's interest earned to.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'INTEREST_EARNED = {amount}', f'USER_ID == "{user_id}"')
    db.close()


def user_deposit(user_id, amount):
    """
    A function that is called when a user deposits money from their regular balance to their Bank Account.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to deposit.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'BANK_BALANCE = BANK_BALANCE + {amount}, BALANCE = BALANCE - {amount}', f'USER_ID == "{user_id}"')
    db.close()


def user_withdraw(user_id, amount):
    """
    A function that is called when a user withdraws money from their Bank Account to their regular balance.
    Accepts two arguments, a string representing the user's ID, and an integer representing the amount to withdraw.
    """

    db = DBManager(db_path)
    db.update('DISCORD_USERS',
              f'BALANCE = BALANCE + {amount}, BANK_BALANCE = BANK_BALANCE - {amount}', f'USER_ID == "{user_id}"')
    db.close()
