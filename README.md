# Welcome to my discord bot template!

I originally created this bot with the sole purpose of using it to play custom soundbites since unboosted Discord servers only allow a maximum number of 8 sounds on the soundboard. I used to run the bot locally on my own machine and it did its simple job well enough.

Over time, I gradually implemented more and more features, and eventually it got sophisticated enough that I decided to move it to the cloud (I am running it on a free tier GCP Compute Engine VM) so that it could run 24/7. Nowadays it does much more than just play stupid sounds.

I've created this public repository to serve as the cleaned-up, ready to use template of the monstrosity that I still update in my original private repo.

## Here's a list of some of the features of this bot which are all accessible through bot commands in Discord:

### soundboard
-users can upload/download custom sounds for/from their server

-bot can play sounds in voice channels: random selections or specified selections on regular time intervals or randomized time intervals

-can loop sounds at desired time interval, can save loop time interval data for future use

-can play sequences of sounds, can save sequence data for future use

-tracks playcount stats for each sound by individual sessions and by all-time (by server)

### text channel fun
-users can set message trigger-response pairs such that the bot will instantly reply with a response to any message that contains the trigger

-by default, and this is something I will never remove for my own instance of the bot, it has a 1/13 chance on every user-sent message to reply telling you to shut up

-of course, the shut up stats are tracked to see who has the worst luck in each server and there is a command to display these stats

### config
-server admins can configure certain settings for the bot (e.g. default text channel, default bot message when a certain command is invoked, etc.)

-while there are not currently many configurable settings, the code has been written such that it would be very easy to add more

### roles
-the bot can generate a special emoji-reactable message which allows users to self-assign server roles

-server admins can set role-emoji pairs such that a reaction with a specific emoji will have the bot assign the user a specific role

### QoL developer commands (owner only)
-shutdown command

-restart command (starts a new process for the bot's script and then shuts down)

-update command (pulls changes from the remote repo and then restarts)

-command for pushing data (stats, sound files, etc) from the bot's connected Discord servers to the remote repo

-git force push command

-git hard reset command

-logs command for displaying log file output

-status command to display the servers in which the bot exists and which voice channels it's in

### other QoL stuff
-can be added to many discord servers and work simultaneously in all of them (it is only limited by the VM's resources, so maybe not 1000 servers at once)

-auto-disconnects from a voice channel once everyone else disconnects

-times out from voice channels after 60 minutes of inactivity

-times out the !play command after 60 minutes

-has a maximum of 30 sounds at a time for intervals of <5 seconds (5 seconds between the start of one sound and the start of another) with the intention of not breaking the bot

-displays a custom Discord activity status by default and a different one when connected to a voice channel

-displays data from text files as messages in 2000 char chunks (Discord's character limit) and formats such that it does not split up lines


## Note
Just to give you an idea of how much my Discord server has used this bot: 

In less than 1 year, the bot has nearly 30000 total sound plays and we've uploaded nearly 300 custom sounds for our server (so much for the built-in soundboard's limit of 8).
