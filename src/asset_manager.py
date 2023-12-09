from random import choice
from os import listdir
from json import load


class AssetManager:
    '''
    This is the project's main asset manager. It manages the random backgrounds,
    random characters and their respective names. Anything regarding asset
    management is here.
    '''
    def __init__(self) -> None:
        self.__BACKGROUND_PATH = 'static/img/akihabara/'
        self.__CHARACTERS_PATH = 'static/img/characters/'
        self.__backgrounds = listdir(self.__BACKGROUND_PATH)
        self.__CHARACTERS_OPTIONS = listdir(self.__CHARACTERS_PATH)
        self.__SELECTED_CHARACTER = ''
        self.__characters = []
        with open('static/json/characters.json', 'r') as file:
            self.character_names = load(file)
        self.new_character()

    def new_character(self):
        '''
        Randomly selects a new character from the database.

        Args:
            None

        Returns:
            None
        '''
        self.__SELECTED_CHARACTER = choice(self.__CHARACTERS_OPTIONS)
        self.__characters = listdir(self.__CHARACTERS_PATH + self.__SELECTED_CHARACTER)

    def get_character(self):
        '''
        Gets the path for a random image from the currently selected character.

        Args:
            None

        Returns:
            str: the path for the image.
        '''
        return self.__CHARACTERS_PATH + self.__SELECTED_CHARACTER + '/' + choice(self.__characters)

    def get_character_name(self):
        '''
        Gets the name of the currently selected character.

        Args:
            None

        Returns:
            str: the character's name.
        '''
        return self.character_names[self.__SELECTED_CHARACTER]

    def get_background(self):
        '''
        Gets the path for a random image from backgrounds' database.

        Args:
            None

        Returns:
            str: the path for the image.
        '''
        return self.__BACKGROUND_PATH + choice(self.__backgrounds)
