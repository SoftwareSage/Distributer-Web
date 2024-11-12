from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sandeep10052010'
app.config['MYSQL_DB'] = 'TI'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = user[1]  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid username or password.', 'danger')
        cursor.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        cursor.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT SUM(amount) FROM tasks WHERE username=%s AND DATE(date) = CURDATE()", (username,))
        today_income = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE username=%s", (username,))
        tasks_done = cursor.fetchone()[0]
        
        notices_distributed = tasks_done * 500
        withdrawable_amount = (tasks_done // 10) * 50  # For every 10 tasks, 50 rs is withdrawable
        
        cursor.close()
        
        return render_template('dashboard.html', username=username, today_income=today_income, notices_distributed=notices_distributed, withdrawable_amount=withdrawable_amount)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'username' in session:
        username = session['username']
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT SUM(amount) FROM tasks WHERE username=%s AND DATE(date) = CURDATE()", (username,))
        tasks_done = cursor.fetchone()[0] or 0
        withdrawable_amount = (tasks_done // 10) * 50  # For every 10 tasks
        
        if withdrawable_amount > 0:
            cursor.execute("INSERT INTO withdrawals (username, amount) VALUES (%s, %s)", (username, withdrawable_amount))
            mysql.connection.commit()
            flash(f"₹{withdrawable_amount} has been withdrawn successfully!", 'success')
        else:
            flash("No funds available for withdrawal.", 'danger')
        
        cursor.close()
        
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
