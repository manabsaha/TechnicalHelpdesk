from flask import Flask, request, render_template,session,redirect,url_for,escape
from flask_mysqldb import MySQL
import random
import bcrypt
import os
import gc

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def session_val(loggedin,id,designation,su_access,emp_access):

    if loggedin==True:
        session['loggedin'] = True
        session['id'] = id
        session['designation'] = designation
        session.pop('SuperuserAccess',su_access)
        session.pop('EmpAccess',emp_access)

    elif su_access==True:
        session['SuperuserAccess'] = True
        session.pop('EmpAccess',emp_access)
    elif emp_access==True:
        session['EmpAccess'] = True
        session['id'] = id
        session['designation'] = designation
        session.pop('SuperuserAccess',su_access)

@app.route('/', methods=['GET', 'POST'])
def home():
	if 'loggedin' in session:
		user=session['id']
		designation=escape(session['designation'])
		cur = mysql.connection.cursor()
		cur.execute("""SELECT fname FROM user where user_id=%s""",(user,))
		name = cur.fetchone()
		name = name['fname']
		return render_template('site/index.html',designation=designation, user=user,name=name,login_flag=True,tab="home")
	return render_template('site/index.html',tab="home")

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
                pass
            
            cur.execute("""SELECT user_id,designation from user where phone=%s""",(phone,))
            user_id=cur.fetchone()
            session_val(True,user_id['user_id'],user_id['designation'],None,None)
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
        cur.execute("""SELECT user_id,designation FROM user where phone = %s""",(phone,))
        id=cur.fetchone()
        if(check_pass==hash_password.encode('utf8')):
            session_val(True,id['user_id'],id['designation'],None,None)
            return redirect(url_for('home'))
        else:
            msg = '*Incorrect password!'
            return render_template('reg-login/login.html',msg=msg)

    return render_template('reg-login/login.html')

#Logout method.
@app.route('/logout/',methods=['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    return redirect(url_for('home'))

#About us method.
@app.route('/about/', methods=['GET', 'POST'])
def about():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        return render_template('site/about.html',designation=designation, user=user,tab="about")
    return render_template('site/about.html',tab="about")

if __name__ == "__main__":
    app.run()