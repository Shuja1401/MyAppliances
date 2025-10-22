from flask import Flask

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(minutes=30)
#Route for MAIN PAGE.
@app.route('/', method='GET','POST')
def main_menu():
    return render_template('main_menu.html')

#Function to connect with the database. 
def get_db():
    conn=sqlite3.connect('database/MyAppliances.db')
    conn.row_factory=sqlite3.Row
    return conn
def close_db(conn):
    conn.commit()
    conn.close()

#Route for login
@app_route('/login', method='GET','POST')
def login():
    if request.method=='POST':
        username_check=request.form[username]
        password_check=request.form[password]
    
        conn=get_db()
        c=conn.cursor()
        c.execute(SELECT userid, contact_number, password from onboarding WHERE username=?, password=?),(username_check, password_check))
        user=c.fetchone()
        close_db(conn)
        if user:
            session.permanent = True
            session['user_id']=user['userid']
            return redirect('/navigation') #move to navigation page
        else:
            return render_template('login.html', "Invalid username or password")
    else:
        return render_template('login.html')
#Route for registration
@app.route('/onboarding', methods=['GET','POST'])
def onboarding():
if request.method=='POST':
    contact_number1=request.form['contact_number']
    first_name1=request.form['first_name']
    last_name1=request.form['last_name']
    state1=request.form['state']
    city1=request.form['city']
    pin_code1=request.form['pin_code']
    complete_address1=request.form['complete_address']
    conn=get_db()
    c=conn.cursor()
    try:
        c.execute("""INSERT INTO onboarding (contact_number, first_name, last_name, state, city, pin_code,              complete_address)      VALUES (?,?,?,?,?,?,?)""", (contact_number1, first_name1, last_name1, state1,             city1, pin_code1, complete_address1))
        c.execute("SELECT * FROM onboarding WHERE contact_number=?", (contact_number1,))
        user=c.fetchone()
        if user:
            welcome_msg=f"Welcome onboard, {first_name1}!"
            return render_template('welcome.html',message=welcome_msg)
        else:
            error_msg="registration failed. Please try again."
            return render_template('onboarding.html', message=error_msg)
        close_db(conn)
    except Exception as e:
        conn.rollback()
        error=f"Database error:{e}"
        return render_template('onboarding.html', error=error)
    close_db()    
return render_template("onboarding.html")

#Welcome route
@app.route(/welcome, methods=['GET','POST'])
def welcome():
    if request.method=='POST':
        return redirect('add_device.html')
    else
    return render_template('welcome.html')

#exit route
@app.route('/exit', methods=['GET','POST'])
def exit():
    if request.method=='POST':
        get_db()
        userid_exit=session.get('userid')
        c.execute("SELECT username FROM onboarding WHERE userid=?",(userid_exit,))
        username_exit=c.fetchone()[0]
        session.clear()
        return render_template('exit.html', username=username_exit)




if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)