from discord.ext import commands
import discord
import asyncio
import random
import shlex
import os
import sys
import subprocess
from collections import Counter


# --------------------------------- GLOBALS ---------------------------------

BOT_TOKEN = "MzU3NjgzMTI2MDY5MzYyNjkw.GugV8Q.GbB2VVNp1BmKt0BktRglikOvke6KIejHjoi47A"
HOME_SERVER_ID = 134415388233433089
HOME_CHANNEL_ID = 1337536863640227881
WINDOWS = False

if "\\" in os.getcwd(): 
    SERVERS_PATH = os.getcwd().replace("\\", "/") + '/servers/'
    WINDOWS = True
else: 
    SERVERS_PATH = os.getcwd() + '/servers/'

PLAYING = {}
STOP_EVENT = {}

handcount = 0

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
tchannel = None

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# --------------------------------- FUNCTIONS ---------------------------------

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
    file_path = SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt'
    try:
        os.remove(file_path)
        await ctx.send("*Session stats deleted.*")
        print(f"{file_path} has been deleted successfully.")
    except FileNotFoundError:
        print(f"{file_path} does not exist.")
    except Exception as e:
        print(f"Error: {e}")


# --------------------------------- EVENTS ---------------------------------

@bot.event
async def on_ready():
    global tchannel, PLAYING, STOP_EVENT
    
    for guild in bot.guilds:
        PLAYING[guild.id] = False
        STOP_EVENT[guild.id] = asyncio.Event()
    
    tchannel = bot.get_channel(HOME_CHANNEL_ID)
    
    await tchannel.send("# Hello there." +  "\n\nConfiguring server folders...")
    
    for guild in bot.guilds:
        
        guild_folder = SERVERS_PATH + str(guild.id)
        guild_sounds_folder = guild_folder + "/all_sounds/"
        guild_title_path = guild_folder + "/0. " + guild.name
        guild_config_path = guild_folder + "/config.txt"
        guild_triggers_path = guild_folder + "/triggers.txt"
        guild_loops_path = guild_folder + "/loops.txt"

        if not os.path.exists(guild_folder):
            os.makedirs(guild_folder)
            print(f"Created folder for server: {guild.name} ({guild.id})")
            await tchannel.send(f"Created folder for server: {guild.name} ({guild.id})")
        if not os.path.exists(guild_sounds_folder):
            os.makedirs(guild_sounds_folder)
            print(f"Created sounds folder for server: {guild.name}")
            await tchannel.send(f"Created sounds folder for server: {guild.name}")
        if not os.path.exists(guild_title_path):
            with open(guild_title_path, 'a'):
                print(f"Created title file for server: {guild.name}")
        if not os.path.exists(guild_config_path):    
            with open(guild_config_path, 'a'):
                print(f"Created config file for server: {guild.name}")
        if not os.path.exists(guild_triggers_path):    
            with open(guild_triggers_path, 'a'):
                print(f"Created triggers file for server: {guild.name}")
        if not os.path.exists(guild_loops_path):    
            with open(guild_loops_path, 'a'):
                print(f"Created loops file for server: {guild.name}")
        
    print("BOT AWAKE AND READY")
    if WINDOWS:
        await tchannel.send("*running locally on Windows*")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for stupid messages"))
    await tchannel.send("**Atyiseusseatyiseuss!**")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    triggers = load_triggers(SERVERS_PATH + str(message.guild.id) + '/triggers.txt')
    
    for trigger, response in triggers.items():
        if trigger in message.content:
            await message.channel.send(response)
            return
    
    num = random.randint(0,4)
    if num == 0:
        num2 = random.randint(0,4)
        if num2 == 0:
            await message.channel.send('# **Wrong! Shuddup.**')
        else: 
            await message.channel.send('**Wrong! Shuddup.**')
    
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("*Invalid command. You piece of shit.*")

    
# --------------------------------- COMMANDS ---------------------------------     
    
