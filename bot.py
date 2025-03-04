from discord.ext import commands
import discord
import asyncio
import random
import shlex
import os
import sys
import subprocess
import time
import zipfile
from collections import Counter


# --------------------------------- GLOBALS ---------------------------------

BOT_TOKEN = "MzU3NjgzMTI2MDY5MzYyNjkw.GugV8Q.GbB2VVNp1BmKt0BktRglikOvke6KIejHjoi47A"
HOME_SERVER_ID = 134415388233433089
HOME_CHANNEL_ID = 1337536863640227881
WINDOWS = False

if "\\" in os.getcwd(): 
    WINDOWS = True

SERVERS_PATH = os.getcwd() + f'{os.sep}servers{os.sep}'

PLAYING = {}
STOP_EVENT = {}
LAST_ACTIVITY = {}
INACTIVITY_THRESHOLD = 3600

handcount = 0

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
tchannel = None
disconnect_lock = asyncio.Lock()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# --------------------------------- FUNCTIONS ---------------------------------

def command_with_attributes(*args, category=None, usage=None, configurable = False, **kwargs):
    def decorator(func):
        cmd = bot.command(*args, **kwargs)(func)
        cmd.category = category
        cmd.usage = usage
        cmd.configurable = configurable
        return cmd
    return decorator

def load_triggers(file_path):
    triggers = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                trigger, response = line.split(',', 1)
                triggers[trigger] = response
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return triggers

async def delete_session_stats(ctx):
    file_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt')
    try:
        os.remove(file_path)
        await ctx.send("*Session stats deleted.*")
        print(f"{file_path} has been deleted successfully.")
    except FileNotFoundError:
        print(f"{file_path} does not exist.")
    except Exception as e:
        print(f"Error: {e}")

async def initialize_guild(guild):
    global PLAYING, STOP_EVENT
    PLAYING[guild.id] = False
    STOP_EVENT[guild.id] = asyncio.Event()
    
    guild_folder = os.path.join(SERVERS_PATH, str(guild.id))
    guild_sounds_folder = os.path.join(guild_folder, "all_sounds")
    guild_title_path = os.path.join(guild_folder, "0. " + guild.name)
    guild_config_path = os.path.join(guild_folder, "config.txt")
    guild_triggers_path = os.path.join(guild_folder, "triggers.txt")
    guild_loops_path = os.path.join(guild_folder, "loops.txt")

    if not os.path.exists(guild_folder):
        os.makedirs(guild_folder)
        print(f"Created folder for server: {guild.name} ({guild.id})")
        await tchannel.send(f"Created folder for server: `{guild.name}` ({guild.id})")
    if not os.path.exists(guild_sounds_folder):
        os.makedirs(guild_sounds_folder)
        print(f"Created sounds folder for server: {guild.name}")
        await tchannel.send(f"Created sounds folder for server: `{guild.name}`")
    if not os.path.exists(guild_title_path):
        with open(guild_title_path, 'a'):
            print(f"Created title file for server: {guild.name}")
    if not os.path.exists(guild_config_path):
        with open(guild_config_path, 'a'):
            print(f"Created config file for server: {guild.name}")
    initialize_config(guild_config_path, guild.id)
    if not os.path.exists(guild_triggers_path):    
        with open(guild_triggers_path, 'a'):
            print(f"Created triggers file for server: {guild.name}")
    if not os.path.exists(guild_loops_path):    
        with open(guild_loops_path, 'a'):
            print(f"Created loops file for server: {guild.name}")

def initialize_config(path, guild_id):
    options = {
        "default_text_channel": ("default", "sets default text channel for non-command-related bot messages. USE CHANNEL ID"),
        # leaving this here for when I add more config options
    }
      
    config = load_config(guild_id)  
    keys = []
    
    with open(path, 'a') as file:
        for command in bot.commands:
            if command.configurable == True and f"!{command.name}_message" not in config:
                file.write(f"!{command.name}_message,default,bot message after command\n")
            keys.append(f"!{command.name}_message")  
        
        for key, (value, description) in options.items():
            if key not in config:
                file.write(f"{key},{value},{description}\n")     
            keys.append(key)
            
    extra_keys = set(config.keys()) - set(keys)
    
    if extra_keys:
        with open(path, 'r') as file:
            lines = file.readlines()
        with open(path, 'w') as file:
            for line in lines:
                key = line.split(',', 1)[0]
                if key not in extra_keys:
                    file.write(line)
        print(f"Removed extra configuration keys: {extra_keys} in server: {guild_id}")
        
def load_config(guild_id):
    config_path = os.path.join(SERVERS_PATH, str(guild_id), "config.txt")
    config = {}
    try:
        with open(config_path, 'r') as file:
            for line in file:
                key, value, description = line.strip().split(',', 2)
                config[key] = (value, description)
    except FileNotFoundError:
        pass
    return config

def save_config(guild_id, config):
    config_path = os.path.join(SERVERS_PATH, guild_id, "config.txt")
    with open(config_path, 'w') as file:
        for key, (value, description) in config.items():
            file.write(f"{key},{value},{description}\n")

def get_config(guild_id, key):
    config = load_config(guild_id)
    return config.get(key)

def set_config(guild_id, key, value, description):
    config = load_config(guild_id)
    if value == "DELETE":
        config[key] = ("default", description)
    else:
        config[key] = (value, description)
    save_config(guild_id, config)

async def disconnect(vc, message):
    global PLAYING, STOP_EVENT, disconnect_lock
    
    async with disconnect_lock:
        if not vc.is_connected():
            return
        
        PLAYING[vc.guild.id] = False      
        STOP_EVENT[vc.guild.id].set()         
        vc.stop()
        
        await vc.disconnect()
                
        default_tc = get_config(vc.channel.guild.id, "default_text_channel")[0]
        if default_tc != "default":
            default_tc = vc.channel.guild.get_channel(int(default_tc))
        if default_tc == "default" or default_tc is None:
            default_tc = vc.channel.guild.system_channel or vc.channel.guild.text_channels[0]
            
        await default_tc.send(message)

        in_vc = False
        for vc in bot.voice_clients:
            if vc.is_connected():
                in_vc = True
                break
        if not in_vc:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for stupid messages"))
            
        ctx = await bot.get_context(default_tc.last_message)    
        await ctx.invoke(bot.get_command('sessionstats'))
        await delete_session_stats(ctx)
        
async def check_inactivity():
    global LAST_ACTIVITY
        
    while not bot.is_closed():
        current_time = time.time()
        
        for vc in bot.voice_clients:
            if vc.is_connected():
                last_activity = LAST_ACTIVITY.get(vc.guild.id, 0)
                
                if len(vc.channel.members) == 1:
                    message = f"*Disconnected from voice channel `{vc.channel.name}` because everyone else fucking left.*"
                    await disconnect(vc, message)
                    
                elif current_time - last_activity > INACTIVITY_THRESHOLD:
                    message = f"*Disconnected from voice channel `{vc.channel.name}` due to inactivity (1 hour).*"
                    await disconnect(vc, message)
                    
        await asyncio.sleep(600)

