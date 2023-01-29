from state_machine import State, StateMachine
from main import user_current_state, keyboard, connection_manager, bot
from keyboard import markup_commands, bot_messages


def __init_state_machine(chat):
    states = {
        'main_menu': __init_main_menu_state(),
        'search_dialogue': __init_search_dialogue_state(),
        'dialogue': __init_dialogue_state()
    }

    state_machine = StateMachine(states, states['main_menu'], chat)

    return state_machine


def __init_main_menu_state():
    def message_handler(message, state_machine):
        if message.text == markup_commands['search_dialogue']:
            # Search dialogue
            user_current_state[state_machine.chat.id].go_to_state('search_dialogue')

    return State(lambda state_machine: keyboard.main_menu(state_machine.chat), message_handler, None)


def __init_search_dialogue_state():
    def message_handler(message, state_machine):
        if message.text == markup_commands['stop_search']:
            user_current_state[state_machine.chat.id].go_to_state('main_menu')
            # connection_manager.remove_from_queue(state_machine.chat.id)

    def enter_state(state_machine):
        keyboard.search_dialogue_menu(state_machine.chat)
        connection_manager.enqueue(state_machine.chat.id)

    return State(enter_state, message_handler, None)


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
                        copy_message(user, message)

    return State(lambda state_machine: keyboard.dialogue_menu(state_machine.chat), message_handler, None)

def copy_message(user, message):
    bot.forward_message(user, message.chat.id, message.message_id)