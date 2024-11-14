from flask import Flask, render_template
from flask_mysql_connector import MySQL

app = Flask(__name__)

# Konfigurasi database
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'banksampah'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

# Menampilkan homepage
@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
