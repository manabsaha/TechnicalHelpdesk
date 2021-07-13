from flask import Flask, url_for, request, redirect, render_template,flash, session, escape
#from flask_mysqldb import MySQL
import bcrypt
import random
import gc
import pyrebase
from datetime import date
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xeao\x1a\x00\xcd\x08\n\x141\xbdr\xe6i\x82+>\xf5\x96\xf2\xa1\xb8\x01\x19\\\x8a\x0e\xdf\xcc3f!\xd4'

#MySQL config.
# app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
# app.config['MYSQL_USER'] = 'sql12357996'
# app.config['MYSQL_PASSWORD'] = '2qdbyd7xCK'
# app.config['MYSQL_DB'] = 'sql12357996'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#mysql = MySQL(app)

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

DB_HOST = "ec2-184-73-192-172.compute-1.amazonaws.com"
DB_USER = "lgldwgidoyuihn"
DB_PASS = "14f0ccae54d7fa77417942f8a11c4e46c8cc710415c5c4a7e1a3eaa541d973bf"
DB_NAME = "dbusrqlquo0res"

# DB_HOST = "localhost"
# DB_USER = "postgres"
# DB_PASS = "root"
# DB_NAME = "helpdesk"

conn = psycopg2.connect(dbname=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST)

def init():
    try:
        cur=conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                                        user_id SERIAL PRIMARY KEY,
                                        fname varchar(20),
                                        lname varchar(20),
                                        phone bigint UNIQUE,
                                        address varchar(100),
                                        pincode bigint,
                                        hash_password varchar(128),
                                        picture varchar(200) DEFAULT '/static/images/no_dp.png',
                                        designation varchar(50) DEFAULT 'customer')""")
    except Exception as e:
        print(e)

    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS feedback (phone bigint,message varchar(200))""")
    except Exception as e:
        print(e)


    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS ticket (ticket_id serial primary key,
                                                        user_id int NOT NULL,
                                                        fname varchar(20),
                                                        lname varchar(20),
                                                        phone bigint,
                                                        address varchar(100),
                                                        app_date date, 
                                                        curr_date date,
                                                        app_type varchar(20) CHECK(app_type IN ('Appointment','Pickup')),
                                                        status varchar(20) DEFAULT 'Processing',
                                                        FOREIGN KEY (user_id)
                                                        REFERENCES users(user_id))""")
    except Exception as e:
        print(e)

    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS inventory (inventory_id serial primary key,
                                                            ticket_id int NOT NULL,
                                                            product_name varchar(50),
                                                            product_type varchar(50),
                                                            product_description varchar(100),
                                                            fault_type varchar(50),
                                                            fault_description varchar(200),
                                                            record_date date,
                                                            FOREIGN KEY (ticket_id)
                                                            REFERENCES ticket(ticket_id))""")
    except Exception as e:
        print(e)

    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS employee (employee_id serial primary key,
                                                            fname varchar(20),
                                                            lname varchar(20),
                                                            phone bigint UNIQUE,
                                                            address varchar(100),
                                                            pincode bigint,
                                                            job_status varchar(20) DEFAULT 'ACTIVE',
                                                            designation varchar(20) DEFAULT 'EXECUTIVE',
                                                            hash_password varchar(128),
                                                            picture varchar(200) DEFAULT '/static/images/no_dp.png'
                                                            )""")
    except Exception as e:
        print(e)

    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS assignment (ticket_id int UNIQUE,
                                                employee_id int,
                                                record_date date,
                                                FOREIGN KEY(employee_id)
                                                REFERENCES employee(employee_id),
                                                FOREIGN KEY(ticket_id)
                                                REFERENCES ticket(ticket_id))""")
    except Exception as e:
        print(e)

    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS employee_superior (employee_id int,
                                                        superior_id int,
                                                        FOREIGN KEY(employee_id)
                                                        REFERENCES employee(employee_id),
                                                        FOREIGN KEY(superior_id)
                                                        REFERENCES employee(employee_id))""")
    except Exception as e:
        print(e)

    cur.close()
    conn.commit()


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

@app.route('/create_all')
def create_all():
    init()
    return redirect(url_for('home'))

#HOME PAGE.
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        user = escape(session['id'])
        designation=escape(session['designation'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT fname FROM users where user_id=%s""",(user,))
        name = cur.fetchone()
        name = name['fname']
        return render_template('site/index.html',designation=designation, user=user,name=name,login_flag=True,tab="home")
    if 'SuperuserAccess' in session:
        return redirect(url_for('super_panel'))
        #return render_template('superuser/superuser_panel.html',desg="SUPERUSER",log=session['SuperuserAccess'])
    if 'EmpAccess' in session:
        return redirect(url_for('emp'))
        #return render_template('admin/admin_panel.html',desg="ADMIN",log=session['AdminAccess'])
    return render_template('site/index.html',tab="home")


