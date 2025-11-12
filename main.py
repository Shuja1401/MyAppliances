# PENDING TASKS
# Create a footbar for logout and go back to main menu. input type submit
# When is the next service due? - change language in add device form
# remove add device url at the bottom from add_device form
# Enter purchase date (in dd-mm-yy format) -- add this line
import os
import sqlite3
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask.sessions import NullSession
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from db_utils import close_db, get_db

app = Flask(__name__)
app.secret_key="abcbd7dce24fea88ff28386a1c8c465c"
app.permanent_session_lifetime = timedelta(minutes=30)

#---------------------------FUNCTIONS--------------------------------------
def update_warranty_service_status():
    conn, c = get_db()
    try:
        c.execute("""
            UPDATE device_details
            SET
              warranty_status_check = CASE
                WHEN date(warranty_expires_on) < date('now') THEN 'Warranty expired'
                ELSE 'In warranty'
              END,
              service_status_check = CASE
                WHEN date(next_service_due) < date('now') THEN 'Service overdue'
                ELSE NULL
              END;
        """)
        print("Warranty & Service statuses updated for all devices.")
    except Exception as e:
        conn.rollback()
        print("Error during update:", e)
    finally:
        close_db(conn)

#User is shown a list of devices registered under their userid, selet a specific device,
#and returns the selected deviceid.
def select_device_flow():
    if 'userid' not in session:
        return redirect('/login')

    next_route = (
        request.args.get('next')
        or request.referrer
        or url_for('home')
    )
    conn, c = get_db()
    c.execute("""
        SELECT deviceid, device_nickname, device_type, manufacturer_name
        FROM device_details
        WHERE userid=?
    """, (session['userid'],))
    devices = c.fetchall()
    close_db(conn)

    if request.method == 'POST':
        selected_deviceid = request.form.get('selected_deviceid')
        if selected_deviceid:
            session['selected_deviceid'] = selected_deviceid
        return redirect(next_route)

    return render_template(
        'select_device.html',
        devices=devices,
        next_route=next_route
    )
# This function is run everytime a user logins.
# The function calculates the status of servicve and warranty for each device in the device_details table.
with app.app_context():
    update_warranty_service_status()

#---------------------------ROUTE--------------------------------------
#Route for MAIN PAGE.
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    return render_template('main_menu.html')


