from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

#! initialize Flask app
expensetracker=Flask(__name__)

#! Connection to database
expensetracker.config['MYSQL_HOST']='sql8.freesqldatabase.com'
expensetracker.config['MYSQL_USER']='sql8750720'
expensetracker.config['MYSQL_PASSWORD']='JkVZEa4fZY'
expensetracker.config['MYSQL_DB']='sql8750720'

#! initialize MySQL Connection
mysql=MySQL(expensetracker)

@expensetracker.route('/')
def index():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM expenses')
    data=cur.fetchall()
    return render_template('index.html', expenses=data)


#! inserting data
@expensetracker.route('/insert', methods=['POST'])
def insert():
    category=request.form['category']
    amount=request.form['amount']
    desc=request.form['description']
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO expenses (category, amount, description) VALUES (%s, %s, %s)',(category, amount, desc))
    mysql.connection.commit()
    return redirect(url_for('index'))

#! delete data
@expensetracker.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM expenses WHERE ID=%s', [id])
    mysql.connection.commit()
    return redirect(url_for('index'))

#! Delete all data
@expensetracker.route('/deleteall', methods=['GET'])
def delete_all():
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM expenses')
    mysql.connection.commit()
    return redirect(url_for('index')) 


#! Sum all amounts
@expensetracker.route('/SUM')
def sum():
    cur = mysql.connection.cursor()
    cur.execute('SELECT SUM(Amount) as Total FROM expenses')
    result = cur.fetchone()
    total = result[0] if result[0] is not None else 0 
    return str(total)

#! run server
#! This has to go last to run everything above
if __name__=="__main__":
    expensetracker.run(debug=True)