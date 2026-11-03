import sqlite3
import os

DB_PATH = 'data/campushub.db'

def get_connection():
    """Returns a connection to the SQLite database."""
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    # Allows column access by name (e.g., row['asset_code'])
    conn.row_factory = sqlite3.Row 
    return conn

def create_schema():
    """Initializes the database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Equipment Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                location TEXT,
                condition TEXT,
                status TEXT DEFAULT 'Available'
            )
        ''')
        
        # Borrowers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowers (
                borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
                borrower_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department_or_program TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Loans Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                borrower_id INTEGER NOT NULL,
                borrowed_on TEXT NOT NULL,
                due_on TEXT NOT NULL,
                returned_on TEXT,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (asset_id) REFERENCES equipment (asset_id),
                FOREIGN KEY (borrower_id) REFERENCES borrowers (borrower_id)
            )
        ''')
        conn.commit()
