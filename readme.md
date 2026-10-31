# CampusHub: School Resource Management System

CampusHub is a local desktop application designed to manage the inventory and borrowing workflow for a school computer laboratory or department. It replaces notebook or spreadsheet-based tracking with a searchable, auditable database system.

## Features Included

* **Inventory Management:** Add new assets, track their condition, and view their real-time availability status.

* **Borrower Registration:** Register new borrowers with unique codes and track their active status.

* **Checkout & Return Workflow:** Process loans by selecting available assets and active borrowers. Enforces due dates and automatically updates asset statuses.

* **Monitoring & Validation:** View active and overdue loans. Includes strict date validation and prevents the checkout of unavailable equipment.

* **CSV Export (Stretch Feature):** Export the full asset inventory to a structured CSV file for external reporting.

## Prerequisites

* **Python 3.7 or higher**

* **Tkinter:** (Included in the standard Python library for Windows/macOS. Linux users may need to install it via `sudo apt-get install python3-tk`).

* **SQLite3:** (Included in the standard Python library).

## File Structure

* `main.py` - Application entry point. Ensures the database schema exists and launches the GUI.

* `gui.py` - Contains the Tkinter windows, forms, event bindings, and Treeview tables.

* `database.py` - Manages the SQLite connection and schema creation.

* `models.py` - Defines the core domain classes (Equipment, Borrower, Loan).

* `services.py` - Contains the business logic for checkouts, returns, and database insertion rules.

* `validators.py` - Handles input checking, date validation, and business rule enforcement.

* `reports.py` - Manages database queries for monitoring views and handles the CSV export feature.

* `data/` - Directory automatically generated upon first run to store the `campushub.db` SQLite database file.

## How to Run the Application

1. Download or extract all project files into a single directory (e.g., `campushub`).

2. Open your command prompt or terminal.

3. Navigate to the project directory:

   ```
   cd path/to/campushub
   
   
   
   
   ```

4. Execute the main script:

   ```
   python main.py
   
   
   
   
   ```

   *(Note: Depending on your system configuration, you may need to use `python3 main.py`)*

## First-Time Setup

Upon running `main.py` for the first time, the application will automatically create a `data/` folder containing the `campushub.db` file. No manual database setup is required. Navigate to the **Inventory** and **Borrowers** tabs to begin adding data before processing checkouts.