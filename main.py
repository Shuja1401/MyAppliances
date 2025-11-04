# PENDING TASKS
# Create a footbar for logout and go back to main menu. input type submit


from flask import Flask, render_template, request, redirect, url_for, session
from flask.sessions import NullSession
from flask_session import Session
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

from db_utils import get_db, close_db
from scheduler import update_due_soon_table

app = Flask(__name__)
app.secret_key="abcbd7dce24fea88ff28386a1c8c465c"
app.permanent_session_lifetime = timedelta(minutes=30)

#---------------------------FUNCTIONS--------------------------------------

#Service due date function
def device_service_due():
    conn, c = get_db()
    userid_session_service_due=session.get('userid')
    c.execute(
        "SELECT * FROM devices_with_service_due WHERE userid_service_due_db=?",
        (userid_session_service_due,)
    )
    list_service_due=c.fetchall()
    close_db(conn)
    return list_service_due

#User is shown a list of devices registered under their userid, selet a specific device,
#and returns the selected deviceid.
def select_device():
    device_list=[]
    if request.method=='POST':
        conn, c = get_db()
        userid_select_device=session.get('userid')
        c.execute(
            """
            SELECT
            deviceid,
            device_nickname,
            device_type,
            manufacturer_name
            FROM device_details
            WHERE userid=?
            """,
            (userid_select_device,)
        )

        device_list=c.fetchall() #list of tupples of devices.
        close_db(conn)
    return render_template('select_device.html', device_list=device_list)
#---------------------------ROUTE--------------------------------------
#Route for MAIN PAGE.
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    return render_template('main_menu.html')

