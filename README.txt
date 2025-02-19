-------------------------------------------------------------------------
			DISCORD BOT INSTRUCTIONS
-------------------------------------------------------------------------

-------------------------------------------------------------------------
Section 1: How to set up a free GCP server for your bot
-------------------------------------------------------------------------


1. Set up a GCP Compute Engine (free tier: https://cloud.google.com/free/docs/free-cloud-features#free-tier).

   Then connect your VM instance via SSH window.

-------------------------------------------------------------------------

2. Install python:

-> sudo apt update
-> sudo apt install python3-venv

-------------------------------------------------------------------------

3. Create a virtual python environment for the bot:

-> python3 -m venv myenv

-------------------------------------------------------------------------

4. Activate the environment and then install dependencies to it (discord.py, pynacl, asyncio, etc.):

-> source myenv/bin/activate

-> pip install discord.py pynacl asyncio

-------------------------------------------------------------------------

5. Install other dependencies to your server (I need ffmpeg and git):

-> sudo apt install ffmpeg -y

-> sudo apt install git -y (if you want to keep your bot updated with git)



-------------------------------------------------------------------------
Section 2: Other SSH Window instructions - Once the bot.py script exists
-------------------------------------------------------------------------


1. to activate the virtual python environment that has the dependencies installed for the discord bot, use the following command:

-> source myenv/bin/activate

-------------------------------------------------------------------------

2. to start the bot use:

-> nohup python bot.py >> output.log 2>&1 &

    nohup → Keep running after disconnecting.
    python bot.py → Runs your Discord bot.
    >> output.log → Appends logs to output.log.
    2>&1 → Include error messages in the same log file.
    & → Run in the background.

-------------------------------------------------------------------------

3. to kill the script, simply create and use a shutdown command in discord (might have to be bot owner).

   **OR** use the following in the SSH window:

-> pkill -f bot.py

    **OR** find the script with:
	
-> ps aux | grep bot.py

   Explanation of Each Column:
	USER: The user who owns the process (lucassu+).
	PID: The process ID (e.g., 103710, 103711, 103813).
	%CPU: The percentage of CPU usage.
	%MEM: The percentage of memory usage.
	VSZ: The virtual memory size.
	RSS: The resident set size (physical memory usage).
	TTY: The terminal associated with the process (? for none, pts/1 for a pseudo-terminal).
	STAT: The process state (e.g., S for sleeping, R for running).
	START: The start time of the process.
	TIME: The cumulative CPU time used by the process.
	COMMAND: The command that started the process.

   and then take the 4digit number it gives at the start and do: 

-> kill *number here*

-------------------------------------------------------------------------

4. to view logs, create and use a bot command in discord. Or use in SSH window:

-> tail -f output.log

-------------------------------------------------------------------------

5. to delete a folder, use:

-> rm -r foldername

   to delete a single file, just use:

-> rm filename.ext

   you can also add as many file names as you want, separated by a space

-------------------------------------------------------------------------

6. to add a new file to a folder (probably a new .ogg sound file to add to all_sounds), use:

-> mv sound.ogg all_sounds/



-------------------------------------------------------------------------
Section 3: How to use git in your VM SSH Window (github)
-------------------------------------------------------------------------


1. IF YOUR GITHUB REPO IS PRIVATE, use an SSH deploy key to connect your bot to your repo.

   i) Generate an SSH key in your VM SSH window:
   
   -> ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

      Press enter to save it in the default path (/home/youruser/.ssh/id_rsa). Press enter twice more to save without a passphrase.

   ii) Display then copy the public key:

   -> cat ~/.ssh/id_rsa.pub

      Copy the output. 

   iii) Add the key as a Deploy Key in GitHub: 

      Go to your repo in Github > Settings > Deploy Keys > Add Deploy Key. 
      Add a title, then paste the key under Key. Allow write access if you want. Click Add Key.

   iv) Test the connection in your SSH window: 

   -> ssh -T git@github.com

      Enter "yes" if prompted to do so.

      You should see the following message: 

      "Hi! You've successfully authenticated, but GitHub does not provide shell access."

-------------------------------------------------------------------------

2. Clone your repository: 

-> git clone git@github.com:yourusername/yourbot.git

-------------------------------------------------------------------------

3. To pull changes, navigate to the repo folder in your VM (-> cd folder) and use:

-> git pull origin main

-------------------------------------------------------------------------

4. To check the status of your repo use:

-> git fetch

-> git status

   If you are up to date, it will show the following:

   "On branch main
    Your branch is up to date with 'origin/main'."

-------------------------------------------------------------------------

5. Set your global git user email and username identity:

-> git config --global user.email "you@example.com"

-> git config --global user.name "Your Name"

-------------------------------------------------------------------------

6. Create a bot command in your script to update your bot.

@bot.command()
@commands.is_owner()
async def update(ctx):
    await ctx.send("Pulling latest updates from github...")

    try:
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)

        await ctx.send(f"```{result.stdout or result.stderr}```")

        if "Already up to date." in result.stdout:
            await ctx.send("*No updates found. Bot is already up to date!*")
            return

        await ctx.send("Update complete! Restarting bot...")

        await bot.close()

        command = "bash -c 'source /home/USERNAME/myenv/bin/activate && nohup python3 bot.py >> output.log 2>&1 &'"
        subprocess.Popen(command, shell=True) 
            
        sys.exit()
    
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Error pulling updates: {e.stderr.decode()}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("# No.")
    else:
        await ctx.send(f"*An unexpected error occurred: {error}*")

-------------------------------------------------------------------------
