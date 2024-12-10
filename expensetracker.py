from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import uuid

#! Initialize Flask app
expensetracker = Flask(__name__)
expensetracker.secret_key = 'bootcamp2024!'

#! Connect to sql database
expensetracker.config['MYSQL_HOST'] = 'sql8.freesqldatabase.com'
expensetracker.config['MYSQL_USER'] = 'sql8750720'
expensetracker.config['MYSQL_PASSWORD'] = 'JkVZEa4fZY'
expensetracker.config['MYSQL_DB'] = 'sql8750720'

mysql = MySQL(expensetracker)

#! Check for unique user id
@expensetracker.before_request
def ensure_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        print(f"Assigned user_id: {session['user_id']}")

#! fetch data
@expensetracker.route('/')
def index():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM expenses WHERE user_id = %s', [user_id])
    data = cur.fetchall()
    cur.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = %s', [user_id])
    result = cur.fetchone()
    total = result[0] if result[0] is not None else 0
    return render_template('index.html', expenses=data, total=total)


#! insert data
@expensetracker.route('/insert', methods=['POST'])
def insert():
    user_id = session['user_id']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']
    cur = mysql.connection.cursor()
    cur.execute(
        'INSERT INTO expenses (category, amount, description, user_id) VALUES (%s, %s, %s, %s)',
        (category, amount, description, user_id)
    )
    mysql.connection.commit()
    return redirect(url_for('index'))

#! delete one row
@expensetracker.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM expenses WHERE id = %s AND user_id = %s', (id, user_id))
    mysql.connection.commit()
    return redirect(url_for('index'))

#! delete all data
@expensetracker.route('/deleteall', methods=['GET'])
def delete_all():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM expenses WHERE user_id = %s', [user_id])
    mysql.connection.commit()
    return redirect(url_for('index'))

#! Run the app - must go last
if __name__ == '__main__':
    expensetracker.run(debug=True)