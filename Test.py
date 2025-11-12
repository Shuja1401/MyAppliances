
# =================================================================================================
# Code below this line is not required.
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

#Service due date function
@app.route('/service_due', methods=['GET', 'POST'])
def device_service_due():
    conn, c = get_db()
    userid_session_service_due=session.get('userid')
    c.execute(
        "SELECT * FROM devices_with_service_due WHERE userid=?",
        (userid_session_service_due,)
    )
    list_service_due=c.fetchall()
    close_db(conn)
    return list_service_due

===================================================================================================


def service_warranty_status(route_name):
    conn, c = get_db()
    if 'userid' not in session:return redirect('/login')
    userid_status=session.get('userid')
    c.execute(
        """SELECT
        device_nickname,
        device_type,
        manufacturer_name,
        warranty_expires_on,
        last_serviced_on,
        next_service_due
        FROM device_details
        WHERE userid=?
        """,
        (userid_status,)
    )
    ser_war_status=c.fetchall()
    current_date=date.today()
    warranty_status_chk= "In warranty" if ser_war_status[3] > current_date else "Warranty expired"
    service_status_chk = "Service overdue" if ser_war_status[5] < current_date else None
    close_db(conn)
    if route_name=="service_warranty_status_chk":
        return render_template ('warranty_service_status.html',
            ser_war_status=ser_war_status,
            warranty_status_chk=warranty_status_chk,
            service_status_chk=service_status_chk
        )
    elif route_name=="navigation"
        

@app.route('/service_warranty_status_chk', methods=['GET', 'POST'])
def service_warranty_status_chk():
    ser_war_sta_chk = service_warranty_status("service_warranty_status_chk")