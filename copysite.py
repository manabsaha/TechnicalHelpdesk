from flask import Flask, url_for, request, redirect, render_template,flash, session, escape
from flask_mysqldb import MySQL
import bcrypt
import os
import gc
import pyrebase
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
#MySQL config.
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
#Firebase config.
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

#SESSION VARIABLES: loggedin, id, designation, SuperuserAccess, AdminAccess, ManagerAccess

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
                                                designation varchar(50) DEFAULT 'customer',
                                                PRIMARY KEY (user_id))auto_increment=1001""")
                cur.execute("""INSERT INTO user(fname, lname, phone,address,pincode,hash_password) 
                    values(%s,%s,%s,%s,%s,%s)""",(fname, lname, phone, address, pincode, hash_password))
            
            cur.execute("""SELECT user_id,designation from user where phone=%s""",(phone,))
            user_id=cur.fetchone()
            session['loggedin'] = True
            session['id'] = user_id['user_id']
            session['designation'] =  user_id['designation']
            session.pop('SuperuserAccess', None)
            session.pop('AdminAccess', None)
            session.pop('ManagerAccess', None)
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
            session['loggedin'] = True
            session['id'] = id['user_id']
            session['designation']= id['designation']
            session.pop('SuperuserAccess', None)
            session.pop('AdminAccess', None)
            session.pop('ManagerAccess', None)
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

#Ticket Generate method
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
                values(%s,%s,%s,%s,%s,%s,%s,%s)""", (session['id'], fname, lname, phone, address, app_date,
                curr_date, type))
            mysql.connection.commit()
            return redirect(url_for('services'))
    gc.collect()
    return render_template('forms/ticket.html',designation=escape(session['designation']), data=data,date=date.today(),
        user=escape(session['id']))



#HOME PAGE.
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation=escape(session['designation'])
        cur = mysql.connection.cursor()
        cur.execute("""SELECT fname FROM user where user_id=%s""",(user,))
        name = cur.fetchone()
        name = name['fname']
        return render_template('site/index.html',designation=designation, user=user,name=name,login_flag=True)
    return render_template('site/index.html')


#About us method.
@app.route('/about/', methods=['GET', 'POST'])
def about():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        return render_template('site/about.html',designation=designation, user=user)
    return render_template('site/about.html')

#All_tickets method.
@app.route('/all_tickets/', methods=['GET', 'POST'])
def all_tickets():
    if 'loggedin' in session and session['designation']=="customer_care":
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT ticket_id, user_id, fname, app_date,app_type,status FROM ticket")
        data=cur.fetchall()
        return render_template('site/all_tickets.html',data=data, designation=designation, user=user,success_msg = "Feedback sent")
    if 'loggedin' in session:
        return redirect(url_for('services'))
    return redirect(url_for('login'))

#inventory_add method
@app.route('/all_tickets/<int:id>')
def add_to_inventory(id):
    if 'loggedin' in session and session['designation']=="customer_care":
        cur=mysql.connection.cursor()
    try:
        cur.execute("""INSERT INTO inventory(inventory_id, product_name, product_type, phone, address, app_date, curr_date,app_type) 
              values(%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (session['id'], fname, lname, phone, address, app_date, curr_date, type))
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
              values(%s,%s,%s,%s,%s,%s,%s,%s)""", (session['id'], fname, lname, phone, address, app_date,
                                                   curr_date, type))
        mysql.connection.commit()
        return redirect(url_for('home'))

        mysql.connection.commit()
        return redirect(url_for('all_tickets'))
    return redirect(url_for('login'))


#Services method.
@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'loggedin' in session and session['designation']=="customer":
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT ticket_id,app_date,app_type,status FROM ticket where user_id=%s",(user,))
        data=cur.fetchall()
        return render_template('site/services.html',data=data, designation=designation, user=user,success_msg = "Feedback sent")
    return redirect(url_for('login'))

#Cancel Ticket method.
@app.route('/services/<int:id>')
def cancel(id):
    if 'loggedin' in session and session['designation']=="customer":
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
        return render_template('site/profile.html',designation=designation, data=d,user=user,pic=pic_url)
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
        return render_template('reg-login/edit_profile.html',designation=designation, data=d,user=user,pic=pic_url)
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
                return render_template('reg-login/change_pass.html',designation=designation, msg=msg,user=user)
            mysql.connection.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/change_pass.html',designation=designation, user=user)
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
        return render_template('site/contact.html', user=user, designation=designation)
    return redirect(url_for('login'))


#SUPERUSER ACCESS METHOD
@app.route('/superuseraccess/',methods=['GET','POST'])
def super_access():
    if request.method == 'POST':
        superuser_password = request.form['su_password']
        if superuser_password == "superuser":
            session['SuperuserAccess'] = True
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('designation',None)
            session.pop('AdminAccess', None)
            session.pop('ManagerAccess', None)
            return redirect(url_for('super_panel'))
    return render_template('superuser/superuser_access.html')

#SUPERUSER PANEL
@app.route('/superuserpanel/',methods=['GET','POST'])
def super_panel():
    if 'SuperuserAccess' in session:
        return render_template('superuser/superuser_panel.html',desg="SUPERUSER",log=session['SuperuserAccess'])
    return redirect(url_for('super_access'))

#SUPERUSER LOGOUT
@app.route('/superuser/logout',methods=['GET','POST'])
def super_logout():
    session.pop('SuperuserAccess', None)
    return redirect(url_for('home'))

#ADMIN ACCESS METHOD
@app.route('/adminaccess/',methods=['GET','POST'])
def admin_access():
    if request.method == 'POST':
        #admin_phone = request.form['phone']
        admin_password = request.form['admin_password']
        if admin_password == "adminpass":
            session['AdminAccess'] = True
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('designation',None)
            session.pop('SuperuserAccess', None)
            session.pop('ManagerAccess', None)
            return redirect(url_for('admin_panel'))
    return render_template('admin/admin_login.html')

#ADMIN PANEL
@app.route('/adminpanel/',methods=['GET','POST'])
def admin_panel():
    if 'AdminAccess' in session:
        return render_template('admin/admin_panel.html',desg="ADMIN",log=session['AdminAccess'])
    return redirect(url_for('admin_access'))

#ADMIN LOGOUT
@app.route('/admin/logout',methods=['GET','POST'])
def admin_logout():
    session.pop('AdminAccess', None)
    return redirect(url_for('home'))


#MANAGER ACCESS METHOD
@app.route('/manageraccess/',methods=['GET','POST'])
def manager_access():
    if request.method == 'POST':
        #Manager_phone = request.form['phone']
        Manager_password = request.form['manager_password']
        if Manager_password == "managerpass":
            session['ManagerAccess'] = True
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('designation',None)
            session.pop('SuperuserAccess', None)
            session.pop('AdminAccess', None)
            return redirect(url_for('manager_panel'))
    return render_template('manager/manager_login.html')

#MANAGER PANEL
@app.route('/managerpanel/',methods=['GET','POST'])
def manager_panel():
    if 'ManagerAccess' in session:
        return render_template('manager/manager_panel.html',desg="MANAGER",log=session['ManagerAccess'])
    return redirect(url_for('manager_access'))

#MANAGER LOGOUT
@app.route('/manager/logout',methods=['GET','POST'])
def Manager_logout():
    session.pop('ManagerAccess', None)
    return redirect(url_for('home'))


#Test methods are moved to myfile.py

if __name__ == "__main__":
    app.run(debug=True)
