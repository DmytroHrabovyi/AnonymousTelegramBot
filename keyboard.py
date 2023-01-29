from telebot import types
from text_messages import markup_commands, bot_messages


class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    def main_menu(self, chat):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(markup_commands['search_dialogue'])
        self.bot.send_message(chat.id, bot_messages['choose_menu_button'], reply_markup=markup)

    def search_dialogue_menu(self, chat):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(markup_commands['stop_search'])
        self.bot.send_message(chat.id, bot_messages['search_dialogue_on'], reply_markup=markup)

    def dialogue_menu(self, chat):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(markup_commands['stop_dialogue'])
        markup.row(markup_commands['ask_question'])
        self.bot.send_message(chat.id, bot_messages['dialogue_on'], reply_markup=markup)
