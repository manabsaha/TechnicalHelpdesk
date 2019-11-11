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

@app.route('/reg/', methods=['GET', 'POST'])
def reg():
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            address = request.form['address']
            pincode = request.form['pincode']
            password = request.form['password']
            print(fname,lname,phone,address,pincode)
            try:
                cur.execute("""INSERT INTO user values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone,address,pincode,password))
            except:
                cur.execute("""CREATE TABLE user (fname varchar(20),lname varchar(20),
                    phone bigint(10),address varchar(20),pincode bigint(6),password varchar(20),
                    PRIMARY KEY (phone))""")
                cur.execute("""INSERT INTO user values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone,address,pincode,password))
            mysql.connection.commit()
            gc.collect()
            return redirect('/')
        except:
            try:
                cur.execute("""SELECT phone FROM user WHERE phone=%s""",(phone,))
                if cur.rowcount == 0:
                    return "Try again"
                else:
                    return "Number used"
            except:
                return "Number already used"
            return "Error accessing database"

    return render_template('reg-login/reg.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        try:
            cur.execute("""SELECT password FROM user where phone = %s""",(phone,))
            mycur = cur.fetchone()
            #print(mycur)
            if str(mycur)=="{'password': '"+password+"'}":
                #return "Login success"
                cur.close()
                return redirect('/')
            else:
                return "Incorrect password"              
        except:
            return "error accessing database"

    return render_template('reg-login/login.html')

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
        try:
            cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
                fname, lname, phone, address, device))
        except:
            cur.execute("""CREATE TABLE pickup (fname varchar(20),lname varchar(20),
                    phone bigint(10),address varchar(20),device varchar(20))""")
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
        try:
            cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
                fname, lname, phone,address,device))
        except:
            cur.execute("""CREATE TABLE pickup (fname varchar(20),lname varchar(20),
                    phone bigint(10),address varchar(20),device varchar(20))""")
            cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
                fname, lname, phone,address,device))
        mysql.connection.commit()
        gc.collect()

    return render_template('forms/index.html')


if __name__ == "__main__":
    app.run()
