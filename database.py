import sqlite3
import hashlib

def create_tables():
    """Create all database tables"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    # Patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            diagnosis TEXT,
            anonymized_name TEXT,
            anonymized_contact TEXT,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_users():
    """Add default users to database"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    users = [
        ('admin', hash_password('admin123'), 'admin'),
        ('dr_bob', hash_password('doc123'), 'doctor'),
        ('alice', hash_password('rec123'), 'receptionist')
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO users (username, password, role) 
        VALUES (?, ?, ?)
    """, users)
    
    conn.commit()
    conn.close()
