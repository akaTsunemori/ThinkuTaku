from json import load
from random import choice, randrange


class DialogueManager:
    def __init__(self) -> None:
        with open('static/json/symptoms.json', 'r') as file:
            self.comments = load(file)
        with open('static/json/questions.json', 'r') as file:
            self.questions = load(file)
        with open('static/json/success.json', 'r') as file:
            self.success = load(file)
        with open('static/json/failure.json', 'r') as file:
            self.failure = load(file)

    def get_comment(self):
        '''
        Rolls for a random comment based on a probability of 20%.

        Args:
            None

        Returns:
            Empty string: if the roll fails.
            Random comment: if the roll succeeds.
        '''
        probability = randrange(100)
        if probability > 20:
            return ''
        return choice(self.comments) + ' '

    def get_dialogue(self, rule):
        if rule.startswith('C '):
            raise Exception('Cause passed to symptom function.')
        question = choice(self.questions)
        question = question.replace('####', f'\“{rule.lower()}\”')
        question = question.capitalize()
        return question

    def get_success(self, rule):
        if not rule.startswith('C '):
            raise Exception('Success is only for causes. Invalid rule string format.')
        message = choice(self.success)
        message = message.replace('####', rule[2:])
        return message

    def get_failure(self):
        return choice(self.failure)






