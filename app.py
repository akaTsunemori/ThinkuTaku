from flask import Flask, render_template, request, url_for, redirect
from src.decision_tree import DecisionTree
from src.input_parser import parse_file
from src.asset_manager import AssetManager
from src.dialogue_manager import DialogueManager


app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)
decision = []
asset_manager = AssetManager()
dialogue_manager = DialogueManager()


def render_template_assets(page, **kwargs):
    return render_template(page,
        image_url=asset_manager.get_background(),
        character=asset_manager.get_character(),
        character_name=asset_manager.get_character_name(),
        **kwargs)


# Routes
@app.route('/')
def home():
    global decision
    decision = tree.decide()
    asset_manager.new_character()
    return render_template_assets('home.html')


@app.route('/game', methods=['GET', 'POST'])
def game():
    global decision
    if decision:
        rule, probability = decision[-1]
    else:
        result = dialogue_manager.get_failure()
        return render_template_assets('result.html', result=result)
    if request.method == 'POST':
        if 'button_yes' in request.form:
            if not rule.startswith('C '):
                decision = tree.decide(rule)
                rule, probability = decision[-1]
            else:
                result = dialogue_manager.get_success(rule)
                return render_template_assets('result.html', result=result)
        elif 'button_no' in request.form:
            decision.pop()
            if decision:
                rule, probability = decision[-1]
            else:
                result = dialogue_manager.get_failure()
                return render_template_assets('result.html', result=result)
        elif 'button_doubt' in request.form:
            while decision and not decision[-1][0].startswith('C '):
                decision.pop()
            if decision:
                rule, probability = decision[-1]
            else:
                result = dialogue_manager.get_failure()
                return render_template_assets('result.html', result=result)
    if not rule.startswith('C '):
        comment = dialogue_manager.get_comment()
        question = dialogue_manager.get_dialogue(rule)
    else:
        comment = ''
        question = f'Seu personagem é o(a) {rule[2:]}? (Confiança: {(probability*100):.0f}%)'
    return render_template_assets('game.html',
        comment=comment,
        question=question,
        rule=rule)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
