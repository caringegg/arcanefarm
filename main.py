# 1.2.0 NOTES
# Confirmation screen finally allows you to see the channel name
# Bugfixing 
# Safelist not showing up properly
# User error handling problem fixed
# bug that prevented users from setting `check_for_last_msg` and `delete_message` false
# config.ini debug statement: type "config_path" in the confirmation screen to get the path to the ini file

import json
import requests
import time
import random
from datetime import datetime, timedelta
import sys
import configparser
import os

def end(): # prevents the window from automatically closing, acts as exit()
    input("\nPress enter to close this window: ")
    sys.exit()
    
# Dynamically locate config.ini in the same directory as the script or executable
base_path = os.path.dirname(sys.argv[0])
config_path = os.path.join(base_path, "config.ini")

# Check if the config file exists
if not os.path.exists(config_path):
    print(f"Error: The config.ini file was not found in the expected location: {config_path}")
    end()

# Load the INI configuration
config = configparser.ConfigParser()
config.read(config_path)
# Retrieve configuration values
try:
    # Strings
    utc_offset = config.get('settings', 'utc_offset')
    input_token = config.get('settings', 'input_token')
    bot_token = config.get('settings', 'bot_token')
    input_channel = config.get('settings', 'input_channel')
    input_userid = config.get('settings', 'input_userid')
    input_message = config.get('settings', 'input_message')
    check_for_last_msg = config.getboolean('settings', 'check_for_last_msg')
    delete_message = config.getboolean('settings', 'delete_message')

    # Integer values
    min_sleep = config.getint('settings', 'min_sleep')
    max_sleep = config.getint('settings', 'max_sleep')
    min_active = config.getint('settings', 'min_active')
    max_active = config.getint('settings', 'max_active')

    # Lists
    safelist = config.get('settings', 'safelist').strip().split(',')
except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e: # error handling
    print(f"Error: {e}")
    exit(1)



# selfbot class: Credits to Max Tan
class selfbot:
    def __init__(self, token):
        self.__class__.token = token
        self.__class__.header = {"authorization": self.token}

    class get_channel:
        def __init__(self, id):
            self.channel_id = id

        def send_message(self, message):
            url = f'https://discord.com/api/v8/channels/{self.channel_id}/messages'
            data = {
                "content": message
                }

            r = requests.post(url, json=data, headers=selfbot.header)

            return r.json()['id']

        def delete_message(self, message_id):
            url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}"

            r = requests.delete(url, headers=selfbot.header)

def countdown_time(seconds): # prints a countdown to the terminal
    for rerun_scripting in range(seconds, 0, -1):
        print(f"Sending {input_message} in [00:{rerun_scripting:02}]", end="\r")
        time.sleep(1)
    # Ends the countdown at 00:00, doesn't serve any purpose, it just looks better in the code
    print(f"Sending {input_message} in [00:00]", end="\r") 

    # Clear the message by overwriting with spaces
    print(" " * 50, end="\r")

def get_utc_offset(): # getting utc offset, which is useful for some stuff
    while True:
        try:
            local_time_str = input("Enter your current time in the proper format (HH:MM AM/PM): ")

            now_utc = datetime.utcnow()

            local_time = datetime.strptime(local_time_str, "%I:%M %p")

            local_datetime = datetime.combine(now_utc.date(), local_time.time())

            if local_datetime > now_utc: 
                local_datetime -= timedelta(days=1)

            time_difference = local_datetime - now_utc 

            hours = time_difference.total_seconds() / 3600 # rounding to the nearest time
            rounded_hours = int(hours)
            utc_offset = f"{rounded_hours:+03d}:00"

            print(f'Your UTC offset is {utc_offset}. Set this in the script and rerun.')
            end()

        except ValueError: 
            print("Invalid format! Please enter the time in HH:MM AM/PM format.")

def get_time(utc_offset): # getting the current local time based on utc offset
    try:
        offset_hours, offset_minutes = map(int, utc_offset.split(':'))
        offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        now_utc = datetime.utcnow()
        now_local = now_utc + offset
        current_time = f"{now_local:%H:%M:%S}.{now_local.microsecond // 1000:03}"
        return current_time
    
    except ValueError:
        print('The inputted UTC offset is unrecognizable. Check config.py and make sure it is in the correct format. If you are not sure of your UTC offset, leave it blank and run the file again.')
        end()
        

def format_time(unformatted_run_time): # formats '[xx:xx:xx.xxx]' to 'xx hours, xx minutes, xx seconds, xxx microseconds'
    parts = str(unformatted_run_time).split(':')
    parts1 = parts[2].split('.')

    run_time = f"{int(parts[0]):01} hours, {int(parts[1]):01} minutes, {int(parts1[0]):01} seconds, {int(parts1[1])} microseconds"
    return run_time

