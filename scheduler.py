import sqlite3
import time
from main import get_db, close_db

def update_due_soon_table():
    """Refresh devices_with_service_due table every 24 hours."""
    conn = get_db()
    c = conn.cursor()

    # Drop old table if it exists
    c.execute("DROP TABLE IF EXISTS devices_with_service_due;")

    # Create the updated table
    c.execute("""
        CREATE TABLE devices_with_service_due AS
        SELECT 
            o.userid, 
            o.username, 
            d.deviceid, 
            d.device_nickname
        FROM onboarding AS o
        JOIN device_details AS d 
            ON o.userid = d.userid
        JOIN service_details AS s 
            ON d.deviceid = s.deviceid
        WHERE 
            date(s.service_due_date, '+3 day') = date('now');
    """)

    conn.commit()
    close_db(conn)
    print("✅ devices_with_service_due table updated successfully!")

# Run every 24 hours (86400 seconds)
if __name__ == "__main__":
    while True:
        update_due_soon_table()
        print("Next update in 24 hours...")
        time.sleep(86400)
