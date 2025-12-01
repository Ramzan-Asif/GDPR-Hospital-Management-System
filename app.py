import streamlit as st
import pandas as pd
from auth import verify_login, log_activity
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
# Add these imports to app.py
from privacy import (
    get_patient_data,
    add_patient,
    anonymize_all_patients,
    encrypt_patient_data,
    decrypt_patient_data,
    set_retention_period,
    check_expired_data,
    delete_expired_data
)
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None


def login_page():
    """
    Display login page
    """
    st.title("🏥 Hospital Management System")
    st.subheader("GDPR-Compliant Patient Data Management")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.write("### 🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = verify_login(username, password)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"✅ Welcome, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Show demo credentials
        with st.expander("👀 Demo Credentials"):
            st.code("""
Admin: admin / admin123
Doctor: dr_bob / doc123
Receptionist: alice / rec123
            """)


def admin_dashboard():
    """
    Dashboard for Admin role with bonus features
    """
    st.title("👑 Admin Dashboard")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Patient Data", 
        "🎭 Anonymize", 
        "📝 Audit Logs",
        "🔐 Encryption",
        "⏰ Data Retention"
    ])
    
    with tab1:
        st.subheader("All Patient Data (Full Access)")
        data = get_patient_data('admin')
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.info(f"📊 Total Patients: {len(df)}")
        else:
            st.warning("⚠️ No patient data available")
    
    with tab2:
        st.subheader("Anonymize Patient Data")
        
        if st.button('🎭 Anonymize All Patients', use_container_width=True):
            with st.spinner('Anonymizing...'):
                anonymize_all_patients()
                log_activity(
                    st.session_state.user['user_id'], 
                    'admin', 
                    'anonymize_all',
                    'Anonymized all patient records'
                )
            st.success("✅ All patients anonymized!")
            st.rerun()
    
    with tab3:
        st.subheader("Audit Logs & Activity Analytics")
        
        # Show activity chart
        display_activity_chart()
        
        st.divider()
        
        # Show logs table
        st.subheader("Detailed Audit Logs")
        logs = get_audit_logs()
        
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)
            
            csv = logs.to_csv(index=False)
            st.download_button(
                "📥 Download Logs",
                csv,
                "audit_logs.csv",
                "text/csv"
            )
        else:
            st.warning("No logs available")
    
    with tab4:
        st.subheader("🔐 Fernet Encryption Management")
        st.write("Encrypt patient data using reversible Fernet encryption")
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id_encrypt = st.number_input(
                "Patient ID to Encrypt",
                min_value=1,
                step=1,
                key="encrypt_id"
            )
            
            if st.button("🔒 Encrypt Patient Data"):
                if encrypt_patient_data(patient_id_encrypt):
                    st.success(f"✅ Patient {patient_id_encrypt} data encrypted!")
                    log_activity(
                        st.session_state.user['user_id'],
                        'admin',
                        'encrypt_data',
                        f'Encrypted patient {patient_id_encrypt}'
                    )
                else:
                    st.error("❌ Encryption failed!")
        
        with col2:
            patient_id_decrypt = st.number_input(
                "Patient ID to Decrypt",
                min_value=1,
                step=1,
                key="decrypt_id"
            )
            
            if st.button("🔓 Decrypt & View Data"):
                decrypted = decrypt_patient_data(patient_id_decrypt)
                if decrypted:
                    st.json(decrypted)
                    log_activity(
                        st.session_state.user['user_id'],
                        'admin',
                        'decrypt_data',
                        f'Decrypted patient {patient_id_decrypt}'
                    )
                else:
                    st.error("❌ Patient not found or decryption failed!")
    
    with tab5:
        st.subheader("⏰ GDPR Data Retention Management")
        
        # Set retention period
        st.write("### Set Retention Period")
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id_retention = st.number_input(
                "Patient ID",
                min_value=1,
                step=1
            )
        
        with col2:
            retention_days = st.number_input(
                "Retention Period (days)",
                min_value=1,
                value=365,
                step=30
            )
        
        if st.button("⏰ Set Retention Period"):
            if set_retention_period(patient_id_retention, retention_days):
                st.success(f"✅ Retention period set: {retention_days} days")
                log_activity(
                    st.session_state.user['user_id'],
                    'admin',
                    'set_retention',
                    f'Set retention for patient {patient_id_retention}: {retention_days} days'
                )
        
        st.divider()
        
        # Check expired data
        st.write("### Check Expired Data")
        if st.button("🔍 Check for Expired Records"):
            expired = check_expired_data()
            if expired:
                st.warning(f"⚠️ Found {len(expired)} expired records:")
                for patient in expired:
                    st.write(f"- Patient ID: {patient[0]}, Expiry: {patient[2]}")
            else:
                st.success("✅ No expired records found")
        
        st.divider()
        
        # Delete expired data
        st.write("### Delete Expired Data")
        st.error("⚠️ **Warning:** This action is irreversible!")
        
        if st.button("🗑️ Delete Expired Records", type="primary"):
            count = delete_expired_data()
            if count > 0:
                st.success(f"✅ Deleted {count} expired records")
                log_activity(
                    st.session_state.user['user_id'],
                    'admin',
                    'delete_expired',
                    f'Deleted {count} expired patient records'
                )
            else:
                st.info("No records to delete")


