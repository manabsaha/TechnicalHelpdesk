from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import random

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
   return '<h1>DEPLOY SUCCESSFULL</h1>'


if __name__ == "__main__":
    app.run()