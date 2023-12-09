from flask import Flask, render_template, request, jsonify
from src.decision_tree import DecisionTree
from src.input_parser import parse_file
from src.asset_manager import AssetManager
from src.dialogue_manager import DialogueManager


app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)
asset_manager = AssetManager()
dialogue_manager = DialogueManager()


def render_template_assets(page, **kwargs):
    return render_template(page,
        image_url=asset_manager.get_background(),
        character=asset_manager.get_character(),
        character_name=asset_manager.get_character_name(),
        **kwargs)


@app.route('/')
def home():
    tree.decide()
    asset_manager.new_character()
    return render_template_assets('home.html')


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        if 'button_yes' in request.form:
            if tree.decision[0].startswith('C '):
                rule, probability = tree.decision
                result = dialogue_manager.get_success(rule)
                return render_template_assets('result.html', result=result)
            else:
                tree.decide('yes')
        elif 'button_no' in request.form:
            tree.decide('no')
        elif 'button_doubt' in request.form:
            if tree.decision[0].startswith('C '):
                tree.decide('no')
            else:
                tree.decide('doubt')
    if not tree.decision:
        result = dialogue_manager.get_failure()
        return render_template_assets('result.html', result=result)
    rule, probability = tree.decision
    if not rule.startswith('C '):
        comment = dialogue_manager.get_comment()
        question = dialogue_manager.get_dialogue(rule)
    else:
        comment = ''
        question = f'Seu personagem é o(a) {rule[2:]}? (Confiança: {(probability*100):.0f}%)'
    return render_template_assets('game.html',
        comment=comment,
        question=question)


@app.route('/get-tree', methods=['GET'])
def getTree():
    return jsonify(tree.to_dict())


@app.route('/display-tree')
def display_tree():
    return render_template('display_tree.html')


if __name__ == '__main__':
    app.run(debug=True)
