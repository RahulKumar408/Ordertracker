from flask import Flask, render_template, request, redirect, url_for, session
import flask

import MySQLdb.cursors

app = Flask(__name__)
from configure import config
mysql = config(app)

from outlet import outlet
from customer import customer
app.register_blueprint(outlet)
app.register_blueprint(customer)

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')
@app.route('/customerhome')
def customerhome():
    cur = mysql.connection.cursor()
    cur.execute("select outlet_id, name, phone_no from outlet;")
    output = cur.fetchall()
    outlets = []
    for detail in output:
        temp = {
            'id': detail[0],
            'name': detail[1],
            'phone_no': detail[2]
        }
        outlets.append(temp)
    return render_template('home.html', outlets=outlets)

@app.route('/login',methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'useremail' in request.form and 'password' in request.form:
        useremail = request.form['useremail']
        password = request.form['password']
        cur = mysql.connection.cursor()
        query = "select outlet_id from outlet where email = %s AND password = %s"
        cur.execute(query, (useremail, password))
        account = cur.fetchone()
        if account:
            session['outlet_id'] = account[0]
            msg = "Logged in successfully!"
            flask.flash(msg)
            return redirect(url_for('outlet.outletdetail'))
        else:
            msg = 'Incorrect username / password !'
        flask.flash(msg)
    return render_template('login.html')

@app.route('/outletsignup')
def outletsignup():
    return render_template('outletsignup.html')

@app.route('/customer/<int:outlet_id>')
def customer(outlet_id):
    
    cur = mysql.connection.cursor()
    query = "SELECT order_status, token_no, placed_time FROM orders WHERE outlet_id = %s"
    cur.execute(query, (outlet_id,))
    output = cur.fetchall()
    orderPrepared = []
    orderQueued = []
    orderCollected = []
    for order in output:
        temp = {
            'order_status': order[0],
            'token_no': order[1],
            'placed-time': order[2]
        }
        if(order[0]=='prepared'):
            orderPrepared.append(temp)
        elif(order[0]=='queued'):
            orderQueued.append(temp)
        else:
            orderCollected.append(temp)
    return render_template('customer.html', orderPrepared=orderPrepared, orderQueued=orderQueued, orderCollected=orderCollected)


if __name__ == '__main__':
    app.run(debug=True)