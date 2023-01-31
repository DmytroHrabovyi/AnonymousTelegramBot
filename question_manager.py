from text_messages import bot_messages


class QuestionManager:
    def __init__(self, bot):
        self.__answers = dict()
        self.bot = bot

    def ask_question(self, connection, user, question):
        if connection is None:
            return

        if len(question) < 1:
            self.bot.send_message(user, bot_messages['answer_empty'], parse_mode='markdown')
            return

        for user2 in connection.users:
            if user2 != user:
                self.bot.send_message(user2, bot_messages['question'].format(question=question), parse_mode='markdown')

    def has_answers(self, users):
        for user in users:
            if user not in self.__answers:
                return False

        return True

    def set_answer(self, connection, user, answer):
        if connection is None:
            return

        if len(answer) < 1:
            self.bot.send_message(user, bot_messages['answer_empty'], parse_mode='markdown')
            return

        self.__answers[user] = answer

    def get_answer(self, user):
        return self.__answers.pop(user)

    def send_answers(self, users):
        if self.has_answers(users):
            for user in users:
                for user2 in users:
                    if user2 != user:
                        self.bot.send_message(user, bot_messages['answer'].format(answer=self.get_answer(user2)))
