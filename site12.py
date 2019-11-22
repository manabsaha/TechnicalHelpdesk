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

#SESSION VARIABLES: loggedin, id, designation, SuperuserAccess, EmpAccess

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

#----------------------------------------------USER---------------------------------------------------#

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
        return render_template('site/index.html',designation=designation, user=user,name=name,login_flag=True,tab="home")
    if 'SuperuserAccess' in session:
        return redirect(url_for('super_panel'))
        #return render_template('superuser/superuser_panel.html',desg="SUPERUSER",log=session['SuperuserAccess'])
    if 'AdminAccess' in session:
        return redirect(url_for('admin_panel'))
        #return render_template('admin/admin_panel.html',desg="ADMIN",log=session['AdminAccess'])
    if 'ManagerAccess' in session:
        return redirect(url_for('manager_panel'))
        #return render_template('manager/manager_panel.html',desg="MANAGER",log=session['ManagerAccess'])
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


#-----------------------------------------SERVICES---------------------------------------------#

#Services method.
@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'loggedin' in session and session['designation']=="customer":
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT ticket_id,app_date,app_type,status FROM ticket where user_id=%s",(user,))
        data=cur.fetchall()
        return render_template('site/services.html',tab="services",data=data, designation=designation, user=user)
    return redirect(url_for('login'))

#Ticket Generate method.
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
    return render_template('forms/ticket.html',tab="services",designation=escape(session['designation']), data=data,date=date.today(),
        user=escape(session['id']))

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


