# arcanefarm
A python script made to automate leveling up in servers. Although being specifically developed for Arcane, it can theoretically work as a XP grinder for other bots as well.

KEEP IN MIND THAT USING THIS SCRIPT VIOLATES DISCORD'S TOS. USE AT YOUR OWN RISK.

Arcane is a discord bot known for its leveling system. Here's how it works:

Arcane gives a random amount of XP to a user at a specific cooldown, every 1 minute. It does not reward the user for sending messages within this cooldown, and deleted messages still count towards XP. This script allows you to send messages at a customized interval and delete your messages automatically. Additionally, the script can detect the presence of another member in the server, which will make the bot immediately stop running.

I do not gather any of the info you enter. The code is open source, so feel free to look through it.

## Features
- Automated message sending with customizable intervals.
- Configurable deletion of sent messages after a random time. Deleted messages still count towards XP.
- Checks the last message sender to prevent conflicts.
- Completely customizable configuration file for user settings.

## How to use

1. Once you download and unzip the folder, you should see a config.ini and a main.exe file.
2. Open config.ini with Notepad FIRST and configure your settings. Please read all the comments in that file to make sure no issues occur!

Static variables:

| `input_token`            | Too complicated to explain how to get it here, search it up. 

| `input_channel`       | Obtainable with developer mode on discord. 

| `input_userid`     | Obtainable with developer mode on discord. 

| `utc_offset`       | The code has built in functions to find your utc offset.  

All other variables are customizable to your liking. I made it very clear how to set these, so you shouldn't have any problems. 

I recommend setting the intervals between messages to be around 1 minute (Arcane's cooldown on messages) to maintain efficiency.

3. Once all variables have been defined, save the file and open main.exe. If you did it right, you now have a working XP farmer!


## Credits

Deleting and sending messages: https://www.youtube.com/watch?v=p-AqYm4IiU4

Scraping channels: https://www.youtube.com/watch?v=xh28F6f-Cds

Everything else is pretty much written by me. 