def get_folder_size(folder_path):
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
            
    return total_size


# --------------------------------- EVENTS ---------------------------------

@bot.event
async def on_ready():
    global tchannel
    
    tchannel = bot.get_channel(HOME_CHANNEL_ID)
    
    await tchannel.send("# Hello there." +  "\n\nConfiguring server folders...")
    
    for guild in bot.guilds:
        await initialize_guild(guild)
        
    print("BOT AWAKE AND READY")
    if WINDOWS:
        await tchannel.send("*running locally on Windows*")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for stupid messages"))
    await tchannel.send("**Atyiseusseatyiseuss!**")
    
    await check_inactivity()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    triggers_path = os.path.join(SERVERS_PATH, str(message.guild.id), 'triggers.txt')
    triggers = load_triggers(triggers_path)
    
    for trigger, response in triggers.items():
        if trigger in message.content:
            await message.channel.send(response)
            return
    
    num = random.randint(0,6)
    if num == 5:
        num2 = random.randint(0,6)
        if num2 == 5:
            await message.channel.send('# **Wrong! Shuddup.**')
        else: 
            await message.channel.send('**Wrong! Shuddup.**')

@bot.event
async def on_guild_join(guild):
    await tchannel.send(f"### Joined server: `{guild.name}` (`{guild.id}`)")
    await initialize_guild(guild)
        
    channel = guild.system_channel or guild.text_channels[0]
    if channel:
        await channel.send("Which idiot added me to this shithole?\n\n Use `!help` to get started.")  
 
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    for vc in bot.voice_clients:
        if vc.channel == before.channel and len(vc.channel.members) == 1:
            message = f"*Disconnected from voice channel `{vc.channel.name}` because everyone else fucking left.*"
            await disconnect(vc, message)
            
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("*Invalid command, you piece of shit.*")

    
# --------------------------------- COMMANDS ---------------------------------     
    
bot.remove_command('help')

@command_with_attributes(name='help', category='Help', help='Displays help information for all commands.', usage='`!help`')
async def help(ctx, *input: str):
    if not input:
        await ctx.send("## Welcome to this scuffed ass soundboard bot!\n\n" +
                       "I can play your saved sounds *(see command category: `SOUNDBOARD - PLAYING`)*\n" + 
                       "and I can reply to your messages *(see command category: `MESSAGE TRIGGERS`)*.\n\n" + 
                       "Use **`!help commands`** to see a full list of my commands, their descriptions, and their correct usage.\n" +
                       "If you are a server admin, try out **`!config`** as well.")
        return
    
    message = ' '.join(input)
    if message != "commands":
        await ctx.send("Invalid input. Try `!help` or `!help commands`.")
        return    
    
    categories = {}
    for command in bot.commands:
        category = getattr(command, 'category', 'Uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(command)
    
    help_message = "## Bot Commands:\n\n"
    
    if ctx.guild.id != HOME_SERVER_ID:
        del categories['DEWEY']
        if not await bot.is_owner(ctx.author):
            del categories['OWNER COMMANDS']
    del categories['Help']
    
    for category, commands in sorted(categories.items()):
        help_message += f"**{category}:**\n"
        for command in commands:
            help_message += f"**`!{command.name}`** -> {command.help}  \||  **Usage:** {command.usage}\n"
        help_message += "\n"
    
    chunk_size = 2000
    lines = help_message.split('\n')
    chunk = ""
    
    for line in lines:
        if len(chunk) + len(line) + 1 > chunk_size:
            await ctx.send(chunk)
            chunk = ""
        chunk += line + '\n'
    if chunk:
        await ctx.send(chunk)
    
@help.error
async def help_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")    
    
    
# -------------- misc commands --------------    
    
@command_with_attributes(name='raisehand', category='DEWEY', help="Raises hands in correct order.", usage='`!raisehand`')
async def raisehand(ctx):
    
    global handcount
    
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    
    if handcount % 3 == 0:
        m = "Frankie?"
    elif handcount % 3 == 1:
        m = "Lenny?"
    else:
        m = "Leonard?"
    await ctx.send(m)
    handcount += 1
@raisehand.error
async def raisehand_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")    
    
    
@command_with_attributes(name='randomhand', category='DEWEY', help="Raises hands in random order.", usage='`!randomhand`')
async def randomhand(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    
    num = random.randint(0,2)
    if num == 0:
        m = "Frankie?"
    elif num == 1:
        m = "Lenny?"
    else:
        m = "Leonard?"
    await ctx.send(m)

@randomhand.error
async def randomhand_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


# -------------- sound commands --------------

@command_with_attributes(name='s', category='SOUNDBOARD - PLAYING', help="Plays desired sound. Chooses randomly if no input given.", usage='`!s` OR `!s <sound name>`')
async def s(ctx, *name):
    global LAST_ACTIVITY
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    
    input = ' '.join(name)
    
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    
    if not name:
        try:
            files = os.listdir(sounds_folder_path)
        except FileNotFoundError:
            await ctx.send("*Sounds folder does not yet exist for this server.*")
        
        sound_path = os.path.join(sounds_folder_path, random.choice(files))
        basename = os.path.basename(sound_path).strip()

        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))

        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'a') as file:
            file.write(basename + '\n')
        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'a') as file:
            file.write(basename + '\n')
            
        LAST_ACTIVITY[ctx.guild.id] = time.time()
        return
    
    sound_path = os.path.join(sounds_folder_path, input + ".ogg")
    sound_path_mp3 = os.path.join(sounds_folder_path, input + ".mp3")
    basename = os.path.basename(sound_path).strip()
    basename_mp3 = os.path.basename(sound_path_mp3).strip()

    sounds = [line.lower() for line in os.listdir(sounds_folder_path)]

    if not basename.lower() in sounds:
        if not basename_mp3.lower() in sounds:
            await ctx.send(f"*Sound `{basename[:-4]}` does not exist, you piece of shit.*")
            return
        sound_path = sound_path_mp3
        basename = basename_mp3
    if not os.path.exists(sound_path) and not WINDOWS:
        await ctx.send(f"*'{basename}' is missing CAPS somewhere, you piece of shit.*")
        return

    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))

    with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'a') as file:
            file.write(basename + '\n')
    with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'a') as file:
        file.write(basename + '\n')

    LAST_ACTIVITY[ctx.guild.id] = time.time()

