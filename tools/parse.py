from telethon.sync import TelegramClient
from time import sleep
from loguru import logger
import sqlite3

logger.remove()
logger.add("./log/parser.log", rotation="500 MB")


def get_last_message(api_id: int, api_hash: str, links: list):
    with TelegramClient('parse_session', api_id, api_hash) as client:
        messages = []
        logger.info(f'Extracting messages')
        for link in links:
            try:
                logger.info(f"Proccesed {links.index(link)}/{len(links)}")
                chat_username = link.split('/')[-2]
                chat = client.get_entity(chat_username)
                last_messages = client.get_messages(chat, limit=10)
                i=0
                for msg in last_messages:
                    sender = client.get_entity(msg.from_id)
                    if sender and sender.username and '_bot' not in sender.username:
                        message_data = {
                            "text": msg.message,
                            "user": sender.username,
                            "chat": link
                        }
                        i+=1
                        messages.append(message_data)
                logger.success(f"Found {i} messages")
            except Exception as e:
                continue
        return {"messages": messages}


def get_api_params():
    logger.info("Reading Telegram API params")
    try:
        with open('./config/api', 'r') as cfg_file:
            lines = cfg_file.readlines()
            for line in lines:
                if line.split('=')[0] == 'api_hash':
                    api_hash = line.split('=')[1]
                if line.split('=')[0] == 'api_id':
                    api_id = line.split('=')[1]
                if line.split('=')[0] == 'token':
                    token = line.split('=')[1]
            if api_hash and api_id and token:
                logger.success('Successfully get params')
                return {'api_id': int(api_id), 'api_hash': api_hash, 'token': token}
            logger.error(f'Could not read one or more properties')
    except Exception as err:
        logger.error(f'Could not read properties from file: \n{err}')

def write_to_db(data):
    logger.info(f'Trying to write [{data}] to ./tmp/messages.db')
    try:
        conn = sqlite3.connect('./tmp/messages.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO data (text, user, chat) VALUES ('{data['text']}','{data['user']}','{data['chat']}')")
        conn.commit()
        conn.close()
    except Exception as err:
        logger.error(f'Could not write to db: \n{err}')

def get_messages():
    params = get_api_params()
    api_id = params['api_id']
    api_hash = params['api_hash']

    logger.info(f'Reading ./config/links')
    with open('./config/links', 'r') as links_file_r:
        links = links_file_r.readlines()
        return(get_last_message(api_id, api_hash, links))


if __name__ == "__main__":
    params = get_api_params()
    api_id = params['api_id']
    api_hash = params['api_hash']
    #sleep(30)
    while True:
        with open('./config/links', 'r') as links_file_r:
            links = links_file_r.readlines()
            res = get_last_message(api_id, api_hash, links)
            for i in res['messages']:
                try:
                    write_to_db(i)
                except Exception:
                    continue

            
        sleep(30)