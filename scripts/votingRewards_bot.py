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

LIMIT = 100

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
    tokens['bribes_raw'] = 0
    tokens['fees_raw'] = 0

    src = tokens.index.to_list()
    prices = []

    call_length = 150
    for start_i in range(0,len(src),call_length):
        in_connectors = src[start_i:start_i + call_length] + connectors + [dst]
        out = oracle.getManyRatesWithConnectors(len(src[start_i:start_i + call_length]), in_connectors)
        prices.extend([i/1e18 for i in out])
    tokens['price'] = prices

    seen = set()
    results = [0] * LIMIT
    offset = 0
    while len(results) == LIMIT:
        results = su.epochsLatest(LIMIT,offset)

        for res in results:
            pool = res[1]
            if pool in seen:
                continue
            else:
                seen.add(pool)
            bribes_votingrewards = res[4]
            fees_votingrewards = res[5]
            
            for addy, amt in bribes_votingrewards:
                if addy.lower() in tokens.index:
                    tokens.at[addy.lower(), 'bribes_raw'] += amt

            for addy, amt in fees_votingrewards:
                if addy.lower() in tokens.index:
                    tokens.at[addy.lower(), 'fees_raw'] += amt
        offset += LIMIT

    tokens['bribes_raw'] = tokens['bribes_raw']/10**tokens['decimals']
    tokens['fees_raw'] = tokens['fees_raw']/10**tokens['decimals']

    bribes = (tokens['bribes_raw'] * tokens['price']).sum()
    incentives = ( (tokens['bribes_raw'] + tokens['fees_raw']) * tokens['price']).sum()


    watching = discord.Activity(name=f"Bribes: {round(bribes/1000,2)}K", type=discord.ActivityType.watching)
    await bot.change_presence(activity=watching)

    # server id
    TARGET_GUILD_ID = data['server_id']

    target_guild = bot.get_guild(TARGET_GUILD_ID)
    await target_guild.me.edit(nick=f"Rewards: {round(incentives/1000,2)}K")

# Run the bot with your token
if is_velo:
    bot.run("MTE1NTQ0MjYyMDkxMTMzNzQ5Mg.Gsh8MB.JKT9FoHUUFr39tHk8jgI3vAHE7oQvjFRpBCUf8")
else:
    bot.run("MTE1NjE4ODI2ODY5MDQxNTY1Nw.GSIM4C.TwR49rZ9pNC5YQ1QdDrR9_KOCQgRc-iN4ThJSI")