@s.error
async def s_error(ctx, error):
    if str(error) == "Command raised an exception: IndexError: Cannot choose from an empty sequence":
        await ctx.send("*You have no sounds saved! Add some before playing.*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='play', category='SOUNDBOARD - PLAYING', help="Plays random sounds at desired time interval. Default 90s.", usage='`!play` OR `!play <delay>` OR `!play <min_delay> <max_delay>`', configurable = True)
async def play(ctx, *arr):
    global PLAYING, STOP_EVENT, LAST_ACTIVITY
    
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    
    STOP_EVENT[ctx.guild.id].clear()
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    
    if len(arr) > 0 and float(arr[0]) < 1:
        await ctx.send("*Use !playfast for delay less than 1 second.*")
        return
    elif len(arr) == 1:
        delay = float(arr[0])
    elif len(arr) >= 2:
        delay = random.uniform(float(arr[0]), float(arr[1]))
    else:
        delay = 90
    
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    files = os.listdir(sounds_folder_path)
    
    PLAYING[ctx.guild.id] = True
    pcount = 0
    
    message = get_config(ctx.guild.id,"!play_message")[0]
    if message == "default":
        message = "I've been sittin on some awesome material"
    await ctx.send(message)
    
    max_duration = 60 * 60
    if delay > max_duration:
        max_duration = 2 * delay + 20
    
    start_time = asyncio.get_event_loop().time()
    
    while PLAYING[ctx.guild.id] and pcount < 30:    
        
        if len(arr) >= 2:
            delay = random.uniform(float(arr[0]), float(arr[1]))
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time >= max_duration:
            await ctx.send(f"*The play command has timed out after maximum of {max_duration // 60} minutes. Start again if you want.*")
            PLAYING[ctx.guild.id] = False
            return
        
        sound_path = os.path.join(sounds_folder_path, random.choice(files))
        basename = os.path.basename(sound_path).strip()
        
        ctx.voice_client.stop()
        
        try:
            if basename.endswith((".ogg", ".mp3")):
                ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
                try:
                    await asyncio.wait_for(STOP_EVENT[ctx.guild.id].wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
                
                with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'a') as file:
                    file.write(basename + '\n')
                with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'a') as file:
                    file.write(basename + '\n')
        except Exception as e:
            await ctx.send(f"*An unexpected error occurred: {e}*")
            
        if delay < 6: pcount += 1
        LAST_ACTIVITY[ctx.guild.id] = time.time()
        
    if pcount == 30:
        await ctx.send(f"*Limit of {pcount} fast sounds reached (1 < delay < 6). Chill for a sec, then start again if you want.*")
        PLAYING[ctx.guild.id] = False

@play.error
async def play_error(ctx, error):
    global PLAYING
    if str(error) == "Command raised an exception: IndexError: Cannot choose from an empty sequence":
        await ctx.send("*You have no sounds saved! Add some before playing.*")
        PLAYING[ctx.guild.id] = False
    elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
        await ctx.send("Wrong input, idiot. \n\nCorrect usage examples: \n\n" +
                       "`!play`: *Plays random sounds at default interval of 90 seconds.* \n" +
                       "`!play 30`: *Plays random sounds at interval of 30 seconds* \n" +
                       "`!play 25 60`: *Plays random sounds at random interval between 25 and 60 seconds (randomized after each sound)*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='playfast', category='SOUNDBOARD - PLAYING', help="Plays random sounds at desired fast time interval. Default 1s.", usage='`!playfast` OR `!playfast <delay>`', configurable = True)
async def playfast(ctx, *arr):
    global PLAYING, LAST_ACTIVITY
    
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    files = os.listdir(sounds_folder_path)
    
    if len(arr) > 1:
            raise ValueError("Wrong input.")
    elif len(arr) == 1:
        if float(arr[0]) > 1:
                await ctx.send("*Use `!play` for delay greater than 1 second.*")
                return
        if float(arr[0]) < 0.1:
                await ctx.send("*Delay less than 0.1 is forbidden. Bot will explode.*")
                return
        delay = float(arr[0])
    else:
        delay = 1
    
    LAST_ACTIVITY[ctx.guild.id] = time.time()
    PLAYING[ctx.guild.id] = True
    pfcount = 0
    
    message = get_config(ctx.guild.id,"!playfast_message")[0]
    if message == "default":
        message = "I've been sittin on some awesome material"
    await ctx.send(message)
    
    while PLAYING[ctx.guild.id] and pfcount < 30:    
        
        sound_path = os.path.join(sounds_folder_path, random.choice(files))
        basename = os.path.basename(sound_path).strip()
        
        ctx.voice_client.stop()
        
        try:
            if basename.endswith((".ogg", ".mp3")):
                ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
                await asyncio.sleep(delay)
                
                with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'a') as file:
                    file.write(basename + '\n')
                with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'a') as file:
                    file.write(basename + '\n')
        except Exception as e:
            await ctx.send(f"*An unexpected error occurred: {e}*")
            
        pfcount += 1
        
    if pfcount == 30:
        await ctx.send(f"*Limit of {pfcount} fast sounds reached (0.1 < delay < 1). Bot is gonna explode if it keeps going.*")
        PLAYING[ctx.guild.id] = False  

@playfast.error
async def playfast_error(ctx, error):
    global PLAYING
    if str(error) == "Command raised an exception: IndexError: Cannot choose from an empty sequence":
        await ctx.send("*You have no sounds saved! Add some before playing.*")
        PLAYING[ctx.guild.id] = False
    elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
        await ctx.send("Wrong input, idiot. \n\nCorrect usage examples: \n\n" +
                       "`!playfast`: *Plays random sounds at default interval of 1 second.* \n" +
                       "`!playfast 0.7`: *Plays random sounds at interval of 0.7 seconds*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='loop', category='SOUNDBOARD - PLAYING', help="Plays desired sound over and over again at desired time interval.", usage='`!loop \"<sound name>\" <delay>`', configurable = True)
async def loop(ctx, soundname: str, delay: float):
    global PLAYING, STOP_EVENT, LAST_ACTIVITY
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    if delay < 0.3:
        await ctx.send("*Delay less than 0.3 is forbidden. Bot would literally kill itself.*")
        return
    
    STOP_EVENT[ctx.guild.id].clear()
    
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    
    sound_path = os.path.join(sounds_folder_path, soundname + ".ogg")
    sound_path_mp3 = os.path.join(sounds_folder_path, soundname + ".mp3")
    basename = os.path.basename(sound_path).strip()
    basename_mp3 = os.path.basename(sound_path_mp3).strip()

    sounds = [line.lower() for line in os.listdir(sounds_folder_path)]

    if not basename.lower() in sounds:
        if not basename_mp3.lower() in sounds:
            await ctx.send(f"*Sound `{basename[:-4]}` does not exist, you piece of shit.*")
            return
        sound_path = sound_path_mp3
        basename = basename_mp3
    if not os.path.exists(sound_path) and not WINDOWS:
        await ctx.send(f"*'{basename}' is missing CAPS somewhere, you piece of shit.*")
        return

    LAST_ACTIVITY[ctx.guild.id] = time.time()
    PLAYING[ctx.guild.id] = True
    lcount = 0
    
    max_duration = 5 * 60
    if delay > max_duration:
        max_duration = 2 * delay + 20
    
    start_time = asyncio.get_event_loop().time()
    
    message = get_config(ctx.guild.id,"!loop_message")[0]
    if message == "default":
        message = "Why are you doing this?"
    
    await ctx.send(f"Looping `{soundname}` with delay {delay}. {message}")
    
    while PLAYING[ctx.guild.id] and lcount < 30:    
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time >= max_duration:
            await ctx.send(f"*The loop command has timed out after maximum of {max_duration // 60} minutes. Start again if you want.*")
            PLAYING[ctx.guild.id] = False
            return
        
        ctx.voice_client.stop()
        
        try:
            ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
            try:
                await asyncio.wait_for(STOP_EVENT[ctx.guild.id].wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass
            
            with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'a') as file:
                    file.write(basename + '\n')
            with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'a') as file:
                file.write(basename + '\n')
        except Exception as e:
            await ctx.send(f"*An unexpected error occurred: {e}*")
            
        if delay < 6: lcount += 1
        
    if lcount == 30:
        await ctx.send(f"*Limit of {lcount} fast sound loops reached (1 < delay < 6). Chill for a sec, then start again if you want.*")
        PLAYING[ctx.guild.id] = False

