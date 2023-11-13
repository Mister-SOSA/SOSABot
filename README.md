# SOSABot
A Discord bot written using PyCord. Features moderation, economy, and more.
> :warning: An abundance of this code is written specifically for my use case. Many of the features are specific to my guild and database schema. There wasn't initially a plan to publish this project, so you'll observe a lack of abstraction in many places. This repo is mostly a showcase of what is possible with the Discord API. Feel free to pull any features that you want to use in your own bot.

# 💫 Features
## Application Commands
This bot is up to standard with the newest features of the Discord API (utilizes Views, Discord UI, Context Commands, etc.)
Commands are invoked with `/<command>`, or with context menus where applicable.

## 🛡 Moderation
Let's get the boring stuff out of the way. The bot has application commands for all the usual moderation tasks, like kicking, banning, etc. It also features a few additional administration commands pertaining to the economy system (more on that later).

## 💰 Economy
Both the bot and the Flask application sustain the made up pseudo-economy based on "Monkeycoin."
The Monkeycoin is the currency used to play gambling games, purchase items, pay other users, and more.
The theme came from a Dall-E generated image of King Kong throwing cash in the air.

### 💵 Payments
Users can pay each other by invoking the `/pay` command. The command will perform the appropriate checks to ensure that the transaction is valid, and will manipulate the database accordingly.

