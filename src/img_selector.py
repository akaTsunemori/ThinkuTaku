from random import choice
from os import listdir
from json import load


class ImgSelector:
    def __init__(self) -> None:
        self.__BACKGROUND_PATH = 'static/img/akihabara/'
        self.__CHARACTERS_PATH = 'static/img/characters/'
        self.__backgrounds = listdir(self.__BACKGROUND_PATH)
        self.__CHARACTERS_OPTIONS = listdir(self.__CHARACTERS_PATH)
        self.__SELECTED_CHARACTER = ''
        self.__characters = []
        with open('static/json/characters.json', 'r') as file:
            self.character_names = load(file)

    def new_character(self):
        self.__SELECTED_CHARACTER = choice(self.__CHARACTERS_OPTIONS)
        self.__characters = listdir(self.__CHARACTERS_PATH + self.__SELECTED_CHARACTER)

    def get_character(self):
        return self.__CHARACTERS_PATH + self.__SELECTED_CHARACTER + '/' + choice(self.__characters)

    def get_character_name(self):
        return self.character_names[self.__SELECTED_CHARACTER]

    def get_background(self):
        return self.__BACKGROUND_PATH + choice(self.__backgrounds)