@loop.error
async def loop_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        await ctx.send("*You must specify a sound name and delay number (in seconds).\n\n Example: `!loop soundname 10`\n Example: `!loop \"sound name with spaces\" 10`*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='stop', category='SOUNDBOARD - PLAYING', help="Stops playing sounds.", usage='`!stop`', configurable = True)
async def stop(ctx):
    global PLAYING, STOP_EVENT
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    
    message = get_config(ctx.guild.id,"!stop_message")[0]
    if message == "default":
        message = "Did you press the stop button?"
    await ctx.send(message)
    
    PLAYING[ctx.guild.id] = False      
    STOP_EVENT[ctx.guild.id].set()         
    ctx.voice_client.stop()

@stop.error
async def stop_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='join', category='VOICE CHANNEL', help="Joins user's current voice channel.", usage='`!join`', configurable = True)
async def join(ctx):
    global LAST_ACTIVITY
    
    if ctx.voice_client is not None:
        await ctx.send("*I already in a voice channel, you piece of shit.*")
        return
    
    if ctx.author.voice is None:
        await ctx.send("*You are not connected to a voice channel, you piece of shit.*")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        message = get_config(ctx.guild.id,"!join_message")[0]
        if message == "default":
            message = "Won't be a problem."
        await ctx.send(message)
        await channel.connect()
        await ctx.send(f'Joined {channel}.')
    else:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f'Moved to {channel}')
    
    await bot.change_presence(activity=discord.Game(name="some MUSIC"))
    LAST_ACTIVITY[ctx.guild.id] = time.time()

@join.error
async def join_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    
        
@command_with_attributes(name='troll', category='VOICE CHANNEL', help="Joins desired voice channel. Does not require user to be connected. **ADMIN COMMAND.**", usage='`!troll <channel name>`', configurable = True)
@commands.has_permissions(administrator=True)
async def troll(ctx, *, chName: str):
    global LAST_ACTIVITY
    
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command is not yet available in your server.*")
        return
   
    if ctx.voice_client is not None:
        await ctx.send("*I already in a voice channel, you piece of shit.*")
        return
   
    if(chName.lower() == "private"): id = 265210092289261570
    elif(chName.lower() == "general"): id = 134415388233433090
    elif(chName.lower() == "poor man's general"): id = 212770924607438848
    elif(chName.lower() == "poverse general"): id = 1234341517041078383
    elif(chName.lower() == "harvey dent"): id = 1339030117430853708
    else: 
        await ctx.send("*Invalid channel name, idiot.*")
        return

    channel = bot.get_channel(id)
    
    if ctx.voice_client is None:
        message = get_config(ctx.guild.id,"!troll_message")[0]
        if message == "default":
            message = "Won't be a problem."
        await ctx.send(message)
        await channel.connect()
        await ctx.send(f'Trolling {channel}.')
    else:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f'Moved to {channel}')
        
    await bot.change_presence(activity=discord.Game(name="some MUSIC"))
    LAST_ACTIVITY[ctx.guild.id] = time.time()

@troll.error
async def troll_error(ctx, error):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command is not yet available in your server.*")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify a channel name.\n\n Example: `!troll general`")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='leave', category='VOICE CHANNEL', help="Leaves the current voice channel and displays sessions stats.", usage='`!leave`', configurable = True)
async def leave(ctx):   
    global PLAYING, STOP_EVENT
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel, you piece of shit.*")
        return
    
    PLAYING[ctx.guild.id] = False      
    STOP_EVENT[ctx.guild.id].set()         
    ctx.voice_client.stop()
    
    message = get_config(ctx.guild.id,"!leave_message")[0]
    if message == "default":
        message = "Won't be a problem."
    await ctx.send(message)
    
    await ctx.voice_client.disconnect()
    
    in_vc = False
    for vc in bot.voice_clients:
        if vc.is_connected():
            in_vc = True
            break
    if not in_vc:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for stupid messages"))
        
    await ctx.invoke(bot.get_command('sessionstats'))
    await delete_session_stats(ctx)

@leave.error
async def leave_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


# -------------- file-related commands --------------

@command_with_attributes(name='soundlist', category='SOUNDBOARD - DATA', help="Displays full soundlist in alphabetical order.", usage='`!soundlist`')
async def soundlist(ctx):
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    
    try:
        lines = os.listdir(sounds_folder_path)
    except FileNotFoundError:
        await ctx.send("*Sounds folder does not yet exist for this server.*")
    
    sorted_lines = sorted(lines, key = str.lower)
    
    output = '\n'.join(sorted_lines)
    numSounds = len(lines)

    if numSounds == 0:
        await ctx.send("*You have no sounds saved!*")
        return

    await ctx.send(f"### **List of all `{numSounds}` soundboard sounds:** \n\n")
    
    chunk_size = 1989
    lines = output.split('\n')
    chunk = ""
    
    for line in lines:
        if len(chunk) + len(line) + 1 > chunk_size:
            await ctx.send(f"```txt\n{chunk}```")
            chunk = ""
        chunk += line + '\n'
    if chunk:
        await ctx.send(f"```txt\n{chunk}```")   
    

@soundlist.error
async def soundlist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    

