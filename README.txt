-------------------------------------------------------------------------
Scuffed Discord Bot Instructions - How To Run From Windows Command Line
-------------------------------------------------------------------------

0. Install Python if you don't have it already, make sure you can run python scripts from the command line. Also install ffmpeg.

1. Download & extract discord_bot.zip (should be a folder called discord_bot)

2. Open the discord_bot folder and copy the path (should look something like C:\Users\urname\Desktop\discord_bot)

3. Open a command prompt window (Windows Key + R, run cmd)

4. Change the directory to the path you copied, use cd (change directory) command, should look like this:
	
	> cd C:\Users\urname\Desktop\discord_bot

-------------------------------------------------------------------------

OPTIONAL: STEPS 5-8

Sets up a virtual Python environment (this means the dependencies you install will only be installed to this specific environment, not to your global Python interpreter) 

TLDR: It's good practice, but if you don't care it doesn't really matter.


5. 	> python -m venv discord_bot_venv

6. 	> cd discord_bot_venv\Scripts

7. 	> activate

8. If everything's good, you should see (discord_bot_venv) to the left of your new line. Now change the directory back to discord_bot, simply go up 2 levels like this:

	> cd ..
	> cd .. 

-------------------------------------------------------------------------

9. Install dependencies:

	> pip install discord.py pynacl asyncio ffmpeg

9. Now run the script:

	> python bot.py

10. Bot should now be running for as long as you want (must keep the command prompt window open)

11. To stop running it, simply press CTRL + C in the command line (or close the command prompt window, but this seems a bit more scuffed)

-------------------------------------------------------------------------





-------------------------------------------------------------------------
Scuffed Discord Bot Instructions - GCP Compute Engine VM SSH Window
-------------------------------------------------------------------------

1. to activate the virtual python environment that has the dependencies installed for the discord bot, use the following command:

-> source myenv/bin/activate

-------------------------------------------------------------------------

2. to start the bot use:

-> nohup python bot.py > output.log 2>&1 &

nohup → Keep running after disconnecting.
python bot.py → Runs your Discord bot.
> output.log → Save logs to output.log.
2>&1 → Include error messages in the same log file.
& → Run in the background.

-------------------------------------------------------------------------

3. to kill the script, find it with:

-> ps aux | grep bot.py

and then take the 4digit number it gives at the start and do 

-> kill *number here*

**OR** simply use the !kys command in discord (must be bot owner).
**OR** pkill -f bot.py

-------------------------------------------------------------------------

4. to view logs, use:

-> tail -f output.log

-------------------------------------------------------------------------

5. to delete a folder (probably the all_sounds folder), use:

-> rm -r all_sounds

   to delete a single file (probably bot.py), just use:

-> rm filename.ext

   you can also add as many file names as you want, separated by a space

-------------------------------------------------------------------------

6. to add a new file to a folder (probably a new .ogg sound file to add to all_sounds), use:

-> mv sound.ogg all_sounds/
