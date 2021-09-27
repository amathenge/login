import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'some-sort-of-a-secret-key'

# Enter your database connection details below
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MYSQL_HOST'] = 'your-mysql-hosting-provider'
app.config['MYSQL_DB'] = 'your-mysql-database'
app.config['MYSQL_USER'] = 'your-mysql-username'
app.config['MYSQL_PASSWORD'] = 'your-mysql-password'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' in session:
        user = session['user']
        return redirect('search.html', user=user)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        sql = 'select user, email, admin from users where password = md5(%s)'
        cur.execute(sql,[password])
        result = cur.fetchone()
        if result is None:
            msg = 'Invalid Admin user/pass'
            return render_template('login.html', msg=msg)
        else:
            session['user'] = username
            session['email'] = result['email']
            user = {'user': username, 'email': result['email']}
            return redirect(url_for('search'))

    return render_template('login.html', msg='')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('home'))

    user = {'user': session['user'], 'email': session['email']}
    return render_template('search.html', user=user)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user' not in session:
        return redirect(url_for('home'))

    user = session['user']

    if request.method == 'POST':
        # if the submit button was pressed - go back to the search form
        if request.form['submit'] == 'cancel':
            return redirect(url_for('search'))

        if request.form['submit'] == 'update':
            return "Form has been posted"

    # the form hasn't been posted.
    username = request.form['username'].strip()
    userid = request.form['userid'].strip()
    email = request.form['email'].strip()

    sql = 'select id, user, email from users where '
    param = []
    paramcount = 0
    joincond = ''
    if username != '':
        sql += joincond+'user = %s'
        joincond = ' and '
        param.append(username)
        paramcount += 1
    if userid != '':
        sql += joincond+'id = %s'
        joincond = ' and '
        param.append(userid)
        paramcount += 1
    if email != '':
        sql += joincond+'email = %s'
        param.append(email)

    if paramcount == 0:
        return redirect(url_for('search'))

    cur = mysql.connection.cursor()
    cur.execute(sql, param)
    results = cur.fetchone()

    if results is not None:
        userdata = {'username': results['user'], 'email': results['email'], 'userid': results['id']}
        return render_template('edit.html', user=user, userdata=userdata)
    else:
        return redirect(url_for('search'))