#Register method.
@app.route('/reg/', methods=['GET', 'POST'])
def reg():
    if 'loggedin' in session or 'EmpAccess' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            address = request.form['address']
            pincode = request.form['pincode']
            password = request.form['password']
            hash_password = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

            try:
                cur.execute("""INSERT INTO users(fname, lname, phone,address,pincode,hash_password) 
                    values(%s,%s,%s,%s,%s,%s)""", (fname, lname, phone,address,pincode,hash_password))
            except:
                pass

            cur.execute("""SELECT user_id,designation from users where phone=%s""",(phone,))
            user_id=cur.fetchone()
            session_val(True,user_id['user_id'],user_id['designation'],None,None)
            conn.commit()
            gc.collect()
            return redirect(url_for('home'))

        except:
            cur.execute("""SELECT phone FROM users WHERE phone=%s""",(phone,))
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
    if request.method == 'POST':
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        phone = request.form['phone']
        password = request.form['password']

        cur.execute("""SELECT hash_password FROM users where phone = %s""",(phone,))
        if(cur.rowcount == 0):
            msg = '*Number not registered'
            return render_template('reg-login/login.html',msg=msg)

        psw=cur.fetchone()
        hash_password = psw['hash_password']
        check_pass = bcrypt.hashpw(password.encode('utf8'),hash_password.encode('utf8'))
        cur.execute("""SELECT user_id,designation FROM users where phone = %s""",(phone,))
        id=cur.fetchone()
        if(check_pass==hash_password.encode('utf8')):
            session_val(True,id['user_id'],id['designation'],None,None)
            flash('You were logged in')
            return redirect(url_for('home'))
        else:
            msg = '*Incorrect password!'
            return render_template('reg-login/login.html',msg=msg)

    return render_template('reg-login/login.html')

#Logout method.
@app.route('/logout/',methods=['GET','POST'])
def logout():
    if 'loggedin' in session:
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select * from users where user_id= %s""", (user,))
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select * from users where user_id= %s""", (session['id'],))
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
                cur.execute("""update users set fname=%s,lname=%s,phone=%s,address=%s,pincode=%s where user_id=%s""", (
                    fname, lname, phone, address, pincode, session['id'],))
                if file.filename!= '':
                    firebase = pyrebase.initialize_app(config)
                    storage = firebase.storage()
                    storage.child("images/"+user+"/new.jpg").put(file)
                    new_pic_url = storage.child("images/" + user + "/new.jpg").get_url(None)
                    cur.execute("""update users set picture=%s where user_id=%s""",(new_pic_url,session['id']))
            except:
                pass
            conn.commit()
            return redirect(url_for('profile'))
        return render_template('reg-login/edit_profile.html',tab="profile",designation=designation, data=d,user=user,pic=pic_url)
    return redirect(url_for('home'))

