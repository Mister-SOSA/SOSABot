"""
This is just a big disaster. I am in the process of rewriting this entire thing.
"""

from flask_socketio import SocketIO
import pytz
import logging
import datetime
from rich import print
import db_manager
import math
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import item_db_manager as item_db
import sys
import os


sys.path.insert(0, '/home/ubuntu/discord_bot')


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find("/update_balance") == -1


log = logging.getLogger('werkzeug')
log.addFilter(HealthCheckFilter())

app = Flask(__name__)
app.config["SECRET_KEY"] = 'key'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
socketio = SocketIO(app)

app.config["DISCORD_CLIENT_ID"] = 793672883716358225
app.config["DISCORD_CLIENT_SECRET"] = "secret"
app.config["DISCORD_REDIRECT_URI"] = "http://URL.NET/callback/"
app.config["DISCORD_BOT_URL.NET"] = "URL.NET"

shop_investor_level = item_db.fetch_tycoon_level_by_name('Shop Investor')

discord = DiscordOAuth2Session(app)

rarity_colors = {
    "Common": "#3a3a3c",
    "Uncommon": "#3fd158",
    "Rare": "#0c84ff",
    "Epic": "#bf5af2",
    "Legendary": "#ffd608",
    "Elite": "#ffffff"
}

rarity_ranks = {
    "Common": 0,
    "Uncommon": 1,
    "Rare": 2,
    "Epic": 3,
    "Legendary": 4,
    "Elite": 5
}


def log_login(user):
    with open('login_log.txt', 'a') as file:
        file.write(
            f'{user.name}#{user.discriminator} logged in at {datetime.datetime.now(pytz.timezone("US/Central")).strftime("%m-%d-%Y %I:%M:%S%p")}\n')


