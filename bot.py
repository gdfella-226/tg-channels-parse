import requests
import telebot
import re
from telebot.types import ReplyKeyboardRemove
from telebot import types
from time import sleep
from os import listdir
from os.path import isfile, join
from json import load
from tools.parse import get_api_params, get_last_message
from tools.update_links import update


class Bot:
    def __init__(self, ext_data: dict) -> None:
        self.data = ext_data
        self.bot = telebot.TeleBot(self.data["token"])
        self.message_handler()
        self.callback_handler()


    def generate_keywords_markup(self):
        keywords_markup = types.InlineKeyboardMarkup()
        keywords_markup.add(
            types.InlineKeyboardButton('\N{clipboard} Добавить ключевое слово', callback_data="add_keyword"),
            types.InlineKeyboardButton('\N{clipboard} Очистить ключевые слова', callback_data="clear"),
            types.InlineKeyboardButton('\N{leftwards arrow with hook} Назад', callback_data="back"))
        return keywords_markup

    def generate_menu_markup(self):
        menu_markup = types.InlineKeyboardMarkup()
        menu_markup.add(
            types.InlineKeyboardButton('\N{globe with meridians} Добавить ссылку', callback_data="add_link"),
            types.InlineKeyboardButton('\N{clipboard} Настроить ключевые слова', callback_data="menu"),
            types.InlineKeyboardButton('\N{clipboard}' +  'Старт / Перезапуск', callback_data="run")
                        )
        #'\N{repeat button}' +  
        return menu_markup


    def message_handler(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id, 'Хелло месседж', parse_mode='Markdown', reply_markup=self.generate_menu_markup())        
            
        
        '''@self.bot.message_handler(func=lambda message: message.text)
        def photo_enter(message):
            self.bot.send_message(message.chat.id, 'xuy')'''

    def callback_handler(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.data == "menu":
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text="edit keywords",
                                           reply_markup=self.generate_keywords_markup())
            elif call.data == "back":
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text="main menu",
                                           reply_markup=self.generate_menu_markup())
            


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