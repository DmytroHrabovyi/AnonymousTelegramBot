class QuestionManager:
    def __init__(self):
        self.__answers = dict()

    def has_answers(self, users):
        for user in users:
            if user not in self.__answers:
                return False

        return True

    def set_answer(self, user, answer):
        self.__answers[user] = answer

    def get_answer(self, user):
        return self.__answers[user]
