# setup.py - Run this once to set up everything

import sqlite3
from database import create_tables, seed_users
from cryptography.fernet import Fernet

def setup_database():
    """Initialize database with all tables"""
    print("📦 Setting up database...")
    create_tables()
    print("✅ Tables created!")


def setup_users():
    """Add default users"""
    print("👥 Setting up users...")
    
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        from database import seed_users
        seed_users()
        print("✅ Users added!")
    else:
        print(f"ℹ️ Users already exist ({count} users found)")
    
    conn.close()


def add_test_patients():
    """Add test patient data"""
    print("🏥 Adding test patients...")
    
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Check if patients already exist
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    
    if count == 0:
        patients = [
            ('John Doe', '0300-1234567', 'Diabetes'),
            ('Jane Smith', '+92-321-9876543', 'Hypertension'),
            ('Ali Khan', '03451234567', 'Flu'),
            ('Sara Ahmed', '0333-7654321', 'Asthma'),
            ('Ahmed Raza', '0345-9998877', 'Migraine')
        ]
        
        cursor.executemany("""
            INSERT INTO patients (name, contact, diagnosis)
            VALUES (?, ?, ?)
        """, patients)
        
        conn.commit()
        print(f"✅ Added {len(patients)} test patients!")
    else:
        print(f"ℹ️ Patients already exist ({count} patients found)")
    
    conn.close()


def add_gdpr_columns():
    """Add GDPR-related columns (safe to run multiple times)"""
    print("🔒 Adding GDPR columns...")
    
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(patients)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    columns_added = 0
    
    # Add consent_given column
    if 'consent_given' not in existing_columns:
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN consent_given INTEGER DEFAULT 0
        """)
        columns_added += 1
        print("  ✅ Added consent_given column")
    else:
        print("  ℹ️ consent_given already exists")
    
    # Add retention_date column
    if 'retention_date' not in existing_columns:
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN retention_date TEXT
        """)
        columns_added += 1
        print("  ✅ Added retention_date column")
    else:
        print("  ℹ️ retention_date already exists")
    
    if columns_added > 0:
        conn.commit()
        print(f"✅ Added {columns_added} GDPR columns!")
    else:
        print("✅ All GDPR columns already exist!")
    
    conn.close()


def setup_encryption_key():
    """Generate encryption key if it doesn't exist"""
    print("🔐 Setting up encryption key...")
    
    try:
        with open('secret.key', 'rb') as f:
            key = f.read()
        print("ℹ️ Encryption key already exists")
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
        print("✅ Encryption key generated!")
    
    return key


def main():
    """Run complete setup"""
    print("\n" + "="*50)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM SETUP")
    print("="*50 + "\n")
    
    try:
        # Step 1: Create database and tables
        setup_database()
        
        # Step 2: Add default users
        setup_users()
        
        # Step 3: Add test patients
        add_test_patients()
        
        # Step 4: Add GDPR columns
        add_gdpr_columns()
        
        # Step 5: Setup encryption
        setup_encryption_key()
        
        print("\n" + "="*50)
        print("✅ SETUP COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\n📝 You can now run: streamlit run app.py")
        print("\n👥 Default Users:")
        print("   Admin: admin / admin123")
        print("   Doctor: dr_bob / doc123")
        print("   Receptionist: alice / rec123")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()