#Registration
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == 'POST':
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn, c = get_db()
        try:
            # Insert user
            c.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (request.form['username'], hashed_password))
            userid_onboarding = c.lastrowid
            print("Inserted into users table successfully")

            # Insert onboarding details
            c.execute("""
                INSERT INTO onboarding (
                    userid,
                    contact_number,
                    first_name,
                    last_name,
                    state,
                    city,
                    pin_code,
                    complete_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                userid_onboarding,
                request.form['contact_number'],
                request.form['first_name'],
                request.form['last_name'],
                request.form['state'],
                request.form['city'],
                request.form['pin_code'],
                request.form['complete_address']
            ))
            print("Inserted into onboarding table successfully")
            conn.commit()

            c.execute("SELECT * FROM onboarding WHERE contact_number=?", 
                      (request.form['contact_number'],))
            user = c.fetchone()

            close_db(conn)

            if user:
                welcome_msg = f"Welcome onboard, {request.form['first_name']}!"
                return render_template('welcome.html', message=welcome_msg)
            else:
                error_msg = "Registration failed. Please try again."
                return render_template('onboarding.html', message=error_msg)

        except Exception as e:
            conn.rollback()
            close_db(conn)
            error = f"Database error: {e}"
            return render_template('onboarding.html', error=error)

    return render_template("onboarding.html")


#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username_check=request.form['username']
        password_check=request.form['password']
        conn, c=get_db()
        conn.row_factory = sqlite3.Row
        c.execute("SELECT * FROM users WHERE username=?",
            (username_check,)
        )
        user=c.fetchone()
        if user and check_password_hash(user['password'], password_check):
            print("user found", user)
            """By default, session expires when a browser is closed, this lines overrides it."""
            session.permanent = True 
            session['userid']=user[0]
            userid_login=session.get('userid')
            c.execute("SELECT * FROM device_details WHERE userid=?",(userid_login,))
            device_exists=c.fetchall()
            close_db(conn)
            if device_exists:
                return redirect('/navigation')
            else:
                messages="Please add a device to continue."
                return render_template('add_device', messages=messages)
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
        c.execute("""
            SELECT device_nickname, device_type, manufacturer_name, last_serviced_on, next_service_due
            FROM device_Details
            WHERE userid=? AND service_status_check=?
            """,
            (userid_nav,"Service overdue")
        )
        service_overdue_exists=c.fetchall()
        close_db(conn)
        return render_template('navigation.html',service_overdue_exists=service_overdue_exists)
    else:
        nav_option = int(request.form.get('navigation_option', 0))
        if nav_option==1:
            return redirect(url_for('device_breakdown'))
        elif nav_option==2:
            return redirect(url_for('service_warranty_status'))
        elif nav_option==3:
            return render_template('service_details.html')
        elif nav_option==4:
            return redirect(url_for('edit_device'))
        elif nav_option==5:
            return redirect(url_for('exit_user'))
        else: 
            error_msg_navigation= "Wrong value entered. Please enter a value between (1-6)."
            return render_template('navigation.html',
                                   error_msg_navigation=error_msg_navigation
            )
            
@app.route('/select_device', methods=['GET', 'POST'])
def select_device():
    return select_device_flow()

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():    
    if request.method == 'POST':
        conn, c = get_db()
        try:
            purchase_date_str = request.form.get('purchase_date')
            if not purchase_date_str:
                flash("Purchase date error")
                return render_template('add_device.html')
            try:
                purchase_date_1 = datetime.strptime(purchase_date_str, "%Y-%m-%d")

            except ValueError:
                flash("Invalid purchase date. Enter in format: dd-mm-yy")
                return render_template('add_device.html')

            warranty_duration_1 = int(request.form.get('warranty_duration', 0))
            extended_warranty_duration_1 = int(request.form.get('extended_warranty_duration', 0))

            total_months = warranty_duration_1 + extended_warranty_duration_1
            warranty_expires_on_1 = purchase_date_1 + relativedelta(months=+total_months)

            userid_dev_det = session.get('userid')
            if not userid_dev_det:
                flash("You must be logged in to add a device.")
                return redirect(url_for('login'))

            # --- Insert into device_details ---
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                userid_dev_det,
                request.form.get('device_nickname'),
                request.form.get('device_type'),
                request.form.get('manufacturer_name'),
                purchase_date_str,
                warranty_duration_1,
                request.form.get('extended_warranty_option'),
                extended_warranty_duration_1,
                warranty_expires_on_1.strftime("%Y-%m-%d"),
                request.form.get('service_plan_active'),
                request.form.get('service_plan_by'),
                request.form.get('service_due_in')
            ))
            deviceid_dev_det = c.lastrowid

            # --- Insert into service_centre_details ---
            c.execute("""
                INSERT INTO service_centre_details(
                    userid,
                    deviceid,
                    device_type,
                    manufacturer_name,
                    name_service_centre,
                    address_service_centre,
                    contact_no_service_centre
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                userid_dev_det,
                deviceid_dev_det,
                request.form.get('device_type'),
                request.form.get('manufacturer_name'),
                request.form.get('service_centre_name'),
                request.form.get('service_centre_address'),
                request.form.get('service_centre_number')
            ))
            # --- calculate and updates service_due_on date ---
            c.execute("""
                SELECT
                service_required_after_months,
                purchase_date,
                last_serviced_on
                FROM device_details
                WHERE deviceid=? AND userid=?
                """, 
                (deviceid_dev_det, userid_dev_det )
            )
            device_details_ser_chk=c.fetchone() # tupple
            ser_req_aft_mnth=device_details_ser_chk[0] or 0 # integer can also be 0.
            pur_dt=device_details_ser_chk[1] # string in the form of date.
            lst_serd_on=device_details_ser_chk[2] # string in the form of date.
        
            if lst_serd_on:
              base_date=datetime.strptime(lst_serd_on,"%Y-%m-%d").date()
            else:
              base_date=datetime.strptime(pur_dt,"%Y-%m-%d").date()
            next_due_ser_date=base_date+relativedelta(months=ser_req_aft_mnth)
            next_due_ser_date_str = next_due_ser_date.strftime("%Y-%m-%d")
            c.execute("""
                UPDATE device_details
                SET next_service_due=?
                WHERE deviceid=? AND userid=?
            """, (next_due_ser_date, deviceid_dev_det, userid_dev_det))
            close_db(conn)
            return render_template('device_success.html')
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"Error: {e}")
            return render_template('add_device.html')
    return render_template('add_device.html')
    