#All_tickets method.
@app.route('/emp/all_tickets/', methods=['GET', 'POST'])
def all_tickets():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT ticket_id, user_id, fname, app_date,app_type,status FROM ticket where status='processing'")
        data=cur.fetchall()
        return render_template('employee/ticket/all_tickets.html',tab="tickets",data=data,user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Inventory method.
@app.route('/emp/inventory/', methods=['GET', 'POST'])
def inventory():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM inventory")
        data=cur.fetchall()
        return render_template('employee/ticket/inventory.html',tab="inventory",data=data,user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Inventory details method
@app.route('/emp/inventory/<int:id>')
def inventory_details(id):
    if 'EmpAccess' in session:
        cur=mysql.connection.cursor()
        cur.execute("""SELECT * FROM ticket WHERE ticket_id=%s""",(id,))
        return render_template('employee/ticket/inventory_details.html',tab="inventory",ticket=cur.fetchone(),
            desg=session['designation'])
    return redirect(url_for('emp'))

#Inventory redirect method
@app.route('/all_tickets/<int:id>', methods=['GET', 'POST'])
def inv_ticket(id):
    if 'EmpAccess' in session:
        return redirect(url_for('inventory_add', ticket_id=id))
    return redirect(url_for('emp'))


#Inventory add method
@app.route('/inventory_add/<int:ticket_id>', methods=['GET', 'POST'])
def inventory_add(ticket_id):
    if 'EmpAccess' in session:
        if request.method == 'POST':
            product_type = request.form['product_type']
            product_name = request.form['product_name']
            product_description = request.form['product_description']
            fault_type = request.form['fault_type']
            fault_description = request.form['fault_description']
            curr_date = date.today()
            cur=mysql.connection.cursor()
            try:
                cur.execute("""INSERT INTO inventory(ticket_id, product_name,product_type, product_description, fault_type, 
                    fault_description, record_date) 
                    values(%s,%s,%s,%s,%s,%s,%s)""",
                            (ticket_id, product_name, product_type, product_description, fault_type, fault_description, curr_date))

                mysql.connection.commit()
                cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",('Inventory',ticket_id))
                mysql.connection.commit()
                return redirect(url_for('all_tickets'))
            except:
                cur.execute("""CREATE TABLE inventory (inventory_id int AUTO_INCREMENT,
                                                    ticket_id int NOT NULL,
                                                    product_name varchar(50),
                                                    product_type varchar(50),
                                                    product_description varchar(100),
                                                    fault_type varchar(50),
                                                    fault_description varchar(200),
                                                    record_date date,
                                                    PRIMARY KEY (inventory_id),
                                                    FOREIGN KEY (ticket_id)
                                                    REFERENCES ticket(ticket_id))AUTO_INCREMENT=20001""")
                cur.execute("""INSERT INTO inventory(ticket_id, product_name,product_type, product_description,
                     fault_type, fault_description, record_date) 
                               values(%s,%s,%s,%s,%s,%s,%s)""",
                            (ticket_id, product_name, product_type, product_description, fault_type, fault_description, curr_date))
                mysql.connection.commit()
                cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",('Inventory',ticket_id))
                mysql.connection.commit()
                return redirect(url_for('all_tickets'))
        gc.collect()
        return render_template('employee/ticket/add_inventory.html',tab="tickets",date=date.today(), 
            user=escape(session['id']),desg=session['designation'])
    else:
        return redirect(url_for('emp'))

#Ticket details method
@app.route('/ticket_details/<int:id>')
def ticket_details(id):
    if 'EmpAccess' in session:
        cur=mysql.connection.cursor()
        cur.execute("""SELECT * FROM inventory WHERE ticket_id=%s""",(id,))
        return render_template('employee/ticket/ticket_details.html',tab="inventory",ticket=cur.fetchone(),
            desg=session['designation'])
    return redirect(url_for('emp'))

#------------------------------------------EMPLOYEE---------------------------------------------------#


#EMPLOYEE REGISTRATION METHOD
@app.route('/emp/reg',methods=['GET','POST'])
def emp_reg():
    if 'loggedin' not in session:
        if request.method == 'POST':

            try:
                fname = request.form['fname']
                lname = request.form['lname']
                phone = request.form['phone']
                address = request.form['address']
                pincode = request.form['pincode']
                password = request.form['password']
                hash_password = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
                cur = mysql.connection.cursor()
                try:
                    cur.execute("""INSERT INTO employee(fname, lname, phone,address,pincode,hash_password) 
                        values(%s,%s,%s,%s,%s,%s)""", (fname, lname, phone,address,pincode,hash_password))
                except:
                    cur.execute("""CREATE TABLE employee (employee_id int AUTO_INCREMENT,
                                                    fname varchar(20),
                                                    lname varchar(20),
                                                    phone bigint(10) UNIQUE,
                                                    address varchar(100),
                                                    pincode bigint(6),
                                                    job_status varchar(20) DEFAULT 'ACTIVE',
                                                    designation varchar(20) DEFAULT 'EXECUTIVE',
                                                    hash_password varchar(128),
                                                    picture varchar(200) DEFAULT '/static/images/no_dp.png',
                                                    PRIMARY KEY (employee_id))auto_increment=2001""")
                    cur.execute("""INSERT INTO employee(fname, lname, phone,address,pincode,hash_password) 
                        values(%s,%s,%s,%s,%s,%s)""",(fname, lname, phone, address, pincode, hash_password))
                
                cur.execute("""SELECT employee_id,designation from employee where phone=%s""",(phone,))
                employee=cur.fetchone()
                session_val(None,employee['employee_id'],employee['designation'],None,True)
                mysql.connection.commit()
                gc.collect()
                return redirect(url_for('emp'))
            
            except:
                cur.execute("""SELECT phone FROM employee WHERE phone=%s""",(phone,))
                if cur.rowcount == 0:
                    msg= "*Error. Try again"
                    return render_template('employee/reg-login/reg.html',msg=msg)
                else:
                    msg= "*Number already used"
                    return render_template('employee/reg-login/reg.html',msg=msg)

        return render_template('employee/reg-login/reg.html')
    return redirect(url_for('emp'))


#EMPLOYEE LOGIN METHOD
@app.route('/emp/login',methods=['GET','POST'])
def emp_access():
    if 'loggedin' not in session:
        if request.method == 'POST':

            phone = request.form['emp_phone']
            password = request.form['emp_password']
            cur = mysql.connection.cursor()
            cur.execute("""SELECT hash_password FROM employee where phone = %s""",(phone,))
            if(cur.rowcount == 0):
                msg = '*Number not registered'
                return render_template('employee/reg-login/login.html',msg=msg)

            psw=cur.fetchone()
            hash_password = psw['hash_password']
            check_pass = bcrypt.hashpw(password.encode('utf8'),hash_password.encode('utf8'))
            if(check_pass==hash_password.encode('utf8')):
                cur.execute("""SELECT employee_id,designation FROM employee where phone = %s""",(phone,))
                id=cur.fetchone()
                session_val(None,id['employee_id'],id['designation'],None,True)
                return redirect(url_for('emp'))
            else:
                msg = '*Incorrect password!'
                return render_template('employee/reg-login/login.html',msg=msg)

        return render_template('employee/reg-login/login.html')
    return redirect(url_for('emp'))


#EMPLOYEE LOGOUT
@app.route('/emp/logout',methods=['GET','POST'])
def emp_logout():
    session.pop('EmpAccess', None)
    return redirect(url_for('emp'))

#EMPLOYEE HOME
@app.route('/emp',methods=['GET','POST'])
def emp():
    if 'EmpAccess' in session:
        print(session['designation'])
        return render_template('/employee/employee.html',desg=session['designation'],tab="stats")
    return redirect(url_for('emp_access'))

#Employee Profile Method.
@app.route('/emp/profile/', methods=['GET', 'POST'])
def emp_profile():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from employee where employee_id= %s""", (user,))
        d = cur.fetchone()
        pic_url = d['picture']
        if request.method=='POST':
            if request.form['submit']=="edit":
                return redirect(url_for('edit_emp_profile'))
            if request.form['submit']=="change":
                return redirect(url_for('change_emp_password'))
        return render_template('employee/profile/emp_profile.html',tab="profile",desg=session['designation'], data=d,user=user,pic=pic_url)
    return redirect(url_for('emp'))

#Edit Employee profile method.
@app.route('/emp/edit_profile/', methods=['GET', 'POST'])
def edit_emp_profile():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur = mysql.connection.cursor()
        cur.execute("""select * from employee where employee_id= %s""", (session['id'],))
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
                cur.execute("""update employee set fname=%s,lname=%s,phone=%s,address=%s,pincode=%s where employee_id=%s""", (
                    fname, lname, phone, address, pincode, session['id'],))
                if file.filename!= '':
                    firebase = pyrebase.initialize_app(config)
                    storage = firebase.storage()
                    storage.child("images/employee/"+user+"/new.jpg").put(file)
                    new_pic_url = storage.child("images/employee/" + user + "/new.jpg").get_url(None)
                    cur.execute("""update employee set picture=%s where employee_id=%s""",(new_pic_url,session['id']))
            except:
                pass
            mysql.connection.commit()
            return redirect(url_for('emp_profile'))
        return render_template('employee/profile/emp_edit_profile.html',tab="profile", data=d,user=user,pic=pic_url,desg=session['designation'])
    return redirect(url_for('emp'))

#Change employee password method.
@app.route('/emp/change_password/', methods=['GET','POST'])
def change_emp_password():
    if 'EmpAccess' in session:
        cur = mysql.connection.cursor()
        user = escape(session['id'])
        designation = escape(session['designation'])
        if request.method == 'POST':
            old_pass = request.form['pass']
            password = request.form['password']

            cur.execute("""SELECT hash_password FROM employee where employee_id = %s""", (session['id'],))
            psw = cur.fetchone()
            hash_password = psw['hash_password']
            check_pass = bcrypt.hashpw(old_pass.encode('utf8'), hash_password.encode('utf8'))
            if (check_pass == hash_password.encode('utf8')):
                new_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                cur.execute("""update employee set hash_password=%s where employee_id = %s""", (new_hash, session['id'],))

            else:
                msg = '*Incorrect password!'
                return render_template('employee/profile/emp_change_pass.html',tab="profile",desg=session['designation'], msg=msg,user=user)
            mysql.connection.commit()
            return redirect(url_for('emp_profile'))
        return render_template('employee/profile/emp_change_pass.html',tab="profile",user=user,desg=session['designation'])
    return redirect(url_for('emp'))


#ADMIN PANEL
@app.route('/emp/adminpanel',methods=['GET','POST'])
def admin_panel():
    if 'AdminAccess' in session:
        return render_template('employee/admin/admin_panel.html',desg="ADMIN",log=session['AdminAccess'])
    return redirect(url_for('emp_access'))

#MANAGER PANEL
@app.route('/emp/managerpanel/',methods=['GET','POST'])
def manager_panel():
    if 'ManagerAccess' in session:
        return render_template('employee/manager/manager_panel.html',desg="MANAGER",log=session['ManagerAccess'])
    return redirect(url_for('emp_access'))


#-----------------------------------------SUPERUSER------------------------------------------------#

#SUPERUSER ACCESS METHOD
@app.route('/emp/superuser/access/',methods=['GET','POST'])
def super_access():
    if 'loggedin' not in session:
        if request.method == 'POST':
            superuser_password = request.form['su_password']
            if superuser_password == "superuser":
                session_val(None,None,None,True,None)
                return redirect(url_for('super_panel'))
        return render_template('employee/superuser/superuser_access.html')
    return redirect(url_for('home'))

#SUPERUSER PANEL
@app.route('/emp/superuser/panel/',methods=['GET','POST'])
def super_panel():
    if 'SuperuserAccess' in session:
        if request.method == 'POST':
            su_query = request.form['su_query']
            phone = request.form['phone']
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE employee SET designation=%s WHERE phone=%s""",(su_query,phone))
            mysql.connection.commit()
        return render_template('employee/superuser/superuser_panel.html',desg="SUPERUSER",log=session['SuperuserAccess'])
    return redirect(url_for('super_access'))

#SUPERUSER LOGOUT
@app.route('/emp/superuser/logout',methods=['GET','POST'])
def super_logout():
    session.pop('SuperuserAccess', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
