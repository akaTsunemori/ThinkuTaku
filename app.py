from flask import Flask, render_template, request
from src.decision_tree import DecisionTree
from src.input_parser import parse_file


# Initialize the Flask app and the Decision Tree
app = Flask(__name__)
PATH = 'static/input.csv'
rules = parse_file(path=PATH)
tree = DecisionTree(rules=rules)


# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/game', methods=('GET', 'POST'))
def game():
    if request.method == "POST":
        tree.display(tree.root)
        next_node = request.form["next_node"]
        children = request.form["children_node"]
        # children = request.form["children_node"]
        print(next_node)
        print(children)
        if request.form["answer"] == "no":
            return render_template('game.html', root=next_node)
        else:
            return render_template('game.html', root=children)
    return render_template('game.html', tree=tree)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
