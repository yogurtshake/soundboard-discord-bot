from discord.ext import commands
import discord
import random
import os
import sys
import asyncio
from collections import Counter

BOT_TOKEN = "MzU3NjgzMTI2MDY5MzYyNjkw.GugV8Q.GbB2VVNp1BmKt0BktRglikOvke6KIejHjoi47A"
TEXT_CHANNEL_ID = 1337536863640227881
WINDOWS = False

if "\\" in os.getcwd(): 
    SOUNDS_FOLDER_PATH = os.getcwd().replace("\\", "/") + '/all_sounds'
    WINDOWS = True
else: 
    SOUNDS_FOLDER_PATH = os.getcwd() + '/all_sounds'
SLASH = "/" 
SOUNDS = [line.lower() for line in os.listdir(SOUNDS_FOLDER_PATH)]

playing = False
handcount = 0
playcount = 0

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Atyiseusseatyiseuss!")
    tchannel = bot.get_channel(TEXT_CHANNEL_ID)
    await tchannel.send("**Atyiseusseatyiseuss!**")
    if WINDOWS:
        await tchannel.send("*scuffed ass Windows*")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
    
    elif "both" in message.content or "two" in message.content:
        await message.channel.send("**BOTH OF YOU!**")
    elif "music" in message.content:
        await message.channel.send("My feeling is: if we're gonna win this thing, we gotta actually start playing some MUSIC.")
    elif "gimme " in message.content:
        await message.channel.send("Last chance. GoOOo0oOooOo!")
    elif "send " in message.content or " send" in message.content:
        await message.channel.send("Hah! What, so you can send secret messages to your sexy bitches? No, sir.")
    elif "not " in message.content:
        await message.channel.send("Not the best choice.")
    elif "six " in message.content or " six" in message.content:
        await message.channel.send("At a push seven")
    elif "yes " in message.content or " yes" in message.content:
        await message.channel.send("## **YES!**")
    elif "key " in message.content or " key" in message.content:
        await message.channel.send("If there is a key, there must be a door.")
    elif " or " in message.content:
        await message.channel.send("I think I'll take the first part")
    elif message.content == "scoring chicks":
        await message.channel.send("That's it!")
    elif "getting wasted" in message.content:
        await message.channel.send("YES!")
    elif message.content == "sticking it to the man":
        await message.channel.send("Wrong! Shuddup.")   
    elif "harvey dent" in message.content :
        await message.channel.send("# **Richard Patrick**") 
    elif message.content == "you must be mr. bond" or message.content == "you must be mr. boba fett" or message.content == "you must be mr. bobomb":
        await message.channel.send("Nope!") 
    elif message.content == "you must be mr. bobobo bobo":
        await message.channel.send("Nope Nope!")
    elif "wait" in message.content:
        await message.channel.send("Move on.") 
    elif message.content == "give me another chance":
        await message.channel.send("Last chance. GoOOo0oOooOo!")
    elif message.content == "we shall pee":
        await message.channel.send("WHEN YOU ANSWER FOR THE BURNING OF THE CHILDREN OF THE BODIES OF THE SOLDIERS OF THE WESTFOLD")
        await message.channel.send("WHEN THE SOLDIERS")
        await message.channel.send("WHOSE BODIES LAY DEAD AGAINST THE GATES OF THE HORNBURG")
        await message.channel.send("ARE DEAD")
        await message.channel.send("when you hang from a chimichim")
        await message.channel.send("WE SHALL PEE.")
    elif message.content == "be careful of what?":
        await message.channel.send("Your friend Palpatine. I just told you.")    
    else:
        num = random.randint(0,4)
        if num == 0:
            num2 = random.randint(0,4)
            if num2 == 0:
                await message.channel.send('# **Wrong! Shuddup.**')
            else: 
                await message.channel.send('**Wrong! Shuddup.**')
    
    
@bot.command()
async def raisehand(ctx):
    global handcount
    if handcount % 3 == 0:
        m = "Frankie?"
    elif handcount % 3 == 1:
        m = "Lenny?"
    else:
        m = "Leonard?"
    await ctx.send(m)
    handcount += 1
    
    
