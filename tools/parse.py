from telethon.sync import TelegramClient
from json import dump
import codecs

def get_last_message(api_id: int, api_hash: str, links: list):
    with TelegramClient('parse_session', api_id, api_hash) as client:
        messages = []
        for link in links:
            try:
                print(f"Proccesed {links.index(link)}/{len(links)}")
                chat_username = link.split('/')[-2]
                chat = client.get_entity(chat_username)
                last_message = client.get_messages(chat, limit=1)
                if last_message and last_message[0].sender and last_message[0].sender.username:
                    message_data = {
                        "text": last_message[0].message,
                        "user": last_message[0].sender.username,
                        "chat": link
                    }
                    print(f"Found message from {message_data['user']}")
                    messages.append(message_data)
            except Exception as e:
                continue
        return {"messages": messages}


def get_api_params():
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
            return {'api_id': int(api_id), 'api_hash': api_hash, 'token': token}


if __name__ == "__main__":
    params = get_api_params()
    api_id = params['api_id']
    api_hash = params['api_hash']

    with open('./config/links', 'r') as links_file_r:
        links = links_file_r.readlines()
        res = get_last_message(api_id, api_hash, links)
    with codecs.open("./tmp/messages.json", "w", "utf-16") as outfile:
        dump(res, outfile, ensure_ascii=False)
