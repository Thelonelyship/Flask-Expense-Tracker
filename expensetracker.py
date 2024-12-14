from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import hashlib
import uuid

#! Initialize Flask app
expensetracker = Flask(__name__)
expensetracker.secret_key = 'bootcamp2024!'

#! Connect to SQL database
expensetracker.config['MYSQL_HOST'] = 'sql8.freesqldatabase.com'
expensetracker.config['MYSQL_USER'] = 'sql8750720'
expensetracker.config['MYSQL_PASSWORD'] = 'JkVZEa4fZY'
expensetracker.config['MYSQL_DB'] = 'sql8750720'

mysql = MySQL(expensetracker)

#! User login
@expensetracker.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT user_id, password FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            stored_password = user[1]
            if stored_password == password:
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                flash('Probably the wrong password... try again.', 'error')
        else:
            flash('Did you register? Give that a go first.', 'error')
    return render_template('login.html')

#! User registration
@expensetracker.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = str(uuid.uuid4())
        cur = mysql.connection.cursor()
        cur.execute('SELECT username FROM users WHERE username = %s', (username,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Someone stole your name. Try a new one!', 'error')
        else:
            try:
                cur.execute(
                'INSERT INTO users (user_id, username, password) VALUES (%s, %s, %s)',
                (user_id, username, password))
                mysql.connection.commit()
                flash('Registration done! You can log in if you want.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"There was a problem: {e}", 'error')
            finally:
                cur.close()
    return render_template('register.html')

#! Logout user and clear session
@expensetracker.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#! Fetch data
@expensetracker.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM expenses WHERE user_id = %s', [user_id])
    data = cur.fetchall()
    cur.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = %s', [user_id])
    result = cur.fetchone()
    total = result[0] if result[0] is not None else 0
    return render_template('index.html', expenses=data, total=total)

#! Insert data
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

#! Delete one row
@expensetracker.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM expenses WHERE id = %s AND user_id = %s', (id, user_id))
    mysql.connection.commit()
    return redirect(url_for('index'))

#! Delete all data
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
