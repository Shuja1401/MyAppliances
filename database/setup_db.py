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
CREATE TABLE IF NOT EXISTS device_details(
device_id TEXT PRIMARY KEY,
contact_number TEXT,
device_nickname TEXT,
device_category TEXT,
device_type TEXT,
manufacturer_name TEXT,
purchase_date TEXT,
original_warranty_duration_in_months INTEGER,
extended_warranty_y_n TEXT,
extended_warranty_duration_in_months INTEGER,
service_plan_y_n TEXT,
manufacturer_or_third_party TEXT,
contact_no_service_centre TEXT,
service_required_after_months INTEGER,
FOREIGN KEY (contact_number) REFERENCES onboarding(contact_number)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS service_details(
service_id INTEGER PRIMARY KEY AUTOINCREMENT,
contact_number TEXT,
device_id TEXT,
amount_spent REAL,
name_part_replaced TEXT,
service_warranty_y_n TEXT,
service_warranty_in_months INTEGER,
part_warranty_in_months INTEGER,
additional_remark TEXT,
FOREIGN KEY (contact_number) REFERENCES onboarding(contact_number),
FOREIGN KEY (device_id) REFERENCES device_details(device_id)
)
''')
                                               
conn.commit()
conn.close()

print("Database and tables created successfully!")