# -------------- misc commands --------------    
    
@bot.command(help="Raises hands in correct order.")
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
    
    
@bot.command(help="Raises hands in random order.")
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

@bot.command(help="Plays full dewey fired scene.")
async def dewey(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("You're fired")
    
    sound_path = SERVERS_PATH + HOME_SERVER_ID + "/all_sounds/" + "dewey full scene.mp3"
    
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {e}'))

@dewey.error
async def dewey_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Plays desired sound. Chooses randomly if no input given.")
async def s(ctx, *name):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    input = ' '.join(name)
    
    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(ctx.guild.id) + "/all_sounds/"
    
    if not name:
        try:
            files = os.listdir(SOUNDS_FOLDER_PATH)
        except FileNotFoundError:
            await ctx.send("*Sounds folder does not yet exist for this server.*")
        
        sound_path = SOUNDS_FOLDER_PATH + random.choice(files)
        basename = sound_path.split('/')[-1].strip()

        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))

        with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'a') as file:
            file.write(basename + '\n')
        with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'a') as file:
            file.write(basename + '\n')
        return
    
    sound_path = SOUNDS_FOLDER_PATH + input + ".ogg"
    sound_path_mp3 = SOUNDS_FOLDER_PATH + input + ".mp3"
    basename = sound_path.split('/')[-1].strip()
    basename_mp3 = sound_path_mp3.split('/')[-1].strip()

    sounds = [line.lower() for line in os.listdir(SOUNDS_FOLDER_PATH)]

    if not basename.lower() in sounds:
        if not basename_mp3.lower() in sounds:
            await ctx.send(f"*Sound `{basename[:-4]}` does not exist. You piece of shit.*")
            return
        sound_path = sound_path_mp3
        basename = basename_mp3
    if not os.path.exists(sound_path) and not WINDOWS:
        await ctx.send(f"*'{basename}' is missing CAPS somewhere. You piece of shit.*")
        return

    choice = "a terrible"
    if random.randint(0,3) == 0:
        choice = "a wonderful"
    if "richard patrick" in input:
        choice = "THE BEST"
    await ctx.send(f"`{basename}` is {choice} choice.")

    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))

    with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'a') as file:
        file.write(basename + '\n')
    with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'a') as file:
        file.write(basename + '\n')

@s.error
async def s_error(ctx, error):
    if str(error) == "Command raised an exception: IndexError: Cannot choose from an empty sequence":
        await ctx.send("*You have no sounds saved! Add some before playing.*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Plays random sounds at desired time interval. Default 90s.")
async def play(ctx, *arr):
    global PLAYING, STOP_EVENT
    
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    
    STOP_EVENT[ctx.guild.id].clear()
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
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
    
    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(ctx.guild.id) + "/all_sounds/"
    files = os.listdir(SOUNDS_FOLDER_PATH)
    
    PLAYING[ctx.guild.id] = True
    pcount = 0
    
    await ctx.send("I've been sittin on some awesome material")
    
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
        
        sound_path = SOUNDS_FOLDER_PATH + random.choice(files)
        basename = sound_path.split('/')[-1].strip()
        
        ctx.voice_client.stop()
        
        try:
            if basename.endswith((".ogg", ".mp3")):
                ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
                try:
                    await asyncio.wait_for(STOP_EVENT[ctx.guild.id].wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
                
                with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'a') as file:
                    file.write(basename + '\n')
                with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'a') as file:
                    file.write(basename + '\n')
        except Exception as e:
            await ctx.send(f"*An unexpected error occurred: {e}*")
            
        if delay < 6: pcount += 1
        
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
        await ctx.send("Wrong input, idiot. \n\nCorrect usage: \n\n" +
                       "`!play`: *Plays random sounds at default interval of 90 seconds.* \n" +
                       "`!play <delay>`: *Plays random sounds at interval of `<delay>` seconds* \n" +
                       "`!play <min_delay> <max_delay>`: *Plays random sounds at random interval between `<min_delay>` and `<max_delay>` seconds (randomized after each sound)*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Plays random sounds at desired fast time interval. Default 1 second.")
