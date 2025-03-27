import sqlite3
from datetime import datetime
import pandas as pd
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database.log')
    ]
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with proper error handling"""
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Current working directory: {os.getcwd()}")
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        logger.info("Creating database tables...")

        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS admin
                         (username TEXT PRIMARY KEY, password TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS employees
                         (id INTEGER PRIMARY KEY, name TEXT, aadhar_number TEXT UNIQUE,
                          phone TEXT, address TEXT, join_date TEXT, daily_wage REAL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                         (id INTEGER PRIMARY KEY, employee_id INTEGER,
                          date TEXT, status TEXT,
                          FOREIGN KEY (employee_id) REFERENCES employees(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS salary_advances
                         (id INTEGER PRIMARY KEY, employee_id INTEGER,
                          amount REAL, date TEXT,
                          FOREIGN KEY (employee_id) REFERENCES employees(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS inventory
                         (id INTEGER PRIMARY KEY, item_name TEXT,
                          quantity REAL, unit TEXT,
                          last_updated TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS rent_payments
                         (id INTEGER PRIMARY KEY, due_date TEXT,
                          amount REAL, status TEXT)''')

        # Insert default admin if not exists
        c.execute("INSERT OR IGNORE INTO admin VALUES (?, ?)",
                  ("admin", "admin123"))


        conn.commit()
        logger.info("Database tables created successfully")

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise Exception(f"Failed to initialize database: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


# Admin functions
def verify_admin(username, password):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?",
                  (username, password))
        result = c.fetchone()
        return result is not None
    except sqlite3.Error as e:
        logger.error(f"Database error during admin verification: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

# Employee functions
def add_employee(name, aadhar, phone, address, wage):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""INSERT INTO employees 
                     (name, aadhar_number, phone, address, join_date, daily_wage)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (name, aadhar, phone, address,
                   datetime.now().strftime('%Y-%m-%d'), wage))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Duplicate aadhar number attempted: {aadhar}")
        return False
    except sqlite3.Error as e:
        logger.error(f"Database error while adding employee: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def update_employee(emp_id, name, phone, address, wage):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""UPDATE employees 
                     SET name=?, phone=?, address=?, daily_wage=?
                     WHERE id=?""",
                  (name, phone, address, wage, emp_id))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating employee: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def delete_employee(emp_id):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting employee: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_employees():
    try:
        conn = sqlite3.connect('hotel_management.db')
        df = pd.read_sql_query("SELECT * FROM employees", conn)
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Error fetching employees: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

# Attendance functions
def mark_attendance(employee_id, date, status):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        # First check if attendance already exists for this date
        c.execute("""SELECT id FROM attendance 
                            WHERE employee_id=? AND date=?""",
                  (employee_id, date))
        existing = c.fetchone()
        if existing:
            # Update existing attendance
            c.execute("""UPDATE attendance SET status=?
                                WHERE employee_id=? AND date=?""",
                      (status, employee_id, date))
        else:
            # Insert new attendance
            c.execute("""INSERT INTO attendance (employee_id, date, status)
                                VALUES (?, ?, ?)""", (employee_id, date, status))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error marking attendance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def update_attendance(attendance_id, status):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""UPDATE attendance SET status=? WHERE id=?""",
                  (status, attendance_id))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating attendance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def delete_attendance(attendance_id):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("DELETE FROM attendance WHERE id=?", (attendance_id,))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting attendance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def get_attendance(start_date, end_date):
    try:
        conn = sqlite3.connect('hotel_management.db')
        query = """
            SELECT a.id, e.name, a.date, a.status
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.date BETWEEN ? AND ?
            """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Error fetching attendance: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

# Inventory functions
def update_inventory(item_name, quantity, unit):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO inventory 
                         (item_name, quantity, unit, last_updated)
                         VALUES (?, ?, ?, ?)""",
                  (item_name, quantity, unit,
                   datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating inventory: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def delete_inventory_item(item_id):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting inventory item: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def get_inventory():
    try:
        conn = sqlite3.connect('hotel_management.db')
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Error fetching inventory: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()
#
def add_advance(employee_id, amount):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""INSERT INTO salary_advances 
                         (employee_id, amount, date)
                         VALUES (?, ?, ?)""",
                  (employee_id, amount, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding salary advance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def update_advance(advance_id, amount):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""UPDATE salary_advances SET amount=? WHERE id=?""",
                  (amount, advance_id))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating salary advance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def delete_advance(advance_id):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("DELETE FROM salary_advances WHERE id=?", (advance_id,))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting salary advance: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def get_advances(employee_id, month, year):
    try:
        conn = sqlite3.connect('hotel_management.db')
        query = """
            SELECT id, amount, date FROM salary_advances
            WHERE employee_id = ?
            AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
            """
        df = pd.read_sql_query(query, conn,
                           params=(employee_id, f"{month:02d}", str(year)))
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Error fetching salary advances: {str(e)}")
        return pd.DataFrame()

    finally:
        if 'conn' in locals():
            conn.close()

# Rent payment functions
def add_rent_payment(due_date, amount, status):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""INSERT INTO rent_payments (due_date, amount, status)
                     VALUES (?, ?, ?)""",
                  (due_date, amount, status))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding rent payment: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def update_rent_payment(payment_id, amount, status):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("""UPDATE rent_payments SET amount=?, status=?
                     WHERE id=?""", (amount, status, payment_id))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating rent payment: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def delete_rent_payment(payment_id):
    try:
        conn = sqlite3.connect('hotel_management.db')
        c = conn.cursor()
        c.execute("DELETE FROM rent_payments WHERE id=?", (payment_id,))
        conn.commit()
        return c.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting rent payment: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
def get_rent_payments():
    try:
        conn = sqlite3.connect('hotel_management.db')
        df = pd.read_sql_query("SELECT * FROM rent_payments", conn)
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Error fetching rent payments: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()