#Change password method.
@app.route('/change_password/', methods=['GET','POST'])
def change_password():
    if 'loggedin' in session:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        user = escape(session['id'])
        designation = escape(session['designation'])
        if request.method == 'POST':
            old_pass = request.form['pass']
            password = request.form['password']

            cur.execute("""SELECT hash_password FROM users where user_id = %s""", (session['id'],))
            psw = cur.fetchone()
            hash_password = psw['hash_password']
            check_pass = bcrypt.hashpw(old_pass.encode('utf8'), hash_password.encode('utf8'))
            if (check_pass == hash_password.encode('utf8')):
                new_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                cur.execute("""update users set hash_password=%s where user_id = %s""", (new_hash, session['id'],))

            else:
                msg = '*Incorrect password!'
                return render_template('reg-login/change_pass.html',tab="profile",designation=designation, msg=msg,user=user)
            conn.commit()
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
            cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute("""INSERT INTO feedback values(%s,%s)""", (user,feedback))
            except:
                cur.execute("""CREATE TABLE feedback (phone bigint(10),message varchar(200))""")
                cur.execute("""INSERT INTO feedback values(%s,%s)""", (user,feedback))
            conn.commit()
            return redirect(url_for('home'))
        return render_template('site/contact.html',tab="contact", user=user, designation=designation)
    return redirect(url_for('login'))


#-----------------------------------------TECHNICIAN(MANAGER VIEW)--------------------------------------------#

#All technicians method.
@app.route('/emp/technicians/', methods=['GET', 'POST'])
def technicians():
    if 'EmpAccess' in session and session['designation']=='MANAGER':
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # cur.execute("SELECT *,count(*) FROM assignment,employee where designation='TECHNICIAN' and "
        #             "assignment.employee_id= employee.employee_id group by employee.employee_id order by count(*)")
        cur.execute("""select * from employee,employee_superior where employee_superior.superior_id=%s
           and employee.employee_id = employee_superior.employee_id and designation='TECHNICIAN'""",(user,))
        data = cur.fetchall()
        cur.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        cur.execute("""select *, count(*) from employee, assignment where employee.employee_id=assignment.employee_id group 
        by employee.employee_id""")
        count = cur.fetchall()
        #print(data)
        return render_template('employee/technician/technicians.html',flag={'value':'False'}, count=count,tab="tickets",data=data, user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#View technician profile.
@app.route('/emp/technician/<int:tech_id>',methods=['GET','POST'])
def technician_profile(tech_id):
    cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT * FROM employee WHERE employee_id=%s""",(tech_id,))
    return render_template('/employee/read_profile.html',data=cur.fetchone(),tab="tickets",desg=session['designation'])

#Assign_job method.
@app.route('/emp/assign_job/', methods=['GET', 'POST'])
def assign_job():
    if 'EmpAccess' in session and session['designation']=='MANAGER':
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # cur.execute("SELECT *,count(*) FROM assignment,employee where designation='TECHNICIAN' and "
        #             "assignment.employee_id= employee.employee_id group by employee.employee_id order by count(*)")
        cur.execute("""select * from employee,employee_superior where employee_superior.superior_id=%s
                   and employee.employee_id = employee_superior.employee_id and designation='TECHNICIAN'""", (user,))
        data = cur.fetchall()
        cur.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        cur.execute("""select *, count(*) from employee, assignment where employee.employee_id=assignment.employee_id group 
                by employee.employee_id""")
        count = cur.fetchall()
        return render_template('employee/technician/assign_job.html',tab="TECHNICIAN",flag={'value':'False'}, count=count,data=data,user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Assign_job method.
@app.route('/emp/assign_job/<int:tech_id>', methods=['GET', 'POST'])
def assign_job_redirect(tech_id):
    if 'EmpAccess' in session and session['designation']=='MANAGER':
        user = escape(session['id'])
        return redirect(url_for('assign_pending_inventory',tech_id=tech_id))
    return redirect(url_for('emp'))

#Job assigned
@app.route('/emp/assigned/<int:tktid>/<int:techid>',methods=['GET','POST'])
def assigned_job(tktid,techid):
    if 'EmpAccess' in session and session['designation']=='MANAGER':
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""insert into assignment values(%s,%s,%s)""",(tktid,techid,0))
        conn.commit()
        cur.execute("""update ticket set status='Assigned' where ticket_id=%s""",(tktid,))
        conn.commit()
        return redirect(url_for('assign_job'))
    return redirect(url_for('emp'))


