from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "ayushi@0987"
DB_PORT = "5000" # Corrected the port number for PostgreSQL

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
except psycopg2.OperationalError as e:
    print("Error while connecting to PostgreSQL", e)
    # Add appropriate error handling here, e.g., exit or retry logic

@app.route('/')
def home():
    if 'loggedin' in session:
        # Ensure profile_picture is available in session, provide a default value if not
        profile_picture = session.get('profile_picture', None)
        return render_template('sidebar.html', profile_picture=profile_picture)
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['email'] = account['email']
                session['profile_picture'] = account['profile_picture']  # Ensure this line is present
                session['full_name'] = f"{account['first_name']} {account['last_name']}"  # Store full name in session
                return redirect(url_for('home'))
            else:
                flash('Incorrect email/password')
        else:
            flash('Incorrect email/password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'first_name' in request.form and 'password' in request.form and 'email' in request.form:
        
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        profile_picture = request.files['profile_picture']
        _hashed_password = generate_password_hash(password)
        
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Save the uploaded file
        if profile_picture and profile_picture.filename != '':
            profile_picture_filename = profile_picture.filename
            profile_picture_path = os.path.join(upload_folder, profile_picture_filename)
            profile_picture.save(profile_picture_path)
        else:
            profile_picture_filename = None
        

        print(f"first_name: {first_name}, last_name: {last_name}, email: {email}, phone: {phone}, profile_picture_path: {profile_picture_path}")

        try:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', first_name):
                flash('Username must contain only characters and numbers!')
            elif not first_name or not password or not email:
                flash('Please fill out the form!')
            else:
                cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, password, phone, profile_picture)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (first_name, last_name, email, _hashed_password, phone, profile_picture_path))  # Removed duplicated 'email' column
                conn.commit()
                flash('You have successfully registered!')
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred during registration. Please try again.')

    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session variables
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        cursor.close()

        # Debugging: Print fetched account data to console
        print("Fetched account data:", account)
        
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/users')
def users():
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # if 'loggedin' in session:
    #     cursor.execute('SELECT * FROM users')
    #     users_list = cursor.fetchall()
    #     cursor.close()
    #     return render_template('users.html', users=users_list)
    # return redirect(url_for('login'))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users')
        users_list = cursor.fetchall()
        cursor.close()
        return render_template('users.html', users=users_list)
    return redirect(url_for('login'))




@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        if request.method == 'POST' and 'first_name' in request.form and 'password' in request.form and 'email' in request.form:
            
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            profile_picture = request.files['profile_picture']
            _hashed_password = generate_password_hash(password)
            
            upload_folder = os.path.join('static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Save the uploaded file
            if profile_picture and profile_picture.filename != '':
                profile_picture_filename = profile_picture.filename
                profile_picture_path = os.path.join(upload_folder, profile_picture_filename)
                profile_picture.save(profile_picture_path)
            else:
                profile_picture_filename = None

            try:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                account = cursor.fetchone()
                if account:
                    flash('Account already exists!')
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!')
                elif not re.match(r'[A-Za-z0-9]+', first_name):
                    flash('Username must contain only characters and numbers!')
                elif not first_name or not password or not email:
                    flash('Please fill out the form!')
                else:
                    cursor.execute("""
                        INSERT INTO users (first_name, last_name, email, password, phone, profile_picture)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (first_name, last_name, email, _hashed_password, phone, profile_picture_path))
                    conn.commit()
                    flash('User has been successfully added!')
                    return redirect(url_for('users'))
            except Exception as e:
                print(f"Error: {e}")
                flash('An error occurred while adding the user. Please try again.')
        return render_template('adduser.html')
    return redirect(url_for('login'))


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        profile_picture = request.files['profile_picture']
        
        # Update user details in the database
        cursor.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, phone = %s, profile_picture = %s 
            WHERE id = %s
        """, (first_name, last_name, email, phone, profile_picture.filename, user_id))
        conn.commit()
        flash('User updated successfully')
        return redirect(url_for('users'))
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    flash('User deleted successfully')
    return redirect(url_for('users'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        if account and check_password_hash(account['password'], current_password):
            if new_password == confirm_password:
                _hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password = %s WHERE id = %s', (_hashed_password, session['id']))
                conn.commit()
                flash('Password successfully changed!')
                return redirect(url_for('profile'))
            else:
                flash('New passwords do not match')
        else:
            flash('Current password is incorrect')
    return render_template('change_password.html')


@app.route('/testtype')
def testtype():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM test_entries')
        test_list = cursor.fetchall()
        cursor.close()
        return render_template('testtype.html', tests=test_list)
    return redirect(url_for('login'))


@app.route('/addtest', methods=['GET', 'POST'])
def addtest():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        if request.method == 'POST':
            # Get form data
            test_id = request.form['Id']
            test_type = request.form['test_type']
            language = request.form['language']
            
            # Insert data into the database
            cursor.execute("""
                        INSERT INTO  test_entries(id, test_type, language)
                        VALUES (%s, %s, %s)
                    """, (test_id,test_type,language))
            conn.commit()
        return render_template('addtest.html')
    return redirect(url_for('login'))
            
@app.route('/deletetest/<int:test_id>', methods=['POST'])
def deletetest(test_id):
    if 'loggedin' in session:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # Delete data from the database
            cursor.execute('DELETE FROM test_entries WHERE id = %s', (test_id,))
            conn.commit()
            cursor.close()
            
            flash('Test type deleted successfully!', 'success')
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            flash(f'Error: {error}', 'danger')
    
    return redirect(url_for('testtype'))         



if __name__ == "__main__":
    app.run(debug=True, port=5001)
    
