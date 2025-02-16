from discord.ext import commands
import discord
import asyncio
import random
import os
import sys
import subprocess
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
        await tchannel.send("*running locally on Windows*")


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
    
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("*Invalid command. You piece of shit.*")
    else:
        await ctx.send(f"An unexpected error occurred: {error}")

    
@bot.command(help="Raises hands in correct order.")
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
    
@raisehand.error
async def raisehand_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")    
    
    
@bot.command(help="Raises hands in random order.")
async def randomhand(ctx):
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
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Displays full soundlist in alphabetical order.")
async def soundlist(ctx):
    global SOUNDS
    numSounds = len(SOUNDS)
    lines = os.listdir(SOUNDS_FOLDER_PATH)
    sorted_lines = sorted(lines, key = str.lower)
    output = '\n'.join(sorted_lines)
    chunk_size = 1994

    await ctx.send(f"### **List of all {numSounds} soundboard sounds:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(f"```{output[i:i + chunk_size]}```")

@soundlist.error
async def soundlist_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Plays full dewey fired scene.")
async def dewey(ctx):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("You're fired")
    sound_path = SOUNDS_FOLDER_PATH + SLASH + "dewey full scene.mp3"
    
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda e: print(f'Finished playing: {e}'))

@dewey.error
async def dewey_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Plays desired sound.")
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

@s.error
async def s_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Plays random sounds at desired time interval. Default 90s.")
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

@play.error
async def play_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Stops playing sounds.")
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("*I am not connected to a voice channel. You piece of shit.*")
        return
    
    await ctx.send("Did you press the stop button?")
    
    global playing
    playing = False               
    ctx.voice_client.stop()

@stop.error
async def stop_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


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

@join.error
async def join_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")
    
        
@bot.command(help="Joines desired voice channel. ADMIN COMMAND.")
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
async def troll_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("There is no way into the mountain.")


@bot.command(help="Leaves the current voice channel.")
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

@leave.error
async def leave_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Displays current session playcount.")
async def count(ctx):
    global playcount
    await ctx.send(f"### **Playcount this session: {str(playcount)}**")
    