def parse_epoch_to_datetime(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%m-%d-%Y %I:%M:%S%p')


def parse_user_inventory(user_id):
    user_inventory = db_manager.fetch_inventory_by_id(user_id)
    inventory_parsed = []
    try:
        for item_id in set(user_inventory.split(',')):

            inventory_parsed.append(
                {
                    'ITEM_ID': item_db.fetch_item_by_id(item_id)[0],
                    'ITEM_NAME': item_db.fetch_item_by_id(item_id)[1],
                    'ITEM_DESCRIPTION': item_db.fetch_item_by_id(item_id)[2],
                    'ITEM_PRICE': f'{int(item_db.fetch_item_by_id(item_id)[3]):,}',
                    'MUST_BE_ACTIVATED': item_db.fetch_item_by_id(item_id)[9],
                    'ITEM_QUANTITY': user_inventory.split(',').count(item_id),
                    'ITEM_EMOJI': item_db.fetch_item_by_id(item_id)[5],
                    'ITEM_RARITY': item_db.fetch_item_by_id(item_id)[12],
                    'BACKGROUND_COLOR': rarity_colors[item_db.fetch_item_by_id(item_id)[12]]
                }
            )

        inventory_sorted_by_rarity = sorted(
            inventory_parsed, key=lambda k: rarity_ranks[k['ITEM_RARITY']], reverse=True)

        return inventory_sorted_by_rarity
    except:
        return []


def parse_transaction_list(transactions):
    transactions_parsed = []
    for transaction in transactions:
        transactions_parsed.append({
            'TIMESTAMP': transaction[0],
            'TRANSACTION_TYPE': transaction[1],
            'RECIPIENT_USERNAME': transaction[2],
            'RECIPIENT_ID': transaction[3],
            'RECIPIENT_NEW_BALACE': transaction[4],
            'SENDER_USERNAME': transaction[5],
            'SENDER_ID': transaction[6],
            'SENDER_NEW_BALANCE': transaction[7],
            'AMOUNT': transaction[8],
            'NOTE': transaction[9],
            'TIMESTAMP_PARSED': parse_epoch_to_datetime(transaction[0])
        })

    return transactions_parsed


@app.route("/update_balance", methods=["POST"])
def update_balance():
    user = discord.fetch_user()
    return str(db_manager.fetch_balance_by_id(user.id))


@app.route("/devtools", methods=["GET"])
@requires_authorization
def devtools_page():
    user = discord.fetch_user()
    if user.id != 268974144593461248:
        return redirect(url_for('me'))
    return render_template('devtools.html', user=user)


@app.route("/inventorymanagement", methods=["GET"])
@requires_authorization
def inventory_management_page():
    user = discord.fetch_user()
    if user.id != 268974144593461248:
        return redirect(url_for('me'))
    return render_template('inventory_management.html', user=user)


@app.route("/inventorymanagement/<query>", methods=["GET"])
@requires_authorization
def inventory_management_page_user(query):
    user = discord.fetch_user()
    if user.id != 268974144593461248:
        return redirect(url_for('me'))

    user_inventory = parse_user_inventory(query)

    return render_template('inventory_management.html', user=user, inventory=user_inventory)


@app.route("/transactionlog", methods=["GET"])
@requires_authorization
def transaction_log():
    user = discord.fetch_user()
    if user.id != 268974144593461248:
        return redirect(url_for('me'))
    transactions = parse_transaction_list(db_manager.fetch_all_transactions())
    return render_template('transaction_log.html', user=user, transactions=transactions)


def parse_shop_items():
    shop_items = {}

    items = item_db.fetch_all_items()

    for item in items:
        shop_items[item[0]] = {
            'ITEM_ID': item[0],
            'ITEM_NAME': item[1],
            'ITEM_DESCRIPTION': item[2],
            'ITEM_PRICE': f'{int(item[3]):,}',
            'ITEM_QUANTITY': item[4],
            'ITEM_EMOJI': item[5],
            'ITEM_STATUS': item[6],
            'MAX_ALLOWED': item[7],
            'BURNOUT_SECONDS': item[8],
            'MUST_BE_ACTIVATED': item[9],
            'BUYABLE': item[10],
            'EMOJI_URL': item[11],
            'ITEM_RARITY': item[12],
            'LOOTABLE': item[13]
        }

    shop_items = {k: v for k, v in sorted(shop_items.items(
    ), key=lambda item: rarity_ranks[item[1]['ITEM_RARITY']], reverse=True)}

    return shop_items


@app.route("/login/")
def login():
    return discord.create_session()


@app.route("/christmas/")
def christmas():
    return render_template('christmas_tree.html')


@app.route("/callback/")
def callback():
    discord.callback()
    user = discord.fetch_user()
    log_login(user)
    print(
        f'[bold green]User {user.name}#{user.discriminator} has logged in.[/bold green]')
    try:
        if session['DESTINATION']:
            return redirect(session['DESTINATION'])
    except:
        return redirect('/me')


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/me/")
@requires_authorization
def me():
    user = discord.fetch_user()
    user_balance = db_manager.fetch_balance_by_id(user.id)
    user_transaction_list = parse_transaction_list(
        db_manager.fetch_user_transactions_by_id(user.id))
    user_inventory = parse_user_inventory(user.id)
    user_daily_balance = db_manager.fetch_user_balance_by_day_by_id(user.id)
    user_earnings_distribution = db_manager.fetch_earnings_distribution_by_id(
        user.id)
    user_net_gambling_by_day = db_manager.fetch_gambling_net_by_day_by_id(
        user.id)
    user_daily_payout = db_manager.fetch_user_payout_amount_by_id(user.id)

    gambling_stats = {
        'net_winnings': db_manager.fetch_winnings_by_id(user.id),
        'highest_balance': f'{db_manager.fetch_highest_balance_by_id(user.id):,}',
        'favorite_game': f'{db_manager.fetch_favorite_game_by_id(user.id)}',
        'games_played': f'{db_manager.fetch_number_of_games_played_by_id(user.id):,}',
        'average_bet': f'{db_manager.fetch_average_bet_by_id(user.id):,}',
        'average_winnings': db_manager.fetch_average_winnings_by_id(user.id),
        'winrate': f'{db_manager.fetch_winrate_by_id(user.id):.2f}%',
        'biggest_win': f'{db_manager.fetch_biggest_win_by_id(user.id):,}',
        'biggest_loss': f'{db_manager.fetch_biggest_loss_by_id(user.id):,}'
    }

    return render_template("me.html", user=user, balance=f'{user_balance:,}', gambling_stats=gambling_stats, transaction_list=user_transaction_list, inventory=user_inventory, balance_history=user_daily_balance, earnings_distribution=user_earnings_distribution, net_gambling_by_day=user_net_gambling_by_day, daily_payout=user_daily_payout)


@app.route('/wheelspin', methods=['GET', 'POST'])
@requires_authorization
def wheelspin_page():
    return render_template('wheelspin.html', user=discord.fetch_user())


@app.route('/')
def home_page():
    try:
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)
        return render_template('index.html', user=user, balance=f'{user_balance:,}')
    except:
        return render_template('./index.html')


