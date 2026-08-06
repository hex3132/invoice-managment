import os
import sqlite3
import datetime

class DatabaseManager:
    """
    Offline SQLite Database Engine with audit trail logging
    and automatic dedicated folder database storage.
    """
    def __init__(self, folder_name="data", db_filename="hospital_billing.db"):
        # Store database in a dedicated subfolder to protect previous data
        self.base_dir = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        self.db_path = os.path.join(self.base_dir, db_filename)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Initializes database schema if missing."""
        # 1. Product Catalog Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL
            )
        ''')

        # 2. Final Receipts Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                mobile TEXT,
                ref_no TEXT,
                patient_id TEXT,
                date_time TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount_amount REAL NOT NULL,
                payable_balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. Audit History Log Table (Requirement 8)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipt_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                field_edited TEXT,
                old_value TEXT,
                new_value TEXT,
                edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (receipt_id) REFERENCES receipts(receipt_id)
            )
        ''')
        self.conn.commit()

    # --- Product CRUD ---
    def add_product(self, name: str, price: float):
        self.cursor.execute("INSERT OR REPLACE INTO products (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()

    def update_product(self, product_id: int, name: str, price: float):
        self.cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (name, price, product_id))
        self.conn.commit()

    def delete_product(self, product_id: int):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()

    def get_all_products(self):
        self.cursor.execute("SELECT id, name, price FROM products ORDER BY name ASC")
        return self.cursor.fetchall()

    # --- Receipts & History CRUD ---
    def save_receipt(self, patient_name, mobile, ref_no, patient_id, date_time, subtotal, discount, payable):
        self.cursor.execute('''
            INSERT INTO receipts (patient_name, mobile, ref_no, patient_id, date_time, subtotal, discount_amount, payable_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_name, mobile, ref_no, patient_id, date_time, subtotal, discount, payable))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_receipt(self, receipt_id, patient_name, mobile, ref_no, patient_id, subtotal, discount, payable):
        self.cursor.execute('''
            UPDATE receipts 
            SET patient_name = ?, mobile = ?, ref_no = ?, patient_id = ?, subtotal = ?, discount_amount = ?, payable_balance = ?
            WHERE receipt_id = ?
        ''', (patient_name, mobile, ref_no, patient_id, subtotal, discount, payable, receipt_id))
        self.conn.commit()

    def get_all_receipts(self):
        self.cursor.execute("SELECT receipt_id, patient_name, mobile, ref_no, patient_id, date_time, subtotal, discount_amount, payable_balance FROM receipts ORDER BY receipt_id DESC")
        return self.cursor.fetchall()

    def get_receipt_by_id(self, receipt_id):
        self.cursor.execute("SELECT receipt_id, patient_name, mobile, ref_no, patient_id, date_time, subtotal, discount_amount, payable_balance FROM receipts WHERE receipt_id = ?", (receipt_id,))
        return self.cursor.fetchone()

    def log_edit(self, receipt_id, field_edited, old_val, new_val):
        """Logs audit history entries whenever an old receipt is updated."""
        self.cursor.execute('''
            INSERT INTO receipt_history (receipt_id, field_edited, old_value, new_value)
            VALUES (?, ?, ?, ?)
        ''', (receipt_id, field_edited, str(old_val), str(new_val)))
        self.conn.commit()

    def get_receipt_history(self, receipt_id):
        self.cursor.execute('''
            SELECT field_edited, old_value, new_value, edited_at 
            FROM receipt_history 
            WHERE receipt_id = ? 
            ORDER BY history_id DESC
        ''', (receipt_id,))
        return self.cursor.fetchall()