#----------------------------------------MANAGER(ADMIN)---------------------------------------------#

#Managers method
@app.route('/emp/managers', methods=['GET','POST'])
def managers():
    if 'EmpAccess' in session and session['designation']=='ADMIN':
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # cur.execute("SELECT *,count(*) FROM assignment,employee where designation='TECHNICIAN' and "
        #             "assignment.employee_id= employee.employee_id group by employee.employee_id order by count(*)")
        cur.execute("""select * from employee,employee_superior where employee_superior.superior_id=%s
           and employee.employee_id = employee_superior.employee_id and designation='MANAGER'""",(user,))
        data = cur.fetchall()
        cur.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        cur.execute("""select *, count(*) from employee, employee_superior where employee.employee_id=employee_superior.superior_id group 
        by employee.employee_id""")
        count = cur.fetchall()
        #print(data)
        return render_template('employee/manager/managers.html',flag={'value':'False'}, count=count,tab="manager",data=data, user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Technician_allot method
@app.route('/emp/allot_technician', methods=['GET','POST'])
def allot_technician():
    if 'EmpAccess' in session and session['designation']=='ADMIN':
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #cur.execute("SELECT * FROM inventory,ticket where inventory.ticket_id=ticket.ticket_id and status='inventory';")
        #data=cur.fetchall()
        cur.execute("""select * from employee,employee_superior where employee_superior.superior_id=%s
                   and employee.employee_id = employee_superior.employee_id and designation='MANAGER'""", (user,))
        alloted=cur.fetchall()
        cur.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        cur.execute("""select *, count(*) from employee, employee_superior where employee.employee_id=employee_superior.superior_id group 
                by employee.employee_id""")
        count = cur.fetchall()
        return render_template('employee/manager/allot_technician.html',tab="inventory",alloted=alloted, user=user,
            desg=session['designation'],emp=emp,flag={'value':'False'}, count=count)
    return redirect(url_for('emp'))

#Allocate redirect method
@app.route('/emp/allot_technician/<int:mgr_id>', methods=['GET','POST'])
def allocate(mgr_id):
    if 'EmpAccess' in session and session['designation']=='ADMIN':
        user = escape(session['id'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select * from employee,employee_superior where superior_id=%s and 
            employee.employee_id = employee_superior.employee_id and designation='TECHNICIAN'""", (mgr_id,))
        technicians = cur.fetchall()
        # cur.execute("""select * from employee where employee_id not in(select employee_id from employee_superior where 
        # superior_id=%s) and designation='TECHNICIAN' or designation='EMPLOYEE'""",(mgr_id,))
        cur.execute("""select * from employee where employee_id not in(select employee_id from employee_superior) and 
                designation='TECHNICIAN' or designation='EMPLOYEE'""")
        pending = cur.fetchall()
        cur.execute(
            """SELECT * FROM employee where employee_id=%s;""", (mgr_id,))
        emp = cur.fetchone()
        return render_template('employee/manager/allocation.html', tab="manager", user=user, emp=emp,technicians=technicians,
                               pending=pending, desg=session['designation'])
    return redirect(url_for('emp'))

#Allot technician to manager final gateway
@app.route('/emp/allot_technician/<int:mgr_id>/<int:emp_id>', methods=['GET', 'POST'])
def allocation_redirect(mgr_id,emp_id):
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""insert into employee_superior values(%s,%s) ;""",(emp_id,mgr_id,))
        cur.execute("""update employee set designation='TECHNICIAN' where employee_id=%s""",(emp_id,))
        conn.commit()
        return redirect(url_for('allocate',mgr_id=mgr_id))
    return redirect(url_for('emp'))

#Remove technician to manager final gateway
@app.route('/emp/remove_technician/<int:mgr_id>/<int:emp_id>', methods=['GET', 'POST'])
def deallocation_redirect(mgr_id,emp_id):
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""delete from employee_superior where employee_id=%s""",(emp_id,))
        conn.commit()
        return redirect(url_for('allocate',mgr_id=mgr_id))
    return redirect(url_for('emp'))

#View manager profile.
@app.route('/emp/manager/<int:mgr_id>',methods=['GET','POST'])
def manager_profile(mgr_id):
    if 'EmpAccess' in session and session['designation'] == 'ADMIN':
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM employee WHERE employee_id=%s""",(mgr_id,))
        return render_template('/employee/read_profile.html',data=cur.fetchone(),tab="tickets",desg=session['designation'])
    return redirect(url_for('emp'))

@app.route('/emp/admin/tickets')
def admin_tickets():
    if 'EmpAccess' in session and session['designation'] == 'ADMIN':
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select * from employee_superior where superior_id=%s""",(session['id'],))
        mg=cur.fetchall()
        tech=[]
        tickets=[]
        for x in mg:
            cur.execute("""select * from employee_superior where superior_id=%s""",(x['employee_id'],))
            tech.append(cur.fetchall())
        for i in range(0,len(tech)):
            for j in range(0,len(tech[i])):
                cur.execute("""select ticket_id from assignment where employee_id=%s""",(tech[i][j]['employee_id'],))
                tickets.append(cur.fetchall())
        return render_template('/employee/admin/all_employee.html', tab="tickets", tech=tech, mg=mg,tkts=tickets,
                               desg=session['designation'])
    return redirect(url_for('emp'))


#----------------------------------------TECHNICIAN---------------------------------------------#
#Technician Tickets
@app.route('/emp/jobs',methods=['GET','POST'])
def tech_tickets():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM ticket,assignment WHERE 
            ticket.ticket_id=assignment.ticket_id AND employee_id=%s ORDER BY record_date DESC""",(user,))
        return render_template('/employee/technician/technician_tickets.html',data=cur.fetchall(),
            tab="inventory",user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Update status
@app.route('/emp/jobs/<string:status>/<int:tkt_id>',methods=['GET','POST'])
def update_status(status,tkt_id):
    if 'EmpAccess' in session:
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",(status,tkt_id))
        conn.commit()
        return redirect(url_for('tech_tickets'))
    return redirect(url_for('emp'))

#-----------------------------------------SERVICES---------------------------------------------#

#Services method.
@app.route('/services/', methods=['GET', 'POST'])
def services():
    if 'loggedin' in session and session['designation']=="customer":
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT ticket_id,app_date,app_type,status FROM ticket where user_id=%s ORDER BY curr_date DESC",(user,))
        data=cur.fetchall()
        return render_template('site/services.html',tab="services",data=data, designation=designation, user=user)
    return redirect(url_for('login'))

#Ticket Generate method.
@app.route('/ticket/', methods=['GET','POST'])
def ticket():
    if 'loggedin' not in session:
         return redirect(url_for('login'))
    cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""select * from users where user_id= %s""", (session['id'],))
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
            conn.commit()
            return redirect(url_for('home'))
        except:
            pass
    gc.collect()
    return render_template('forms/ticket.html',tab="services",designation=escape(session['designation']), data=data,date=date.today(),
        user=escape(session['id']))

#Cancel Ticket method.
@app.route('/services/<int:id>')
def cancel(id):
    if 'loggedin' in session and session['designation']=="customer":
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        status = "CANCELLED BY USER"
        cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",(status,id))
        conn.commit()
        return redirect(url_for('services'))
    return redirect(url_for('login'))


#All_tickets method.
@app.route('/emp/all_tickets/', methods=['GET', 'POST'])
def all_tickets():
    if 'EmpAccess' in session and session['designation']=='EXECUTIVE':
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT ticket_id, user_id, fname, app_date,app_type,status FROM ticket 
            where status='processing' ORDER BY app_date DESC""")
        data=cur.fetchall()
        return render_template('employee/ticket/all_tickets.html',tab="tickets",data=data,user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Inventory method.
@app.route('/emp/inventory/', methods=['GET', 'POST'])
def inventory():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM inventory,ticket where inventory.ticket_id=ticket.ticket_id
             ORDER BY record_date DESC;""")
        data=cur.fetchall()
        return render_template('employee/ticket/inventory.html',tab="inventory",data=data,user=user,desg=session['designation'])
    return redirect(url_for('emp'))