@app.route('/shop', methods=['GET', 'POST'])
def set_shop_session():
    session['DESTINATION'] = '/shop'
    return shop_page()


@requires_authorization
def shop_page():
    try:
        user = discord.fetch_user()
        shop_items = parse_shop_items()
        user_balance = db_manager.fetch_balance_by_id(user.id)

        if db_manager.fetch_tycoon_level_by_id(user.id) >= 6:
            for item in shop_items:
                shop_items[item]['ITEM_PRICE'] = math.ceil(
                    int(item_db.fetch_item_price(shop_items[item]['ITEM_ID'])) * 0.9)

        if request.method == 'POST':
            return shop_items

        return render_template('./shop.html', user=user, balance=f'{user_balance:,}', shop_items=shop_items, tycoon_level=db_manager.fetch_tycoon_level_by_id(user.id))
    except:
        return render_template('./shop.html', shop_items=parse_shop_items())


@app.route('/listings')
def set_listings_session():
    session['DESTINATION'] = '/listings'
    return listings_page()


@app.route('/listings')
@requires_authorization
def listings_page():
    try:
        user = discord.fetch_user()
        listings = db_manager.fetch_listings()
        user_balance = db_manager.fetch_balance_by_id(user.id)
        return render_template('./listings.html', user=user, balance=f'{user_balance:,}', listings=listings)
    except:
        return render_template('./listings.html', listings=db_manager.fetch_listings())


@app.route('/invest')
@requires_authorization
def invest_page():
    try:
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)
        return render_template('./invest.html', user=user, balance=f'{user_balance:,}')
    except:
        return render_template('./invest.html')


@app.route('/terminal')
def set_terminal_session():
    session['DESTINATION'] = '/terminal'
    return terminal_page()


@requires_authorization
def terminal_page():
    try:
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)
    except:
        return redirect('/login')

    floppy_quantity = db_manager.fetch_inventory_quantity_by_user_id(
        user.id, '14')

    btc_amount = db_manager.fetch_joe_crypto_balance()

    if floppy_quantity > 0:
        floppy_status = 'ACTIVE'
    else:
        floppy_status = 'INACTIVE'

    return render_template('./terminal.html', user=user, floppy_status=floppy_status, btc_amount=btc_amount)


@app.route('/terminal/withdraw', methods=['POST'])
@requires_authorization
def terminal_withdraw():
    try:
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)
    except:
        return redirect('/login')

    floppy_quantity = db_manager.fetch_inventory_quantity_by_user_id(
        user.id, '14')
    btc_amount = db_manager.fetch_joe_crypto_balance()

    if floppy_quantity == 0:
        return Response('NO_FLOPPY', status=200, mimetype='text/plain')

    else:
        db_manager.set_joe_crypto_balance(0)
        db_manager.update_balance_by_id(user.id, btc_amount)
        db_manager.use_item(user.id, '14')
        db_manager.new_transaction(trans_type='BITCOIN TRANSFER',
                                   recip_username=user.name,
                                   recip_id=user.id,
                                   recip_newbal=db_manager.fetch_balance_by_id(
                                       user.id),
                                   sender_username='DR. JOE',
                                   sender_id=0,
                                   sender_newbal=0,
                                   amount=btc_amount,
                                   note=f'BITCOIN TRANSFER FROM DR. JOE OF {btc_amount} COINS')

        return Response('SUCCESS', status=200, mimetype='text/plain')


