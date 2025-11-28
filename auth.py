import sqlite3
import hashlib

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """
    Verify user credentials
    Returns: dict with user info if successful, None if failed
    """
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, username, password, role 
            FROM users 
            WHERE username = ?
        """, (username,))
        user = cursor.fetchone()
        
        # Check if user exists
        if user is None:
            log_activity(0, 'unknown', 'login attempt failed', f'username: {username} not found')
            return None
        
        # Verify password
        input_password = hash_password(password)
        if user[2] == input_password:
            log_activity(user[0], user[3], 'login successful', f'username: {username}')
            return {
                'user_id': user[0],
                'username': user[1],
                'role': user[3]
            }
        else:
            log_activity(user[0], user[3], 'login attempt failed', f'wrong password for {username}')
            return None
            
    finally:
        conn.close()


def log_activity(user_id, role, action, details=""):
    """Log user activities to the logs table"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO logs (user_id, role, action, details)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, action, details))
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    # Test successful login
    print("Test 1: Valid credentials")
    creds = verify_login('admin', 'admin123')
    print(creds)
    
    # Test wrong password
    print("\nTest 2: Wrong password")
    creds = verify_login('admin', 'wrongpass')
    print(creds)
    
    # Test non-existent user
    print("\nTest 3: Non-existent user")
    creds = verify_login('hacker', 'password')
    print(creds)