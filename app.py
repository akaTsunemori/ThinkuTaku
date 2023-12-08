from flask import Flask, render_template, request
from src.decision_tree import DecisionTree
from src.input_parser import parse_file
from src.asset_manager import AssetManager


app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)
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


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        if 'button_yes' in request.form:
            print('yes')
        elif 'button_no' in request.form:
            print('no')
        elif 'button_doubt' in request.form:
            print('doubt')
    return render_template_assets('game.html',
        comment=asset_manager.get_comment())


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