@app.route('/stats')
def stats_page():
    users = db_manager.fetch_normal_users()
    # sort users by balance
    users = sorted(users, key=lambda k: k[4], reverse=True)
    for user in users:
        users[users.index(user)] = list(user)

    for user in users:
        user.append(db_manager.fetch_favorite_game_by_id(user[1]))
        user.append(db_manager.fetch_top_income_source_by_id(user[1]))
        print(user)

    print(users)
    try:
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)
        return render_template('stats.html', user=user, balance=f'{user_balance:,}', users=users)
    except:
        return render_template('./stats.html', users=users)


@app.route('/shop/transaction', methods=['POST'])
@requires_authorization
def transaction():
    if request.method == 'POST':
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)

        if request.headers.get('item_id'):
            item = item_db.fetch_item_by_id(request.headers.get('item_id'))
            if db_manager.fetch_tycoon_level_by_id(user.id) >= 6:
                item_price = math.ceil(int(item[3]) * 0.9)
            else:
                item_price = int(item[3])
            quantity = int(request.headers.get('quantity'))

            if int(user_balance) >= int(item_price) * int(quantity):
                quantity_owned_by_user = db_manager.fetch_inventory_quantity_by_user_id(
                    user.id, item[0])
                maximum_quantity_allowed = item[7]
                store_quantity = item[4]

                if quantity_owned_by_user + quantity >= maximum_quantity_allowed:
                    return Response(
                        response='FAILED',
                        status=302,
                        headers={
                            'user_balance': f'{db_manager.fetch_balance_by_id(user.id):,}',
                            'item_name': item[1],
                            'transaction': 'MAX_QUANTITY',
                            'new_quantity': store_quantity
                        }
                    )

                if quantity > store_quantity:
                    return Response(
                        response='FAILED',
                        status=302,
                        headers={
                            'user_balance': f'{db_manager.fetch_balance_by_id(user.id):,}',
                            'item_name': item[1],
                            'transaction': 'NOT_ENOUGH_IN_STORE',
                            'new_quantity': store_quantity
                        }
                    )

                db_manager.update_balance_by_id(
                    user.id, -int(item_price) * int(quantity))
                db_manager.add_x_items_to_inventory_by_id(
                    user.id, item[0], quantity)
                store_quantity = store_quantity - quantity
                item_db.reduce_item_quantity_by_id(item[0], quantity)
                db_manager.new_transaction(trans_type='PURCHASE',
                                           recip_username=user.name,
                                           recip_id=user.id,
                                           recip_newbal=db_manager.fetch_balance_by_id(
                                               user.id),
                                           sender_username='SHOP',
                                           sender_id=0,
                                           sender_newbal=0,
                                           amount=-int(item_price) *
                                           int(quantity),
                                           note=f'PURCHASED {quantity}x {item[1]} from the SHOP')

                for investor_id in db_manager.fetch_user_ids_by_minimum_tycoon_level(shop_investor_level):
                    if investor_id == user.id:
                        continue
                    royalty = math.ceil((item_price * quantity) * 0.05)
                    db_manager.update_balance_by_id(investor_id, royalty)
                    db_manager.new_transaction(
                        'SHOP ROYALTY',
                        db_manager.fetch_username_by_id(investor_id),
                        investor_id,
                        db_manager.fetch_balance_by_id(investor_id),
                        'TYCOON',
                        '0',
                        0,
                        royalty,
                        f'Shop Royalty of {royalty} from {user.name}\'s purchase.')

                return Response(
                    response='SUCCESS',
                    status=302,
                    headers={
                        'user_balance': f'{db_manager.fetch_balance_by_id(user.id):,}',
                        'item_name': item[1],
                        'transaction': 'SUCCESS',
                        'new_quantity': store_quantity
                    })

            else:
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'user_balance': f'{db_manager.fetch_balance_by_id(user.id):,}',
                        'item_name': item[1],
                        'transaction': 'INSUFFICIENT_FUNDS'
                    })

    return render_template('./shop.html', user=user, balance=f'{user_balance:,}', transaction='None')


