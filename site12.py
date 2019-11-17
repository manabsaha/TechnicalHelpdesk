from flask import Flask, url_for, request, redirect, render_template,flash,session,escape
from flask_mysqldb import MySQL
import bcrypt
import os
import gc
import pyrebase
from datetime import date

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

config = {
    "apiKey": "AIzaSyBjlH55tLK6JRNlMybLMf5EX_BgrA7tbT4",
    "authDomain": "technicalhelpdesk-c4612.firebaseapp.com",
    "databaseURL": "https://technicalhelpdesk-c4612.firebaseio.com",
    "projectId": "technicalhelpdesk-c4612",
    "storageBucket": "technicalhelpdesk-c4612.appspot.com",
    "messagingSenderId": "448324302994",
    "appId": "1:448324302994:web:da49238fd03eab01f3ce4b",
    "measurementId": "G-KSX47MVXRN"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

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
                cur.execute("""INSERT INTO user(fname, lname, phone,address,pincode,hash_password) 
                    values(%s,%s,%s,%s,%s,%s)""", (fname, lname, phone,address,pincode,hash_password))
            except:
                cur.execute("""CREATE TABLE user (
                                                user_id int AUTO_INCREMENT,
                                                fname varchar(20),
                                                lname varchar(20),
                                                phone bigint(10) UNIQUE,
                                                address varchar(100),
                                                pincode bigint(6),
                                                hash_password varchar(128),
                                                picture varchar(200) DEFAULT '/static/images/no_dp.png',
                                                PRIMARY KEY (user_id))auto_increment=1001""")
                cur.execute("""INSERT INTO user(fname, lname, phone,address,pincode,hash_password) 
                    values(%s,%s,%s,%s,%s,%s)""",(fname, lname, phone, address, pincode, hash_password))
            
            cur.execute("""SELECT user_id from user where phone=%s""",(phone,))
            user_id=cur.fetchone()
            session['loggedin'] = True
            session['id'] = user_id['user_id']
            mysql.connection.commit()
            gc.collect()
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

        psw=cur.fetchone()
        hash_password = psw['hash_password']
        check_pass = bcrypt.hashpw(password.encode('utf8'),hash_password.encode('utf8'))
        cur.execute("""SELECT user_id FROM user where phone = %s""",(phone,))
        id=cur.fetchone()
        if(check_pass==hash_password.encode('utf8')):
            session['loggedin'] = True
            session['id'] = id['user_id']
            return redirect(url_for('home'))
        else:
            msg = '*Incorrect password!'
            return render_template('reg-login/login.html',msg=msg)

    return render_template('reg-login/login.html')

#Logout method.
#@app.route('/logout/',methods=['GET','POST'])
@app.route('/logout/',methods=['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    return redirect(url_for('home'))

#Generate ticket method
@app.route('/ticket/', methods=['GET','POST'])
def ticket():
    if 'loggedin' not in session:
         return redirect(url_for('login'))
    cur=mysql.connection.cursor()
    cur.execute("""select * from user where user_id= %s""", (session['id'],))
    data=cur.fetchone()
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        pickup=request.form['pickup']
        app_date = request.form['date']
        curr_date = date.today()
        if pickup=='True':
            type='Pickup'
        else:
            type='Appointment'

        try:
            cur.execute("""INSERT INTO ticket(user_id, fname, lname, phone, address, app_date, curr_date,app_type) 
                values(%s,%s,%s,%s,%s,%s,%s,%s)""", (session['id'], fname, lname, phone, address, app_date, curr_date,type))
            mysql.connection.commit()
            return redirect(url_for('home'))
        except:
            cur.execute("""CREATE TABLE ticket (ticket_id int AUTO_INCREMENT,
                                                user_id int NOT NULL,
                                                fname varchar(20),
                                                lname varchar(20),
                                                phone bigint(10),
                                                address varchar(100),
                                                app_date date, 
                                                curr_date date,
                                                app_type varchar(20) CHECK(app_type IN ('Appointment','Pickup')),
                                                status varchar(20) DEFAULT 'Processing',
                                                PRIMARY KEY (ticket_id),
                                                FOREIGN KEY (user_id)
                                                REFERENCES user(user_id))AUTO_INCREMENT=10001""")
            cur.execute("""INSERT INTO ticket(user_id,fname, lname, phone, address, app_date, curr_date,app_type) 
                            values(%s,%s,%s,%s,%s,%s,%s,%s)""", (session['id'], fname, lname, phone, address, app_date, curr_date, type))
            mysql.connection.commit()
            return redirect(url_for('home'))
    gc.collect()
    return render_template('forms/ticket.html',data=data,date=date.today(), user=escape(session['id']))



#HOME PAGE.
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        user = escape(session['id'])
        cur = mysql.connection.cursor()
        cur.execute("""SELECT fname FROM user where user_id=%s""",(user,))
        name = cur.fetchone()
        name = name['fname']
        return render_template('site/index.html', user=user,name=name,login_flag=True)
    return render_template('site/index.html')


#About us method.
@app.route('/about/', methods=['GET', 'POST'])
def about():
    if 'loggedin' in session:
        user = escape(session['id'])
        return render_template('site/about.html', user=user)
    return render_template('site/about.html')


#Services method.
@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'loggedin' in session:
        if request.method == 'POST':
            if request.form['submit'] == "cancel":
                print("adsa")
        user = escape(session['id'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT ticket_id,app_date,app_type,status FROM ticket where user_id=%s",(user,))
        data=cur.fetchall()
        return render_template('site/services.html',data=data, user=user,success_msg = "Feedback sent")
    return redirect(url_for('login'))

#Cancel Ticket method.
@app.route('/services/<int:id>')
def cancel(id):
    if 'loggedin' in session:
        print(id)
        cur=mysql.connection.cursor()
        status = "CANCELLED BY USER"
        cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",(status,id))
        mysql.connection.commit()
        return redirect(url_for('services'))
    return redirect(url_for('login'))


#Profile Method.
@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user = escape(session['id'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where user_id= %s""", (user,))
        d = cur.fetchone()
        #pic_url =storage.child("images/"+user+"/new.jpg").get_url(None)
        pic_url = d['picture']
        # if pic_url =="":
        #     pic_url = d['picture']
        if request.method=='POST':
            if request.form['submit']=="edit":
                return redirect(url_for('edit_profile'))
            if request.form['submit']=="change":
                return redirect(url_for('change_password'))
        return render_template('site/profile.html', data=d,user=user,pic=pic_url)
    return redirect(url_for('login'))

#Edit profile method.
@app.route('/edit_profile/', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        user = escape(session['id'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where user_id= %s""", (session['id'],))
        d = cur.fetchone()
        #pic_url = storage.child("images/" + user + "/new.jpg").get_url(None)
        pic_url = d['picture']
        # if pic_url =="":
        #     pic_url = d['picture']
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            address = request.form['address']
            pincode = request.form['pincode']
            file = request.files['display_pic']
            try:
                cur.execute("""update user set fname=%s,lname=%s,phone=%s,address=%s,pincode=%s where user_id=%s""", (
                    fname, lname, phone, address, pincode, session['id'],))
                if file.filename!= '':
                    storage.child("images/"+user+"/new.jpg").put(file)
                    new_pic_url = storage.child("images/" + user + "/new.jpg").get_url(None)
                    cur.execute("""update user set picture=%s where user_id=%s""",(new_pic_url,session['id']))
            except:
                pass
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/edit_profile.html', data=d,user=user,pic=pic_url)
    return redirect(url_for('home'))

#Change password method.
@app.route('/change_password/', methods=['GET','POST'])
def change_password():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        user = escape(session['id'])
        if request.method == 'POST':
            old_pass = request.form['pass']
            password = request.form['password']

            cur.execute("""SELECT hash_password FROM user where user_id = %s""", (session['id'],))
            psw = cur.fetchone()
            hash_password = psw['hash_password']
            check_pass = bcrypt.hashpw(old_pass.encode('utf8'), hash_password.encode('utf8'))
            if (check_pass == hash_password.encode('utf8')):
                new_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                cur.execute("""update user set hash_password=%s where user_id = %s""", (new_hash, session['id'],))

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
        user = escape(session['id'])
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


#----------------------------------------TEST METHODS---------------------------------------

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
            msg = '*Incorrect password!'
            return render_template('reg-login/change_pass.html',msg=msg, user=user)
        mysql.connection.commit()

    return render_template('reg-login/change_pass.html', user=user)


@app.route('/pickup/', methods=['GET', 'POST'])
def pickup():
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        device = request.form['device']
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

#----------------------------------------END------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
