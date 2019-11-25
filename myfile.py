from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import random

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'abc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    # if request.method=='POST':
    #     a=request.form['x']
    #     b=request.form['y']
    #     return render_template('hello.html',sum=int(a)+int(b))
    cur = mysql.connection.cursor()
    # cur.execute('''show tables''')
    cur.execute("SELECT * FROM products_product")
    results = cur.fetchall()

    if request.method == 'POST':
        id = request.form['id']
        title = request.form['title']
        desc = request.form['desc']
        p_id = request.form['p_id']
        #cur.execute("""INSERT INTO products_product
        #         values(%s,%s,%s,%s)""", (id, title, desc, p_id))
    cur.execute("""INSERT INTO products_product values(%s,%s,%s,%s)""", (random.randint(1,1000), random.randint(1,1000), random.randint(1,1000), random.randint(1,1000)))
    mysql.connection.commit()
    return render_template('tables.html', data=results)



#----------------------------------------TEST METHODS---------------------------------------#

@app.route('/user/<username>', methods=['GET', 'POST'])
def home_user(username):
    flash("successful")
    return render_template('site/index.html',user=username)


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

#----------------------------------------END------------------------------------------------------#


if __name__ == "__main__":
    app.run()



# except:
            #     cur.execute("""CREATE TABLE user (
            #                                     user_id int AUTO_INCREMENT,
            #                                     fname varchar(20),
            #                                     lname varchar(20),
            #                                     phone bigint(10) UNIQUE,
            #                                     address varchar(100),
            #                                     pincode bigint(6),
            #                                     hash_password varchar(128),
            #                                     picture varchar(200) DEFAULT '/static/images/no_dp.png',
            #                                     designation varchar(50) DEFAULT 'customer',
            #                                     PRIMARY KEY (user_id))auto_increment=1001""")
            #     cur.execute("""INSERT INTO user(fname, lname, phone,address,pincode,hash_password) 
            #         values(%s,%s,%s,%s,%s,%s)""",(fname, lname, phone, address, pincode, hash_password))


# except:
        #     cur.execute("""CREATE TABLE ticket (ticket_id int AUTO_INCREMENT,
        #                                         user_id int NOT NULL,
        #                                         fname varchar(20),
        #                                         lname varchar(20),
        #                                         phone bigint(10),
        #                                         address varchar(100),
        #                                         app_date date, 
        #                                         curr_date date,
        #                                         app_type varchar(20) CHECK(app_type IN ('Appointment','Pickup')),
        #                                         status varchar(20) DEFAULT 'Processing',
        #                                         PRIMARY KEY (ticket_id),
        #                                         FOREIGN KEY (user_id)
        #                                         REFERENCES user(user_id))AUTO_INCREMENT=10001""")
        #     cur.execute("""INSERT INTO ticket(user_id,fname, lname, phone, address, app_date, curr_date,app_type) 
        #         values(%s,%s,%s,%s,%s,%s,%s,%s)""", (session['id'], fname, lname, phone, address, app_date,
        #         curr_date, type))
        #     mysql.connection.commit()
        #    return redirect(url_for('services'))



# except:
        #     cur.execute("""CREATE TABLE inventory (inventory_id int AUTO_INCREMENT,
        #                                         ticket_id int NOT NULL,
        #                                         product_name varchar(50),
        #                                         product_type varchar(50),
        #                                         product_description varchar(100),
        #                                         fault_type varchar(50),
        #                                         fault_description varchar(200),
        #                                         record_date date,
        #                                         PRIMARY KEY (inventory_id),
        #                                         FOREIGN KEY (ticket_id)
        #                                         REFERENCES ticket(ticket_id))AUTO_INCREMENT=20001""")
        #     cur.execute("""INSERT INTO inventory(ticket_id, product_name,product_type, product_description,
        #          fault_type, fault_description, record_date) 
        #                    values(%s,%s,%s,%s,%s,%s,%s)""",
        #                 (ticket_id, product_name, product_type, product_description, fault_type, fault_description, curr_date))
        #     mysql.connection.commit()
        #     cur.execute("""UPDATE ticket SET status=%s WHERE ticket_id=%s""",('Inventory',ticket_id))
        #     mysql.connection.commit()
        #     return redirect(url_for('all_tickets'))


# except:
                #     cur.execute("""CREATE TABLE employee (employee_id int AUTO_INCREMENT,
                #                                     fname varchar(20),
                #                                     lname varchar(20),
                #                                     phone bigint(10) UNIQUE,
                #                                     address varchar(100),
                #                                     pincode bigint(6),
                #                                     job_status varchar(20) DEFAULT 'ACTIVE',
                #                                     designation varchar(20) DEFAULT 'EXECUTIVE',
                #                                     hash_password varchar(128),
                #                                     picture varchar(200) DEFAULT '/static/images/no_dp.png',
                #                                     PRIMARY KEY (employee_id))auto_increment=2001""")
                #     cur.execute("""INSERT INTO employee(fname, lname, phone,address,pincode,hash_password) 
                #         values(%s,%s,%s,%s,%s,%s)""",(fname, lname, phone, address, pincode, hash_password))