@command_with_attributes(name='sessionstats', category='SOUNDBOARD - DATA', help="Displays sound playcount stats for this session. Session stats delete upon bot leaving.", usage='`!sessionstats`')
async def sessionstats(ctx):
    try:
        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'session_stats.txt'), 'r') as file:
            filelines = file.readlines()
        
        shortened_lines = [s.strip() for s in filelines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 1989
        lines = output.split('\n')
        chunk = ""
        num = len(filelines)

        await ctx.send("## **Bot soundboard stats for this session:** \n\n")
        await ctx.send(f"### Playcount: `{num}` \n\n")
        
        for line in lines:
            if len(chunk) + len(line) + 1 > chunk_size:
                await ctx.send(f"```txt\n{chunk}```")
                chunk = ""
            chunk += line + '\n'
        if chunk:
            await ctx.send(f"```txt\n{chunk}```")
    except FileNotFoundError:
        await ctx.send("*No stats for this session yet!*")

@sessionstats.error
async def sessionstats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    

@command_with_attributes(name='alltimestats', category='SOUNDBOARD - DATA', help="Displays sound playcount stats for all time.", usage='`!alltimestats`')
async def alltimestats(ctx):
    try:
        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'all_time_stats.txt'), 'r') as file:
            filelines = file.readlines()
        
        shortened_lines = [s.strip() for s in filelines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
        
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 1989
        lines = output.split('\n')
        chunk = ""
        num = len(filelines)

        await ctx.send("## **Bot soundboard stats for all time:** \n\n")
        await ctx.send(f"### Playcount: `{num}` \n\n")
        
        for line in lines:
            if len(chunk) + len(line) + 1 > chunk_size:
                await ctx.send(f"```txt\n{chunk}```")
                chunk = ""
            chunk += line + '\n'
        if chunk:
            await ctx.send(f"```txt\n{chunk}```")
    except FileNotFoundError:
        await ctx.send("*No stats yet! Use `!s`, `!play`, or `!playfast` to start tracking playcount stats.*")

@alltimestats.error
async def alltimestats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='addtrigger', category='MESSAGE TRIGGERS', help='Adds a message trigger (if message CONTAINS trigger, bot will respond). **ADMIN COMMAND.**', usage='`!addtrigger \"<trigger>\" \"<response>\"`')
@commands.has_permissions(administrator=True)
async def addtrigger(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            await ctx.send('Usage: `!addtrigger "<trigger>" "<response>"`')
            return
        
        trigger, response = parts
        
        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'triggers.txt'), 'a') as file:
            file.write(f"{trigger},{response}\n")
        await ctx.send(f"New trigger added: `{trigger}` with response: `{response}`")
        
    except Exception as e:
        await ctx.send(f"*An error occurred while adding the trigger: `{e}`*")

@addtrigger.error
async def addtrigger_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")

@command_with_attributes(name='removetrigger', category='MESSAGE TRIGGERS', help='Removes a message trigger. **ADMIN COMMAND.**', usage='`!removetrigger \"<trigger>\"`')
@commands.has_permissions(administrator=True)
async def removetrigger(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 1:
            await ctx.send('Usage: `!removetrigger "<trigger>"`')
            return
        
        triggers_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), 'triggers.txt')
        
        trigger = parts[0]
        triggers = load_triggers(triggers_path)
        
        if trigger in triggers:
            with open(triggers_path, 'r') as file:
                lines = file.readlines()
            with open(triggers_path, 'w') as file:
                for line in lines:
                    if not line.startswith(trigger + ','):
                        file.write(line)
            await ctx.send(f"Trigger `{trigger}` removed successfully.")
        else:
            await ctx.send(f"Trigger `{trigger}` not found.")
    
    except Exception as e:
        await ctx.send(f"An error occurred while removing the trigger: {e}")

@removetrigger.error
async def removetrigger_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='triggerlist', category='MESSAGE TRIGGERS', help="Displays all triggers and their responses, sorted alphabetically by triggers.", usage='`!triggerlist`')
async def triggerlist(ctx):
    triggers = load_triggers(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'triggers.txt'))
    
    if not triggers:
        await ctx.send("*No triggers found.*")
        return

    sorted_triggers = sorted(triggers.items())
    output = "\n".join([f"{trigger}: {response}" for trigger, response in sorted_triggers])
    
    chunk_size = 1989
    lines = output.split('\n')
    chunk = ""

    await ctx.send(f"## **List of all `{len(triggers)}` triggers and their responses:** \n\n")
    
    for line in lines:
        if len(chunk) + len(line) + 1 > chunk_size:
            await ctx.send(f"```txt\n{chunk}```")
            chunk = ""
        chunk += line + '\n'
    if chunk:
        await ctx.send(f"```txt\n{chunk}```")

@triggerlist.error
async def triggerlist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='addloop', category='SOUNDBOARD - DATA', help='Use to note down a good loop time. **ADMIN COMMAND.**', usage='`!addloop \"<sound name>\" \"<delay>\"`')
@commands.has_permissions(administrator=True)
async def addloop(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            await ctx.send('Usage: `!addloop "<sound name>" "<delay>"`')
            return
        
        soundname, delay = parts
        
        with open(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'loops.txt'), 'a') as file:
            file.write(f"{soundname},{delay}\n")
        await ctx.send(f"New loop info saved. Sound name: `{soundname}` with delay: `{delay}`")
        
    except Exception as e:
        await ctx.send(f"*An error occurred while adding the loop info: `{e}`*")

@addloop.error
async def addloop_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")

@command_with_attributes(name='removeloop', category='SOUNDBOARD - DATA', help='Removes a saved loop time. **ADMIN COMMAND.**', usage='`!removeloop \"<sound name>\"`')
@commands.has_permissions(administrator=True)
async def removeloop(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 1:
            await ctx.send('Usage: `!removeloop "<sound name>"`')
            return
        
        loops_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), 'loops.txt')
        
        soundname = parts[0]
        loops = load_triggers(loops_path)
        
        if soundname in loops:
            with open(loops_path, 'r') as file:
                lines = file.readlines()
            with open(loops_path, 'w') as file:
                for line in lines:
                    if not line.startswith(soundname + ','):
                        file.write(line)
            await ctx.send(f"Loop info for `{soundname}` removed successfully.")
        else:
            await ctx.send(f"Loop info for `{soundname}` not found.")
    
    except Exception as e:
        await ctx.send(f"An error occurred while removing the loop info: {e}")

@removeloop.error
async def removeloop_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='looplist', category='SOUNDBOARD - DATA', help="Displays all saved loop infos, sorted alphabetically by sound name.", usage='`!looplist`')
async def looplist(ctx):
    loops = load_triggers(os.path.join(SERVERS_PATH, str(ctx.guild.id), 'loops.txt'))
    
    if not loops:
        await ctx.send("*No loops found.*")
        return

    sorted_loops = sorted(loops.items())
    output = "\n".join([f"{soundname}: {delay}" for soundname, delay in sorted_loops])
    
    chunk_size = 1989
    lines = output.split('\n')
    chunk = ""

    await ctx.send(f"## **List of all `{len(loops)}` sounds with saved loop info:** \n\n")
    
    for line in lines:
        if len(chunk) + len(line) + 1 > chunk_size:
            await ctx.send(f"```txt\n{chunk}```")
            chunk = ""
        chunk += line + '\n'
    if chunk:
        await ctx.send(f"```txt\n{chunk}```")

