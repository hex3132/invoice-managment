# 🦷 Billing System

A modern, offline-first Desktop Billing System built with Python and CustomTkinter. It features dynamic search autocomplete, auto-cursor navigation, A4 receipt printing with logo branding, audit modification logging, and non-blocking background auto-updates via GitHub Releases.

---

## ✨ Key Features

* **🎨 Water-Transparent UI:** Clean, modern glassmorphic interface built using CustomTkinter.
* **🔍 Dynamic Product Search:** Instant letter/word matching search with arrow-key navigation.
* **⚡ Single-Click Table Editing:** Edit quantities and discount percentages directly inside the billing table with a single click.
* **📄 Instant A4 Printing:** High-quality A4 invoice generation with automatic browser print triggers and custom logo integration.
* **📜 Old Invoice Manager & Audit Logs:** Edit past receipts and view full audit history logs (tracks who changed what, previous values, new values, and timestamps).
* **🔒 Data Retention Guarantee:** SQLite database is stored separately under `data/hospital_billing.db` to prevent data loss during updates.
* **🔄 Automatic Updates:** Non-blocking background GitHub Release updater that updates binary executables without affecting local patient data.

---

## 📁 Project Structure

```text
Billing System/
├── data/                     # Dedicated directory for database (Excluded from Git)
│   └── hospital_billing.db   # SQLite database storing catalog, invoices & audit history
├── __pycache__/              # Python compiled files
├── app.py                    # Main GUI Application & Business Logic
├── database.py               # SQLite Database Manager & Audit Trail Engine
├── updater.py                # Asynchronous GitHub Release Auto-Updater
├── setup_script.iss          # Inno Setup script for creating Windows setup executable
└── .gitignore                # Git exclusion rules