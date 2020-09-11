from telethon import TelegramClient, events, sync
import time
import math
import os
import itertools
from telethon.tl.functions.channels import GetParticipantsRequest

from  telethon import  functions
import logging
logging.basicConfig(level=logging.DEBUG)


######## VARS ########
api_id = 0000000
api_hash = str(os.environ.get("TGHASH"))

# Big dict with all messages all_messages_database
all_db = []
delay_time_before_next_chat = 10
minuts_after_last_post_for_blacklist = 10000
chats_file = "chats_test.txt"
keywords_file = "keywords.txt"
result_file_name = "result.txt"
blacklist_file_name = "blacklist.txt"
debug = False #if true skip NEW_POSTS AND skip Send to CRM

print(api_hash)

#######START CLIENT
client = TelegramClient('session_name2', api_id, api_hash)
client.start()

client.action(entity=)

#Read files with chats and keywords

file_chats = open(chats_file, "r")
read_file_chats = file_chats.read()
chats_list = read_file_chats.split("\n")
print(chats_list)

file_keywords = open(keywords_file, "r")
read_file_keywords = file_keywords.read()
keywords_list = read_file_keywords.split("\n")
print(keywords_list)
## Clean result file
with open("result.txt", 'tw', encoding='utf-8') as f:
    pass




async def read_chats_first():
    for chat in chats_list:
        #Get first info about chats and channels
        channel_entity = await client.get_entity(chat)
        channel_id = channel_entity.to_dict()['id']
        channel_title = channel_entity.to_dict()['title']
        channel_name = channel_entity.to_dict()['username']


        #Get info about last post
        last_post = await client.get_messages(chat, limit=1)
        last_post_id, last_post_message, last_post_date, time_after_last_post = post_info(last_post)
        skip = skip_constructor(time_after_last_post)



        if time_after_last_post < minuts_after_last_post_for_blacklist:
            print('sucess!')

            new_chat_to_db = {
                'skip': skip,
                'channel_id': channel_id,
                'channel_title': channel_title,
                'channel_name': channel_name,
                'last_post_id': last_post_id,
                'last_post_message': last_post_message,
                'last_post_date': last_post_date
            }
            all_db.append(new_chat_to_db)
            print(all_db)
            with open(result_file_name, 'a', encoding='utf-8') as f:
                f.write(str(new_chat_to_db) + "\n")

            #check and send to CRM
            check_keys_and_send_to_crm(last_post)

        else:
            print('blacklist!')
            with open(blacklist_file_name, 'a', encoding='utf-8') as f_bl:
                f_bl.write(str(channel_name) +";"+ str(time_after_last_post) + "\n")

        time.sleep(delay_time_before_next_chat)





async def read_chats_after():
    print("length:", len(all_db))
    # Iterate  all good chats
    for chat in itertools.cycle(all_db):
        print("========================Rot===============================")
        if chat['skip'] <= 0:
            print(chat)
            if not debug:
                #Get one new post
                last_post = await client.get_messages(chat, limit=1)
                last_post_id, last_post_message, last_post_date, time_after_last_post = post_info(last_post)
                skip = skip_constructor(time_after_last_post)

                #Count how many new posts apear
                count_posts = int(last_post_id) - int(chat['last_post_id'])
                print("NEW POSTS IN CHAT >>> ", count_posts)

                if count_posts <= 0:
                    chat['skip'] = skip
                elif count_posts == 1:
                    check_keys_and_send_to_crm(last_post)
                else:
                    print("get", count_posts, "posts")
                    new_posts = await client.get_messages(chat['channel_name'], limit = count_posts)
                    for post in new_posts:
                        check_keys_and_send_to_crm(last_post)

        else:
            print("chat_skip - 1", chat['skip']," ",chat['skip']-1)
            chat['skip'] -= 1
            continue
        time.sleep(delay_time_before_next_chat)


async def check_keys_and_send_to_crm(msg):
    if not debug:
        for key in keywords_list:
            if key.lower() in msg.message.lower():
                await client.forward_messages('dotparsed', msg)
                print("message sended to CRM with key: ", key)


# convert last post
def skip_constructor(last_post_time):
    if last_post_time < 10:
        return 0
    elif last_post_time < 30:
        return 1
    else:
        return 100


def post_info(post):
    post_id = post[0].id
    post_message = post[0].message
    post_date_time = post[0].date.timestamp()
    time_after_post = math.floor((time.time() - post_date_time) / 60)
    return post_id, post_message, post_date_time, time_after_post


async def main_f():
    await read_chats_first()
    await read_chats_after()


while client:
    client.loop.run_until_complete(main_f())