#Registration
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method=='POST':
        password=request.form['password']
        hashed_password = generate_password_hash(password)
        conn, c = get_db()
        try:
            c.execute("""
            INSERT INTO users (
            username,
            password_hash
            ) VALUES (?, ?)
            """,(request.form['username'], hashed_password))
            userid_onboarding=c.fetchone()[0]
            c.execute("""
            INSERT INTO onboarding (
                userid,
                contact_number,
                first_name,
                last_name,
                state,
                city,
                pin_code,
                complete_address)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (userid_onboarding,
             request.form['contact_number'],
             request.form['first_name'],
             request.form['last_name'],
             request.form['state'],
             request.form['city'],
             request.form['pin_code'],
             request.form['complete_address']
            )
            )

            #Check if the records were successfully added into the database.
            c.execute("SELECT * FROM onboarding WHERE contact_number=?",
            (request.form['contact_number'],)
            )
            user=c.fetchone()            
            if user:
                welcome_msg=f"Welcome onboard, {request.form['first_name']}!"
                return render_template('welcome.html',message=welcome_msg)
            else:
                error_msg="registration failed. Please try again."
                return render_template('onboarding.html', message=error_msg)
        except Exception as e:
            conn.rollback()
            close_db(conn)
            error=f"Database error:{e}"
            return render_template('onboarding.html', error=error)
    return render_template("onboarding.html")

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username_check=request.form['username']
        password_check=request.form['password']
        conn, c=get_db()
        c.execute("""
            SELECT
            username,
            password
            FROM user WHERE username=? AND password=?
            """,
            (username_check, password_check
        ))
        user_exist=c.fetchone()
        close_db(conn)
        if user_exist:
            """By default, session expires when a browser is closed, this lines overrides it."""
            session.permanent = True 
            session['userid']=user_exist['userid']
            return redirect('/navigation') #move to navigation page
        else:
            error_message="Invalid username or password"
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

#Exit option, executed after a user selects exit navigation.
@app.route('/exit_user', methods=['GET', 'POST'])
def exit_user():    
    conn, c = get_db()
    session.clear()
    close_db(conn)
    message_exit="Thanks for using MyAppliances. Visit again!"
    return render_template('main_menu.html', message_exit=message_exit)

#Navigation
@app.route('/navigation', methods=['GET', 'POST'])
def navigation():
    conn, c=get_db()
    userid_nav=session.get('userid')
    if request.method=='GET':
        c.execute("SELECT userid FROM device_details WHERE userid=?",
            (userid_nav,
        ))
        userid_exists=c.fetchall()
        list_service_due=device_service_due()
        if userid_exists:
            if list_service_due:
                return render_template('service_due_details.html',
                    list_service_due=list_service_due
                )
            else:
                return render_template('navigation.html')
        else:
            nav_message="Please add a device before proceeding."
            return render_template('add_device.html', nav_message=nav_message)
    else:
        nav_option=request.form.get('navigation_option')
        nav_option = int(nav_option)
        if nav_option==1:
            return redirect('/device_breakdown')
        elif nav_option==2:
            list_service_due_op=device_service_due()
            return render_template('service_due_details.html',
                list_service_due=list_service_due_op
            )
        elif nav_option==3:
            return redirect('/warranty_expire')
        elif nav_option==4:
            return redirect('/display_devices')
        elif nav_option==5:
            return  redirect('edit_device')
        elif nav_option==6:
            return redirect('/exit_user')
        else: 
            error_msg_navigation= "Wrong value entered. Please enter a value between (1-6)."
            return render_template('navigation.html',
                                   error_msg_navigation=error_msg_navigation
            )

#User adds device to their account. 
@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if request.method=='POST':
        purchase_date_1=datetime.strptime(request.form['purchase_date'], "%d-%m-%y")
        warranty_duration_1=int(request.form.get('warranty_duration',0))
        extended_warranty_duration_1=int(request.form.get('extended_warranty_duration',0))

        # Calculate total months
        total_months = warranty_duration_1 + extended_warranty_duration_1
        warranty_expires_on_1 = purchase_date_1 + relativedelta(months=+total_months)
        userid_dev_det=session.get('userid')
        conn, c = get_db()
        try:        
            c.execute("""
                INSERT INTO device_details(
                    userid,
                    device_nickname,
                    device_type,
                    manufacturer_name,
                    purchase_date,
                    original_warranty_duration_in_months,
                    extended_warranty_y_n,
                    extended_warranty_duration_in_months,
                    warranty_expires_on,
                    service_plan_y_n,
                    manufacturer_or_third_party,
                    service_required_after_months
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                    userid_dev_det,
                    request.form.get('device_nickname'),
                    request.form.get('device_type'),
                    request.form.get('manufacturer_name'),
                    request.form.get('purchase_date'),
                    request.form.get('warranty_duration'),
                    request.form.get('extended_warranty_option'),
                    request.form.get('extended_warranty_duration'),
                    warranty_expires_on_1,
                    request.form.get('service_plan_active'),
                    request.form.get('service_plan_by'),
                    request.form.get('service_due_in')
            ))
            deviceid_dev_det=c.fetchone()[0]
            c.execute("""
                INSERT INTO service_centre_details(
                    userid,
                    deviceid,
                    device_type,
                    manufacturer_name,
                    name_service_centre,
                    address_service_centre,
                    contact_no_service_centre
                    )
                    VALUES (?,?,?)""", (
                    userid_dev_det,
                    deviceid_dev_det,
                    request.form.get('device_type'),
                    request.form.get('manufacturer_name'),
                    request.form.get('service_centre_name'),
                    request.form.get('service_centre_address'),
                    request.form.get('service_centre_number')
            ))
            
        except Exception as e:
            conn.rollback()  # undo partial changes
            message = f"Error inserting data: {e}"
        finally:
            close_db(conn)
    return render_template('add_device.html')

#Device breakdown
@app.route('/device_breakdown', methods=['GET', 'POST'])
def dev_breakdown():
    selected_device_id=select_device()
    conn, c = get_db()
    if request.method=='GET':        
        #Retrieves device type and manufacturer name for the malfunctioning device.
        c.execute(
        """
        SELECT
            device_type,
            manufacturer_name,
            device_nickname 
            FROM device_details
            WHERE deviceid=?
        """,
            (selected_device_id,
        ))
        dev_breakdown_details=c.fetchall()
        #Retrieves service centre name & contact number by comparing with device_type & manufacturer name.
        c.execute(
        """
        SELECT
            company_name,
            company_contact_no
            FROM service_centre_details
            WHERE device_type=? AND manufacturer_name=?
        """,
        (dev_breakdown_details[0][0],dev_breakdown_details[0][1])
    )
    service_centre_details_breakdown=c.fetchall()
    return render_template(
        'dev_breakdown_service_centre.html',
        service_centre_details_breakdown=service_centre_details_breakdown
    )

