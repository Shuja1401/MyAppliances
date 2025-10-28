from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from datetime import datetime
import os
import sqlite3
from scheduler import update_due_soon_table

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(minutes=30)


#Route for MAIN PAGE.
@app.route('/', method='GET','POST')
def main_menu():
    return render_template('main_menu.html')


#Function to connect with the database and close it. 
def get_db():
    conn=sqlite3.connect('database/MyAppliances.db')
    c=conn.cursor()
    conn.row_factory=sqlite3.Row
    return conn, c
def close_db(conn):
    conn.commit()
    conn.close()


#Service due date function
def device_service_due():
    conn, c=get_db()
    userid_session_service_due=session.get('userid')
    c.execute(
        ("SELECT * FROM devices_with_service_due WHERE userid_service_due_db=?"),
        (userid_session_service_due,)
    )
    list_devices_service_due=c.fetchall()
    close_db(conn)
    if list_devices_service_due:
        return render_template('devices_with_due_service.html', list_devices=list_devices_service_due)
    else:
        return redirect('/navigation')


#Route for login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username_check=request.form[username]
        password_check=request.form[password]
    
        conn=get_db()
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


#Welcome page after onboarding
@app.route(/welcome, methods=['GET','POST'])
def welcome():
#Add device route. The user will add devices. This will either be triggered from /welcome or /add_device option in navigation.
@app.route('/add_device', methods=['GET','POST'])
def add_device():
    if request.method=='POST:
        deviceid=request.form.get('deviceid')
        device_nickname=request.form.get('device_nickname')
        device_type=request.form.get('device_type')
        device_type=request.form.get('manufacturer_name')
        purchase_date=request.form.get('purchase_date')
        warranty_duration=request.form.get('warranty_duration')
        extended_warranty_option=request.form.get('extended_warranty_option')
        extended_warranty_duration=request.form.get('extended_warranty_duration')
        service_plan_active=request.form.get('service_plan_active')
        service_plan_by=request.form.get('service_plan_by')
        service_due_in=request.form.get('service_due_in')
        service_centre_name=request.form.get('service_centre_name')
        service_centre_address=request.form.get('service_centre_address')
        service_centre_number=request.form.get('service_centre_number')
        navigation_option=request.form.get('nav_option')
        if navigation_option=='ADD AGAIN':
            userid_device=session.get('userid')
            return render_template('add_device.html', userid_form=userid_device)
        elif navigation_option='Exit':
            return render_template(exit.html)
        


#Exit option, executed after a user selects exit navigation.
@app.route('/exit', methods=['GET','POST'])
def exit():
    if request.method=='POST':
        get_db()
        userid_exit=session.get('userid')
        c.execute("SELECT username FROM onboarding WHERE userid=?",(userid_exit,))
        username_exit=c.fetchone()[0]
        session.clear()
        return render_template('exit.html', username=username_exit)

#Route to select a device from a list of registered devices.
@app.route('/select_device',methods=['GET','POST'])
def select_device():
    if method=='POST':
        get_db()
        userid_select_device=session.get(userid)
        c.execute(SELECT deviceid, device_nickname, device_type, manufacturer_name FROM device_details WHERE userid=?),(userid_select_device,))
        device_list=c.fetchall() #list of tupples of devices.
    return render_template('select_device.html', device_list=device_list)

    
#Route to publish details of the service centre
@app.route('/service_centre_details', methods=['GET','POST'])
def service_centre_details():
    if method==['POST']:
        deviceid=request.form.get('selected_device')
        get_db()
        c.execute(SELECT device_type, manufacturer_name FROM device_details WHERE deviceid=?),(deviceid))
        device_details_service=c.fetchone()
        c.execute(SELECT company_name, company_contact_no WHERE device_type=? AND manufacturer_name=?), (device_details_service[0], device_details_service[1])
        service_centre_details=c.fetchone()
        return render_template('service_centre_details.html', service_cente_details)


#Display devices
@app.route('/display_devices', methods=['GET','POST'])
def display_devices():
    return render_template('display_device.html')


#Navigation route
@app.route('/navigation', methods=['POST','GET'])
def navigation():
    if method==['POST']:
        userid_service_check=session.get('userid')
        get_db()
        c.execute(SELECT * FROM )
        userid_in_service_due_tabe=
        if userid_select_device==
            navi_option=request.form('navigation_option')
            if navi_option==1:
                return redirect('select_device.html')
            elif navi_option==2:
    
            elif navi_option==3:
                return redirect('warranty_expires_date.html')
    return render_template(navigation.html)
    


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)