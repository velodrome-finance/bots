import discord
from discord.ext import commands, tasks
import requests
import json
import argparse

parser = argparse.ArgumentParser()

# Define an argument named '--coords' that expects two values
parser.add_argument('--platform', choices=['velo', 'aero'], required=True,
                        help='velo or aero')
args = parser.parse_args()

data = json.load(open('./config.json'))[args.platform]
session = requests.Session()
URL = f"https://api.geckoterminal.com/api/v2/networks/{'optimism' if args.platform == 'velo' else 'base'}/pools/{data['pool']}"
prev_price = 0

def run_request(link):
    finished = False
    while not finished:
        try:
            response = session.get(link)
            finished = True
        except:
            finished = False
            continue
    return response.json()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Set up the bot with the command prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    update_status_and_nickname.start()  # Start the background task

@tasks.loop(seconds=60)  # Set the interval (e.g., 60 seconds)
async def update_status_and_nickname():
    global prev_price

    result = run_request(URL)['data']['attributes']
    price = round(float(result['base_token_price_usd']),3)
    direction = "↗" if price >= prev_price else "↘"
    price_title = f"${price} ({direction})"
    
    # Setting the 'playing' status to 24h price change
    game = discord.Game(f"24h: {result['price_change_percentage']['h24']}%")
    await bot.change_presence(status=discord.Status.online, activity=game)

    # server ID
    TARGET_GUILD_ID = data['server_id']   

    # Setting the nickname to the current price
    target_guild = bot.get_guild(TARGET_GUILD_ID)
    await target_guild.me.edit(nick=price_title)
    
    prev_price = price

if args.platform == 'velo':
    bot.run("MTE1NTAzNjEyODgxOTI5NDI3OA.GaYQ3p.tN70WFNbllp2gLrZuZA8gQQwQgkn2v2UimQJPQ")
else:
    bot.run("MTE1NTcyNzY2MjA3NDA0ODUyMg.GOkWtZ.HJSWEVMcVzErcnK9jn7XDW_kVoB2huqdY2g2k8")