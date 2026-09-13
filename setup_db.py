import sqlite3
from faker import Faker

conn = sqlite3.connect('company.db')
cursor = conn.cursor()
fake = Faker()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT,
    hire_date DATE
)
""")

employees = []

for i in range (100) :
    name = fake.name()
    role = fake.job()
    doj = fake.date()
    data = (i+1, name, role, doj)
    employees.append(data)

cursor.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?)", employees)
conn.commit()
conn.close()
print("Database 'company.db' initialized with sample data.")