import telebot
from state_machine import State, StateMachine
from keyboard import Keyboard
from connection_manager import ConnectionManager
from api_key import API_KEY
from question_manager import QuestionManager
from text_messages import bot_messages, markup_commands


bot = telebot.TeleBot(API_KEY)
question_manager = QuestionManager()
connection_manager = ConnectionManager()
keyboard = Keyboard(bot)
user_current_state = {}
content_types = [
    'text', 'photo', 'document', 'sticker', 'audio', 'voice', 'video', 'video_note',
    'contact', 'dice', 'game', 'poll', 'invoice', 'pinned_message',
    'successful_payment', 'connected_website', 'location', 'venue', 'animation'
]


@bot.message_handler(commands=['ask'])
def ask_question(message):
    connection = connection_manager.get_connection(message.chat.id)
    text = message.text[5:]
    if connection is None:
        return

    if len(text) < 1:
        bot.send_message(message.chat.id, bot_messages['answer_empty'])
        return

    for user in connection.users:
        if user != message.chat.id:
            bot.send_message(user, bot_messages['question'].format(question=text))


@bot.message_handler(commands=['answer'])
def answer_question(message):
    connection = connection_manager.get_connection(message.chat.id)
    user_message = message.text[8:]
    if connection is None:
        return

    if len(user_message) < 1:
        bot.send_message(message.chat.id, bot_messages['answer_empty'])
        return

    if question_manager.has_answers(connection.users):
        for user in connection.users:
            for user2 in connection.users:
                if user2 != message.chat.id:
                    bot.send_message(user, question_manager.get_answer(user2))


@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.chat.id not in user_current_state:
        user_current_state[message.chat.id] = __init_state_machine(message.chat)


# Передаємо месседж хендлеру усі можливі типи, щоб пересилались стікери, фото і т.д.
@bot.message_handler(content_types=content_types)
def handle_message(message):
    if message.chat.type == 'private':
        user_current_state[message.chat.id].handle_message(message)


# Ініціалізація стейт машини, по дефолту кидає юзера в мейн меню
def __init_state_machine(chat):
    states = {
        'main_menu': __init_main_menu_state(),
        'search_dialogue': __init_search_dialogue_state(),
        'dialogue': __init_dialogue_state()
    }

    state_machine = StateMachine(states, states['main_menu'], chat)

    return state_machine


# Сам стейт мейн меню, в якому можна почати пошук співрозмовника
def __init_main_menu_state():
    def message_handler(message, state_machine):
        if message.text == markup_commands['search_dialogue']:
            # Search dialogue
            user_current_state[state_machine.chat.id].go_to_state('search_dialogue')

    return State(lambda state_machine: keyboard.main_menu(state_machine.chat), message_handler, None)


# Стейт пошуку діалогу, в який потрапляє юзер після натискання "пошук співрозмовника"
def __init_search_dialogue_state():
    def message_handler(message, state_machine):
        if message.text == markup_commands['stop_search']:
            user_current_state[state_machine.chat.id].go_to_state('main_menu')
            # connection_manager.remove_from_queue(state_machine.chat.id)

    def enter_state(state_machine):
        keyboard.search_dialogue_menu(state_machine.chat)
        connection_manager.enqueue(state_machine.chat.id)

    return State(enter_state, message_handler, None)


# Стейт діалогу, в ньому знаходяться обидва юзера задля можливості спілкування
def __init_dialogue_state():
    def message_handler(message, state_machine):
        if message.text == markup_commands['stop_dialogue']:
            connection_manager.disconnect_user(state_machine.chat.id)
        elif message.text == markup_commands['ask_question']:
            bot.send_message(message.chat.id, bot_messages['write_question'])
        else:
            connection = connection_manager.get_connection(message.chat.id)
            if connection is not None:
                for user in connection.users:
                    if user != message.chat.id:
                        forward_message(user, message)

    return State(lambda state_machine: keyboard.dialogue_menu(state_machine.chat), message_handler, None)


# Функція, що пересилає повідомлення юзерів один одному
def forward_message(to_user, message):
    bot.copy_message(to_user, message.chat.id, message.message_id)


# Функція встановлення конекшна між юзерами
def on_setup_connection(connection):
    for user in connection.users:
        chat = user_current_state[user]
        chat.go_to_state('dialogue')


def on_user_disconnected(user, connection):
    for user2 in connection.users:
        if len(connection.users) < 2:
            bot.send_message(user2, bot_messages['only_user_disconnected'])
            user_current_state[user].go_to_state('main_menu')
        else:
            bot.send_message(user2, bot_messages['one_of_users_disconnected'])

    user_current_state[user].go_to_state('main_menu')


def on_connection_destroyed(connection):
    for user in connection.users:
        user_current_state[user].go_to_state('main_menu')


# Підписуємо функцію setup_connection на івент connection_created
connection_manager.events.connection_destroyed += on_connection_destroyed
connection_manager.events.user_disconnected += on_user_disconnected
connection_manager.events.connection_created += on_setup_connection
bot.infinity_polling()