async def playfast(ctx, *arr):
    global PLAYING
    
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(ctx.guild.id) + "/all_sounds/"
    files = os.listdir(SOUNDS_FOLDER_PATH)
    
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
    
    PLAYING[ctx.guild.id] = True
    pfcount = 0
    
    await ctx.send("I've been sittin on some awesome material")
    
    while PLAYING[ctx.guild.id] and pfcount < 30:    
        
        sound_path = SOUNDS_FOLDER_PATH + random.choice(files)
        basename = sound_path.split('/')[-1].strip()
        
        ctx.voice_client.stop()
        
        try:
            if basename.endswith((".ogg", ".mp3")):
                ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
                await asyncio.sleep(delay)
                
                with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'a') as file:
                    file.write(basename + '\n')
                with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'a') as file:
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
        await ctx.send("Wrong input, idiot. \n\nCorrect usage: \n\n" +
                       "`!playfast`: *Plays random sounds at default interval of 1 second.* \n" +
                       "`!playfast <delay>`: *Plays random sounds at interval of `<delay>` seconds*")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Plays desired sound over and over again at desired time interval.")
async def loop(ctx, soundname: str, delay: float):
    global PLAYING, STOP_EVENT
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    if PLAYING[ctx.guild.id]:
        await ctx.send("*I am already playing, idiot. Stop first and then try again.*")
        return
    if delay < 0.1:
        await ctx.send("*Delay less than 0.1 is forbidden. Bot would literally kill itself.*")
        return
    
    STOP_EVENT[ctx.guild.id].clear()
    
    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(ctx.guild.id) + "/all_sounds/"
    
    sound_path = SOUNDS_FOLDER_PATH + soundname + ".ogg"
    sound_path_mp3 = SOUNDS_FOLDER_PATH + soundname + ".mp3"
    basename = sound_path.split('/')[-1].strip()
    basename_mp3 = sound_path_mp3.split('/')[-1].strip()

    sounds = [line.lower() for line in os.listdir(SOUNDS_FOLDER_PATH)]

    if not basename.lower() in sounds:
        if not basename_mp3.lower() in sounds:
            await ctx.send(f"*Sound `{basename[:-4]}` does not exist. You piece of shit.*")
            return
        sound_path = sound_path_mp3
        basename = basename_mp3
    if not os.path.exists(sound_path) and not WINDOWS:
        await ctx.send(f"*'{basename}' is missing CAPS somewhere. You piece of shit.*")
        return

    PLAYING[ctx.guild.id] = True
    lcount = 0
    
    max_duration = 5 * 60
    if delay > max_duration:
        max_duration = 2 * delay + 20
    
    start_time = asyncio.get_event_loop().time()
    
    await ctx.send(f"Looping `{soundname}` with delay {delay}. Why are you doing this?")
    
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
            
            with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'a') as file:
                file.write(basename + '\n')
            with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'a') as file:
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


@bot.command(help="Stops playing sounds.")
async def stop(ctx):
    global PLAYING, STOP_EVENT
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("Did you press the stop button?")
    
    PLAYING[ctx.guild.id] = False      
    STOP_EVENT[ctx.guild.id].set()         
    ctx.voice_client.stop()

@stop.error
async def stop_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Joins user's voice channel.")
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("*You are not connected to a voice channel. You piece of shit.*")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await ctx.send("Won't be a problem.")
        await channel.connect()
        await ctx.send(f'Joined {channel}.')
    else:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f'Moved to {channel}')
    
    await bot.change_presence(activity=discord.Game(name="some MUSIC"))


@join.error
async def join_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    
        
