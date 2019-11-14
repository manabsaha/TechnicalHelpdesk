from flask import Flask, url_for, request, redirect, render_template,flash,session,escape
from flask_mysqldb import MySQL
import bcrypt
import os
import gc
from datetime import date

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

#Register method.
@app.route('/reg/', methods=['GET', 'POST'])
def reg():
    if 'number' in session:
        return redirect(url_for('home'))
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            address = request.form['address']
            pincode = request.form['pincode']
            password = request.form['password']
            hash_password = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

            try:
                cur.execute("""INSERT INTO user values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone,address,pincode,hash_password))
            except:
                cur.execute("""CREATE TABLE user (fname varchar(20),lname varchar(20),
                    phone bigint(10),address varchar(20),pincode bigint(6),hash_password varchar(128),
                    PRIMARY KEY (phone))""")
                cur.execute("""INSERT INTO user values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone,address,pincode,hash_password))

            mysql.connection.commit()
            gc.collect()
            session['loggedin'] = True
            session['number'] = phone
            return redirect(url_for('home'))
            
        except:
            cur.execute("""SELECT phone FROM user WHERE phone=%s""",(phone,))
            if cur.rowcount == 0:
                msg= "*Error. Try again"
                return render_template('reg-login/reg.html',msg=msg)
            else:
                msg= "*Number already used"
                return render_template('reg-login/reg.html',msg=msg)
        
    return render_template('reg-login/reg.html')

#Login method.
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'number' in session:
        return redirect(url_for('home'))
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        cur.execute("""SELECT hash_password FROM user where phone = %s""",(phone,))
        if(cur.rowcount == 0):
            msg = '*Number not registered'
            return render_template('reg-login/login.html',msg=msg)

        psw=str(cur.fetchone())
        hash_password = psw[19:len(psw)-2]
        check_pass = bcrypt.hashpw(password.encode('utf8'),hash_password.encode('utf8'))

        if(check_pass==hash_password.encode('utf8')):
            print(True)
            session['loggedin'] = True
            session['number'] = phone
            return redirect(url_for('home'))
        else:
            print(False)
            msg = '*Incorrect password!'
            return render_template('reg-login/login.html',msg=msg)

    return render_template('reg-login/login.html')

#Logout method.
@app.route('/logout/',methods=['GET','POST'])
@app.route('/logout/',methods=['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('number', None)
    return redirect(url_for('home'))

#Generate ticket method
@app.route('/ticket/', methods=['GET','POST'])
def ticket():
    if 'loggedin' not in session:
         return redirect(url_for('login'))
    cur=mysql.connection.cursor()
    cur.execute("""select * from user where phone= %s""", (session['number'],))
    data=cur.fetchone()
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        pickup=request.form['pickup']
        app_date = request.form['date']
        curr_date = date.today()
        print(pickup)
        if pickup=='True':
            try:
                cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone, address, app_date, curr_date))
            except:
                cur.execute("""CREATE TABLE pickup (fname varchar(20),lname varchar(20),
                                    phone bigint(10),address varchar(20) ,app_date date, curr_date date,
                                    PRIMARY KEY (phone))""")
                cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone, address, app_date, curr_date))
            mysql.connection.commit()
            return redirect(url_for('home'))
        else:
            try:
                cur.execute("""INSERT INTO appointment values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone, address, app_date, curr_date))
            except:
                cur.execute("""CREATE TABLE appointment (fname varchar(20),lname varchar(20),
                                                phone bigint(10),address varchar(20) ,pickup_date date, curr_date date,
                                                PRIMARY KEY (phone))""")
                cur.execute("""INSERT INTO appointment values(%s,%s,%s,%s,%s,%s)""", (
                    fname, lname, phone, address, app_date, curr_date))
            mysql.connection.commit()
            return redirect(url_for('home'))


    gc.collect()


    return render_template('forms/ticket.html',data=data,date=date.today(),user=escape(session['number']))



#HOME PAGE.
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'number' in session:
        user = escape(session['number'])
        cur = mysql.connection.cursor()
        cur.execute("""SELECT fname FROM user where phone=%s""",(user,))
        name = str(cur.fetchone())
        name = name[11:len(name)-2]
        return render_template('site/index.html', user=user,name=name)
    return render_template('site/index.html')


# @app.route('/user/<username>', methods=['GET', 'POST'])
# def home_user(username):
#     flash("successful")
#     return render_template('site/index.html',user=username)


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
            cur.execute("""INSERT INTO pickup1 values(%s,%s,%s,%s,%s)""", (
                fname, lname, phone, address, device))
        except:
            cur.execute("""CREATE TABLE pickup1(fname varchar(50),lname varchar(50),phone bigint(10), address varchar(100), 
            device varchar(50))""")
            cur.execute("""INSERT INTO pickup values(%s,%s,%s,%s,%s)""", (
                fname, lname, phone, address, device))

        mysql.connection.commit()
        gc.collect()
    return render_template('test.html')



@app.route('/about/', methods=['GET', 'POST'])
def about():
    if 'number' in session:
        user = escape(session['number'])
        return render_template('site/about.html', user=user)
    return render_template('site/about.html')


@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'number' in session:
        user = escape(session['number'])
        return render_template('site/services.html', user=user)
    return render_template('site/services.html')

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'number' in session:
        user = escape(session['number'])
        return render_template('site/profile.html', user=user)
    return render_template('site/profile.html')

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if 'number' in session:
        user = escape(session['number'])
        return render_template('site/contact.html', user=user)
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
@app.route('/test/')
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(debug=True)
