import ast
from flask import Flask, render_template, request, jsonify
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
    return render_template('display_tree.html')


@app.route('/game', methods=('GET', 'POST'))
def game():
    if request.method == "POST":
        next_tuple = ast.literal_eval(request.form["next"])
        if request.form["answer"] == "no":
            if next_tuple[0][0][0:2] == "C ":
                return render_template('guess.html', decision=decision)
            return render_template('game.html', decision=next_tuple[1:])
        elif request.form["answer"] == "win":
            return render_template('win.html')
        elif request.form["answer"] == "loose":
            return render_template('loose.html')
        else:
            decision = tree.decide(next_tuple[0][0])
            if decision[0][0][0:2] == "C ":
                return render_template('guess.html', decision=decision)
            return render_template('game.html', decision=decision)
    decision = tree.decide()
    return render_template('game.html', decision=decision)

 
@app.route('/get-tree', methods=['GET'])
def getTree():
    return jsonify(tree.to_dict())

  
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