def fetch_username(user_id): # uses the bot token to find the corresponding name for a user ID
    url = f"https://discord.com/api/v10/users/{user_id}"
    headers = {
        "Authorization": f"Bot {bot_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data['username']
        if username:
            return username # Ex: '123456' -> 'name'
        else:
            return "Unknown"
    else:
        return "Unknown"
def retrieve_messages(channelid): # Defines the function to scrape discord messages: Credits to Codium
    headers = {
        'authorization': input_token
    }
    r = requests.get( # makes a request to the channel with the authorization token provided
         f"https://discord.com/api/v9/channels/{channelid}/messages", headers=headers)
    # Possible error messages 
    if r.status_code != 200:
        if r.status_code == 401: 
            print("Token invalid or expired.")
        elif r.status_code == 403:
            print("You have no permission to access this channel.")
        elif r.status_code == 404:
            print("Channel not found. Double check the channel you inputted is correct")
        else:
            print(f"An error occurred: {r.status_code} - {r.reason}")
        end()

    msg_list = json.loads(r.text)
    return msg_list 
        
def fetch_channel_name(channelid): # uses basically same code as the above function
    headers = {
        'authorization': input_token
    }
    r = requests.get( # makes a request to the channel with the authorization token provided
         f"https://discord.com/api/v9/channels/{channelid}", headers=headers)
    # Possible error messages 
    if r.status_code != 200:
        if r.status_code == 401: 
            print("Token invalid or expired.")
        elif r.status_code == 403:
            print("You have no permission to access this channel.")
        elif r.status_code == 404:
            print("Channel not found. Double check the channel you inputted is correct")
        else:
            print(f"An error occurred: {r.status_code} - {r.reason}")
        end()
 
    channel_name = r.json()['name']

    return channel_name

        

def get_safelist_with_names(safelist): # The argument is a list of IDs. The function adds the name to the correct user ID
    result = []
    for user_id in safelist:
        name = fetch_username(user_id)
        result.append(f"{user_id} ({name})")
    result = ' '.join(", ".join(result).split())
    return result  # Ex: ['userid1', 'userid2'] -> 'userid1 (Bob), userid2 (Jeff)'

def run_script(): # all functions are run
    start_time_str = get_time(utc_offset)
    times_run = 0

    while True: # the actual loop for sending messages
        try:
            if check_for_last_msg: # if the user wants to check for last message

                # scrape the channel 
                r = retrieve_messages(input_channel)

                # get only the last chatter's user ID
                last_messager_id = r[0]['author']['id']

                # If the last user is not part of the safelist, go to next part of testing. otherwise, pass
                if last_messager_id not in safelist:
                    # If the last user is not me, shut down. otherwise if it is me, continue sending messages
                    if input_userid != last_messager_id:
                        # if the script got here it means the script shuts down. 
                        end_time_str = get_time(utc_offset)

                        start_time = datetime.strptime(start_time_str, "%H:%M:%S.%f") # Converting to datetime
                        end_time = datetime.strptime(end_time_str, "%H:%M:%S.%f")

                        unformatted_run_time = end_time - start_time

                        run_time = format_time(unformatted_run_time)

                        # gather additional info about the last chatter
                        nickname = r[0]['author']['global_name']
                        username = r[0]['author']['username']

                        # an "end screen" is made
                        print(f'Program has been ended by {username}, also known as {nickname}')
                        print(f'Program was running for {run_time}.')
                        print(f'You successfully sent {times_run} messages!')
                        end()
        
            # If we have continued here, this means the last message is still sent by the user.  
            # This means we can continue the loop.

            token = input_token
            bot = selfbot(token=token)
            channel = bot.get_channel(input_channel)
            message_id = channel.send_message(input_message) # sends message and gets the message id

            # gets current time
            current_time = get_time(utc_offset)

            # self explanatory
            times_run = times_run + 1

            random_sleep = random.randint(min_sleep, max_sleep)

            if delete_message: # deletes the message 
                random_active = random.randint(min_active, max_active)/10
                time.sleep(random_active)
                channel.delete_message(message_id)
                print(f'[{current_time}] Message {times_run} deleted in {random_active} seconds. Next message in {random_sleep} seconds.')
            else: 
                print(f'[{current_time}] Message {times_run} was sent. Next message in {random_sleep} seconds.')
            
            if random_sleep > 1: 
                countdown_time(random_sleep)
            else: # theres no point doing a countdown if the interval between messages is under a second
                time.sleep(random_sleep)
        except Exception as e:
            print(f'{e}') # error
            end()

# Possible errors the user made in config.ini
if not utc_offset or utc_offset == "-0:00":
    print('You haven\'t set your UTC offset yet! If you don\'t know it, use this to figure it out.')
    get_utc_offset()
if any(value < 0 for value in (min_sleep, max_sleep, min_active, max_active)): 
    print('Why did bro put a NEGATIVE number for a time duration. ')
    end()
if not all([input_token, input_channel, input_userid, input_message, min_sleep, max_sleep]):
    print('A variable that was necessary to run was left blank.')
    end()

# Confirmation screen
print('Confirm settings:\n')
print(f'Message to be sent: {input_message}')
print(f'Message will be sent in: {fetch_channel_name(input_channel)}')
print(f'Check for last message: {check_for_last_msg}')
if check_for_last_msg:
    if bot_token:
        print(f'Safelist: {get_safelist_with_names(safelist)}') 
    else:
        print(f'Safelist: {", ".join(safelist)}')
print(f'Interval between messages: {min_sleep} - {max_sleep} seconds')
print(f'Delete messages: {delete_message}')
if delete_message:
    print(f'Time before message deletion: {min_active/10} - {max_active/10} seconds')
if input(f'\nPress enter to confirm and run the program: ') == "config_path": # quick debugging statement if you need to find the location of config.ini
    print(config_path)
    input('')

run_script()