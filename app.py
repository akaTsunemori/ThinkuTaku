from flask import Flask, render_template
from src.decision_tree import DecisionTree
from src.input_parser import parse_file
from src.img_selector import ImgSelector


# Initialize the Flask app and the Decision Tree
app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)

# Initialize the image selector
img_selector = ImgSelector()


def render_template_util(page):
    return render_template(page,
        image_url=img_selector.get_background(),
        character=img_selector.get_character(),
        character_name=img_selector.get_character_name())


# Routes
@app.route('/')
def home():
    img_selector.new_character()
    return render_template_util('home.html')



@app.route('/game')
def game():
    return render_template_util('game.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
