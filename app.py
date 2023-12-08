from flask import Flask, render_template
from src.decision_tree import DecisionTree
from src.input_parser import parse_file
from src.asset_manager import AssetManager


# Initialize the Flask app and the Decision Tree
app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)

# Initialize the image selector
asset_manager = AssetManager()


def render_template_assets(page, **kwargs):
    return render_template(page,
        image_url=asset_manager.get_background(),
        character=asset_manager.get_character(),
        character_name=asset_manager.get_character_name(),
        **kwargs)


# Routes
@app.route('/')
def home():
    asset_manager.new_character()
    return render_template_assets('home.html')



@app.route('/game')
def game():
    return render_template_assets('game.html',
        comment=asset_manager.get_comment())


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