@bot.command(help="Joins desired voice channel. Does not require user to be connected. ADMIN COMMAND.")
@commands.has_permissions(administrator=True)
async def troll(ctx, *, chName: str):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
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
        await ctx.send("Won't be a problem.")
        await channel.connect()
        await ctx.send(f'Trolling {channel}.')
    else:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f'Moved to {channel}')
        
    await bot.change_presence(activity=discord.Game(name="some MUSIC"))

@troll.error
async def troll_error(ctx, error):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("No.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify a channel name.\n\n Example: `!troll general`")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Leaves the current voice channel and displays sessions stats.")
async def leave(ctx):   
    global PLAYING, STOP_EVENT
    
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    PLAYING[ctx.guild.id] = False      
    STOP_EVENT[ctx.guild.id].set()         
    ctx.voice_client.stop()
    await ctx.send("Won't be a problem.")
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

@bot.command(help="Displays full soundlist in alphabetical order.")
async def soundlist(ctx):
    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(ctx.guild.id) + "/all_sounds/"
    
    try:
        lines = os.listdir(SOUNDS_FOLDER_PATH)
    except FileNotFoundError:
        await ctx.send("*Sounds folder does not yet exist for this server.*")
    
    sorted_lines = sorted(lines, key = str.lower)
    output = '\n'.join(sorted_lines)
    numSounds = len(lines)
    chunk_size = 1994

    if numSounds == 0:
        await ctx.send("*You have no sounds saved!*")
        return

    await ctx.send(f"### **List of all `{numSounds}` soundboard sounds:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(f"```{output[i:i + chunk_size]}```")

@soundlist.error
async def soundlist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    

@bot.command(help="Displays sound playcount stats for this session. Session stats delete upon bot leaving.")
async def sessionstats(ctx):
    try:
        with open(SERVERS_PATH + str(ctx.guild.id) + '/session_stats.txt', 'r') as file:
            lines = file.readlines()
        
        shortened_lines = [s.strip() for s in lines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 1994
        num = len(lines)

        await ctx.send("## **Bot soundboard stats for this session:** \n\n")
        await ctx.send(f"### Playcount: `{num}` \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(f"```{output[i:i + chunk_size]}```")
    except FileNotFoundError:
        await ctx.send("*No stats for this session yet!*")

@sessionstats.error
async def sessionstats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")
    

@bot.command(help="Displays sound playcount stats for all time.")
async def alltimestats(ctx):
    try:
        with open(SERVERS_PATH + str(ctx.guild.id) + '/all_time_stats.txt', 'r') as file:
            lines = file.readlines()
        
        shortened_lines = [s.strip() for s in lines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
        
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 1994
        num = len(lines)

        await ctx.send("## **Bot soundboard stats for all time:** \n\n")
        await ctx.send(f"### Playcount: `{num}` \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(f"```{output[i:i + chunk_size]}```")
    except FileNotFoundError:
        await ctx.send("*No stats yet! Use `!s`, `!play`, or `!playfast` to start tracking playcount stats.*")

@alltimestats.error
async def alltimestats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help='Adds a message trigger (if message CONTAINS trigger, bot will respond). Usage: !addtrigger "<trigger>" "<response>". ADMIN COMMAND.')
@commands.has_permissions(administrator=True)
async def addtrigger(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            await ctx.send('Usage: `!addtrigger "<trigger>" "<response>"`')
            return
        
        trigger, response = parts
        
        with open(SERVERS_PATH + str(ctx.guild.id) + '/triggers.txt', 'a') as file:
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

@bot.command(help='Removes a message trigger. Usage: !removetrigger "<trigger>". ADMIN COMMAND.')
@commands.has_permissions(administrator=True)
async def removetrigger(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 1:
            await ctx.send('Usage: `!removetrigger "<trigger>"`')
            return
        
        trigger = parts[0]
        triggers = load_triggers(SERVERS_PATH + str(ctx.guild.id) + '/triggers.txt')
        
        if trigger in triggers:
            with open(SERVERS_PATH + str(ctx.guild.id) + '/triggers.txt', 'r') as file:
                lines = file.readlines()
            with open(SERVERS_PATH + str(ctx.guild.id) + '/triggers.txt', 'w') as file:
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


@bot.command(help="Displays all triggers and their responses, sorted alphabetically by triggers.")
async def triggerlist(ctx):
    triggers = load_triggers(SERVERS_PATH + str(ctx.guild.id) + '/triggers.txt')
    
    if not triggers:
        await ctx.send("*No triggers found.*")
        return

    sorted_triggers = sorted(triggers.items())
    output = "\n".join([f"{trigger}: {response}" for trigger, response in sorted_triggers])
    chunk_size = 1994

    await ctx.send(f"## **List of all `{len(triggers)}` triggers and their responses:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(f"```{output[i:i + chunk_size]}```")

@triggerlist.error
async def triggerlist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help='Use to note down a good loop time. Usage: !addloop "<sound name>" "<delay>". ADMIN COMMAND.')
@commands.has_permissions(administrator=True)
async def addloop(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            await ctx.send('Usage: `!addloop "<sound name>" "<delay>"`')
            return
        
        soundname, delay = parts
        
        with open(SERVERS_PATH + str(ctx.guild.id) + '/loops.txt', 'a') as file:
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

@bot.command(help='Removes a saved loop time. Usage: !removeloop "<sound name>". ADMIN COMMAND.')
@commands.has_permissions(administrator=True)
async def removeloop(ctx, *, args: str):
    try:
        parts = shlex.split(args)
        if len(parts) != 1:
            await ctx.send('Usage: `!removeloop "<sound name>"`')
            return
        
        soundname = parts[0]
        loops = load_triggers(SERVERS_PATH + str(ctx.guild.id) + '/loops.txt')
        
        if soundname in loops:
            with open(SERVERS_PATH + str(ctx.guild.id) + '/loops.txt', 'r') as file:
                lines = file.readlines()
            with open(SERVERS_PATH + str(ctx.guild.id) + '/loops.txt', 'w') as file:
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


@bot.command(help="Displays all saved loop infos, sorted alphabetically by sound name.")
async def looplist(ctx):
    loops = load_triggers(SERVERS_PATH + str(ctx.guild.id) + '/loops.txt')
    
    if not loops:
        await ctx.send("*No loops found.*")
        return

    sorted_loops = sorted(loops.items())
    output = "\n".join([f"{soundname}: {delay}" for soundname, delay in sorted_loops])
    chunk_size = 1994

    await ctx.send(f"## **List of all `{len(loops)}` sounds with saved loop info:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(f"```{output[i:i + chunk_size]}```")

@looplist.error
async def looplist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: `{error}`*")



# -------------- owner commands --------------

@bot.command(help="Displays desired number of lines of log file output. Default 20 lines. OWNER COMMAND.")
@commands.is_owner()
async def logs(ctx, lines: int = 20):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    
    log_file_path = 'output.log'
    chunk_size = 1994

    try:
        with open(log_file_path, 'r') as file:
            log_content = file.readlines()

        recent_log_content = log_content[-lines:]
        output = ''.join(recent_log_content)

        await tchannel.send("## **Recent logs from output.log:** \n\n")
        
        for i in range(0, len(output), chunk_size):
            await tchannel.send(f"```{output[i:i + chunk_size]}```")
            
    except FileNotFoundError:
        await tchannel.send("*The log file does not exist. You piece of shit.*")
    except Exception as e:
        await tchannel.send(f"*An error occurred while reading the log file: {e}*")

@logs.error
async def logs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")  


@bot.command(help="Displays entire log file output. OWNER COMMAND.")
@commands.is_owner()
async def alllogs(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    log_file_path = 'output.log'
    chunk_size = 1994
    
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()

        await tchannel.send("## **Contents of output.log:** \n\n")
        
        for i in range(0, len(log_content), chunk_size):
            await tchannel.send(f"```{log_content[i:i + chunk_size]}```")
            
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


@bot.command(help="Pulls changes from github repo and restarts if necessary. OWNER COMMAND.")
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
        SOUNDS_FOLDER_PATH = SERVERS_PATH + str(guild.id) + "/all_sounds/"
        sounds = os.listdir(SOUNDS_FOLDER_PATH)
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
                    SOUNDS_FOLDER_PATH = SERVERS_PATH + str(guild.id) + "/all_sounds/"
                    oldCount = len(sounds)
                    
                    sounds_new = os.listdir(SOUNDS_FOLDER_PATH)
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
            
        await tchannel.send("Updates pulled successfully. They did not affect `bot.py`.")
    
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


@bot.command(help="Pushes text file(s) updates to github repo. OWNER COMMAND.")
@commands.is_owner()
async def pushtextfiles(ctx):
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
            "**Staging** changes for `output.log` and all servers' `all_time_stats.txt`, `triggers.txt`, `loops.txt`, and `config.txt` files...")
        subprocess.run(["git", "add", "output.log"], check=True)
        for guild in bot.guilds:
            guild_path = "servers/" + str(guild.id) + "/"
            subprocess.run(["git", "add", guild_path + "all_time_stats.txt", guild_path + "triggers.txt", guild_path + "loops.txt", guild_path + "config.txt"], check=True)

        await tchannel.send("*Checking if changes actually exist...*")
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            await tchannel.send("*No changes to commit for all text files.*")
            return

        await tchannel.send("*Changes exist!*\n\n" + "**Committing** updates...")
        commit_result = subprocess.run(["git", "commit", "-m", "Update text files"], capture_output=True, text=True, check=True)
        await tchannel.send(f"```{commit_result.stdout or commit_result.stderr}```")
        
        await tchannel.send("*Updates committed!*\n\n" + "**Pushing** updates to github repo...")
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)

        output = result.stdout if result.stdout else result.stderr
        await tchannel.send(f"```{output}```")
        await tchannel.send("**Updates pushed successfully!**")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else "An error occurred, but no error message was provided."
        await tchannel.send(f"Error pushing updates: {error_message}")
    except Exception as e:
        await tchannel.send(f"An unexpected error occurred: {str(e)}")

@pushtextfiles.error
async def pushtextfiles_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: `{error}`*")


@bot.command(help="Displays the servers in which the bot exists and the voice channels to which it is connected. OWNER COMMAND.")
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


@bot.command(help="Restarts the bot. OWNER COMMAND.")
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
                channel = vc.channel.guild.system_channel or vc.channel.guild.text_channels[0]
                await channel.send(f"*Disconnected from voice channel: `{vc.channel.name}`. Bot owner is restarting the bot.*")
            
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


@bot.command(help="Shuts down the bot. OWNER COMMAND.")
@commands.is_owner()
async def kys(ctx):
    if ctx.guild.id != HOME_SERVER_ID:
        await ctx.send("*This command can only be used in the bot's home server.*")
        return
    if ctx.channel.id != HOME_CHANNEL_ID:
        await ctx.send("*This command can only be used in the bot's home channel.*")
        return
    
    if not WINDOWS:
        await ctx.send("*First, invoking `!pushtextfiles`:*")
        await ctx.invoke(bot.get_command('pushtextfiles'))
    
    for vc in bot.voice_clients:
        if vc.is_connected():
            vc.stop()
            await vc.disconnect()
            
            if vc.channel.guild.id != HOME_SERVER_ID:
                channel = vc.channel.guild.system_channel or vc.channel.guild.text_channels[0]
                await channel.send(f"*Disconnected from voice channel: `{vc.channel.name}`. Bot owner has shut down the bot.*")
                
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