@app.route('/listings/transaction', methods=['POST'])
@requires_authorization
def listings_transaction():
    if request.method == 'POST':
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)

        if request.headers.get('timestamp'):
            listing = db_manager.fetch_listing_by_timestamp(
                request.headers.get('timestamp'))
            item = item_db.fetch_item_by_id(listing['item_id'])
            item_price = listing['buy_price']
            if int(user_balance) >= int(listing['buy_price']):
                quantity_owned_by_user = db_manager.fetch_inventory_quantity_by_user_id(
                    user.id, item[0])
                maximum_quantity_allowed = item[7]

                if quantity_owned_by_user + int(listing['number_for_sale']) > maximum_quantity_allowed:
                    return Response(
                        response='FAILED',
                        status=302,
                        headers={
                            'transaction': 'MAX_QUANTITY',
                        }
                    )

                db_manager.update_balance_by_id(user.id, -int(item_price))
                db_manager.update_balance_by_id(
                    listing['seller_id'], int(item_price))
                for i in range(int(listing['number_for_sale'])):
                    db_manager.add_to_inventory_by_id(user.id, item)

                db_manager.new_transaction(trans_type='PURCHASE',
                                           recip_username=user.name,
                                           recip_id=user.id,
                                           recip_newbal=db_manager.fetch_balance_by_id(
                                               user.id),
                                           sender_username=listing['seller_name'],
                                           sender_id=listing['seller_id'],
                                           sender_newbal=db_manager.fetch_balance_by_id(
                                               listing['seller_id']),
                                           amount=-int(item_price),
                                           note=f'PURCHASED {listing["number_for_sale"]}x {item[1]} FROM {listing["seller_name"]} for {item_price} coins.')

                db_manager.new_transaction(trans_type='SALE',
                                           recip_username=listing['seller_name'],
                                           recip_id=listing['seller_id'],
                                           recip_newbal=db_manager.fetch_balance_by_id(
                                               listing['seller_id']),
                                           sender_username=user.name,
                                           sender_id=user.id,
                                           sender_newbal=db_manager.fetch_balance_by_id(
                                               user.id),
                                           amount=int(item_price),
                                           note=f'SOLD {listing["number_for_sale"]}x {item[1]} TO {user.name} for {item_price} coins.')

                db_manager.close_listing_by_timestamp(
                    request.headers.get('timestamp'))
                discord.bot_request(f'/channels/734646852154163214/messages', 'POST', json={
                    'embed': {
                        'title': f'💰 Listing Closed',
                        'description': f'Listing for {listing["number_for_sale"]}x **{item[1]}** has been closed.',
                        'color': 0x00ff00,
                        'fields': [
                            {
                                'name': '__Seller__',
                                'value': f'<@{listing["seller_id"]}>',
                                'inline': True
                            },
                            {
                                'name': '__Buyer__',
                                'value': f'<@{user.id}>',
                                'inline': True
                            },
                            {
                                'name': '__Price__',
                                'value': f'<:monkeycoin:1038242128045809674> {item_price}'
                            }
                        ]
                    }
                })
                return Response(
                    response='SUCCESS',
                    status=302,
                    headers={
                        'transaction': 'SUCCESS',
                    })

            else:
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'transaction': 'INSUFFICIENT_FUNDS'
                    })

    return render_template('./listings.html', user=user, balance=f'{user_balance:,}', transaction='None')


