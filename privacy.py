import sqlite3
import hashlib
from cryptography.fernet import Fernet
from auth import log_activity  # Import for logging
import os
from datetime import datetime
from setup import setup_encryption_key

def anonymize_name(patient_id):
    """
    Convert patient name to anonymous ID
    Example: 'John Doe' → 'ANON_1021'
    """
    return f"ANON_{patient_id}"

def mask_contact(contact):
    """
    Mask contact number keeping last 4 digits
    Example: '0300-1234567' → 'XXX-XXX-4567'
    """
    if not contact:
        return "XXX-XXX-XXXX"
    
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, contact))
    
    # Keep last 4 digits
    if len(digits_only) >= 4:
        last_four = digits_only[-4:]
        return f"XXX-XXX-{last_four}"
    else:
        return "XXX-XXX-XXXX"


def anonymize_patient(patient_id):
    """
    Anonymize a specific patient's data in the database
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fetch patient's current data
        cursor.execute("SELECT name, contact FROM patients WHERE patient_id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if patient is None:
            print(f"❌ Patient {patient_id} not found!")
            return None
        
        # 2. Generate anonymized versions
        anon_name = anonymize_name(patient_id)
        anon_contact = mask_contact(patient[1])

        # 3. UPDATE the patient record with anonymized data
        cursor.execute("""
            UPDATE patients 
            SET anonymized_name = ?, anonymized_contact = ? 
            WHERE patient_id = ?
        """, (anon_name, anon_contact, patient_id))
        
        conn.commit()
        print(f"✅ Patient {patient_id} anonymized successfully!")
        return True
        
    finally:
        conn.close()


def anonymize_all_patients():
    """
    Anonymize ALL patients in the database
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # 1. Get ALL patient IDs
        cursor.execute("SELECT patient_id FROM patients")
        patients = cursor.fetchall()
        
        if not patients:
            print("❌ No patients found in database!")
            return
        
        # 2. Loop through each patient and anonymize
        count = 0
        for patient in patients:
            patient_id = patient[0]
            
            # Fetch contact for this patient
            cursor.execute("SELECT contact FROM patients WHERE patient_id = ?", (patient_id,))
            result = cursor.fetchone()
            
            if result:
                anon_name = anonymize_name(patient_id)
                anon_contact = mask_contact(result[0])
                
                # Update this patient
                cursor.execute("""
                    UPDATE patients 
                    SET anonymized_name = ?, anonymized_contact = ? 
                    WHERE patient_id = ?
                """, (anon_name, anon_contact, patient_id))
                count += 1
        
        conn.commit()
        print(f"✅ Successfully anonymized {count} patients!")
        
    finally:
        conn.close()


def get_patient_data(role):
    """
    Fetch patient data based on user role
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            query = """
                SELECT patient_id, name, contact, diagnosis, 
                       anonymized_name, anonymized_contact, date_added
                FROM patients
            """
            
        elif role == 'doctor':
            query = """
                SELECT patient_id, anonymized_name, anonymized_contact, 
                       diagnosis, date_added
                FROM patients
            """
            
        elif role == 'receptionist':
            query = """
                SELECT patient_id, anonymized_name, anonymized_contact, 
                       date_added
                FROM patients
            """
        else:
            return []
        
        # Execute query
        cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]
        
        return data
        
    finally:
        conn.close()


def get_patient_by_id(patient_id, role):
    """
    Get a single patient's data based on role
    
    Returns: Dictionary with patient data or None
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            query = """
                SELECT patient_id, name, contact, diagnosis, 
                       anonymized_name, anonymized_contact, date_added
                FROM patients WHERE patient_id = ?
            """
            
        elif role == 'doctor':
            query = """
                SELECT patient_id, anonymized_name, anonymized_contact, 
                       diagnosis, date_added
                FROM patients WHERE patient_id = ?
            """
            
        elif role == 'receptionist':
            query = """
                SELECT patient_id, anonymized_name, anonymized_contact, 
                       date_added
                FROM patients WHERE patient_id = ?
            """
        else:
            return None
        
        # Execute query
        cursor.execute(query, (patient_id,))
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch the row
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        # Convert to dictionary
        data = dict(zip(columns, row))
        
        return data
        
    finally:
        conn.close()


