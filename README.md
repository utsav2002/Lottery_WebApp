# Lottery_WebApp

Introduction:
This repository contains the source code for a secure lottery webapp built with Flask, a Python web framework. The app integrates robust security protocols including HTTPS enforcement, user authentication, and data encryption, making it a secure platform for managing lottery events.

Features:
- User Authentication: Utilizes Flask-Login for secure user management.
- Data Encryption: Employs cryptography for encrypting sensitive data.
- Two-Factor Authentication (2FA): Implements 2FA using pyotp for enhanced security.
- Secure Database Interaction: Integrates Flask-SQLAlchemy for database operations
- Modular Design: Organized into separate blueprints for admin, lottery, and user functionalities.
- Security Enhancement: Uses Talisman for enforcing HTTPS and setting security headers.

Security Protocols:
- HTTPS Enforcement: Ensured by Talisman.
- Password Hashing: Uses bcrypt for secure password storage.
- Data Encryption: Encryption and decryption functions for sensitive data.
- 2FA Implementation: For an additional layer of security.
