import sqlite3
from database import get_connection
import validators

def add_new_asset(asset_code, name, category, location, condition):
    # Validate essential fields
    fields_to_check = {
        "Asset Code": asset_code, 
        "Name": name, 
        "Category": category, 
        "Location": location, 
        "Condition": condition
    }
    is_valid, msg = validators.validate_required_fields(fields_to_check)
    if not is_valid:
        return False, msg

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO equipment (asset_code, name, category, location, condition, status)
                VALUES (?, ?, ?, ?, ?, 'Available')
            ''', (asset_code, name, category, location, condition))
            conn.commit()
            return True, "Asset added successfully."
            
    except sqlite3.IntegrityError:
        return False, f"Error: Asset code '{asset_code}' already exists."
    except Exception as e:
        return False, f"Database error: {e}"



def get_all_assets():
    """Retrieves all assets to populate the GUI inventory table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT asset_code, name, category, condition, status FROM equipment')
        return cursor.fetchall()
        
        
        
# --- Borrower Registration Logic ---
def add_new_borrower(borrower_code, display_name, department_or_program):
    """Adds a new borrower and rejects duplicate borrower codes."""
    if not all([borrower_code, display_name]):
        return False, "Borrower code and display name are required."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO borrowers (borrower_code, display_name, department_or_program, active)
                VALUES (?, ?, ?, 1)
            ''', (borrower_code, display_name, department_or_program))
            conn.commit()
            return True, "Borrower added successfully."
    except sqlite3.IntegrityError:
        return False, f"Error: Borrower code '{borrower_code}' already exists."
    except Exception as e:
        return False, f"Database error: {e}"



def get_all_borrowers():
    """Retrieves all borrowers for the GUI."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT borrower_code, display_name, department_or_program, active FROM borrowers')
        return cursor.fetchall()



def get_active_borrowers():
    """Retrieves only active borrowers for the checkout dropdown."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT borrower_code, display_name FROM borrowers WHERE active = 1")
        return cursor.fetchall()


def toggle_borrower_status(borrower_code, current_status):
    new_status = 0 if current_status else 1
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE borrowers 
                SET active = ? 
                WHERE borrower_code = ?
            ''', (new_status, borrower_code))
            conn.commit()
            
            status_text = "Active" if new_status else "Inactive"
            return True, f"Borrower {borrower_code} is now {status_text}."
    except Exception as e:
        return False, f"Database error: {e}"


# --- Checkout Logic ---
def get_available_assets():
    """Retrieves only available assets for the checkout dropdown."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT asset_code, name FROM equipment WHERE status = 'Available'")
        return cursor.fetchall()



def checkout_asset(asset_code, borrower_code, borrow_date, due_date):
    """Processes a loan transaction and updates asset status."""
    fields_to_check = {
        "Asset Code": asset_code, 
        "Borrower Code": borrower_code,
        "Borrow Date": borrow_date,
        "Due Date": due_date
    }
    is_valid, msg = validators.validate_required_fields(fields_to_check)
    if not is_valid:
        return False, msg
    
    # Date Validation
    #Validate dates and chronological order
    date_valid, date_msg = validators.validate_checkout_dates(borrow_date, due_date)
    if not date_valid:
        return False, date_msg

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Verify asset is available
            cursor.execute('SELECT asset_id, status FROM equipment WHERE asset_code = ?', (asset_code,))
            asset = cursor.fetchone()
            if not asset:
                return False, "Asset not found."
            if asset['status'] != 'Available':
                return False, f"Asset checkout blocked: currently {asset['status']}."
                
            # Verify borrower is active
            cursor.execute('SELECT borrower_id, active FROM borrowers WHERE borrower_code = ?', (borrower_code,))
            borrower = cursor.fetchone()
            if not borrower:
                return False, "Borrower not found."
            if not borrower['active']:
                return False, "Borrower is inactive and cannot borrow assets."
                
            # Execute Transaction: Save loan and update asset status
            cursor.execute('''
                INSERT INTO loans (asset_id, borrower_id, borrowed_on, due_on, status)
                VALUES (?, ?, ?, ?, 'Active')
            ''', (asset['asset_id'], borrower['borrower_id'], borrow_date, due_date))
            
            cursor.execute('''
                UPDATE equipment SET status = 'Borrowed' WHERE asset_id = ?
            ''', (asset['asset_id'],))
            
            conn.commit()
            return True, "Checkout transaction successful."
    except Exception as e:
        return False, f"Database error: {e}"
        
        
        
        #--returnasset--#
def return_asset(loan_id, return_date):
    #Validate return date
    is_valid, msg = validators.validate_required_fields({"Return Date": return_date})
    if not is_valid:
        return False, msg
        
    date_valid, date_result = validators.validate_date_format(return_date)
    if not date_valid:
        return False, date_result

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Find the active loan and associated asset
            cursor.execute('SELECT asset_id, status FROM loans WHERE loan_id = ?', (loan_id,))
            loan = cursor.fetchone()
            
            if not loan:
                return False, "Loan record not found."
            if loan['status'] != 'Active':
                return False, "This loan is already closed or returned."

            # Update loan status
            cursor.execute('''
                UPDATE loans 
                SET status = 'Returned', returned_on = ? 
                WHERE loan_id = ?
            ''', (return_date, loan_id))
            
            # Make the asset available again
            cursor.execute('''
                UPDATE equipment 
                SET status = 'Available' 
                WHERE asset_id = ?
            ''', (loan['asset_id'],))
            
            conn.commit()
            return True, "Asset returned successfully."
    except Exception as e:
        return False, f"Database error: {e}"
