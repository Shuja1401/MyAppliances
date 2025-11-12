import time

from db_utils import close_db, get_db


def update_due_soon_table():
    """Refresh devices_with_service_due table every 24 hours."""
    conn, c = get_db()

    # Ensure table exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS devices_with_service_due (
        userid TEXT,
        username TEXT,
        deviceid TEXT,
        device_nickname TEXT
    );
    """)
    
    # Clear existing entries
    c.execute("DELETE FROM devices_with_service_due;")
    
    # Refill with new data
    c.execute("""
    INSERT INTO devices_with_service_due
    SELECT 
        o.userid, 
        u.username, 
        d.deviceid, 
        d.device_nickname
    FROM onboarding AS o
    JOIN users AS u
        ON o.userid=u.userid
    JOIN device_details AS d 
        ON o.userid = d.userid
    JOIN service_details AS s 
        ON d.deviceid = s.deviceid
    WHERE
        date(d.next_service_due) <= date('now', '+3 day')
        AND date(d.next_service_due) >= date('now');
    """)


# Run every 24 hours (86400 seconds)
if __name__ == "__main__":
    while True:
        update_due_soon_table()
        print("Next update in 24 hours...")
        time.sleep(86400)