#Pending Inventory method(For manager).
@app.route('/emp/pending_inventory/', methods=['GET', 'POST'])
def pending_inventory():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM inventory,ticket where inventory.ticket_id=ticket.ticket_id and 
            status='inventory' ORDER BY app_date DESC;""")
        data=cur.fetchall()
        return render_template('employee/ticket/inventory.html',tab="inventory",data=data,user=user,
            desg=session['designation'])
    return redirect(url_for('emp'))

#Pending inventory items assignment.
@app.route('/emp/pending_inventory/<int:tech_id>', methods=['GET', 'POST'])
def assign_pending_inventory(tech_id):
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #cur.execute("SELECT * FROM inventory,ticket where inventory.ticket_id=ticket.ticket_id and status='inventory';")
        #data=cur.fetchall()
        cur.execute("""SELECT * FROM inventory,ticket where inventory.ticket_id=ticket.ticket_id 
            and status='inventory' ORDER BY ticket.app_date DESC;""")
        pending=cur.fetchall()
        cur.execute("""SELECT * FROM assignment, ticket,inventory where inventory.ticket_id=assignment.ticket_id 
            and assignment.ticket_id=ticket.ticket_id and assignment.employee_id=%s
            ORDER BY assignment.record_date DESC;""",(tech_id,))
        assigned = cur.fetchall()
        cur.execute(
            """SELECT * FROM employee where employee_id=%s;""",(tech_id,))
        emp = cur.fetchone()
        return render_template('employee/ticket/pending_inventory.html',tab="inventory",pending=pending,assigned=assigned, user=user,
            desg=session['designation'],assign=True,tech_id=tech_id,emp=emp)
    return redirect(url_for('emp'))

#Pending inventory items assignment redirect.
@app.route('/emp/pending_inventory/<int:tech_id>/<int:ticket_id>', methods=['GET', 'POST'])
def assign_pending_redirect(tech_id,ticket_id):
    if 'EmpAccess' in session:
        user = escape(session['id'])
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""insert into assignment values(%s,%s,%s) ;""",(ticket_id,tech_id,date.today()))
        cur.execute("""update ticket set status='Assigned' where ticket_id=%s""",(ticket_id,))
        conn.commit()

        return redirect(url_for('assign_pending_inventory',tech_id=tech_id))
    return redirect(url_for('emp'))

