import sqlite3

conn = sqlite3.connect('database/MyAppliances.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS onboarding (
userid number AUTOINCREMENT PRIMARY KEY,
username TEXT,
contact_number TEXT
first_name TEXT,
last_name TEXT,
state TEXT,
city TEXT,
pin_code TEXT,
complete_address TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS device_details (
    device_id TEXT PRIMARY KEY,
    contact_number TEXT,
    device_nickname TEXT,
    device_category TEXT,
    device_type TEXT,
    manufacturer_name TEXT,
    purchase_date TEXT NOT NULL,  -- must have a purchase date
    original_warranty_duration_in_months INTEGER NOT NULL,
    extended_warranty_y_n TEXT,
    extended_warranty_duration_in_months INTEGER,
    extended_warranty_expires_date TEXT GENERATED ALWAYS AS (
        CASE
            WHEN extended_warranty_duration_in_months IS NOT NULL
            THEN date(purchase_date, '+' || (original_warranty_duration_in_months + extended_warranty_duration_in_months) || ' months')
            ELSE date(purchase_date, '+' || original_warranty_duration_in_months || ' months')
        END
    ) STORED,
    service_plan_y_n TEXT,
    manufacturer_or_third_party TEXT,
    contact_no_service_centre TEXT,
    service_required_after_months INTEGER,
    FOREIGN KEY (contact_number) REFERENCES onboarding(contact_number)
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS service_centre_details(
device_type TEXT
manufacturer_name TEXT
company_name TEXT
company_contact_no TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS service_details(
service_id INTEGER PRIMARY KEY AUTOINCREMENT,
contact_number TEXT,
device_id TEXT,
serviced_on_date TEXT,
amount_spent REAL,
name_part_replaced TEXT,
service_warranty_y_n TEXT,
service_warranty_in_months INTEGER,
part_warranty_y_n TEXT,
part_warranty_in_months INTEGER,
additional_remark TEXT,
FOREIGN KEY (contact_number) REFERENCES onboarding(contact_number),
FOREIGN KEY (device_id) REFERENCES device_details(device_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS devices_with_service_due(
userid_service_due_db INTEGER
username_service_due VARCHAR(255)
device_id_service_due INTEGER
device_nickname_service_due(255)
)
''')
conn.commit()
conn.close()

print("Database and tables created successfully!")