@bot.command()
async def randomhand(ctx):
    num = random.randint(0,2)
    if num == 0:
        m = "Frankie?"
    elif num == 1:
        m = "Lenny?"
    else:
        m = "Leonard?"
    await ctx.send(m)


@bot.command()
async def soundlist(ctx):
    lines = os.listdir(SOUNDS_FOLDER_PATH)
    sorted_lines = sorted(lines, key = str.lower)
    output = '\n'.join(sorted_lines)
    chunk_size = 2000

    await ctx.send("### **List of all soundboard sounds:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(output[i:i + chunk_size])
    

@bot.command()
async def dewey(ctx):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("You're fired")
    sound_path = SOUNDS_FOLDER_PATH + SLASH + "dewey full scene.mp3"
    
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {e}'))
    

@bot.command()
async def s(ctx, *name):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    input = ' '.join(name)
    
    sound_path = SOUNDS_FOLDER_PATH + SLASH + input + ".ogg"
    basename = sound_path.split('/')[-1].strip()

    if not basename.lower() in SOUNDS:
        await ctx.send(f"*'{basename}' does not exist. You piece of shit.*")
        return
    elif not os.path.exists(sound_path) and not WINDOWS:
        await ctx.send(f"*'{basename}' is missing CAPS somewhere. You piece of shit.*")
        return


    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))

    with open('session_stats.txt', 'a') as file:
        file.write(basename + '\n')
    with open('all_time_stats.txt', 'a') as file:
        file.write(basename + '\n')


@bot.command()
async def play(ctx, *arr):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    files = os.listdir(SOUNDS_FOLDER_PATH)
    
    global playcount
    global playing
    playing = True
    
    await ctx.send("I've been sittin on some awesome material")
    while playing:    
        
        if len(arr) > 0 and isinstance(float(arr[0]), float) and float(arr[0]) < 0.1:
            await ctx.send("Don't do less than 0.1 you scoundrel")
            break
        elif len(arr) == 1 and isinstance(float(arr[0]), float):
            delay = float(arr[0])
        elif len(arr) >= 2 and isinstance(float(arr[0]), float) and isinstance(float(arr[1]), float) and float(arr[0]) > float(arr[1]):
            delay = random.randint(float(arr[0]), float(arr[1]))
        else:
            delay = 90
        
        sound_path = SOUNDS_FOLDER_PATH + SLASH + random.choice(files)
        basename = sound_path.split('/')[-1].strip()
        
        ctx.voice_client.stop()
        
        if basename.endswith((".ogg", ".mp3")):
            ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {basename}'))
            await asyncio.sleep(delay)
            
            with open('session_stats.txt', 'a') as file:
                file.write(basename + '\n')
            with open('all_time_stats.txt', 'a') as file:
                file.write(basename + '\n')
                
            playcount += 1


@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("Did you press the stop button?")
    
    global playing
    playing = False               
    ctx.voice_client.stop()


@bot.command()
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
        
        
@bot.command()
@commands.has_permissions(administrator=True)
async def troll(ctx, *, chName: str):
   
    if(chName.lower() == "private"): id = 265210092289261570
    elif(chName.lower() == "general"): id = 134415388233433090
    elif(chName.lower() == "poor man's general"): id = 212770924607438848
    elif(chName.lower() == "poverse general"): id = 1234341517041078383
    elif(chName.lower() == "harvey dent"): id = 1339030117430853708
    else: id = 134415388233433090

    channel = bot.get_channel(id)
    
    if ctx.voice_client is None:
        await ctx.send("Won't be a problem.")
        await channel.connect()
        await ctx.send(f'Trolling {channel}.')
    else:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f'Moved to {channel}')

