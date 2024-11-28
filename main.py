import sqlite3
from threading import Thread
from time import sleep
from tools.parse import get_api_params
from tools.bot import Bot
from loguru import logger

logger.remove()
logger.add("./log/bot.log", rotation="500 MB")

def read_from_db():
    try:
        logger.info("Reading unsent messages ./tmp/messages.db")
        conn = sqlite3.connect('./tmp/messages.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT text, user, chat FROM data WHERE is_resent = 0")
        data = cursor.fetchall()
        if data:
            logger.success(f"Got unsent message '{data[0][:5]}...' from user {data[1]}")
        else:
            logger.info(f"No new messages")
        conn.close()
        return data
    except Exception as err:
        logger.error(f"Could not read from DB:\n{err}")


def update_db(text):
    try:
        logger.info(f"Set message '{text[:5]}...' as sent")
        conn = sqlite3.connect('./tmp/messages.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE data set is_resent = 1 WHERE text = '{text}'")
        logger.success("Successfully updated")
        conn.commit()
        conn.close()
    except Exception as err:
        logger.error(f"Could update DB:\n{err}")


def monitor(bot):
    while True:
        with open('./config/keywords', 'r', encoding='utf-8') as keywords_file:
            messages = read_from_db()
            keywords = keywords_file.readlines()
            logger.info(f"Get {len(messages)} new messages\nChecking for keywords:")
            for line in messages:
                for key in keywords:
                    if key in line[0]:
                        try:
                            logger.success(f"Got message with keyword: '{line[0][:5]}...' from user @{line[1]}")
                            msg = {"text": line[0], "user": line[1], "chat": line[2]}
                            logger.success(f"Resend to chat: {bot.chat_id}")
                            bot.notificate(msg)
                            update_db(msg['text']) 
                        except Exception as err:
                            logger.error(f"Error: {err}")
        logger.info('Sleep until next iteration (1 min)...')
        sleep(60)                      


def main():
    data = get_api_params()
    bot = Bot(data)
    sniffThread = Thread(target=monitor, args=[bot])
    sniffThread.start()
    bot.run()


if __name__ == "__main__":
    main()