#Inventory details method
@app.route('/emp/inventory/<int:id>')
def inventory_details(id):
    if 'EmpAccess' in session:
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute("""INSERT INTO inventory(ticket_id, product_name,product_type, product_description, fault_type, 
                    fault_description, record_date) 
                    values(%s,%s,%s,%s,%s,%s,%s)""",
                            (ticket_id, product_name, product_type, product_description, fault_type, fault_description, curr_date))

                conn.commit()
                cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",('Inventory',ticket_id))
                conn.commit()
                return redirect(url_for('all_tickets'))
            except:
                pass
        gc.collect()
        return render_template('employee/ticket/add_inventory.html',tab="tickets",date=date.today(), 
            user=escape(session['id']),desg=session['designation'])
    else:
        return redirect(url_for('emp'))

#Inventory completed tickets
@app.route('/emp/completed_tickets',methods=['GET','POST'])
def completed_tickets():
    if 'EmpAccess' in session:
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM inventory,ticket WHERE inventory.ticket_id=ticket.ticket_id and (status='Completed' or status='Ready for delivery')
            ORDER BY record_date DESC;""")
        return render_template('/employee/ticket/completed_tickets.html',data=cur.fetchall(),tab="inventory",
            user=session['id'],desg=session['designation'])
    return redirect(url_for('emp'))

#Ticket ready for delivery.
#Ticket delivered and removed from inventory.
@app.route('/emp/completed_tickets/<int:tkt_id>/<string:status>',methods=['GET','POST'])
def completed_ticket(tkt_id,status):
    if 'EmpAccess' in session:
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if status=="ready":
            cur.execute("""UPDATE ticket SET status='Ready for delivery' WHERE ticket_id=%s""",(tkt_id,))
            conn.commit()
        elif status=="delivered":
            cur.execute("""UPDATE ticket SET status='DELIVERED' WHERE ticket_id=%s""",(tkt_id,))
            conn.commit()
            cur.execute("""DELETE FROM inventory WHERE ticket_id=%s""",(tkt_id,))
        return redirect(url_for('completed_tickets'))
    return redirect(url_for('emp'))

#Ticket details method
@app.route('/ticket_details/<int:id>')
def ticket_details(id):
    if 'EmpAccess' in session:
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT * FROM inventory WHERE ticket_id=%s""",(id,))
        return render_template('employee/ticket/ticket_details.html',tab="inventory",ticket=cur.fetchone(),
            desg=session['designation'])
    return redirect(url_for('emp'))

