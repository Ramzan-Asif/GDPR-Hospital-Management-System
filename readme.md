# 🏥 GDPR Hospital Management System

A privacy-centric hospital management dashboard implementing GDPR compliance and the CIA Triad (Confidentiality, Integrity, Availability) using Python and Streamlit.

## ✨ Features

### Core Features
- 🔐 **Role-Based Access Control (RBAC)** - Admin, Doctor, Receptionist roles
- 🎭 **Data Anonymization** - Patient name and contact masking
- 📝 **Audit Logging** - Complete activity tracking
- 🔒 **Fernet Encryption** - Reversible data encryption
- ⏰ **Data Retention Policy** - Automated expired data deletion
- ✅ **GDPR Consent Management** - User consent banner

### CIA Triad Implementation
- **Confidentiality**: Data anonymization, encryption, RBAC
- **Integrity**: Audit logs, access controls, data validation
- **Availability**: System uptime, data backup/export

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.x
- **Database**: SQLite
- **Encryption**: Fernet (cryptography library)
- **Visualization**: Plotly
- **Security**: SHA-256 password hashing

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/gdpr-hospital-management-system.git

# Navigate to directory
cd gdpr-hospital-management-system

# Install dependencies
pip install -r requirements.txt

# Start the application
streamlit run app.py
```

## 👥 Default Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| dr_bob | doc123 | Doctor |
| alice | rec123 | Receptionist |

## 📸 Screenshots

[Add screenshots here]

## 🎓 Academic Context

This project was developed for the **Information Security (CS-3002)** course, 
Assignment #4: Privacy, Trust & the CIA Triad in Modern Information Systems.

Inspired by the lecture "Privacy Past and Present: A Father-Daughter Dive 
into Data Privacy Evolution" from RSA Conference 2024.

## 📄 License

MIT / Apache 2.0
![Project](https://img.shields.io/badge/Project-Hospital_Management_System-blue)

## 👨‍💻 Author

Ramzan Asif
