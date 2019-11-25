from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import random

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
        user = escape(session['id'])
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
    if 'loggedin' in session or 'EmpAccess' in session:
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
    if 'loggedin' in session or 'EmpAccess' in session:
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


#Profile Method.
@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where user_id= %s""", (user,))
        d = cur.fetchone()
        pic_url = d['picture']
        if request.method=='POST':
            if request.form['submit']=="edit":
                return redirect(url_for('edit_profile'))
            if request.form['submit']=="change":
                return redirect(url_for('change_password'))
        return render_template('site/profile.html',tab="profile",designation=designation, data=d,user=user,pic=pic_url)
    return redirect(url_for('login'))

#Edit profile method.
@app.route('/edit_profile/', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from user where user_id= %s""", (session['id'],))
        d = cur.fetchone()
        pic_url = d['picture']
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
                    firebase = pyrebase.initialize_app(config)
                    storage = firebase.storage()
                    storage.child("images/"+user+"/new.jpg").put(file)
                    new_pic_url = storage.child("images/" + user + "/new.jpg").get_url(None)
                    cur.execute("""update user set picture=%s where user_id=%s""",(new_pic_url,session['id']))
            except:
                pass
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/edit_profile.html',tab="profile",designation=designation, data=d,user=user,pic=pic_url)
    return redirect(url_for('home'))

#Change password method.
@app.route('/change_password/', methods=['GET','POST'])
def change_password():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        user = escape(session['id'])
        designation = escape(session['designation'])
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
                return render_template('reg-login/change_pass.html',tab="profile",designation=designation, msg=msg,user=user)
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/change_pass.html',tab="profile",designation=designation, user=user)
    return redirect(url_for('home'))


#Feedback method.
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
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
        return render_template('site/contact.html',tab="contact", user=user, designation=designation)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()