#------------------------------------------EMPLOYEE---------------------------------------------------#


#EMPLOYEE REGISTRATION METHOD
@app.route('/emp/reg',methods=['GET','POST'])
def emp_reg():
    if 'loggedin' not in session and 'EmpAccess' not in session:
        if request.method == 'POST':

            try:
                fname = request.form['fname']
                lname = request.form['lname']
                phone = request.form['phone']
                address = request.form['address']
                pincode = request.form['pincode']
                password = request.form['password']
                hash_password = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                try:
                    cur.execute("""INSERT INTO employee(fname, lname, phone,address,pincode,hash_password) 
                        values(%s,%s,%s,%s,%s,%s)""", (fname, lname, phone,address,pincode,hash_password))
                except:
                    pass
                
                cur.execute("""SELECT employee_id,designation from employee where phone=%s""",(phone,))
                employee=cur.fetchone()
                session_val(None,employee['employee_id'],employee['designation'],None,True)
                conn.commit()
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
    if 'loggedin' not in session and 'EmpAccess' not in session:
        if request.method == 'POST':

            phone = request.form['emp_phone']
            password = request.form['emp_password']
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
                flash('You were logged in')
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
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from feedback")
        feedback=cur.fetchall()
        feedback=random.sample(feedback,5)
        return render_template('/employee/employee.html',desg=session['designation'],tab="stats",feedback=feedback)
    return redirect(url_for('emp_access'))

#Employee Profile Method.
@app.route('/emp/profile/', methods=['GET', 'POST'])
def emp_profile():
    if 'EmpAccess' in session:
        user = escape(session['id'])
        designation = escape(session['designation'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            conn.commit()
            return redirect(url_for('emp_profile'))
        return render_template('employee/profile/emp_edit_profile.html',tab="profile", data=d,user=user,pic=pic_url,desg=session['designation'])
    return redirect(url_for('emp'))

#Change employee password method.
@app.route('/emp/change_password/', methods=['GET','POST'])
def change_emp_password():
    if 'EmpAccess' in session:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            conn.commit()
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
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""UPDATE employee SET designation=%s WHERE phone=%s""",(su_query,phone))
            conn.commit()
        return render_template('employee/superuser/superuser_panel.html',desg="SUPERUSER",log=session['SuperuserAccess'])
    return redirect(url_for('super_access'))

#SUPERUSER LOGOUT
@app.route('/emp/superuser/logout',methods=['GET','POST'])
def super_logout():
    session.pop('SuperuserAccess', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
   app.run(debug=True)