@count.error
async def count_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Displays sound playcount stats for this session. Session stats delete upon bot leaving.")
async def sessionstats(ctx):
    try:
        with open('session_stats.txt', 'r') as file:
            lines = file.readlines()
        
        shortened_lines = [s.strip() for s in lines]
        counter = Counter(shortened_lines)
        
        sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
        stuff = [f'{item}: {count}' for item, count in sorted_items]
        output = '\n'.join(stuff)
        
        chunk_size = 1994

        await ctx.send("## **Bot soundboard stats for this session:** \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(f"```{output[i:i + chunk_size]}```")
    
    except FileNotFoundError:
        await ctx.send("*No stats for this session yet!*")

@sessionstats.error
async def sessionstats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")
    

@bot.command(help="Displays sound playcount stats for all time.")
async def alltimestats(ctx):
    with open('all_time_stats.txt', 'r') as file:
        lines = file.readlines()
    
    shortened_lines = [s.strip() for s in lines]
    counter = Counter(shortened_lines)
    
    sorted_items = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    
    stuff = [f'{item}: {count}' for item, count in sorted_items]
    output = '\n'.join(stuff)
    
    chunk_size = 1994

    await ctx.send("## **Bot soundboard stats for all time:** \n\n")
    
    for i in range(0, len(output), chunk_size):
        await ctx.send(f"```{output[i:i + chunk_size]}```")

@alltimestats.error
async def alltimestats_error(ctx, error):
    await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Displays desired number of lines of log file output. Default 20 lines. OWNER COMMAND.")
@commands.is_owner()
async def logs(ctx, lines: int = 20):
    log_file_path = 'output.log'
    chunk_size = 1994

    try:
        with open(log_file_path, 'r') as file:
            log_content = file.readlines()

        recent_log_content = log_content[-lines:]
        output = ''.join(recent_log_content)

        await ctx.send("## **Recent logs from output.log:** \n\n")
        
        for i in range(0, len(output), chunk_size):
            await ctx.send(f"```{output[i:i + chunk_size]}```")
            
    except FileNotFoundError:
        await ctx.send("*The log file does not exist. You piece of shit.*")
    except Exception as e:
        await ctx.send(f"*An error occurred while reading the log file: {e}*")

@logs.error
async def logs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")  


@commands.is_owner(help="Displays entire log file output. OWNER COMMAND.")
@bot.command()
async def alllogs(ctx):
    log_file_path = 'output.log'
    chunk_size = 1994
    
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()

        await ctx.send("## **Contents of output.log:** \n\n")
        
        for i in range(0, len(log_content), chunk_size):
            await ctx.send(f"```{log_content[i:i + chunk_size]}```")
            
    except FileNotFoundError:
        await ctx.send("*The log file does not exist.*")
    except Exception as e:
        await ctx.send(f"*An error occurred while reading the log file: {e}*")

@alllogs.error
async def alllogs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")  


@bot.command(help="Sends the output.log file in discord. OWNER COMMAND.")
@commands.is_owner()
async def sendlogfile(ctx):
    log_file_path = 'output.log'

    try:
        with open(log_file_path, 'r') as file:
            await ctx.send("Here is the log file:", file=discord.File(file, log_file_path))
    except FileNotFoundError:
        await ctx.send("*The log file does not exist.*")
    except Exception as e:
        await ctx.send(f"*An error occurred while reading the log file: {e}*")

@sendlogfile.error
async def sendlogfile_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Pulls changes from github repo and restarts if necessary. OWNER COMMAND.")
@commands.is_owner()
async def update(ctx):
    global SOUNDS
    await ctx.send("Pulling latest updates from github...")

    try:
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)

        await ctx.send(f"```{result.stdout or result.stderr}```")

        if "Already up to date." in result.stdout:
            await ctx.send("*No updates found. Bot is already up to date!*")
            return

        if "all_sounds" in result.stdout:
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

        if "bot.py" in result.stdout:
            await ctx.send("Update complete.")

            await ctx.invoke(bot.get_command('restart'))
            
        await ctx.send("Updates pulled successfully. They did not affect bot.py nor all_sounds/.")
    
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Error pulling updates: {e.stderr}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")  


@bot.command(help="Pushes output.log and all_time_stats.txt to github repo. OWNER COMMAND.")
@commands.is_owner()
async def pushtextfiles(ctx):
    await ctx.send("Fetching latest changes from GitHub...")

    try:
        subprocess.run(["git", "fetch"], capture_output=True, text=True, check=True)

        status_result = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
        if "Your branch is behind" in status_result.stdout:
            await ctx.send("*There are changes on the remote repository, idiot. Update then try again.*")
            return

        await ctx.send("Pushing updates for *output.log* and *all_time_stats.txt* to GitHub...")

        subprocess.run(["git", "add", "output.log", "all_time_stats.txt"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            await ctx.send("No changes to commit for *output.log* and *all_time_stats.txt*.")
            return

        commit_result = subprocess.run(["git", "commit", "-m", "Update output.log and all_time_stats.txt"], capture_output=True, text=True, check=True)
        await ctx.send(f"```{commit_result.stdout or commit_result.stderr}```")

        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)

        output = result.stdout if result.stdout else result.stderr
        await ctx.send(f"```{output}```")
        await ctx.send("Updates pushed successfully!")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else "An error occurred, but no error message was provided."
        await ctx.send(f"Error pushing updates: {error_message}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@pushtextfiles.error
async def pushtextfiles_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Restarts the bot. OWNER COMMAND.")
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting...")

    try:
        await bot.close()

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

        if WINDOWS:
            subprocess.Popen("python bot.py", shell=True)
        else:
            command = "bash -c 'source /home/lucassukeunkim/myenv/bin/activate && nohup python3 bot.py >> output.log 2>&1 &'"
            subprocess.Popen(command, shell=True) 
    
        sys.exit()
        
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@restart.error
async def restart_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")


@bot.command(help="Shuts down the bot. OWNER COMMAND.")
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
async def kys_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")    


bot.run(BOT_TOKEN, reconnect=True)
