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
    if 'loggedin' in session:
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
    if 'loggedin' in session:
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
#@app.route('/logout/',methods=['GET','POST'])
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
    if 'loggedin' in session:
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
        old_pass = request.form['pass']
        password = request.form['password']

        cur.execute("""SELECT hash_password FROM user where phone = %s""",(8486006074,))
        psw=str(cur.fetchone())
        hash_password = psw[19:len(psw)-2]
        check_pass = bcrypt.hashpw(old_pass.encode('utf8'),hash_password.encode('utf8'))
        hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        if(check_pass==hash_password.encode('utf8')):
            cur.execute("""update user set hash_password=%s where phone = %s""", (hash,8486006074,))
        else:
            print(False)
            msg = '*Incorrect password!'
            return render_template('reg-login/change_pass.html',msg=msg, user=user)
        mysql.connection.commit()

    return render_template('reg-login/change_pass.html', user=user)



@app.route('/about/', methods=['GET', 'POST'])
def about():
    if 'loggedin' in session:
        user = escape(session['number'])
        return render_template('site/about.html', user=user)
    return render_template('site/about.html')


@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'loggedin' in session:
        user = escape(session['number'])
        return render_template('site/services.html', user=user,success_msg = "Feedback sent")
    return render_template('site/services.html')

#Profile Method.
@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user = escape(session['number'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where phone= %s""", (session['number'],))
        d = cur.fetchone()
        if request.method=='POST':
            if request.form['submit']=="edit":
                return redirect(url_for('edit_profile'))
            if request.form['submit']=="change":
                return redirect(url_for('change_password'))
        return render_template('site/profile.html', data=d,user=user)
    return redirect(url_for('login'))

#Edit profile method.
@app.route('/edit_profile/', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        user = escape(session['number'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where phone= %s""", (session['number'],))
        d = cur.fetchone()
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            #phone = request.form['phone']
            address = request.form['address']
            pincode = request.form['pincode']
            try:
                cur.execute("""update user set fname=%s,lname=%s,phone=%s,address=%s,pincode=%s where phone=%s""", (
                    fname, lname, user, address, pincode, session['number'],))
            except:
                pass
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/edit_profile.html', data=d,user=user)
    return redirect(url_for('home'))

#Change password method.
@app.route('/change_password/', methods=['GET','POST'])
def change_password():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        user = escape(session['number'])
        if request.method == 'POST':
            old_pass = request.form['pass']
            password = request.form['password']

            cur.execute("""SELECT hash_password FROM user where phone = %s""", (session['number'],))
            psw = str(cur.fetchone())
            hash_password = psw[19:len(psw) - 2]
            check_pass = bcrypt.hashpw(old_pass.encode('utf8'), hash_password.encode('utf8'))
            if (check_pass == hash_password.encode('utf8')):
                new_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                cur.execute("""update user set hash_password=%s where phone = %s""", (new_hash, session['number'],))

            else:
                msg = '*Incorrect password!'
                return render_template('reg-login/change_pass.html', msg=msg,user=user)
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/change_pass.html', user=user)
    return redirect(url_for('home'))


#Feedback method.
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if 'loggedin' in session:
        user = escape(session['number'])
        if request.method == 'POST':
            feedback = request.form['feedback']
            cur=mysql.connection.cursor()
            try:
                cur.execute("""INSERT INTO feedback values(%s,%s)""", (user,feedback))
            except:
                cur.execute("""CREATE TABLE feedback (phone bigint(10),message varchar(200))""")
                cur.execute("""INSERT INTO feedback values(%s,%s)""", (user,feedback))
            mysql.connection.commit()
            return redirect(url_for('home'))
        return render_template('site/contact.html', user=user)
    return redirect(url_for('login'))


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
