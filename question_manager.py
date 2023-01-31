from text_messages import bot_messages


class QuestionManager:
    def __init__(self, bot):
        self.__answers = dict()
        self.__questions = dict()
        self.bot = bot

    def ask_question(self, connection, user, question):
        if len(question) < 1:
            self.bot.send_message(user, bot_messages['question_empty'], parse_mode='markdown')
            return

        # Видяляємо попередні відповіді юзерів, які потенціально можуть бути задля уникнення колізій
        self.clear_answers(connection)
        self.__questions[connection] = question

        for user2 in connection.users:
            if user2 != user:
                self.bot.send_message(user2, bot_messages['question'].format(question=question), parse_mode='markdown')

        self.bot.send_message(user, bot_messages['question_delivered'], parse_mode='markdown')

    def has_answers(self, connection):
        for user in connection.users:
            if user not in self.__answers:
                return False

        return True

    def has_question(self, connection):
        return connection in self.__questions

    def set_answer(self, connection, user, answer):
        if len(answer) < 1:
            self.bot.send_message(user, bot_messages['answer_empty'], parse_mode='markdown')
            return

        if not self.has_question(connection):
            return

        for user2 in connection.users:
            if user2 != user:
                self.bot.send_message(user2, bot_messages['answer_ready'])

        self.__answers[user] = answer

    def get_answer(self, user):
        return self.__answers.pop(user)

    def send_answers(self, connection):
        if self.has_question(connection) and self.has_answers(connection):
            for user in connection.users:
                for user2 in connection.users:
                    if user2 != user:
                        self.bot.send_message(user, bot_messages['answer'].format(answer=self.get_answer(user2)))
            # Чистимо словник від відповідей які вже були відправлені юзерам
            self.clear_answers(connection)

    def clear_answers(self, connection):
        if connection in self.__questions:
            del self.__questions[connection]

        for user in connection.users:
            if user in self.__answers:
                del self.__answers[user]
