# Declaration system – Secure Backend System

## Purpose

This project is developed as part of the Software Quality course assignment.  
The goal is to design and implement a secure console-based backend system in Python that demonstrates proper application of security principles in software development.

The focus of this project is not only functionality, but especially:

- Secure authentication
- Input validation
- Protection against common attacks
- Secure data storage
- Logging and monitoring

---

## Project Objective

Build a secure backend system for an internal company application (DeclaratieApp) that allows:

- Employees to submit expense claims
- Managers to approve or reject claims
- A Super Administrator to manage users and system backups

All sensitive data must be protected using proper security mechanisms.

---

## Security Topics Covered

This project explicitly implements and demonstrates the following topics:

### 1. Authentication & Authorization
- Role-based access control (Super Admin, Manager, Employee)
- Secure password hashing (no plaintext storage)
- Login attempt logging
- Protection against brute-force attempts

### 2. Input Validation
- Whitelist-based validation
- Regex validation
- Length and range checks
- Null-byte detection
- Validation of both user-generated and server-generated input

### 3. SQL Injection Protection
- Exclusive use of prepared statements
- No string concatenation in SQL queries
- Parameterized database interactions

### 4. Cryptography
- Symmetric encryption for sensitive database data
- Secure password hashing
- Encrypted log files
- Data protection at rest

### 5. Logging & Monitoring
- All system activities logged
- Suspicious activities flagged
- Encrypted logs readable only through the system
- Alert system for suspicious behavior

### 6. Backup & Restore Security
- Encrypted database backups (ZIP format)
- Multiple backup support
- One-time restore codes
- Role-restricted restore permissions

### 7. Secure Architecture Principles
- Separation of concerns (UI, validation, authorization, data layer)
- Defense in depth
- Secure handling of sensitive information

---

## System Functionality

### User Roles

#### Super Administrator
- Manage Managers and Employees
- Approve or reject claims
- Generate restore codes
- View encrypted logs
- Create and restore backups

#### Manager
- Manage Employees
- Approve or reject claims
- Assign salary-batch identifiers
- Create backups
- Restore backups (with valid restore code)

#### Employee
- Submit travel or home-office claims
- Modify own claims (if not processed)
- View own claims
- Update own password

---

## 🛠 Technologies Used

- Python 3
- SQLite3
- Regular Expressions (re)
- Cryptography library
- Password hashing library

---

## Current Status

This README is temporary and will be updated as development progresses.

The system is currently under development.

Note to developers: delete whole data folder in order to have a clean system