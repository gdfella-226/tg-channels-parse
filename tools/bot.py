import requests
import telebot
import re
import codecs
from telebot.types import ReplyKeyboardMarkup
from telebot import types
from time import sleep
from json import load
from tools.parse import get_api_params
from tools.update_links import update


class Bot:
    def __init__(self, ext_data: dict) -> None:
        self.data = ext_data
        self.bot = telebot.TeleBot(self.data["token"])
        self.keybord = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Menu")
        self.awaitKeyword = False
        self.chat_id = None
        self.message_handler()
        self.callback_handler()


    def generate_keywords_markup(self):
        keywords_markup = types.InlineKeyboardMarkup()
        keywords_markup.add(
            types.InlineKeyboardButton('\N{clipboard} Add keyword', callback_data="add_keyword"),
            types.InlineKeyboardButton('\N{clipboard} Clear', callback_data="clear"),
            types.InlineKeyboardButton('\N{leftwards arrow with hook} Back', callback_data="back"))
        return keywords_markup

    def generate_menu_markup(self):
        menu_markup = types.InlineKeyboardMarkup()
        menu_markup.add(
            types.InlineKeyboardButton('\N{globe with meridians} Add chat', callback_data="add_link"),
            types.InlineKeyboardButton('\N{clipboard} Keywords', callback_data="menu"),
            types.InlineKeyboardButton('\N{clipboard}' +  'Reload', callback_data="run")
                        )
        #'\N{repeat button}' +  
        return menu_markup


    def message_handler(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.chat_id = message.chat.id
            self.bot.send_message(message.chat.id, 'Hello message', parse_mode='Markdown', reply_markup=self.keybord)        

        @self.bot.message_handler(func=lambda message: message.text == 'Menu')
        def show_menu(message):
            self.chat_id = message.chat.id
            self.bot.send_message(chat_id=message.chat.id, text="Main menu",
                                           reply_markup=self.generate_menu_markup())

        @self.bot.message_handler(func=lambda message: re.match(r'^https://t.me/\w+/$', message.text))
        def add_chat(message):
            self.chat_id = message.chat.id
            update(message.text)
            self.bot.send_message(message.chat.id, 'Added new chat to listen', reply_markup=self.generate_menu_markup())

        @self.bot.message_handler(func=lambda message: message.text and self.awaitKeyword)
        def add_keyword(message):
            self.chat_id = message.chat.id
            with open('./config/keywords', 'a', encoding='utf-8') as keywords:
                    keywords.write('\n' + message.text)
                    self.awaitKeyword = False
            self.bot.send_message(message.chat.id, 'Added new keyword to string', reply_markup=self.generate_menu_markup())


    def callback_handler(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            self.chat_id = call.message.chat.id
            if call.data == "menu":
                with open('./config/keywords', 'r', encoding='utf-8') as keywords:
                    kws = ''.join(keywords.readlines())
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text=f"*Keywords menu*\n\n```Your current keywords:\n{kws}```\n\n"+ 
                                           "- \"__Add keyword__\" press and send new keyword\n" + 
                                           "- \"__Clear__\" remove all keywords from list", 
                                           parse_mode='Markdown', reply_markup=self.generate_keywords_markup())
            elif call.data == "back":
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text="Main menu",
                                           reply_markup=self.generate_menu_markup())
            elif call.data == "add_keyword":
                self.awaitKeyword = True

            elif call.data == "add_link":
                print(call.message.chat.id, self.chat_id)
                with codecs.open("./tmp/messages.json", "r", "utf-16") as infile:
                    msgs = load(infile)
                    if msgs:
                        self.notificate(msgs["messages"][0])
            
            elif call.data == "clear":
                with open('./config/keywords', 'w', encoding='utf-8') as keywords:
                    keywords.write('')
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="All keywords have been removed",
                                        reply_markup=self.generate_menu_markup())
                
            
    def notificate(self, data):
        self.bot.send_message(self.chat_id, f'<b>New tracked message!</b>\nIn chat: {data["chat"]}\nFrom user: @{data["user"]}\n\nMessage text:\n<blockquote>{data["text"]}</blockquote>',
                              parse_mode='HTML', reply_markup=self.keybord)


    def run(self):
        try:
            self.bot.polling(none_stop=True)
        except requests.exceptions.ConnectionError as err:
            sleep(5)
            self.run()

if __name__ == "__main__":
    data = get_api_params()
    bot = Bot(data)
    bot.run()