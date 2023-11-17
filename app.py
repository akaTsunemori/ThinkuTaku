from flask import Flask, render_template


# Main app
app = Flask(__name__)


# Routes
@app.route('/')
def home():
    return render_template('home.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