@troll.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("There is no way into the mountain.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.send("Won't be a problem.")
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        
    file_path = 'session_stats.txt'

    try:
        os.remove(file_path)
        await ctx.send("*Session stats deleted.*")
        print(f"{file_path} has been deleted successfully.")
    except FileNotFoundError:
        print(f"{file_path} does not exist.")
    except PermissionError:
        print(f"Permission denied: unable to delete {file_path}.")
    except Exception as e:
        print(f"Error: {e}")


@bot.command()
async def count(ctx):
    global playcount
    await ctx.send(f"### **Playcount this session: {str(playcount)}**")


@bot.command()
async def sessionstats(ctx):
    try:
        with open('session_stats.txt', 'r') as file:
            lines = file.readlines()
        
        shortened_lines = [s.strip() for s in lines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 2000

        await ctx.send("## **Bot soundboard stats for this session:** \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(output[i:i + chunk_size])
    
    except FileNotFoundError:
        await ctx.send("*No stats for this session yet!*")
    

@bot.command()
async def alltimestats(ctx):
    with open('all_time_stats.txt', 'r') as file:
        lines = file.readlines()
    
    shortened_lines = [s.strip() for s in lines]
    counter = Counter(shortened_lines)
    
    sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
    stuff = [f'{item}: {count}' for item, count in sorted_items]
    output = '\n'.join(stuff)
    
    chunk_size = 2000

    await ctx.send("## **Bot soundboard stats for all time:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(output[i:i + chunk_size])


@bot.command()
async def refresh(ctx):
    global SOUNDS
    
    oldCount = len(SOUNDS)
    SOUNDS_NEW = [line.lower() for line in os.listdir(SOUNDS_FOLDER_PATH)]
    newCount = len(SOUNDS_NEW)
    
    if oldCount == newCount:
        await ctx.send(f"*No new sounds to add. Current soundlist count: {newCount}.*")
   
    elif newCount > oldCount: 
        difference = list(set(SOUNDS_NEW) - set(SOUNDS))
        difference_str = '\n'.join(difference)
        
        if newCount - oldCount == 1: word = "sound"
        else: word = "sounds"
        
        await ctx.send(f"### Soundlist refreshed: **{newCount - oldCount}** new {word} added. Current soundlist count: {newCount}.\n\n**New sounds:**\n{difference_str}")
    
    elif newCount < oldCount:
        difference = list(set(SOUNDS) - set(SOUNDS_NEW))
        difference_str = '\n'.join(difference)
        
        if oldCount - newCount == 1: word = "sound"
        else: word = "sounds"
        
        await ctx.send(f"### Soundlist refreshed: **{oldCount - newCount}** {word} removed. Current soundlist count: {newCount}.\n\n**Removed sounds:**\n{difference_str}")
    
    SOUNDS = SOUNDS_NEW


@bot.command()
@commands.is_owner()
async def logs(ctx, lines: int = 20):
    log_file_path = 'output.log'
    chunk_size = 2000

    try:
        with open(log_file_path, 'r') as file:
            log_content = file.readlines()

        recent_log_content = log_content[-lines:]
        output = ''.join(recent_log_content)

        await ctx.send("## **Recent logs from output.log:** \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(output[i:i + chunk_size])
    except FileNotFoundError:
        await ctx.send("*The log file does not exist. You piece of shit.*")
    except Exception as e:
        await ctx.send(f"*An error occurred while reading the log file: {e}*")

@logs.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")  


@commands.is_owner()
@bot.command()
async def alllogs(ctx):
    log_file_path = 'output.log'
    chunk_size = 2000
    
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()

        await ctx.send("## **Contents of output.log:** \n\n")
        
        for i in range(0, len(log_content), chunk_size):
            await ctx.send(log_content[i:i + chunk_size])
    except FileNotFoundError:
        await ctx.send("*The log file does not exist.*")
    except Exception as e:
        await ctx.send(f"*An error occurred while reading the log file: {e}*")

@alllogs.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")  


@bot.command()
@commands.is_owner()
async def kys(ctx):
    await ctx.send("So uncivilized. Shutting down...")
    
    file_path = 'session_stats.txt'

    try:
        os.remove(file_path)
        await ctx.send("*Session stats deleted.*")
        print(f"{file_path} has been deleted successfully.")
    except FileNotFoundError:
        print(f"{file_path} does not exist.")
    except PermissionError:
        print(f"Permission denied: unable to delete {file_path}.")
    except Exception as e:
        print(f"Error: {e}")
    
    await bot.close()
    sys.exit()
    
@kys.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")    


bot.run(BOT_TOKEN, reconnect=True)