![Pay Command Example](https://cdn.discordapp.com/attachments/929674655801958400/1052623781178376192/image.png)

Users may also request money from other users by invoking the `/request` command.

### 🎲 Gambling
As with any good economy, there must be some form of gambling. The bot features several casino games such as
Crash, Blackjack, Horse Racing, and more. To initiate a gamble, a user can simply invoke `/gamble`. This command, among others, utilizes [discord.Option.autocomplete](https://docs.pycord.dev/en/stable/api/application_commands.html#discord.Option.autocomplete) to populate a list of valid games.

![Autocomplete Example](https://cdn.discordapp.com/attachments/929674655801958400/1052625167152586762/image.png)

#### 🖼 Screenshots

![Horse Racing](https://cdn.discordapp.com/attachments/929674655801958400/1052625597286858752/image.png)

*Example of a Horse Race, made with updating embeds and `Racehorse` objects*

![Blackjack](https://cdn.discordapp.com/attachments/929674655801958400/1052625857212059668/image.png)

*Example of Blackjack, made using updating embeds and PIL*

![Crash](https://cdn.discordapp.com/attachments/929674655801958400/1052626846585454693/image.png)

*Example of Crash, made using updating embeds*

### 🪙 Command Tolls

There are some commands that shouldn't be spammed all the time. For instance, I have written a command which connects to OpenAI's Dall-E to generate images based on text. This API costs me money, so to prevent users from overdoing it, they must spend 100 of their hard earned Monkeycoins to use the command.

![Command Toll Example](https://cdn.discordapp.com/attachments/929674655801958400/1052627981228576891/image.png)

This obviously does not negate the cost to me, but it certainly alleviates some of it.
This can be applied to any command.

### 🔀 Item Exchange

For any economy to work, there must be purchasable items to reinforce the value of the currency.
I have created an assortment of items that can be purchased, sold, traded, and crafted. Many of the items perform some sort of function, while others are simply ingredients for larger items or are sellable for profit.
For instance, the `I.C.B.M.` costs 100,000 Monkeycoins, and can be fired at another user to instantly destroy 50% of their Monkeycoin balance. This adds incentive to earn Monkeycoins and significantly increases user engagement.

#### Obtaining items
There are numerous ways a user can obtain items:
- Purchasing them in the shop (via the web application)
- Collecting Airdrops which randomly spawn throughout the day
- Trading with other users
- Opening Lootboxes

#### Selling items
Users can sell items by invoking `/sell` in the bot, or by using the web application.
The selling wizard will guide them through a sale.
A user can either:
- Sell an item back to the shop for 50% of its value (quick buck)
- List in on the declassifieds (via the web application)

#### Using items
Items can be used by invoking `/use` followed by the item name or alias.
If the item has some sort of actual function, it will be performed. Otherwise, if the item is simply a prop, it will display a message explaining what the item is used for.
Like the commands, items also use the newest Discord API features like Discord UI.

![I.C.B.M. Usage](https://cdn.discordapp.com/attachments/929674655801958400/1052630352151187466/image.png)

*An example of what happens when `/use ICBM` is invoked*

### 📥 Other forms of income

#### Pickpocketing
One user may attempt to pickpocket another user by invoking `/pickpocket`, or by using the context menu under another user:

![Starting a Pickpocket](https://cdn.discordapp.com/attachments/929674655801958400/1052632320357716061/image.png)

Once a pickpocket is initiated, an embed will appear, and the victim will be notified via DM. A timer will countdown, stating that the victim has 60 seconds to stop the pickpocket. The user may stop the pickpocket by opening the channel and clicking on the embed's button.
If the victim fails to stop the pickpocket, the attacker is rewarded with a random amount of the victim's total balance, between 3% and 8%.

![Example 1](https://media.discordapp.net/attachments/929674655801958400/1052632893928788028/image.png)

*Example of an ongoing pickpocket*

![Example 2](https://cdn.discordapp.com/attachments/929674655801958400/1052633197155995698/image.png)

*Example of a successful pickpocket*

![Example 3](https://cdn.discordapp.com/attachments/929674655801958400/1052654704800313355/image.png)

*Example of the direct message you receive when being pickpocketted.*

#### Game APIs
The bot is linked to popular game APIs to reward players in Monkeycoin for performing well in their favorite game.
Most commonly, users will play the game *Valorant* to earn Monkeycoin.
There is a task coroutine which polls the Valorant API every few minutes to check if any participating users have played a match.
The match data is then passed through some scrutiny to assure that the game mode is valid, then the reward is calculated.
Once the reward is calculated, the user will receive a direct message notifying them of their earnings:

![Valorant Match Reward](https://cdn.discordapp.com/attachments/929674655801958400/1052631326672572486/image.png)

*There is a known bug where the embed is missing some calculations, and therefore does not accurately reflect the total amount received. It's on the todo list.*

#### Tycoon
Each user is given a tycoon. They can upgrade their tycoon by spending Monkeycoins on it, in exchange for a daily payout + other perks, like shop discounts and auto-pickpockets.
Users can upgrade their tycoon via the web application.

#### Airdrops
At random times throughout the day, the bot will send an Airdrop to a random channel. The Airdrop takes 30 seconds to land, which gives users ample time to open Discord and fight for it. The dropped crate can contain rare items, coins, etc.

![Airdrop Image 1](https://cdn.discordapp.com/attachments/929674655801958400/1052663083966927010/image.png)

*The embed plays a gif displaying a supply plane dropping a crate*

![Airdrop Image 2](https://cdn.discordapp.com/attachments/929674655801958400/1052663161926471790/image.png)

*Once the airdrop lands, it will sit in this state until it is claimed, with no timeout.*

![Airdrop Image 3](https://cdn.discordapp.com/attachments/929674655801958400/1052663197666127892/image.png)

*Once claimed, the user is rewarded with the contents of the airdrop, and it is no longer claimable.*

## 💻 Web Application
Along with the bot itself, a web application is also served via Flask. This application serves as something of a "Dashboard" for users to interact with. Users authenticate to the app by using Discord OAuth, where my script will pull their Discord information to accordingly interact with the database.
The app is built using Flask, vanilla HTML/CSS/JS, Jinja2, SQL, etc.
It's approaching Christmas at the time of this documentation, so excuse our falling snow and candycanes in the screenshots.

### Stats
A stats page is available for a user to see how they stack up against the competition.

![Stats Page](https://cdn.discordapp.com/attachments/929674655801958400/1052634796951613531/image.png)

### Shop
The page for users to buy items they want. The item shop is randomized and restocked every night at 12:00AM.

![Shop Image](https://cdn.discordapp.com/attachments/929674655801958400/1052657165355200643/image.png)

### Tycoon
The page where users can upgrade their Tycoon to earn more coins each day and unlock special perks.

![Tycoon Image](https://cdn.discordapp.com/attachments/929674655801958400/1052657661604274187/image.png)

### Listings
An obvious Craigslist knockoff where users can sell and trade items. (The page intentionally looks as bad as Craigslist lol)

![Listings Image](https://cdn.discordapp.com/attachments/929674655801958400/1052658181567959160/image.png)

### Me
The main dashboard where users can see stats about themselves and manage their inventories. Includes visuals built with Chart.js

![Me Image 1](https://cdn.discordapp.com/attachments/929674655801958400/1052658390939209828/image.png)

![Me Image 2](https://cdn.discordapp.com/attachments/929674655801958400/1052658832427462758/image.png)

### Christmas
A special page which can be accessed by clicking the little sign at the bottom right corner of any page.
I've set up a little Christmas tree with gifts underneath for each one of my friends. They can only be opened after Christmas.
Everything is animated and audio coordinated, built on top of a Canvas.

![Christmas Image](https://cdn.discordapp.com/attachments/929674655801958400/1052661069719543900/image.png)

### Additional Admin Tools
There are some specific pages only available to me for managing other user inventories, viewing all transactions, etc

# Footnote
This project has been a joy to write (although the code has certainly gotten out of control in some areas). 
At the time of writing, there have been over 2,500 transactions made in Monkeycoin (holy crap).
This project was started in early November of 2022, when I couldn't figure out how to get the bot to respond to me:

![Screenshot 1](https://cdn.discordapp.com/attachments/929674655801958400/1052665221010968726/image.png)

It has certainly come a long way.

## Technologies Used
- Python
- PyCord
- SQLite3
- Async
- APIs
- OOP
- Flask
- Jinja2
- HTML
- CSS
- JavaScript
- AJAX
- Threading
- Photoshop
- Illustrator
- AWS EC2
- Ubuntu
- OAuth2
- SocketIO
