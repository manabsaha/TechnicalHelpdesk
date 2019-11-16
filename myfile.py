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


if __name__ == "__main__":
    app.run()
