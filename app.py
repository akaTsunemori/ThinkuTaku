from flask import Flask, render_template
from src.decision_tree import DecisionTree, rules_expanded

# Main app
app = Flask(__name__)

# Routes
@app.route('/')
def home():
    return render_template('edit_tree.html')

@app.route('/get-tree', methods=['GET'])
def getTree():
    decision_tree = DecisionTree(rules=rules_expanded)
    tree = decision_tree.to_dict()
    return tree 

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