def add_patient(name, contact, diagnosis, added_by_user_id):
    """
    Add a new patient to the database
    Automatically anonymizes upon insertion
    
    Returns: patient_id of newly created patient
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # 1. INSERT new patient with name, contact, diagnosis
        cursor.execute("""
            INSERT INTO patients (name, contact, diagnosis)
            VALUES (?, ?, ?)
        """, (name, contact, diagnosis))
        
        # 2. Get the new patient_id
        new_patient_id = cursor.lastrowid
        
        # 3. Automatically anonymize this new patient
        anon_name = anonymize_name(new_patient_id)
        anon_contact = mask_contact(contact)
        
        cursor.execute("""
            UPDATE patients 
            SET anonymized_name = ?, anonymized_contact = ? 
            WHERE patient_id = ?
        """, (anon_name, anon_contact, new_patient_id))
        
        conn.commit()
        
        # 4. Log the activity
        log_activity(added_by_user_id, 'receptionist', 'add_patient', 
                    f'Added patient {new_patient_id}: {name}')
        
        print(f"✅ Patient {new_patient_id} added and anonymized successfully!")
        
        # 5. Return the patient_id
        return new_patient_id
        
    finally:
        conn.close()


from datetime import datetime, timedelta

def set_retention_period(patient_id, days=365):
    """
    Set data retention period for a patient
    Default: 365 days (1 year)
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        retention_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            UPDATE patients 
            SET retention_date = ?
            WHERE patient_id = ?
        """, (retention_date, patient_id))
        
        conn.commit()
        print(f"✅ Retention period set for patient {patient_id}: {retention_date}")
        return True
        
    finally:
        conn.close()


def check_expired_data():
    """
    Check for patients whose data retention period has expired
    Returns: List of patient IDs with expired data
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT patient_id, name, retention_date 
            FROM patients 
            WHERE retention_date IS NOT NULL 
            AND retention_date <= ?
        """, (today,))
        
        expired = cursor.fetchall()
        return expired
        
    finally:
        conn.close()


def delete_expired_data():
    """
    Delete patient data that has exceeded retention period
    Returns: Number of records deleted
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get count first
        cursor.execute("""
            SELECT COUNT(*) FROM patients 
            WHERE retention_date IS NOT NULL 
            AND retention_date <= ?
        """, (today,))
        count = cursor.fetchone()[0]
        
        # Delete expired records
        cursor.execute("""
            DELETE FROM patients 
            WHERE retention_date IS NOT NULL 
            AND retention_date <= ?
        """, (today,))
        
        conn.commit()
        print(f"✅ Deleted {count} expired patient records")
        return count
        
    finally:
        conn.close()



def load_encryption_key():
    """Load the encryption key"""
    try:
        return open('secret.key', 'rb').read()
    except FileNotFoundError:
        print("⚠️ Key file not found. Generating new key...")
        return setup_encryption_key()


def encrypt_data(data):
    """
    Encrypt data using Fernet
    Returns: Encrypted string
    """
    if not data:
        return None
    
    key = load_encryption_key()
    fernet = Fernet(key)
    
    # Encrypt the data (must be bytes)
    encrypted = fernet.encrypt(data.encode())
    
    # Return as string for database storage
    return encrypted.decode()


def decrypt_data(encrypted_data):
    """
    Decrypt data using Fernet
    Returns: Original string
    """
    if not encrypted_data:
        return None
    
    key = load_encryption_key()
    fernet = Fernet(key)
    
    # Decrypt (convert string back to bytes first)
    decrypted = fernet.decrypt(encrypted_data.encode())
    
    # Return as string
    return decrypted.decode()


def encrypt_patient_data(patient_id):
    """
    Encrypt sensitive patient data (reversible)
    Stores encrypted version in database
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # Get patient data
        cursor.execute("""
            SELECT name, contact, diagnosis 
            FROM patients 
            WHERE patient_id = ?
        """, (patient_id,))
        
        patient = cursor.fetchone()
        if not patient:
            return False
        
        name, contact, diagnosis = patient
        
        # Encrypt sensitive fields
        encrypted_name = encrypt_data(name)
        encrypted_contact = encrypt_data(contact)
        encrypted_diagnosis = encrypt_data(diagnosis)
        
        # Update database with encrypted versions
        # Add new columns if needed (or reuse existing ones)
        cursor.execute("""
            UPDATE patients 
            SET name = ?, contact = ?, diagnosis = ?
            WHERE patient_id = ?
        """, (encrypted_name, encrypted_contact, encrypted_diagnosis, patient_id))
        
        conn.commit()
        print(f"✅ Patient {patient_id} data encrypted!")
        return True
        
    finally:
        conn.close()


def decrypt_patient_data(patient_id):
    """
    Decrypt patient data for authorized viewing
    Returns: Dictionary with decrypted data
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT patient_id, name, contact, diagnosis 
            FROM patients 
            WHERE patient_id = ?
        """, (patient_id,))
        
        patient = cursor.fetchone()
        if not patient:
            return None
        
        pid, encrypted_name, encrypted_contact, encrypted_diagnosis = patient
        
        # Decrypt the data
        decrypted_data = {
            'patient_id': pid,
            'name': decrypt_data(encrypted_name),
            'contact': decrypt_data(encrypted_contact),
            'diagnosis': decrypt_data(encrypted_diagnosis)
        }
        
        return decrypted_data
        
    finally:
        conn.close()


# Test the functions
if __name__ == "__main__":
    print("Testing anonymization functions:")
    print(f"Name: {anonymize_name(1021)}")
    print(f"Contact: {mask_contact('0300-1234567')}")
    print(f"Contact: {mask_contact('+92-321-9876543')}")
    
    print("\n--- Testing Database Anonymization ---")
    # Test single patient anonymization
    anonymize_patient(1)
    
    # Test all patients anonymization
    anonymize_all_patients()
    
    print("\n--- Testing RBAC ---")
    print("\nAdmin view:")
    print(get_patient_data('admin'))
    
    print("\nDoctor view:")
    print(get_patient_data('doctor'))
    
    print("\nReceptionist view:")
    print(get_patient_data('receptionist'))
    
    print("\n--- Testing Add Patient ---")
    new_id = add_patient('Test Patient', '0321-9999999', 'Test Condition', 3)
    print(f"New patient ID: {new_id}")