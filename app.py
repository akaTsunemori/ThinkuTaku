from flask import Flask, render_template
from os import listdir
from random import choice
from src.decision_tree import DecisionTree
from src.input_parser import parse_file


# Initialize the Flask app and the Decision Tree
app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)

# Initialize images
BACKGROUND_PATH = 'static/img/akihabara'
backgrounds = listdir(BACKGROUND_PATH)
CHARACTER_PATH = 'static/img/characters'
characters = listdir(CHARACTER_PATH)


# Routes
@app.route('/')
def home():
    return render_template('home.html',
        image_url=f'{BACKGROUND_PATH}/{choice(backgrounds)}',
        character=f'{CHARACTER_PATH}/{choice(characters)}')


@app.route('/game')
def game():
    return render_template('game.html',
        image_url=f'{BACKGROUND_PATH}/{choice(backgrounds)}',
        character=f'{CHARACTER_PATH}/{choice(characters)}')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
