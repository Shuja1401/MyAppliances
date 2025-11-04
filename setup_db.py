import contextlib
import textwrap

from db_utils import get_db


def init_db():
    """Create all tables from scratch."""
    conn, c = get_db()
    
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        sql_script=textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS onboarding (
            userid INTEGER PRIMARY KEY,
            contact_number TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            state TEXT,
            city TEXT,
            pin_code TEXT,
            complete_address TEXT,
            FOREIGN KEY (userid) REFERENCES users(userid)
        );
        CREATE TABLE IF NOT EXISTS device_details (
            deviceid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            device_nickname TEXT,
            device_type TEXT,
            manufacturer_name TEXT,
            purchase_date TEXT NOT NULL,
            original_warranty_duration_in_months INTEGER NOT NULL,
            extended_warranty_y_n TEXT,
            extended_warranty_duration_in_months INTEGER,
            warranty_expires_on TEXT,
            service_plan_y_n TEXT,
            manufacturer_or_third_party TEXT,
            service_required_after_months INTEGER,
            last_serviced_on TEXT,
            next_service_due TEXT,
            FOREIGN KEY (userid) REFERENCES users(userid)
        );
        CREATE TABLE IF NOT EXISTS service_details (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deviceid INTEGER NOT NULL,
            serviced_on TEXT,
            amount_spent REAL,
            name_part_replaced TEXT,
            service_warranty_y_n TEXT,
            service_warranty_in_months INTEGER,
            part_warranty_y_n TEXT,
            part_warranty_in_months INTEGER,
            additional_remark TEXT,
            FOREIGN KEY (deviceid) REFERENCES device_details(deviceid)
        );
        CREATE TABLE IF NOT EXISTS service_centre_details (
            userid INTEGER PRIMARY KEY,
            deviceid INTEGER,
            device_type TEXT,
            manufacturer_name TEXT,
            name_service_centre TEXT,
            address_service_centre TEXT,
            contact_no_service_centre TEXT
        );
        """)
        print(sql_script)
        conn.executescript(sql_script)
        conn.commit()
        print("Success")
    except Exception:
        import traceback
        traceback.print_exc()

    finally:
        with contextlib.suppress(Exception):
            c.close()
        with contextlib.suppress(Exception):
            conn.close()
if __name__ == "__main__":
    init_db()
