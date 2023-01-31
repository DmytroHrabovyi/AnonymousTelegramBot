from text_messages import bot_messages


class QuestionManager:
    def __init__(self, bot):
        self.__answers = dict()
        self.bot = bot

    def ask_question(self, connection, user, question):
        if len(question) < 1:
            self.bot.send_message(user, bot_messages['question_empty'], parse_mode='markdown')
            return

        # Видяляємо попередні відповіді юзерів, які потенціально можуть бути задля уникнення колізій
        self.clear_answers(connection.users)

        for user2 in connection.users:
            if user2 != user:
                self.bot.send_message(user2, bot_messages['question'].format(question=question), parse_mode='markdown')


        self.bot.send_message(user, bot_messages['question_delivered'], parse_mode='markdown')

    def has_answers(self, users):
        for user in users:
            if user not in self.__answers:
                return False

        return True

    def set_answer(self, users, user, answer):
        if len(answer) < 1:
            self.bot.send_message(user, bot_messages['answer_empty'], parse_mode='markdown')
            return

        for user2 in users:
            if user2 != user:
                self.bot.send_message(user2, bot_messages['answer_ready'])

        self.__answers[user] = answer

    def get_answer(self, user):
        return self.__answers.pop(user)

    def send_answers(self, users):
        if self.has_answers(users):
            for user in users:
                for user2 in users:
                    if user2 != user:
                        self.bot.send_message(user, bot_messages['answer'].format(answer=self.get_answer(user2)))
            # Чистимо словник від відповідей які вже були відправлені юзерам
            self.clear_answers(users)

    def clear_answers(self, users):
        for user in users:
            if user in self.__answers:
                del self.__answers[user]