# Device Breakdown
@app.route('/device_breakdown', methods=['GET', 'POST'])
def device_breakdown():
    if 'selected_deviceid' not in session:        
        return redirect(url_for('select_device', next=request.path))
    deviceid_breakdown = session.get('selected_deviceid')
    conn, c = get_db()
    c.execute("""
        SELECT
            device_type,
            manufacturer_name,
            device_nickname
        FROM device_details
        WHERE deviceid=?
    """, (deviceid_breakdown,))
    dev_breakdown_details = c.fetchone()

    if not dev_breakdown_details:
        close_db(conn)
        return "Device not found", 404
    c.execute("""
        SELECT
            name_service_centre,
            contact_no_service_centre
        FROM service_centre_details
        WHERE device_type=? AND manufacturer_name=?
    """, (dev_breakdown_details[0], dev_breakdown_details[1]))
    service_centre_details_breakdown = c.fetchall()
    close_db(conn)

    session.pop('selected_deviceid', None)
    
    if service_centre_details_breakdown:
        return render_template(
        'dev_breakdown_service_centre.html',
        dev_breakdown_details=dev_breakdown_details,
        service_centre_details_breakdown=service_centre_details_breakdown
    )
    else:
        flash("No details exists.")
        return redirect(url_for('select_device'))

@app.route('/service_warranty_status', methods=['GET', 'POST'])
def service_warranty_status():
    conn, c = get_db()
    if 'userid' not in session:return redirect('/login')
    userid_status=session.get('userid')
    c.execute(
        """SELECT
        device_nickname,
        device_type,
        manufacturer_name,
        purchase_date,
        warranty_expires_on,
        warranty_status_check,
        last_serviced_on,
        next_service_due,
        service_status_check
        FROM device_details
        WHERE userid=?
        """,
        (userid_status,)
    )
    ser_war_status=c.fetchall()
    close_db(conn)
    return render_template ('warranty_service_status.html', ser_war_status=ser_war_status)
    
#Enter service details
@app.route('/add_service_details', methods=['GET', 'POST'])
def add_service_details():
    if 'selected_deviceid' not in session:
        return redirect(url_for('select_device', next=request.path))
    deviceid_service_details = session.get('selected_deviceid')    
    if request.method == 'POST':
        serviced_on1 = request.form.get('serviced_on')
        amount_spent1 = request.form.get('amount_spent', 0)
        name_part_replaced1 = request.form.get('name_part_replaced', '')
        service_warranty_y_n1 = request.form.get('service_warranty_y_n')
        service_warranty_in_months1 = int(request.form.get('service_warranty_in_months', 0))
        part_warranty_y_n1 = request.form.get('part_warranty_y_n')
        part_warranty_in_months1 = int(request.form.get('part_warranty_in_months', 0))
        additional_remark1 = request.form.get('additional_remark', '')
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            userid_ser_det,
            deviceid_service_details,
            serviced_on1,
            amount_spent1,
            name_part_replaced1,
            service_warranty_y_n1,
            service_warranty_in_months1,
            part_warranty_y_n1,
            part_warranty_in_months1,
            additional_remark1
        ))
        c.execute("""
            UPDATE device_details
            SET last_serviced_on = ?
            WHERE deviceid = ?
            """,
            (serviced_on1, deviceid_service_details)
        )
        
        c.execute("""
            SELECT * FROM service_details WHERE userid=? and deviceid=?
            """,
            (userid_ser_det, deviceid_service_details)
        )
        ser_det_suc=c.fetchone()
        close_db(conn)
        session.pop('selected_deviceid', None)
        if ser_det_suc:
            ser_dt_message="Service details added successfully."
        else:
            ser_dt_message="Failed!!"
        return render_template('service_details_add_success.html', message=ser_dt_message)
    return render_template('add_service_details.html')

