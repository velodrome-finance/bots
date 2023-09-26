from brownie import interface, chain
import json
from scripts.get_token_info import get_active_tokens
import discord
from discord.ext import commands, tasks

if chain.id == 10:
    is_velo = True
    data = json.load(open('./config.json'))['velo']
else:
    is_velo = False
    data = json.load(open('./config.json'))['aero']

oracle = interface.IOracle(data['oracle'])
connectors = data['connectors']
dst = data['dst']

tokens_original = get_active_tokens(data)

su = interface.sugar(data['sugar'])

LIMIT = 50

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Set up the bot with the command prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    update_status_and_nickname.start()  # Start the background task

@tasks.loop(minutes=30) 
async def update_status_and_nickname():
    tokens = tokens_original.copy(deep=True)
    tokens['reserves_raw'] = 0

    src = tokens.index.to_list()
    prices = []

    call_length = 150
    for start_i in range(0,len(src),call_length):
        in_connectors = src[start_i:start_i + call_length] + connectors + [dst]
        out = oracle.getManyRatesWithConnectors(len(src[start_i:start_i + call_length]), in_connectors)
        prices.extend([i/1e18 for i in out])
    tokens['price'] = prices

    results = [0] * LIMIT
    offset = 0
    while len(results) == LIMIT:
        results = su.all(LIMIT,offset,'0x0000000000000000000000000000000000000000')
        for res in results:
            token0, reserve0, token1, reserve1 = res[5].lower(), res[6], res[8].lower(), res[9]
            if token0 in tokens.index:
                tokens.at[token0, 'reserves_raw'] += reserve0
            if token1 in tokens.index:
                tokens.at[token1, 'reserves_raw'] += reserve1
        offset += LIMIT

    tokens['reserves_raw'] = tokens['reserves_raw']/10**tokens['decimals']

    tvl = (tokens['reserves_raw'] * tokens['price']).sum()

    watching = discord.Activity(name=f"TVL {'Velodrome' if is_velo else 'Aerodrome'}", type=discord.ActivityType.watching)
    await bot.change_presence(activity=watching)

    # Your specific server ID (replace with your actual server ID)
    TARGET_GUILD_ID = data['server_id']  # replace this with your server's ID

    # Check if the bot is in the target server and set its nickname there
    target_guild = bot.get_guild(TARGET_GUILD_ID)
    await target_guild.me.edit(nick=f"{round(tvl/1000000,2)}M")

# Run the bot with your token
bot.run("MTE1NTUwMTUyOTM0ODk4NDkxNA.Gai4v1.lwQmOfbKnImDaokirlsHb-K3ekaS7scJEJyHfs")