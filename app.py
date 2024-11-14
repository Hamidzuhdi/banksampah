from flask import Flask, render_template 
from flaskext.mysql import MySQL
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
