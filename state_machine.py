class State:
    def __init__(self, start_handler, message_handler, exit_handler):
        self.start_handler = start_handler
        self.message_handler = message_handler
        self.exit_handler = exit_handler

    def start(self, state_machine):
        if self.start_handler is not None:
            self.start_handler(state_machine)

    def handle_message(self, message, state_machine):
        if self.message_handler is not None:
            self.message_handler(message, state_machine)

    def exit(self, state_machine):
        if self.exit_handler is not None:
            self.exit_handler(state_machine)


class StateMachine:
    def __init__(self, states: dict, init_state: State, chat):
        self.__states = states
        self.chat = chat
        self.__current_state = init_state
        self.__current_state.start(self)

    def go_to_state(self, state):
        if state in self.__states:
            self.__current_state.exit(self)
            self.__current_state = self.__states[state]
            self.__current_state.start(self)

    def handle_message(self, message):
        if self.__current_state is not None:
            self.__current_state.handle_message(message, self)
