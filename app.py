from flask import Flask, render_template, jsonify
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
    return render_template('edit_tree.html')

@app.route('/get-tree', methods=['GET'])
def getTree():
    return jsonify(tree.to_dict())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
