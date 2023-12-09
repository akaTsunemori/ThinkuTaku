from json import load
from random import choice, randrange


class DialogueManager:
    '''
    This is the project's dialogue manager. It manages everything
    related to dialogues from the characters.
    '''
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
            Random comment + ' ': if the roll succeeds.
        '''
        probability = randrange(100)
        if probability > 20:
            return ''
        return choice(self.comments) + ' '

    def get_dialogue(self, rule):
        '''
        Gets a random dialogue that will question for the presence of [symptom].

        Args:
            symptom [str]: the symptom which the presence will be asked.

        Returns:
            question [str]: the properly formatted question.
        '''
        if rule.startswith('C '):
            raise Exception('Cause passed to symptom function.')
        question = choice(self.questions)
        question = question.replace('####', f'\“{rule.lower()}\”')
        question = question.capitalize()
        return question

    def get_success(self, rule):
        '''
        Gets a random success message, i.e. the DecisionTree succeeded
        in finding the cause for the symptoms.

        Args:
            rule [str]: the name of the character.

        Returns:
            message [str]: the success message.
        '''
        if not rule.startswith('C '):
            raise Exception('Success is only for causes. Invalid rule string format.')
        message = choice(self.success)
        message = message.replace('####', rule[2:])
        return message

    def get_failure(self):
        '''
        Returns a random failure message, i.e. the DecisionTree failed to identify the
        cause of the symptoms.

        Args:
            None

        Returns:
            message [str]: the failure message.
        '''
        return choice(self.failure)