#Enter service details
@app.route('/add_service_details', methods=['GET', 'POST'])
def add_service_details():
    deviceid_ser_det=select_device()
    if request.method == 'POST':
        serviced_on = request.form.get('serviced_on')
        amount_spent = request.form.get('amount_spent', 0)
        name_part_replaced = request.form.get('name_part_replaced', '')
        service_warranty_y_n = request.form.get('service_warranty_y_n', 'No')
        service_warranty_in_months = int(request.form.get('service_warranty_in_months', 0))
        part_warranty_y_n = request.form.get('part_warranty_y_n', 'No')
        part_warranty_in_months = int(request.form.get('part_warranty_in_months', 0))
        additional_remark = request.form.get('additional_remark', '')
        userid_ser_det=session.get('userid')
        conn, c= get_db()        
        c.execute("""
            INSERT INTO service_details (
                userid,
                deviceid,
                serviced_on,
                amount_spent,
                name_part_replaced,
                service_warranty_y_n,
                service_warranty_in_months,
                part_warranty_y_n,
                part_warranty_in_months,
                additional_remark
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            userid_ser_det,
            deviceid_ser_det,
            serviced_on,
            amount_spent,
            name_part_replaced,
            service_warranty_y_n,
            service_warranty_in_months,
            part_warranty_y_n,
            part_warranty_in_months,
            additional_remark
        ))
        close_db()
    return render_template('add_service_details.html')
        
#Warranty expire date
@app.route('/warranty_expire', methods=['GET', 'POST'])
def warranty_expire():
    if request.method=='GET':
        conn, c=get_db()
        userid_warranty=session.get('userid')
        device_id_warranty=select_device()
        c.execute("""
            SELECT warranty_expires_on
            FROM device_details
            WHERE userid=? AND deviceid=?
        """, (userid_warranty, device_id_warranty))
        date_warranty_expires=c.fetchone()
        return render_template('warranty_expires_date.html',
            date_warranty_expires=date_warranty_expires)
    return render_template('warranty_expires_date.html')

#ONLY Display devices
@app.route('/display_devices', methods=['GET', 'POST'])
def display_devices():
    deviceid_display=select_device()
    userid_display=session.get('userid')
    if request.method=='POST':
        conn, c = get_db()
        c.execute("SELECT username FROM onboarding WHERE userid=?", (userid_display,))
        username_display=c.fetchall()[0]
        c.execute(
        """SELECT
        device_nickname,
        device_type,
        manufacturer_name,
        warranty_expires_on,
        last_serviced_on,
        next_service_due,
        FROM device_details
        WHERE userid=? AND deviceid=?
        """,
        (userid_display, deviceid_display
        ))
        devices_display=c.fetchall()
        close_db(conn)
        return render_template('display_device.html', devices=devices_display)
    return render_template('display_device.html')

#Edit device
@app.route('/edit_device', methods=['GET', 'POST'])
def edit_device():
    return render_template('edit_device.html')

#Delete a device
@app.route('/delete_device', methods=['GET', 'POST'])
def delete_device():
    #This part shows the list of devices to be deleted.
    if request.method=='GET':
        return render_template('select_device.html')
    #This part takes the input of the device id to be deleted and removes it from table.
    userid_device_delete=session.get('userid')
    deviceid_device_delete=request.form.get('selected_device')
    conn, c=get_db()
    try:
        c.execute(
            "DELETE FROM device_details WHERE userid=? AND deviceid=?",
            (userid_device_delete, deviceid_device_delete 
            ))
        message="Device deletion successful"
    except Exception as e:
        conn.rollback()
        message= f"Error: {e}"
    finally:
        close_db(conn)
    return message

#Device delete success route
@app.route('/dev_del_success', methods=['GET', 'POST'])
def dev_del_success():
    return render_template('add_delete_device.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)