@app.route('/listings/delete', methods=['POST'])
@requires_authorization
def listings_delete():
    if request.method == 'POST':
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)

        if request.headers.get('timestamp'):
            listing = db_manager.fetch_listing_by_timestamp(
                request.headers.get('timestamp'))

            if listing['seller_id'] == user.id and listing['status'] == 'OPEN':
                db_manager.remove_listing_by_timestamp(
                    request.headers.get('timestamp'))
                return Response(
                    response='SUCCESS',
                    status=302,
                    headers={
                        'transaction': 'SUCCESS',
                    })

            elif listing['seller_id'] != user.id:
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'transaction': 'NOT_OWNER'
                    })

            elif listing['status'] != 'OPEN':
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'transaction': 'ALREADY_CLOSED'
                    })

    return render_template('./listings.html', user=user, balance=f'{user_balance:,}', transaction='None')


@app.route('/tycoon', methods=['GET'])
def set_tycoon_session():
    session['DESTINATION'] = '/tycoon'
    return tycoon_page()


@requires_authorization
def tycoon_page():
    user = discord.fetch_user()
    user_balance = db_manager.fetch_balance_by_id(user.id)
    tycoon_items = item_db.fetch_tycoon_items()
    tycoon_entitlements = list(
        range(0, db_manager.fetch_tycoon_level_by_id(user.id) + 1))
    print(tycoon_entitlements)
    if tycoon_entitlements == []:
        tycoon_entitlements = [0]

    return render_template('./tycoon.html', user=user, balance=f'{user_balance:,}', tycoon_items=tycoon_items, tycoon_entitlements=tycoon_entitlements)


@app.route('/tycoon/transaction', methods=['POST'])
@requires_authorization
def tycoon_transaction():
    if request.method == 'POST':
        user = discord.fetch_user()
        user_balance = db_manager.fetch_balance_by_id(user.id)

        if request.headers.get('item_id'):
            item = item_db.fetch_tycoon_item_by_id(
                request.headers.get('item_id'))
            item_id = item[0]
            item_name = item[1]
            new_payout_amount = item[3]
            item_price = item[5]

            if user_balance >= item_price and db_manager.fetch_tycoon_level_by_id(user.id) + 1 == int(item_id):
                db_manager.set_tycoon_level_by_id(user.id, item_id)
                db_manager.update_balance_by_id(user.id, -item_price)
                db_manager.new_transaction(
                    'TYCOON UPGRADE',
                    user.name,
                    user.id,
                    db_manager.fetch_balance_by_id(user.id),
                    'TYCOON SHOP',
                    '0',
                    0,
                    -item_price,
                    f'PURCHASED {item_name} FROM TYCOON SHOP for {item_price} coins.'
                )

                return Response(
                    response='SUCCESS',
                    status=302,
                    headers={
                        'transaction': 'SUCCESS',
                        'message': f'You have successfully purchased {item_name} for {item_price} coins.'
                    })

            if user_balance < item_price:
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'transaction': 'FAILED',
                        'message': f'You do not have enough coins to purchase {item_name}.'
                    })

            if db_manager.fetch_tycoon_level_by_id(user.id) + 1 != int(item_id):
                return Response(
                    response='FAILED',
                    status=302,
                    headers={
                        'transaction': 'FAILED',
                        'message': f'You must purchase Tycoon items in a linear fashion.'
                    })


@app.route('/api/fetch_coin_balance/<user_id>', methods=['GET'])
def fetch_coin_balance(user_id):
    return f'{db_manager.fetch_balance_by_id(user_id):,}'


@app.route('/items', methods=['GET'])
def set_items_session():
    session['DESTINATION'] = '/items'
    return items_page()


@requires_authorization
def items_page():
    user = discord.fetch_user()
    user_balance = db_manager.fetch_balance_by_id(user.id)
    items = item_db.fetch_all_items_parsed()
    return render_template('./items.html', user=user, balance=f'{user_balance:,}', items=items)


@socketio.on('message')
def handle_message(data):
    print(f'received message: {data}')
    socketio.emit('message', data)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