@looplist.error
async def looplist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='config', category='CONFIG', help="Configures certain bot settings", usage='*use `!config` to see full usage*')
@commands.has_permissions(administrator=True)
async def config(ctx, *input: str):
    if len(input) == 0:
        await ctx.send("Welcome to the config command. From here you can view and set certain configurations for the bot.")
        await ctx.send("**Usage:** \n`!config \"<variable>\" \"<value>\"` to set a configuration or " + 
                       "\n`!config \"<variable>\" DELETE` to delete a configuration (reset to default) or " + 
                       "\n`!config \"<variable>\"` to view a single configuration or " +
                       "\n`!config viewall` to view all the variables you can set and their current values." + 
                       "\n\n*Example: `!config \"!play_message\" \"playing stupid shit\"` - now every time you use !play, the bot will say \"playing stupid shit\".*")
        return
    
    key = input[0]
    config = load_config(ctx.guild.id)
    
    if key == 'viewall':
        if not config:
            await ctx.send("No configurations found. Message bot owner to fix this.")
            return
        output = "\n".join([f"**`{key}`**: `{value}`  \||  Description: *{description}.*" for key, (value, description) in sorted(config.items())])
        await ctx.send(f"## List of all configurables, their values, and descriptions: \n\n")
        
        chunk_size = 2000
        lines = output.split('\n')
        chunk = ""
        
        for line in lines:
            if len(chunk) + len(line) + 1 > chunk_size:
                await ctx.send(f"{chunk}")
                chunk = ""
            chunk += line + '\n'
        if chunk:
            await ctx.send(f"{chunk}")
        return
    
    value_description = get_config(ctx.guild.id, key)
    if value_description is None:
        await ctx.send(f"`{key}` is not a configurable variable.")
        return
    value, description = value_description
    
    if len(input) == 1:
        await ctx.send(f"Configuration for **`{key}`** is: `{value}`  \||  Description: *{description}.*")
    else:
        new_value = ' '.join(input[1:])
        
        if key == "default_text_channel":
            if new_value == 'DELETE':
                set_config(ctx.guild.id, key, new_value, description)
                await ctx.send(f"Configuration for `{key}` reset to default.")
                return
            if not new_value.isdigit():
                await ctx.send("*You must input a channel ID, not a name, idiot. Find this by right-clicking the channel and selecting 'Copy Channel ID'.*")
                return
            channel_id = int(new_value)
            channel = ctx.guild.get_channel(channel_id)
            if channel is None:
                await ctx.send("*The provided channel ID does not exist, dumbass. Please provide a valid channel ID.*")
                return
        
        set_config(ctx.guild.id, key, new_value, description)
        if new_value == 'DELETE':
            await ctx.send(f"Configuration for `{key}` reset to default.")
        else:
            await ctx.send(f"Configuration for `{key}` set to `{new_value}`.")
            if key == "default_text_channel":
                await channel.send("*This channel is now the default text channel for any of my non-command-related bot messages (update messages, restart/shutdown notices, etc.)*")

@config.error
async def config_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='upload', category='SOUNDBOARD - DATA', help='Uploads a sound file for your server. **ADMIN COMMAND.**', usage='`!upload` with a single file attachment (can be zipped folder)')
@commands.has_permissions(administrator=True)
async def upload(ctx):
    if not ctx.message.attachments:
        await ctx.send("_No file attached. Attach a **.mp3** or **.ogg** sound file or a zipped folder, dumbass._")
        return
    
    if len(ctx.message.attachments) > 1:
        await ctx.send("*I can only do one file at a time. Fuck off and try again with a single file OR a zipped folder containing many sound files.*")
        return

    attachment = ctx.message.attachments[0]
    valid_extensions = ('.mp3', '.ogg')
    max_folder_size = 100 * 1024 * 1024  # 100 MB
    guild_path = os.path.join(SERVERS_PATH, str(ctx.guild.id))
    sounds_folder_path = os.path.join(guild_path, "all_sounds")

    folder_size = get_folder_size(sounds_folder_path)
    if folder_size > max_folder_size:
        await ctx.send("*You have used all of the allotted 100 MB for your server's sounds folder. Cannot upload more files.*")
        return
    
    if attachment.filename.endswith('.zip'):
        zip_path = os.path.join(guild_path, attachment.filename)
        try:
            await attachment.save(zip_path)
            
            temp_path = os.path.join(guild_path, "temp_extracted")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            extracted_files = os.listdir(temp_path)
            
            valid_files = []
            invalid_files = []
            duplicate_files = []
            
            for file in extracted_files:
                if not file.endswith(valid_extensions):
                    invalid_files.append(file)
                else:
                    if os.path.exists(os.path.join(sounds_folder_path, file)):
                        duplicate_files.append(file)
                    else:
                        valid_files.append(file)
            
            for file in invalid_files:
                os.remove(os.path.join(temp_path, file))
            for file in duplicate_files:
                os.remove(os.path.join(temp_path, file))
                
            temp_valid_size = get_folder_size(temp_path)
            
            if folder_size + temp_valid_size > max_folder_size:
                for file in valid_files:
                    os.remove(os.path.join(temp_path, file))
                await ctx.send(f"*Upload failed. Your server's sound folder would exceed the 100 MB limit with this upload.*")
                return
            
            for file in valid_files:
                os.rename(os.path.join(temp_path, file), os.path.join(sounds_folder_path, file))    
                
            os.rmdir(temp_path)
            os.remove(zip_path)

            if valid_files:
                message = ', '.join(valid_files)
                if len(message) > 1900:
                    message = "Too many files to list, but all the **.mp3** and or **.ogg files** were uploaded successfully."
                await ctx.send(f"Files uploaded successfully: `{message}`")
            if invalid_files:
                message = ', '.join(invalid_files)
                if len(message) > 1800:
                    message = "Too many files to list."
                await ctx.send(f"_Invalid file types in zip: `{message}`. Only **.mp3** and **.ogg** files are supported._")
            if duplicate_files:
                message = ', '.join(duplicate_files)
                if len(message) > 1800:
                    message = "Too many files to list."
                await ctx.send(f"*Some files already exist and were not replaced: `{message}`. If you want to replace them, upload them one by one (not in zip folder).*")
                
        except Exception as e:
            await ctx.send(f"An error occurred while processing the zip file: {e}")
            
    else:
        if not attachment.filename.endswith(valid_extensions):
            await ctx.send("_Invalid file type. Only **.mp3**, **.ogg**, and **.zip** files are supported._")
            return
        
        if folder_size + attachment.size > max_folder_size:
                await ctx.send(f"*Upload failed. Your server's sound folder would exceed the 100 MB limit with this upload.*")
                return

        file_path = os.path.join(sounds_folder_path, attachment.filename)
        
        try:
            await attachment.save(file_path)
            await ctx.send(f"Sound file `{attachment.filename}` uploaded successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while uploading the file: {e}")