def doctor_dashboard():
    """
    Dashboard for Doctor role
    """
    st.title("👨‍⚕️ Doctor Dashboard")
    st.subheader("Anonymized Patient Records with Diagnosis")
    
    # Get anonymized patient data with diagnosis
    data = get_patient_data('doctor')
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.info(f"📊 Total Patients: {len(df)}")
        
        # Show information about data access
        st.info("ℹ️ **Privacy Note:** You are viewing anonymized patient identifiers. Real names and contacts are hidden for privacy protection.")
    else:
        st.warning("⚠️ No patient data available")


def receptionist_dashboard():
    """
    Dashboard for Receptionist role
    """
    st.title("👩‍💼 Receptionist Dashboard")
    
    # Create tabs for viewing and adding patients
    tab1, tab2 = st.tabs(["📋 View Patients", "➕ Add Patient"])
    
    with tab1:
        st.subheader("Patient Records (Limited Access)")
        data = get_patient_data('receptionist')
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.info(f"📊 Total Patients: {len(df)}")
            st.warning("⚠️ **Privacy Note:** Diagnosis information is hidden for privacy compliance.")
        else:
            st.warning("⚠️ No patient data available")
    
    with tab2:
        st.subheader("Add New Patient")
        
        with st.form("add_patient_form"):
            name = st.text_input("Patient Name *", placeholder="e.g., John Doe")
            contact = st.text_input("Contact Number *", placeholder="e.g., 0300-1234567")
            diagnosis = st.text_area("Diagnosis *", placeholder="Enter diagnosis details")
            
            submit = st.form_submit_button("➕ Add Patient", use_container_width=True)
            
            if submit:
                if name and contact and diagnosis:
                    try:
                        new_id = add_patient(
                            name, 
                            contact, 
                            diagnosis, 
                            st.session_state.user['user_id']
                        )
                        st.success(f"✅ Patient added successfully! Patient ID: {new_id}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error adding patient: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields!")


def get_audit_logs():
    """
    Fetch audit logs from database
    Returns: DataFrame
    """
    conn = sqlite3.connect('hospital.db')
    
    try:
        query = """
            SELECT log_id, user_id, role, action, timestamp, details
            FROM logs
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching logs: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()


def logout():
    """
    Clear session and logout user
    """
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()



def get_activity_stats():
    """
    Get activity statistics for visualization
    Returns: DataFrame with daily activity counts
    """
    conn = sqlite3.connect('hospital.db')
    
    try:
        query = """
            SELECT 
                DATE(timestamp) as date,
                action,
                COUNT(*) as count
            FROM logs
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY DATE(timestamp), action
            ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


def display_activity_chart():
    """Display real-time activity chart"""
    st.subheader("📊 User Activity (Last 7 Days)")
    
    df = get_activity_stats()
    
    if not df.empty:
        # Create bar chart
        fig = px.bar(
            df, 
            x='date', 
            y='count', 
            color='action',
            title='Daily Activity by Action Type',
            labels={'count': 'Number of Actions', 'date': 'Date'},
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_actions = df['count'].sum()
            st.metric("Total Actions", total_actions)
        
        with col2:
            unique_days = df['date'].nunique()
            st.metric("Active Days", unique_days)
        
        with col3:
            avg_per_day = total_actions / unique_days if unique_days > 0 else 0
            st.metric("Avg Actions/Day", f"{avg_per_day:.1f}")
    else:
        st.info("No activity data available for the last 7 days")


def show_gdpr_consent_banner():
    """
    Display GDPR consent banner
    """
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    
    if not st.session_state.consent_given:
        with st.container():
            st.warning("### 🔒 Data Privacy Notice")
            st.write("""
            This system processes personal health data in compliance with GDPR regulations.
            By using this system, you consent to:
            
            - Processing of personal and medical data for healthcare purposes
            - Data anonymization for privacy protection
            - Secure storage and encryption of sensitive information
            - Audit logging of all system activities
            
            **Your Rights:**
            - Right to access your data
            - Right to data portability
            - Right to be forgotten (data deletion)
            - Right to rectification
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Accept & Continue", use_container_width=True):
                    st.session_state.consent_given = True
                    st.rerun()
            
            with col2:
                if st.button("❌ Decline", use_container_width=True):
                    st.error("You must accept to use the system")
                    st.stop()
        
        st.stop()  # Don't show rest of the app until consent is given


def main():
    """
    Main application logic with GDPR consent
    """
    if not st.session_state.logged_in:
        login_page()
    else:
        # Show GDPR consent banner first
        show_gdpr_consent_banner()
        
        # Rest of your existing code...
        with st.sidebar:
            st.title("🏥 Hospital System")
            st.divider()
            
            st.write("### 👤 User Information")
            st.write(f"**Username:** {st.session_state.user['username']}")
            st.write(f"**Role:** {st.session_state.user['role'].title()}")
            st.write(f"**User ID:** {st.session_state.user['user_id']}")
            
            st.divider()
            
            if st.button("🚪 Logout", use_container_width=True):
                log_activity(
                    st.session_state.user['user_id'],
                    st.session_state.user['role'],
                    'logout',
                    f"User {st.session_state.user['username']} logged out"
                )
                logout()
            
            st.divider()
            
            st.write("### ℹ️ System Info")
            st.caption("✅ GDPR-Compliant")
            st.caption("✅ Fernet Encryption")
            st.caption("✅ Data Retention Policy")
            st.caption("✅ Activity Analytics")
            st.caption("Version 2.0 (Bonus Features)")
            st.caption("Developed by Ramzan - Mufrah")
        
        role = st.session_state.user['role']
        
        if role == 'admin':
            admin_dashboard()
        elif role == 'doctor':
            doctor_dashboard()
        elif role == 'receptionist':
            receptionist_dashboard()


if __name__ == "__main__":
    main()