#View service details
@app.route('/view_service_details', methods=['POST', 'GET'])
def view_service_details():
  if 'selected_deviceid' not in session:        
      return redirect(url_for('select_device', next=request.path))
  deviceid_view_service_details = session.get('selected_deviceid')
  userid_view_service_details=session.get('userid')
  conn, c= get_db()
  c.execute("""
    SELECT * FROM service_details
    WHERE userid=? AND deviceid=?
    """,
    (userid_view_service_details, deviceid_view_service_details))
  view_service_details_list=c.fetchall()
  close_db(conn)
  session.pop('selected_deviceid', None)
  return render_template('view_service_details.html', view_service_details_list=view_service_details_list)

# Delete service details
@app.route('/delete_service_details', methods=['GET', 'POST'])
def delete_service_details():
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session['userid']
    conn, c = get_db()
    #-------------User submits the service details to be deleted.------------------
    if request.method=='POST':
        service_id_to_del=request.form.get('selected_serviceid')
        c.execute("DELETE FROM service_details WHERE service_id = ?", (service_id_to_del,))
        flash(f"Service record {service_id_to_del} deleted successfully!")
        close_db(conn)
        return redirect(url_for('service_details_delete_success'))
        
    #---------------A GET request all service details by the user for all devices---
    
    else:
      c.execute("""
        SELECT 
            s.service_id,
            s.serviced_on,
            s.amount_spent,
            d.device_nickname,
            d.device_type,
            d.manufacturer_name
        FROM service_details AS s
        JOIN device_details AS d
            ON s.deviceid = d.deviceid
        WHERE d.userid = ?
    """, (userid,))
    
    service_list = c.fetchall()
    close_db(conn)
    if service_list:
        return render_template('delete_service_details.html', service_list=service_list)
    else:
        return render_template('delete_service_details_error.html')

@app.route('/service_details_delete_success')
def service_details_delete_success():
    return render_template('service_details_delete_success.html')

#ONLY Display devices
@app.route('/display_devices', methods=['POST', 'GET'])
def display_devices():
  if request.method=='GET':
    if 'userid' not in session:
        return redirect('/login')
    conn, c = get_db()
    userid_display_device=session.get('userid')
    c.execute("""
        SELECT
        device_nickname,
        device_type,
        manufacturer_name
        FROM device_details
        WHERE userid=?
        """,
        (userid_display_device,)
    )
    device_list_display=c.fetchall()
    close_db(conn)
    if device_list_display:
        return render_template('display_devices.html', devices=device_list_display)
    er_disp_msg="No devices registered."
    return render_template('display_devices.html', er_msg=er_disp_msg)
  return redirect(url_for('display_devices'))
    

#Edit device
@app.route('/edit_device', methods=['GET', 'POST'])
def edit_device():
    return render_template('add_delete_device.html')

#Delete a device
@app.route('/delete_device', methods=['GET', 'POST'])
def delete_device():
    if 'selected_deviceid' not in session:        
        return redirect(url_for('select_device', next=request.path))
    deviceid_delete_device = session.get('selected_deviceid')
    userid_device_delete=session.get('userid')
    conn, c=get_db()
    try:
        c.execute(
            "DELETE FROM device_details WHERE userid=? AND deviceid=?",
            (userid_device_delete, deviceid_delete_device 
            ))
        message="Device deletion successful"
    except Exception as e:
        conn.rollback()
        message= f"Error: {e}"
    finally:
        close_db(conn)
    return render_template('device_delete_success.html', message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)