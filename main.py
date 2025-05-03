import json
import requests
import time
import random
from datetime import datetime, timedelta
import sys
import configparser
import os

# Path to the external config file
config_path = "config.ini"

# Check if the config file exists
if not os.path.exists(config_path):
    print(f"Error: {config_path} not found!")
    exit()

# Load the INI configuration
config = configparser.ConfigParser()
config.read(config_path)

# Retrieve configuration values
try:
    # Strings
    utc_offset = config.get('settings', 'utc_offset')
    input_token = config.get('settings', 'input_token')
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
except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
    print(f"Error reading configuration: {e}")
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

def end():
    input("\nPress enter to close this window: ")
    sys.exit()
    

def countdown_time(seconds):
    for rerun_scripting in range(seconds, 0, -1):
        print(f"Awaiting next message  [00:{rerun_scripting:02}]", end="\r")
        time.sleep(1)
    # Ends the countdown at 00:00, doesn't serve any purpose, it just looks better in the code
    print("Awaiting next message  [00:00]", end="\r") 

    # Clear the message by overwriting with spaces
    print(" " * 50, end="\r")

def get_utc_offset():
    while True:
        try:
            local_time_str = input("Enter your current time in the proper format (HH:MM AM/PM): ")

            now_utc = datetime.utcnow()

            local_time = datetime.strptime(local_time_str, "%I:%M %p")

            local_datetime = datetime.combine(now_utc.date(), local_time.time())

            if local_datetime > now_utc:
                local_datetime -= timedelta(days=1)

            time_difference = local_datetime - now_utc

            hours = time_difference.total_seconds() / 3600
            rounded_hours = int(hours)
            utc_offset = f"{rounded_hours:+03d}:00"

            print(f'Your UTC offset is {utc_offset}. Set this in the script and rerun.')
            end()

        except ValueError:
            print("Invalid format! Please enter the time in HH:MM AM/PM format.")

def get_time(utc_offset):
    try:
        offset_hours, offset_minutes = map(int, utc_offset.split(':'))
        offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        now_utc = datetime.utcnow()
        now_local = now_utc + offset
        current_time = f"{now_local:%H:%M:%S}.{now_local.microsecond // 1000:03}"
        return current_time
    except ValueError:
        print('The inputted UTC offset is unrecognizable. Check config.py and make sure it is in the correct format.')
        end()
        


# Defines the function to scrape discord messages: Credits to Codium
def retrieve_messages(channelid):
    headers = {
        'authorization': input_token
    }
    r = requests.get(
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
    
def format_time(unformatted_run_time):
    parts = str(unformatted_run_time).split(':')  # Splits into [hours, minutes, seconds.microseconds]
    parts1 = parts[2].split('.')

    run_time = f"{int(parts[0]):01} hours, {int(parts[1]):01} minutes, {int(parts1[0]):01} seconds, {int(parts1[1])} microseconds"
    return run_time

def run_script():

    times_run = 0
    if any(value < 0 for value in (min_sleep, max_sleep, min_active, max_active)):
        print('One or more of your values are invalid. This can be caused if a value is negative or left blank.')
        end()
    while(True):
        try:
            if check_for_last_msg:
                # Retrieves messages from the channel provided
                r = retrieve_messages(input_channel)

                # retrieve info about the last sender
                nickname = r[0]['author']['global_name']
                username = r[0]['author']['username']
                user_id = r[0]['author']['id']

                # if the user's message is not the last, terminate the program
                if(input_userid != user_id):
                    end_time_str = get_time(utc_offset)

                    start_time = datetime.strptime(start_time_str, "%H:%M:%S.%f") # Converting to datetime
                    end_time = datetime.strptime(end_time_str, "%H:%M:%S.%f")

                    unformatted_run_time = end_time - start_time
                    run_time = format_time(unformatted_run_time)

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

            # makes a random time for each message to send and delete, (hopefully) prevents detection
            random_sleep = random.randint(min_sleep, max_sleep)
            
            times_run = times_run + 1

            if delete_message: # deletes the message 
                random_active = random.randint(min_active, max_active)/10
                time.sleep(random_active)
                channel.delete_message(message_id)
                print(f'Message {times_run} was active for {random_active} seconds. Next message in {random_sleep} seconds.')
            else: 
                print(f'Message {times_run} was sent. Next message in {random_sleep} seconds.')

            countdown_time(random_sleep)
        except Exception as e:
            print('An error occured. imma be honest how did you get here :skull:')
            end()

if not utc_offset or utc_offset == "-0:00":
    print('You haven\'t set your UTC offset yet! If you don\'t know it, use this to figure it out.')
    get_utc_offset()

start_time_str = get_time(utc_offset)
print(f"Program started at [{start_time_str}]")


run_script()