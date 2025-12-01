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

# Add to database.py

def add_gdpr_columns():
    """Add GDPR-related columns (FIXED VERSION)"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Check existing columns first
    cursor.execute("PRAGMA table_info(patients)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Add consent_given if missing
    if 'consent_given' not in existing_columns:
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN consent_given INTEGER DEFAULT 0
        """)
        print("✅ Added consent_given column")
    else:
        print("ℹ️ consent_given already exists")
    
    # Add retention_date if missing
    if 'retention_date' not in existing_columns:
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN retention_date TEXT
        """)
        print("✅ Added retention_date column")
    else:
        print("ℹ️ retention_date already exists")
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    seed_users()
    add_gdpr_columns()
    print("✅ Database setup completed!")