from flask import Flask, url_for, request, redirect, render_template,flash
from flask_mysqldb import MySQL
import os
import gc

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/a/', methods=['GET', 'POST'])
def base():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        device = request.form['device']
        print(fname, lname, phone, address, device)
        cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
            fname, lname, phone, address, device))
        mysql.connection.commit()
        gc.collect()
    return render_template('test.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    flash("successful")
    return render_template('site/index.html')


@app.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('site/about.html')


@app.route('/services/', methods=['GET', 'POST'])
def services():
    return render_template('site/services.html')


@app.route('/gallery/', methods=['GET', 'POST'])
def gallery():
    return render_template('site/gallery.html')


@app.route('/blog/', methods=['GET', 'POST'])
def blog():
    return render_template('site/blog.html')


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    return render_template('site/contact.html')


@app.route('/pickup/', methods=['GET', 'POST'])
def pickup():
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        device = request.form['device']
        print(fname,lname,phone,address,device)
        cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
        fname, lname, phone,address,device))
        mysql.connection.commit()
        gc.collect()
    return render_template('forms/index.html')


if __name__ == "__main__":
    app.run()
