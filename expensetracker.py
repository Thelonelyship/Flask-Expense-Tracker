from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import uuid

#! Initialize Flask app
expensetracker = Flask(__name__)
expensetracker.secret_key = 'bootcamp2024!'

#! Connect to Render.com
expensetracker.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:dbKM0K2jgvQ0xN6SUrXjaK5XzmEQSHfb@dpg-ctg0udggph6c73fr3d0g-a.oregon-postgres.render.com/expensetrackerdb_ddau'
expensetracker.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#! Initialize SQLAlchemy
db = SQLAlchemy(expensetracker)

#! User login
@expensetracker.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.execute('SELECT user_id, password FROM users WHERE username = :username', {'username': username}).fetchone()
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
        existing_user = db.session.execute('SELECT username FROM users WHERE username = :username', {'username': username}).fetchone()
        if existing_user:
            flash('Someone stole your name. Try a new one!', 'error')
        else:
            try:
                db.session.execute('INSERT INTO users (user_id, username, password) VALUES (:user_id, :username, :password)', 
                {'user_id': user_id, 'username': username, 'password': password})
                db.session.commit()
                flash('Registration done! You can log in if you want.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"There was a problem: {e}", 'error')
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
    expenses = db.session.execute('SELECT id, category, amount, description FROM expenses WHERE user_id = :user_id', {'user_id': user_id}).fetchall()
    total = db.session.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = :user_id', {'user_id': user_id}).fetchone()[0]
    return render_template('index.html', expenses=expenses, total=total)

#! Insert data
@expensetracker.route('/insert', methods=['POST'])
def insert():
    if 'user_id' not in session:
        flash('You need to be logged in to add expenses.', 'error')
        return redirect(url_for('login'))
    user_id = session['user_id']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']
    if not amount or not amount.replace('.', '', 1).isdigit():
        flash("Please enter a valid amount.", "error")
        return redirect(url_for('index'))
    amount = float(amount)
    try:
        db.session.execute('INSERT INTO expenses (category, amount, description, user_id) VALUES (:category, :amount, :description, :user_id)',
            {'category': category, 'amount': amount, 'description': description, 'user_id': user_id})
        db.session.commit()
        flash('Expense added successfully!', 'success')
    except Exception as e:
        flash(f"There was a problem: {e}", 'error')
    return redirect(url_for('index'))

#! Delete one row
@expensetracker.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    user_id = session['user_id']
    db.session.execute('DELETE FROM expenses WHERE id = :id AND user_id = :user_id', {'id': id, 'user_id': user_id})
    db.session.commit()
    return redirect(url_for('index'))

#! Delete all data
@expensetracker.route('/deleteall', methods=['GET'])
def delete_all():
    user_id = session['user_id']
    db.session.execute('DELETE FROM expenses WHERE user_id = :user_id', {'user_id': user_id})
    db.session.commit()
    return redirect(url_for('index'))

#! Run the app - must go last
if __name__ == '__main__':
    expensetracker.run(debug=True)