@upload.error
async def upload_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='download', category='SOUNDBOARD - DATA', help='Gets a sound file from the bot for download.', usage='`!download <soundname with extension>`')
async def download(ctx, *, sound_name: str):
    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
    sound_path = os.path.join(sounds_folder_path, sound_name)

    if not sound_name.endswith('.mp3') and not sound_name.endswith('.ogg'):
        await ctx.send("_You must specify the file extension. Only **.mp3** and **.ogg** files are supported._")
        return

    if os.path.exists(sound_path):
        file_path = sound_path
    else:
        await ctx.send(f"*Sound `{sound_name}` does not exist, you piece of shit.*")
        return

    try:
        await ctx.send(file=discord.File(file_path))
    except discord.errors.HTTPException as e:
        if "413 Request Entity Too Large" in str(e):
            await ctx.send("*The file is too large to be sent via Discord. Just give up.*")
        else:
            await ctx.send(f"*An error occurred while sending the file: `{e}`*")
    except Exception as e:
        await ctx.send(f"*An error occurred while sending the file: `{e}`*")

@download.error
async def download_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("*You must specify a sound name.\n\n Example: `!download dumb sound.mp3` (spaces are allowed in file name)*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


# -------------- owner commands --------------

@command_with_attributes(name='logs', category='OWNER COMMANDS', help="Displays desired number of lines of log file output. Default 20 lines.", usage='`!logs` OR `!logs <numLines>`')
@commands.is_owner()
async def logs(ctx, lines: int = 20):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    log_file_path = 'output.log'

    try:
        with open(log_file_path, 'r') as file:
            log_content = file.readlines()

        recent_log_content = log_content[-lines:]
        output = ''.join(recent_log_content)

        await tchannel.send("## **Recent logs from output.log:** \n\n")
        
        chunk_size = 1989
        lines = output.split('\n')
        chunk = ""
        
        for line in lines:
            if len(chunk) + len(line) + 1 > chunk_size:
                await ctx.send(f"```txt\n{chunk}```")
                chunk = ""
            chunk += line + '\n'
        if chunk:
            await ctx.send(f"```txt\n{chunk}```")
    except FileNotFoundError:
        await tchannel.send("*The log file does not exist, you piece of shit.*")
    except Exception as e:
        await tchannel.send(f"*An error occurred while reading the log file: {e}*")

@logs.error
async def logs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")  


@command_with_attributes(name='alllogs', category='OWNER COMMANDS', help="Displays entire log file output.", usage='`!alllogs`')
@commands.is_owner()
async def alllogs(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    log_file_path = 'output.log'
    
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()

        await tchannel.send("## **Contents of output.log:** \n\n")
        
        chunk_size = 1989
        lines = log_content.split('\n')
        chunk = ""
        
        for line in lines:
            if len(chunk) + len(line) + 1 > chunk_size:
                await ctx.send(f"```txt\n{chunk}```")
                chunk = ""
            chunk += line + '\n'
        if chunk:
            await ctx.send(f"```txt\n{chunk}```")
            
    except FileNotFoundError:
        await tchannel.send("*The log file does not exist.*")
    except Exception as e:
        await tchannel.send(f"*An error occurred while reading the log file: {e}*")

@alllogs.error
async def alllogs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")  


@command_with_attributes(name='update', category='OWNER COMMANDS', help="Pulls changes from github repo and restarts if necessary.", usage='`!update`')
@commands.is_owner()
async def update(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    servers_sounds = {}
    for guild in bot.guilds:
        sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
        sounds = os.listdir(sounds_folder_path)
        servers_sounds[guild.id] = sounds
    
    await tchannel.send("Pulling latest updates from github...")

    try:
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)

        await tchannel.send(f"```{result.stdout or result.stderr}```")

        if "Already up to date." in result.stdout:
            await tchannel.send("*No updates found. Bot is already up to date!*")
            return

        if "all_sounds" in result.stdout:
            for guild in bot.guilds: 
                if str(guild.id) + "/all_sounds" in result.stdout:  
                    await tchannel.send(f"### Refreshing soundlist for server: `{guild.name}`...")
                    
                    sounds = servers_sounds[guild.id]
                    sounds_folder_path = os.path.join(SERVERS_PATH, str(ctx.guild.id), "all_sounds")
                    oldCount = len(sounds)
                    
                    sounds_new = os.listdir(sounds_folder_path)
                    newCount = len(sounds_new)
                    
                    if oldCount == newCount:
                        await tchannel.send(f"*No new sounds to add. Current soundlist count: {newCount}.*")

                    elif newCount > oldCount: 
                        difference = list(set(sounds_new) - set(sounds))
                        difference_str = '\n'.join(difference)
                        
                        if newCount - oldCount == 1: word = "sound"
                        else: word = "sounds"
                        
                        await tchannel.send(f"Soundlist refreshed: `{newCount - oldCount}` new {word} added. Current soundlist count: `{newCount}`.\n\n**New sounds:**\n`{difference_str}`")
                    
                    elif newCount < oldCount:
                        difference = list(set(sounds) - set(sounds_new))
                        difference_str = '\n'.join(difference)
                        
                        if oldCount - newCount == 1: word = "sound"
                        else: word = "sounds"
                        
                        await tchannel.send(f"### Soundlist refreshed: `{oldCount - newCount}` {word} removed. Current soundlist count: `{newCount}`.\n\n**Removed sounds:**\n`{difference_str}`")

        if "bot.py" in result.stdout:
            await tchannel.send("Update complete.")
            await ctx.invoke(bot.get_command('restart'))
            return
        
        if "Fast-forward" in result.stdout:  
            await tchannel.send("Updates pulled successfully. They did not affect `bot.py`.")
        else:
            await tchannel.send("Conflicts detected. Resolve manually or use `!hardreset`. Or, use `!forcepush` and try again.")
    
    except subprocess.CalledProcessError as e:
        await tchannel.send(f"Error pulling updates: {e.stderr}")
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")  


@command_with_attributes(name='pushdata', category='OWNER COMMANDS', help="Pushes all servers' data updates to github repo.", usage='`!pushdata`')
@commands.is_owner()
async def pushdata(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    await tchannel.send("**Fetching** latest changes from github...")

    try:
        subprocess.run(["git", "fetch"], capture_output=True, text=True, check=True)

        status_result = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
        if "Your branch is behind" in status_result.stdout:
            await tchannel.send("*There are changes on the remote repository, idiot. Update then try again.*")
            return
        
        await tchannel.send("*Local repo is up to date. Continuing with pushing updates.*\n\n" +
            "**Staging** changes for `output.log` and all servers' folders...")
        subprocess.run(["git", "add", "output.log"], check=True)
        subprocess.run(["git", "add", "servers/"], check=True)
        
        await tchannel.send("*Checking if changes actually exist...*")
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            await tchannel.send("*No changes to commit for all data.*")
            return

        await tchannel.send("*Changes exist!*\n\n" + "**Committing** updates...")
        commit_result = subprocess.run(["git", "commit", "-m", "Update servers' data"], capture_output=True, text=True, check=True)
        await tchannel.send(f"```{commit_result.stdout or commit_result.stderr}```")
        
        await tchannel.send("*Updates committed!*\n\n" + "**Pushing** updates to github repo...")
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)

        output = result.stdout if result.stdout else result.stderr
        await tchannel.send(f"```{output}```")
        if result.returncode == 0: 
            await tchannel.send("**Updates pushed successfully!**")
        else:
            await tchannel.send("*An error occurred while pushing updates.*")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else "An error occurred, but no error message was provided."
        await tchannel.send(f"Error pushing updates: {error_message}")
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")

@pushdata.error
async def pushdata_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='hardreset', category='OWNER COMMANDS', help="Hard resets local repo to match github repo.", usage='`!hardreset`')
@commands.is_owner()
async def hardreset(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    await tchannel.send("Hard resetting local branch to match remote branch...")

    try:
        result = subprocess.run(["git", "reset", "--hard", "origin/main"], capture_output=True, text=True)
        await tchannel.send(f"```{result.stdout or result.stderr}```")

        if "HEAD is now at" in result.stdout:
            await tchannel.send("Local branch successfully reset to match remote branch.")
        else:
            await tchannel.send("Reset failed??? Idk what to do.")
    
    except subprocess.CalledProcessError as e:
        await tchannel.send(f"Error pulling updates: {e.stderr}")
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")

@hardreset.error
async def hardreset_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='forcepush', category='OWNER COMMANDS', help="Force pushes all servers' data updates to github repo.", usage='`!forcepush`')
@commands.is_owner()
async def forcepush(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return

    try:
        subprocess.run(["git", "add", "output.log"], check=True)
        subprocess.run(["git", "add", "servers/"], check=True)
        
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            await tchannel.send("*No changes to commit for all data.*")
            return

        commit_result = subprocess.run(["git", "commit", "-m", "Update servers' data"], capture_output=True, text=True, check=True)
        await tchannel.send(f"```{commit_result.stdout or commit_result.stderr}```")
        
        await tchannel.send("*Updates committed.*\n\n" + "**Force Pushing** updates to github repo...")
        result = subprocess.run(["git", "push", "--force", "origin", "main"], capture_output=True, text=True, check=True)

        output = result.stdout if result.stdout else result.stderr
        await tchannel.send(f"```{output}```")
        if result.returncode == 0: 
            await tchannel.send("**Updates pushed successfully!**")
        else:
            await tchannel.send("*An error occurred while pushing updates.*")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else "An error occurred, but no error message was provided."
        await tchannel.send(f"Error pushing updates: {error_message}")
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")
    
@forcepush.error
async def forcepush_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='status', category='OWNER COMMANDS', help="Displays the servers in which the bot exists and the voice channels to which it is connected.", usage='`!status`')
@commands.is_owner()
async def status(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return

    server_info = []
    for guild in bot.guilds:
        voice_channels = [vc.name for vc in guild.voice_channels if vc.members and bot.user in vc.members]
        if voice_channels:
            server_info.append(f"Exists in: `{guild.name}`. Connected to voice channel: `{', '.join(voice_channels)}`")
        else:
            server_info.append(f"Exists in: `{guild.name}`. *Not connected to any voice channels.*")

    await tchannel.send("## **Bot Status:**\n" + f"**Exists in `{len(bot.guilds)}` servers. Connected to `{len(voice_channels)}` voice channels.** \n\n" + "\n".join(server_info))

@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='restart', category='OWNER COMMANDS', help="Restarts the bot.", usage='`!restart`')
@commands.is_owner()
async def restart(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    for vc in bot.voice_clients:
        if vc.is_connected():
            vc.stop()
            await vc.disconnect()
            
            if vc.channel.guild.id != HOME_SERVER_ID:
                default_tc = get_config(vc.channel.guild.id, "default_text_channel")[0]
                if default_tc != "default":
                    default_tc = vc.channel.guild.get_channel(int(default_tc))
                if default_tc == "default" or default_tc is None:
                    default_tc = vc.channel.guild.system_channel or vc.channel.guild.text_channels[0]
                await default_tc.send(f"*Disconnected from voice channel: `{vc.channel.name}`. Bot owner is restarting the bot.*")
            
            await delete_session_stats(ctx)
            
            await tchannel.send(f"*Disconnected from voice channel: `{vc.channel.name}` in server `{vc.channel.guild.name}`.*")
    
    await tchannel.send("Restarting...")

    try:   
        await bot.close()
        
        if WINDOWS:
            subprocess.Popen("python bot.py", shell=True)
        else:
            command = "bash -c 'source /home/lucassukeunkim/myenv/bin/activate && nohup python3 bot.py >> output.log 2>&1 &'"
            subprocess.Popen(command, shell=True) 
    
        sys.exit()
        
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")

@restart.error
async def restart_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@command_with_attributes(name='kys', category='OWNER COMMANDS', help="Shuts down the bot.", usage='`!kys`')
@commands.is_owner()
async def kys(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    if not WINDOWS:
        await ctx.send("*First, invoking `!pushdata`:*")
        await ctx.invoke(bot.get_command('pushdata'))
    
    for vc in bot.voice_clients:
        if vc.is_connected():
            vc.stop()
            await vc.disconnect()
            
            if vc.channel.guild.id != HOME_SERVER_ID:
                default_tc = get_config(vc.channel.guild.id, "default_text_channel")[0]
                if default_tc != "default":
                    default_tc = vc.channel.guild.get_channel(int(default_tc))
                if default_tc == "default" or default_tc is None:
                    default_tc = vc.channel.guild.system_channel or vc.channel.guild.text_channels[0]
                await default_tc.send(f"*Disconnected from voice channel: `{vc.channel.name}`. Bot owner has shut down the bot.*")
                
            await delete_session_stats(ctx)  
                    
            await tchannel.send(f"*Disconnected from voice channel: `{vc.channel.name}` in server `{vc.channel.guild.name}`.*")
    
    await ctx.send("So uncivilized. Shutting down...")
    
    await bot.close()
    sys.exit()
    
@kys.error
async def kys_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")    


# --------------------------------- RUN ---------------------------------

bot.run(BOT_TOKEN, reconnect=True)
