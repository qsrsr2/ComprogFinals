import sqlite3
from datetime import datetime
from database import get_connection
import csv

def search_assets(search_term):
    """Searches assets by code or name using a partial match filter."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = f"%{search_term}%"
        cursor.execute('''
            SELECT asset_code, name, category, condition, status 
            FROM equipment 
            WHERE asset_code LIKE ? OR name LIKE ?
        ''', (query, query))
        return cursor.fetchall()



def get_active_and_overdue_loans():
    """Retrieves active loans and flags them if they are overdue."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.loan_id, e.asset_code, e.name, b.display_name, l.borrowed_on, l.due_on
            FROM loans l
            JOIN equipment e ON l.asset_id = e.asset_id
            JOIN borrowers b ON l.borrower_id = b.borrower_id
            WHERE l.status = 'Active'
        ''')
        records = cursor.fetchall()
        
        processed_loans = []
        today = datetime.today().date()
        for row in records:
            due_date = datetime.strptime(row['due_on'], '%Y-%m-%d').date()
            calculated_status = "Overdue" if due_date < today else "Active"
            processed_loans.append({
                'loan_id': row['loan_id'],
                'asset_code': row['asset_code'],
                'asset_name': row['name'],
                'borrower': row['display_name'],
                'due_on': row['due_on'],
                'status': calculated_status
            })
        return processed_loans
        
        
        
def export_inventory_to_csv(filepath):
    """Exports all inventory assets to a CSV file."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT asset_code, name, category, location, condition, status FROM equipment')
            records = cursor.fetchall()
            
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write CSV Headers
                writer.writerow(["Asset Code", "Name", "Category", "Location", "Condition", "Status"])
                
                # Write rows
                for row in records:
                    writer.writerow([
                        row['asset_code'], 
                        row['name'], 
                        row['category'], 
                        row['location'], 
                        row['condition'], 
                        row['status']
                    ])
        return True, "Inventory exported successfully."
    except Exception as e:
        return False, f"Export error: {e}"
        
        
        
def generate_custom_report(report_category):
    """
    Uses match-case to dispatch report generation. 
    Returns a tuple of (columns_list, data_records).
    """
    match report_category:
        case "All Assets":
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT asset_code, name, category, status FROM equipment')
                return ("Code", "Name", "Category", "Status"), cursor.fetchall()
                
        case "Available Assets Only":
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT asset_code, name, location FROM equipment WHERE status = 'Available'")
                return ("Code", "Name", "Location"), cursor.fetchall()
                
        case "Active Borrowers":
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT borrower_code, display_name, department_or_program FROM borrowers WHERE active = 1")
                return ("Borrower Code", "Name", "Department"), cursor.fetchall()
                
        case _:
            # Default fallback case if an unknown string is passed
            return ("Error",), [{"Error": "Unknown report category selected."}]
